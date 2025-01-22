from django.urls import path
from my_erp.views import catalog, editCatalog, deleteRecord, getSelectOptions, update_table, newRecord

app_name = 'catalog'

urlpatterns = [
    path('', catalog, name='index'),
    path('editCatalog/<int:id>/', editCatalog, name='editCatalog'),
    path('getSelectOptions/', getSelectOptions, name='getSelectOptions'),
    path('deleteRecord/<int:id>/', deleteRecord, name='deleteRecord'),
    path('newRecord/', newRecord, name='newRecord'),
    path('update_table/', update_table, name='update_table'),
]
