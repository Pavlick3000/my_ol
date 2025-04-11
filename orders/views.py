from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import OrdersBook, OrderList
from django.db.models import Q

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

    # ordersBook = ordersBook.order_by('-id')
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

def orderDetails(request, id):
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     # Это AJAX-запрос
    #     order = get_object_or_404(OrdersBook, id=id)
    #     data = {
    #         'formatted_number': order.formatted_number,
    #         # другие данные...
    #     }
    #     return JsonResponse(data)
    # return render(request, 'orders/orders.html')
    order_id = request.GET.get('order_id')
    if order_id:
        items = OrderList.objects.filter(order__id=order_id)
        data = [
            {
                'nomenclature': item.nomenclature.name if item.nomenclature else '-',
                'quantity': float(item.quantity),
                'line_number': int(item.line_number),
                'amount': float(item.amount),
                'amount_nalog': float(item.amount_nalog),
                'sum_total': float(item.sum_total)
            }
            for item in items
        ]
        return JsonResponse({'items': data})
    return JsonResponse({'items': []})