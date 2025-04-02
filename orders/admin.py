from django.contrib import admin
from .models import OrdersBook, BuyerBook, RealizationBook

class OrdersBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'cost', 'buyer')

class BuyerBookAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'inn_code')

class RealizationBookAdmin(admin.ModelAdmin):
    list_display = ('number', 'date_of')

admin.site.register(OrdersBook, OrdersBookAdmin)
admin.site.register(BuyerBook, BuyerBookAdmin)
admin.site.register(RealizationBook, RealizationBookAdmin)
