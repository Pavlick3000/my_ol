from django.contrib import admin
from .models import OrdersBook, BuyerBook, RealizationBook, OrderList, InfoRg23775, SpecList


class OrdersBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'cost', 'buyer')

class BuyerBookAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'inn_code')

class RealizationBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'date_of')

class InfoRg23775Admin(admin.ModelAdmin):
    list_display = ('id', 'nomenclature_name', 'sp_idrref')

    def nomenclature_name(self, obj):
        return obj.name_nomenc.name if obj.name_nomenc else '-'
    nomenclature_name.short_description = 'nomenclature_name'


class SpecListAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference259_idrref', 'line_number', 'nomenclature_name', 'quantity')
    # search_fields = ['id']

    search_fields = ['id__exact']  # Точный поиск по ID
    show_full_result_count = True  # Показывать реальное количество результатов

    def get_search_results(self, request, queryset, search_term):
        # Переопределяем поиск для обработки всех записей
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(id=search_term_as_int)
        except ValueError:
            pass
        return queryset, use_distinct

    def nomenclature_name(self, obj):
        return obj.nomenclature.name if obj.nomenclature else '-'
    nomenclature_name.short_description = 'nomenclature_name'

class OrderListAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'nomenclature_name', 'line_number', 'quantity', 'price', 'amount', 'amount_nalog', 'sum_total')
    ordering = ('order__number',)  # Сортировка от большего к меньшему по id

    def nomenclature_name(self, obj):
        return obj.nomenclature.name if obj.nomenclature else '-'
    nomenclature_name.short_description = 'nomenclature_name'

    def order_number(self, obj):
        return obj.order.number if obj.order else '-'
    order_number.short_description = 'Order Number'


admin.site.register(OrdersBook, OrdersBookAdmin)
admin.site.register(BuyerBook, BuyerBookAdmin)
admin.site.register(RealizationBook, RealizationBookAdmin)
admin.site.register(OrderList, OrderListAdmin)
admin.site.register(InfoRg23775, InfoRg23775Admin)
admin.site.register(SpecList, SpecListAdmin)
