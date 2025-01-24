import binascii
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.views.decorators.cache import cache_page
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
    session_key = request.session.session_key
    print("Текущий номер сессии:", session_key)
    context = {
        'title': 'ERP - main',
        'is_promotion': False,
            }
    return render(request, 'my_erp/index.html', context)

# def index(request):
#     session_key = request.session.session_key
#     print("Текущий номер сессии:", session_key)
#     context = {
#         'title': 'ERP - main',
#         'is_promotion': False,
#             }
#     return render(request, 'my_erp/index.html', context)

# Представление для страницы Каталог
@group_required("Конструктор", "Гость")
@login_required
def catalog(request):
    nbook = NomencBook.objects.only('id','type_of_reproduction', 'basic_unit', 'field_code', 'name').order_by('-id')

    # Подгружаем данные для выбора
    type_of_reproduction_choices = {
        prod.reproduction: prod.name
        for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False)
    }
    basic_unit_choices = {
        unit.db_id: unit.name
        for unit in BasicUnitBook.objects.all()
    }

    page_number = request.GET.get('page', 1)
    paginator = Paginator(nbook, 20)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'title': 'ERP - catalog',
        'type_of_reproduction_choices': type_of_reproduction_choices,
        'basic_unit_choices': basic_unit_choices,
        # 'form': form,
        'form': None,
        }
    return render(request, 'my_erp/catalog.html', context)

# Представление для формы "Новая запись"
@group_required("Конструктор")
@login_required
def newRecord(request):
    post_data = request.POST.copy()

    # Преобразуем значение basic_unit в hex (если оно есть)
    if 'basic_unit' in post_data:
        try:
            # Преобразуем значение basic_unit в bytes и затем в hex
            basic_unit_bytes = bytes.fromhex(post_data['basic_unit'])
            post_data['basic_unit'] = basic_unit_bytes.hex().upper()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid basic_unit value'}, status=400)

    # Преобразуем значение type_of_reproduction в hex (если оно есть)
    if 'type_of_reproduction' in post_data:
        try:
            # Преобразуем значение type_of_reproduction в bytes и затем в hex
            type_of_reproduction_bytes = bytes.fromhex(post_data['type_of_reproduction'])
            post_data['type_of_reproduction'] = type_of_reproduction_bytes.hex().upper()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid type_of_reproduction value'}, status=400)

    # Инициализация формы с преобразованными данными
    form = NomencBookForm(data=post_data)

    # Проверяем корректность данных формы
    if form.is_valid():
        try:
            # Сохраняем объект через форму
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

    if form.is_valid():
        try:
            # Сохраняем объект через форму
            form.save()
            # request.session.modified = True
            return JsonResponse({"status": "success", "message": "Запись успешно обновлена."})
        except (binascii.Error, ValueError) as e:
            return JsonResponse({"status": "error", "message": f"Ошибка декодирования данных: {str(e)}"}, status=400)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400) # Значение с котором всё работало

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

# Представление для обновления таблицы, после изменения записи
def update_table(request):
    nbook = NomencBook.objects.only('id', 'type_of_reproduction', 'basic_unit', 'field_code', 'name').order_by('-id')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(nbook, 20)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    type_of_reproduction_choices = {
        prod.reproduction: prod.name
        for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False)
    }
    basic_unit_choices = {
        unit.db_id: unit.name
        for unit in BasicUnitBook.objects.all()
    }

    data = [
        {
            'id': product.id,
            'field_code': product.field_code,
            'name': product.name,
            'type_of_reproduction': type_of_reproduction_choices.get(product.type_of_reproduction, ''),
            'basic_unit': basic_unit_choices.get(product.basic_unit, ''),
            'url': reverse('catalog:editCatalog', args=[product.id]),
        }
        for product in page_obj
    ]
    response_data = {'data': data, 'has_next': page_obj.has_next(), 'has_previous': page_obj.has_previous()}
    return JsonResponse(response_data, safe=False)
