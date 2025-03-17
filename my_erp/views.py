import binascii
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse

from .models import NomencBook, ProductionTypeBook, BasicUnitBook, NomencUnitBook
from my_erp.forms import NomencBookForm

# Декоратор проверки прав
def group_required(*group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name__in=group_name).exists():
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Проверяем, AJAX ли запрос
                    return render(request, 'my_erp/no_modal.html', status=403)
                else:
                    return render(request, 'my_erp/no_modal.html', status=403)  # На случай прямого запроса
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Представление главной страницы
def index(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    can_view_catalog = "Гость" in user_groups or "Конструктор" in user_groups
    can_view_orders = "Гость" in user_groups or "Конструктор" in user_groups

    context = {
        'title': 'ERP - main',
        'is_promotion': False,
        'can_view_catalog': can_view_catalog,
        'can_view_orders': can_view_orders,
        }
    return render(request, 'my_erp/index.html', context)

# Представление для страницы Каталог, включая обновление при внесении изменений в таблицу
def catalog(request):
    search_query = request.GET.get('search', '')
    nbook = NomencBook.objects.only('id', 'type_of_reproduction', 'basic_unit', 'field_code', 'name', 'qnt')

    if search_query:
        nbook = nbook.filter(
            Q(field_code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    nbook = nbook.order_by('-id')

    # Загружаем справочники
    type_of_reproduction_choices = {
        prod.reproduction: prod.name
        for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False)
    }
    basic_unit_choices = {
        unit.db_id: unit.name
        for unit in BasicUnitBook.objects.all()
    }

    # Пагинация
    page_number = request.GET.get('page', 1)
    paginator = Paginator(nbook, 20)
    page_obj = paginator.get_page(page_number)

    # Проверяем, является ли запрос AJAX-запросом
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = [
            {
                'id': product.id,
                'field_code': product.field_code,
                'name': product.name,
                'type_of_reproduction': type_of_reproduction_choices.get(product.type_of_reproduction, ''),
                'basic_unit': basic_unit_choices.get(product.basic_unit, ''),
                'qnt': product.qnt,
                'url': reverse('catalog:editCatalog', args=[product.id]),
            }
            for product in page_obj
        ]
        response_data = {
            'data': data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            # 'num_pages': paginator.num_pages,  # Добавляем количество страниц
            # 'current_page': page_obj.number  # Добавляем текущую страницу
        }
        return JsonResponse(response_data, safe=False)

    # Если запрос не AJAX, рендерим HTML-страницу
    context = {
        'page_obj': page_obj,
        'title': 'ERP - номенклатура',
        'type_of_reproduction_choices': type_of_reproduction_choices,
        'basic_unit_choices': basic_unit_choices,
        'search_query': search_query,
        'is_paginated': paginator.num_pages > 1,
        'form': None,
    }
    return render(request, 'my_erp/catalog.html', context)

# Представление для формы "Новая запись"
@group_required("Конструктор")
@login_required
def newRecord(request):
    post_data = request.POST.copy()

    # Инициализация формы с преобразованными данными
    form = NomencBookForm(data=post_data)

    # Проверяем корректность данных формы
    if form.is_valid():
        try:
            form.save()
            return JsonResponse({"status": "success", "message": "Запись успешно добавлена."})

        except (binascii.Error, ValueError) as e:
            return JsonResponse({"status": "error", "message": f"Ошибка декодирования данных: {str(e)}"},
                                status=400)

    # Если форма не прошла валидацию, выводим ошибки
    print("Form errors:", form.errors)
    return JsonResponse({'status': 'error', 'message': 'Invalid form data'}, status=400)

# Представление для формы "Изменить запись"
@group_required("Конструктор")
@login_required
def editCatalog(request, id):
    product = get_object_or_404(NomencBook, id=id)
    form = NomencBookForm(request.POST or None, instance=product)

    # Загружаем справочники
    type_of_reproduction_choices = {
        prod.reproduction: prod.name
        for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False)
    }
    basic_unit_choices = {
        unit.db_id: unit.name
        for unit in BasicUnitBook.objects.all()
    }

    if form.is_valid():
        try:
            product = form.save()  # Сохраняем объект через форму

            # Подготовка данных для обновления таблицы
            updated_product_data = {
                "id": product.id,
                "field_code": product.field_code,
                "name": product.name,
                'type_of_reproduction': type_of_reproduction_choices.get(product.type_of_reproduction, ''),
                'basic_unit': basic_unit_choices.get(product.basic_unit, ''),
                "qnt": product.qnt,
            }

            return JsonResponse({"status": "success", "message": "Запись успешно обновлена.", "data": updated_product_data})
        except (binascii.Error, ValueError) as e:
            return JsonResponse({"status": "error", "message": f"Ошибка декодирования данных: {str(e)}"}, status=400)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

# Представление для "Удалить запись"
@group_required("Конструктор")
@login_required
def deleteRecord(request, id):
    if request.method == 'POST':
        record = get_object_or_404(NomencBook, id=id)
        NomencUnitBook.objects.filter(field_ownerid_rrref=record.db_id).delete() # Так же удаляем запись из таблицы NomencUnitBook (_Reference105)
        record.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Представление для выпадающих списков формы "Изменить запись" - конвертация в hex (иначе JSON запрос ругается на бинарные данные)
def getSelectOptions(request):
        try:
            # Получаем все записи из ProductionTypeBook
            reproduction_choices = ProductionTypeBook.objects.all()
            reproduction_choices_list = [
                {
                    'id': item.id,
                    'name': item.name,
                    'reproduction': item.reproduction.hex().upper() if item.reproduction else None # Преобразуем бинарное поле reproduction в Base64
                }
                for item in reproduction_choices
            ]

            # Получаем все записи из BasicUnitBook
            basic_units = BasicUnitBook.objects.all()
            basic_units_list = [
                {
                    'id': item.id,
                    'name': item.name,
                    'db_id': item.db_id.hex().upper() if item.db_id else None # Преобразуем бинарное поле reproduction в Base64
                }
                for item in basic_units
            ]

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'reproduction_choices': reproduction_choices_list,
            'basic_units': basic_units_list,
        })

@receiver([post_save, post_delete], sender=NomencBook)
def clear_cache_on_update(sender, instance, **kwargs):
    # Очистка всего кэша или конкретной страницы
    cache.clear()





