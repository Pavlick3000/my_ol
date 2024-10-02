from django.contrib import admin
from .forms import NomencBookAdminForm
from .models import NomencBook, ProductionTypeBook, BasicUnitBook

class NomencBookAdmin(admin.ModelAdmin):
    form = NomencBookAdminForm
    list_display = ('name', 'field_code', 'type_of_reproduction_display', 'basic_unit_display')

    def save_model(self, request, obj, form, change):
        obj.write()

class ProductionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'reproduction', 'name')

class BasicUnitBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(ProductionTypeBook, ProductionTypeAdmin)
admin.site.register(NomencBook, NomencBookAdmin)
admin.site.register(BasicUnitBook, BasicUnitBookAdmin)
