import binascii
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import NomencBook, ProductionTypeBook, BasicUnitBook
from my_erp.forms import NomencBookForm

# Create your views here.
def index(request):
    context = {
        'title': 'ERP - main',
        'is_promotion': False,
            }
    return render(request, 'my_erp/index.html', context)

# Представление для формы "Новая запись"
def catalog(request):
    if request.method == 'POST':
        form = NomencBookForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog:index') # Возвращаемся на ту же страницу для обновления после записи
    else:
        form = NomencBookForm()

    context = {
        'title': 'ERP - catalog',
        'products': NomencBook.objects.all().order_by('-id')[:20],
        'form': form,
        }
    return render(request, 'my_erp/catalog.html', context)

# Представление для формы "Изменить запись"
def editCatalog(request, id):
    product = get_object_or_404(NomencBook, id=id)
    form = NomencBookForm(request.POST or None, instance=product)
    type_of_reproduction_hex = request.POST.get('type_of_reproduction')
    basic_unit_hex = request.POST.get('basic_unit')

    if form.is_valid():
        try:
            # Декодируем hex-строку в бинарный формат
            reproduction_binary = binascii.unhexlify(type_of_reproduction_hex)
            basic_unit_binary = binascii.unhexlify(basic_unit_hex)

            # Обновляем поле reproduction и db_id в форме
            form.instance.reproduction = reproduction_binary
            form.instance.db_id = basic_unit_binary

            # Сохраняем объект через форму
            form.save()
            return JsonResponse({"status": "success", "message": "Запись успешно обновлена."})
        except (binascii.Error, ValueError) as e:
            return JsonResponse({"status": "error", "message": f"Ошибка декодирования данных: {str(e)}"}, status=400)
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400) # Значение с котором всё работало

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