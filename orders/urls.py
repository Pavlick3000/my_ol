from django.urls import path
from orders.views import orders, orderDetails, specsDetails, specsDetailsSQL, getSpecTreeByItem, getFlatMaterials

app_name = 'orders'

urlpatterns = [
    path('', orders, name='orders'),
    path('orderDetails/<int:id>/', orderDetails, name='orderDetails'),
    path('specsDetails/<int:itemId>/', specsDetails, name='specsDetails'),
    path('specsDetailsSQL/<int:orderId>/', specsDetailsSQL, name='specsDetailsSQL'),
    path('getSpecTreeByItem/<int:orderId>/<int:itemId>/', getSpecTreeByItem, name='getSpecTreeByItem'),
    path('getFlatMaterials/<int:orderId>/', getFlatMaterials, name='getFlatMaterials'),
    path('getFlatMaterials/<int:orderId>/item/<int:itemId>/', getFlatMaterials, name='getFlatMaterials_by_item'),

]