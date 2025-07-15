from django.urls import path
from orders.views import orders, orderDetails, specsDetails, specsDetailsSQL, get_spec_tree_by_item

app_name = 'orders'

urlpatterns = [
    path('', orders, name='orders'),
    path('orderDetails/<int:id>/', orderDetails, name='orderDetails'),
    path('specsDetails/<int:itemId>/', specsDetails, name='specsDetails'),
    path('specsDetailsSQL/<int:orderId>/', specsDetailsSQL, name='specsDetailsSQL'),
    path('get_spec_tree_by_item/<int:orderId>/<int:itemId>/', get_spec_tree_by_item, name='get_spec_tree_by_item')
]