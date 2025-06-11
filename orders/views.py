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

# "Заказы покупателей"
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

# Детали "Заказа покупателя"
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
        print(f"Получен order_items из запроса: {order_items}")

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

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import traceback

@require_GET
def specsDetailsSQL(request, orderId):

    try:
        raw_sql = """
        SET NOCOUNT ON;
        DECLARE @MaxIds TABLE (
            _Fld23776RRef binary(16),
            MaxId int
        );
        INSERT INTO @MaxIds (_Fld23776RRef, MaxId)
        SELECT _Fld23776RRef, MAX(id) AS MaxId FROM _InfoRg23775 GROUP BY _Fld23776RRef;

        CREATE TABLE #RecursiveBOM (
            ParentID binary(16) NOT NULL,
            ComponentID binary(16) NOT NULL,
            Quantity numeric(30,6) NOT NULL,
            Level int NOT NULL
        );
        WITH RecursiveBOM AS (
            SELECT d._Document400_IDRRef AS ParentID, d._Fld7944RRef AS ComponentID,
                   CAST(d._Fld7941 AS numeric(30,6)) AS Quantity, 1 AS Level
            FROM _Document400_VT7937 d
            INNER JOIN _Document400 doc ON doc._IDRRef = d._Document400_IDRRef
            WHERE doc.id = %s

            UNION ALL
            SELECT r.ComponentID, c._Fld23223RRef,
                   CAST(r.Quantity * c._Fld23225 AS numeric(30,6)), Level + 1
            FROM RecursiveBOM r
            INNER JOIN _Reference175 ref ON ref._IDRRef = r.ComponentID
            INNER JOIN _InfoRg23220 c ON c._Fld23221RRef = r.ComponentID
            WHERE ref._Fld3203RRef IN (
                0xB7E6DB21B73167DF4BB0CD4A7D143950,
                0x96CF67336CF685BA4EFFDD934DCF15E6)

            UNION ALL
            SELECT r.ComponentID, c._Fld4125_RRRef,
                   CAST(r.Quantity * c._Fld4127 AS numeric(30,6)), Level + 1
            FROM RecursiveBOM r
            INNER JOIN _Reference175 ref ON ref._IDRRef = r.ComponentID
            INNER JOIN @MaxIds mi ON mi._Fld23776RRef = r.ComponentID
            INNER JOIN _InfoRg23775 rel 
                ON rel._Fld23776RRef = mi._Fld23776RRef AND rel.id = mi.MaxId
            INNER JOIN _Reference259_VT4122 c 
                ON c._Reference259_IDRRef = rel._Fld23779RRef
            WHERE ref._Fld3203RRef NOT IN (
                0xB7E6DB21B73167DF4BB0CD4A7D143950,
                0x96CF67336CF685BA4EFFDD934DCF15E6
            )
        )
        INSERT INTO #RecursiveBOM (ParentID, ComponentID, Quantity, Level)
        SELECT ParentID, ComponentID, Quantity, Level FROM RecursiveBOM WHERE Level > 0;

        CREATE NONCLUSTERED INDEX IX_RecursiveBOM_ComponentID 
            ON #RecursiveBOM (ComponentID);

        SELECT
            comp._Description AS ComponentName,
            SUM(r.Quantity) AS TotalQuantity,
            cat._Description AS CategoryName,
            catParent._Description AS CategoryParentName,
            catGrandParent._Description AS CategoryGrandParentName
        FROM #RecursiveBOM r
        LEFT JOIN _Reference175 comp ON comp._IDRRef = r.ComponentID
        LEFT JOIN _Reference175 cat ON cat._IDRRef = comp._ParentIDRRef
        LEFT JOIN _Reference175 catParent ON catParent._IDRRef = cat._ParentIDRRef
        LEFT JOIN _Reference175 catGrandParent ON catGrandParent._IDRRef = catParent._ParentIDRRef
        GROUP BY
            comp._Description,
            cat._Description,
            catParent._Description,
            catGrandParent._Description
        ORDER BY ComponentName;

        DROP TABLE #RecursiveBOM;
        """

        with connection.cursor() as cursor:
            cursor.execute(raw_sql, [orderId])
            if cursor.description is None:
                # SELECT не вернул ничего
                return JsonResponse({"specs": []})

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in rows]
        return JsonResponse({"specs": data})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)


