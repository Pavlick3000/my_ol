from django.urls import path
from orders.views import orders, orderDetails, specsDetails, specsDetailsSQL

app_name = 'orders'

urlpatterns = [
    path('', orders, name='orders'),
    path('orderDetails/<int:id>/', orderDetails, name='orderDetails'),
    path('specsDetails/<int:itemId>/', specsDetails, name='specsDetails'),
    path('specsDetailsSQL/<int:orderId>/', specsDetailsSQL, name='specsDetailsSQL'),
]