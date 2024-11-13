from django.urls import path
from my_erp.views import catalog, editCatalog

app_name = 'catalog'

urlpatterns = [
    path('', catalog, name='index'),
    path('editCatalog/<int:id>/', editCatalog, name='editCatalog'),
]

