from django.contrib import admin
from django.urls import path, include
from my_erp.views import index, catalog
from users.views import signup

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('catalog/', include('my_erp.urls', namespace='catalog')),
    path('users/', include('users.urls', namespace='users')),
]
