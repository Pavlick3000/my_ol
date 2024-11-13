from django.contrib import admin
from .forms import NomencBookForm
from .models import NomencBook, ProductionTypeBook, BasicUnitBook
from my_erp.models import NomencUnitBook


class NomencBookAdmin(admin.ModelAdmin):
    form = NomencBookForm
    list_display = ('name', 'field_code', 'type_of_reproduction_display', 'basic_unit_display', 'field_fld3222rref')

    def save_model(self, request, obj, form, change):
        obj.write()

class ProductionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'reproduction', 'name')

class BasicUnitBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(ProductionTypeBook, ProductionTypeAdmin)
admin.site.register(NomencBook, NomencBookAdmin)
admin.site.register(BasicUnitBook, BasicUnitBookAdmin)



