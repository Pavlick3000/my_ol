from django.contrib import admin
from .models import OrdersBook, BuyerBook, RealizationBook, OrderList

class OrdersBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'cost', 'buyer')

class BuyerBookAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'inn_code')

class RealizationBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'date_of')

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
