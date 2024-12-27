import binascii

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.views.decorators.cache import cache_page
from django.core.cache import cache

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import NomencBook, ProductionTypeBook, BasicUnitBook, NomencUnitBook
from my_erp.forms import NomencBookForm

# Представление главной страницы
def index(request):
    context = {
        'title': 'ERP - main',
        'is_promotion': False,
            }
    return render(request, 'my_erp/index.html', context)

# Представление для страницы Каталог
def catalog(request):
    session_key = request.session.session_key
    print("Текущий номер сессии:", session_key)
    nbook = NomencBook.objects.only('id','type_of_reproduction', 'basic_unit', 'field_code', 'name').order_by('-id')

    # Подгружаем данные для выбора
    type_of_reproduction_choices = {
        prod.reproduction: prod.name
        # prod.reproduction: prod.name
        for prod in ProductionTypeBook.objects.filter(reproduction__isnull=False)
    }
    basic_unit_choices = {
        unit.db_id: unit.name
        for unit in BasicUnitBook.objects.all()
    }

    page_number = request.GET.get('page', 1)
    paginator = Paginator(nbook, 20)

    if request.method == 'POST':
        form = NomencBookForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:index') # Возвращаемся на ту же страницу для обновления после записи
    else:
        form = NomencBookForm()

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
        'form': form,
        }
    return render(request, 'my_erp/catalog.html', context)

# Представление для формы "Изменить запись"
def editCatalog(request, id):
    product = get_object_or_404(NomencBook, id=id)
    form = NomencBookForm(request.POST or None, instance=product)

    if form.is_valid():
        try:
            # Сохраняем объект через форму
            form.save()
            return JsonResponse({"status": "success", "message": "Запись успешно обновлена."})
        except (binascii.Error, ValueError) as e:
            return JsonResponse({"status": "error", "message": f"Ошибка декодирования данных: {str(e)}"}, status=400)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400) # Значение с котором всё работало

# Представление для "Удалить запись"
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