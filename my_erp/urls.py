from django.urls import path
from my_erp.views import catalog, editCatalog, getSelectOptions, deleteRecord

app_name = 'catalog'

urlpatterns = [
    path('', catalog, name='index'),
    path('editCatalog/<int:id>/', editCatalog, name='editCatalog'),
    path('getSelectOptions/', getSelectOptions, name='getSelectOptions'),
    path('deleteRecord/<int:id>/', deleteRecord, name='deleteRecord'),
]
