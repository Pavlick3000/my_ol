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

    try:
        order = OrdersBook.objects.get(pk=id)
        order_items = order.order_items.select_related('nomenclature')

        order_items = order_items.order_by('line_number')

        data = {
            'number': order.formatted_number(),
            'date_of_formation': order.date_of_formation.strftime('%d.%m.%Y'),
            'buyer': order.buyer.description if order.buyer else 'неизвестен',
            'total': float(order.cost),
            'items': [
                {
                    'line_number': item.line_number,
                    'name': item.nomenclature.name,
                    'price': item.price,
                    'amount': item.amount,
                    'quantity': item.quantity,
                    'total': item.sum_total,
                }
                for item in order_items
            ]
        }

        return JsonResponse(data)
    except OrdersBook.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
