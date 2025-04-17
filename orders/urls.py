from django.urls import path
from orders.views import orders, orderDetails

app_name = 'orders'

urlpatterns = [
    path('', orders, name='orders'),
    path('orderDetails/<int:id>/', orderDetails, name='orderDetails'),
]