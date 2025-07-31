from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from django.views.decorators.cache import cache_page

from django.views.decorators.http import require_GET
from django.core.cache import cache

from my_erp.models import NomencBook
from .models import OrdersBook, SpecList, Inforg23220, OrderList
from django.db.models import Q

import traceback

from src.py.utils import get_specs_tree, group_children, group_flat_materials
from django.db import connection


# "Заказы покупателей" - отображаем все заказы
@cache_page(20)
def orders(request):
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    ordersBook = OrdersBook.objects.select_related(
        'buyer'  # Прямая связь с BuyerBook
    ).prefetch_related(
        'realizations'  # Обратная связь с RealizationBook
    ).only(
        'db_id',  # Поле id в OrdersBook
        'number',  # Поле number в OrdersBook
        'cost',  # Поле cost в OrdersBook
        'date_of_formation',  # Поле date_of_formation в OrdersBook
        'shipment',  # Поле shipment в OrdersBook
        'payment',  # Поле payment в OrdersBook
        'buyer__description',  # Поле description в BuyerBook
        'realizations__date_of'  # Поле date_of в RealizationBook
    )

    if search_query:
        ordersBook = ordersBook.filter(
            Q(number__icontains=search_query) |
            Q(buyer__description__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    ordersBook = ordersBook.order_by('-date_of_formation')
    paginator = Paginator(ordersBook, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'ERP - заказы',
        'is_promotion': False,
        'search_query': search_query,
        'is_paginated': paginator.num_pages > 1,
        'form': None,
        }
    return render(request, 'orders/orders.html', context)

# Детали "Заказа покупателя" - отображаем, что внутри выбранного заказа
@require_GET
def orderDetails(request, id):
    try:
        refresh = request.GET.get("refresh") == "1"
        cache_key = f"order_details:{id}"

        if refresh:
            cache.delete(cache_key)

        data = cache.get(cache_key)
        if data:
            return JsonResponse(data)

        order = OrdersBook.objects.get(pk=id)
        order_items = order.order_items.select_related('nomenclature').order_by('line_number')
        # print(f"Получен order_items из запроса: {order_items}")

        items_data = []
        for item in order_items:
            reproduction = item.nomenclature.type_of_reproduction
            key = reproduction.hex().upper() if reproduction else 'Вид воспроизводства не выбран'

            items_data.append({
                'id_for_filter_material': item.id,
                'id': item.nomenclature.id,
                'line_number': item.line_number,
                'name': item.nomenclature.name,
                'key': key,
                'key_material': item.nomenclature.view.hex().upper(),
                'price': item.price,
                'amount': item.amount,
                'quantity': item.quantity,
                'total': item.sum_total,
            })

        data = {
            'number': order.formatted_number(),
            'date_of_formation': order.date_of_formation.strftime('%d.%m.%Y'),
            'buyer': order.buyer.description if order.buyer else 'неизвестен',
            'total': float(order.cost),
            'items': items_data,
        }

        cache.set(cache_key, data, timeout=1)  # кэш на 10 минут
        return JsonResponse(data)

    except OrdersBook.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

# Спецификации внутри заказа по позиции или список комплектующих (для номенклатуры без СП, т.е. для вида воспроизводства "Покупка" и "Переработка")
@require_GET # Можно только Get, POST нельзя ) потестим как оно
def specsDetails(request, itemId):
    try:
        components_keys = [
            "96CF67336CF685BA4EFFDD934DCF15E6",  # Принятые в переработку
            "B7E6DB21B73167DF4BB0CD4A7D143950"  # Покупка
        ]

        material_keys = [
            "BA800CC47A229A2311E6C84091631332",  # Товар
            "BA800CC47A229A2311E6C84091631333"  # Материал
        ]

        key = request.GET.get("key", "").strip().upper()
        use_components = key in components_keys

        key_material = request.GET.get("key_material", "").strip().upper()
        nomenc = get_object_or_404(NomencBook, pk=itemId)
        db_id = nomenc.db_id

        specs_data = []
        title_prefix = ""

        id_for_filter_material = request.GET.get('id_for_filter_material', '') # Получаем значение id_for_filter_material для фильтрации номенклатуры под конкретный заказ

        if key_material in material_keys:
            order_lines = OrderList.objects.filter(id=id_for_filter_material)

            for line in order_lines:
                specs_data.append({
                    "line_number": line.line_number,
                    "name": line.nomenclature.name,
                    "quantity": float(line.quantity),
                    "basic_unit": line.basic_unit_name
                })

            title_prefix = "Материал"
            return JsonResponse({"specs": specs_data, "title_prefix": title_prefix, "use_quantity_multiplier": False})

        # Сначала пробуем получить спецификацию
        if not use_components:
            specs = SpecList.get_latest_specs(db_id)
            if specs.exists():
                for spec in specs:
                    specs_data.append({
                        "id": spec.id,
                        "name": spec.nomenclature.name,
                        "line_number": int(spec.line_number),
                        "quantity": float(spec.quantity),
                        "basic_unit": spec.basic_unit_name
                    })
                specs_data.sort(key=lambda x: x["line_number"])
                title_prefix = "Спецификация"
            else:
                # Если спецификации нет, переходим к компонентам
                use_components = True

        # Если нужно использовать компоненты (либо по ключу, либо после fallback-а)
        if use_components:
            components = Inforg23220.objects.filter(name_nomenc=db_id)
            if not components.exists():
                return JsonResponse({"error": "Нет зарегистрированных комплектующих"}, status=404)

            for idx, comp in enumerate(components, start=1):
                specs_data.append({
                    "line_number": idx,
                    "name": comp.nomenclature.name,
                    "quantity": float(comp.quantity),
                    "basic_unit": comp.basic_unit_name
                })
            title_prefix = "Комплектующие"

        return JsonResponse({"specs": specs_data, "title_prefix": title_prefix})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)

# Это старый вызов процедуры - пока оставлю на всякий случай
@require_GET
def specsDetailsSQL(request, orderId):
    try:
        data = get_specs_tree(orderId)
        return JsonResponse({
            'success': True,
            'count': len(data),
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# Вызов SQL процедуры, передаем ID заказа и ID номенклатуры для фильтрации. Для дерева.
def getSpecTreeByItem(request, orderId, itemId):
    try:
        full_tree = get_specs_tree(orderId, itemId)
        raw_subtree = findSpecSubtreeByItemId(full_tree, itemId)

        if not raw_subtree:
            print("Поддерево не найдено")

        # Группируем поддерево
        grouped_subtree = group_children(raw_subtree)

        return JsonResponse({'items': grouped_subtree})

    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Возвращает список дочерних элементов дерева по указанному ID номенклатуры
def findSpecSubtreeByItemId(tree, itemId, level=0):
    # indent = '  ' * level # Для отступов
    for node in tree:
        if node.get('ComponentDbId') == itemId:
            return node.get('children', [])

        children = node.get('children', [])
        if children:
            result = findSpecSubtreeByItemId(children, itemId, level + 1)
            if result:
                return result
    return []

# Возвращает список материалов
def getFlatMaterials(request, orderId, itemId=None):
    try:
        node_path = request.GET.get('path')  # получаем path из query-параметра
        category_name = request.GET.get('category') # получаем category из query-параметра

        # Если path задан и itemId не передан, то берем первый ID из path
        if node_path and not itemId:
            try:
                itemId = int(node_path.split(' > ')[0])
            except (ValueError, IndexError):
                itemId = None  # fallback, чтобы не ломать вызов

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC GetSpecsDetailsByOrderId %s, NULL, %s, %s",
                [orderId, itemId, node_path]
            )

            if not cursor.description:
                return JsonResponse({'items': []})

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            # Фильтрация по пути (на всякий случай)
            if node_path:
                path_prefix = node_path + ' > '
                rows = [
                    row for row in rows
                    if str(row[columns.index('Path')]).startswith(path_prefix)
                ]

            # Получаем все пути
            all_paths = set(str(row[columns.index('Path')]) for row in rows)

            # Собираем все родительские пути (префиксы)
            parent_paths = set()
            for path in all_paths:
                parts = path.split(' > ')
                for i in range(1, len(parts)):
                    parent_path = ' > '.join(parts[:i])
                    parent_paths.add(parent_path)

            # Оставляем только те строки, чей Path не является родительским
            leaf_rows = [
                row for row in rows
                if str(row[columns.index('Path')]) not in parent_paths
            ]

            # Группировка одинаковых материалов
            result = group_flat_materials(leaf_rows, columns)

            unique_categories = sorted(set(
                row[columns.index('CategoryName')]
                # for row in rows
                for row in leaf_rows # из категорий листовых элементов
                if row[columns.index('CategoryName')] is not None

            ))

            # Фильтрация по категории
            if category_name:
                result = [
                    item for item in result
                    if item.get('CategoryName') == category_name
                ]

        return JsonResponse({
            'items': result,
            'categories': unique_categories,
        })

    except Exception as e:
        print(f"Exception in getFlatMaterials: {e}")
        return JsonResponse({'error': str(e)}, status=500)







