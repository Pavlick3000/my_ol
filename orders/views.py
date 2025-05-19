from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET

from my_erp.models import NomencBook
from .models import OrdersBook, SpecList, Inforg23220
from django.db.models import Q

import traceback

# Заказы
def orders(request):
    search_query = request.GET.get('search', '')
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

    page_number = request.GET.get('page', 1)
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

# Детали заказа
def orderDetails(request, id):
    try:
        order = OrdersBook.objects.get(pk=id)
        order_items = order.order_items.select_related('nomenclature')
        order_items = order_items.order_by('line_number')

        has_missing_keys = False

        items_data = []
        for item in order_items:

            # Обыгрываем отсутствие информации по "Виду воспроизводства"
            type_of_reproduction = item.nomenclature.type_of_reproduction
            if type_of_reproduction:
                key = type_of_reproduction.hex().upper()
            else:
                key = 'Вид воспроизводства не выбран'

            items_data.append({
                'id': item.nomenclature.id,
                'line_number': item.line_number,
                'name': item.nomenclature.name,
                'key': key,
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

        return JsonResponse(data)
    except OrdersBook.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

# Спецификации внутри заказа по позиции или список комплектующих (для номенклатуры без СП, т.е. для вида воспроизводства "Покупка" и "Переработка")
@require_GET # Можно только Get, POST нельзя ) потестим как оно
def specsDetails(request, itemId):
    try:
        components_keys = [
            "8A9F19A74BAB45774108C4B1FE652ABF",  # Переработка
            "B7E6DB21B73167DF4BB0CD4A7D143950"  # Покупка
        ]

        key = request.GET.get("key", "").strip().upper()
        nomenc = get_object_or_404(NomencBook, pk=itemId)
        db_id = nomenc.db_id

        specs_data = []
        title_prefix = ""

        use_components = key in components_keys

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