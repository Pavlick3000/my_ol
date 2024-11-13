from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from .models import NomencBook, ProductionTypeBook, BasicUnitBook
from my_erp.forms import NomencBookForm
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.
def index(request):
    context = {
        'title': 'ERP - main',
        'is_promotion': False,
            }
    return render(request, 'my_erp/index.html', context)

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
        'products': NomencBook.objects.all().order_by('-id')[:15],
        'form': form,
        }
    return render(request, 'my_erp/catalog.html', context)

def editCatalog(request, id):
    product = get_object_or_404(NomencBook, id=id)
    form = NomencBookForm(request.POST or None, instance=product)

    if form.is_valid():
        form.save()
        return JsonResponse({"status": "success", "message": "Запись успешно обновлена."})
    else:
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)
