from django.contrib import admin
from django.urls import path, include
from my_erp.views import index, catalog
from my_ol import settings
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('catalog/', include('my_erp.urls', namespace='catalog')),
    path('users/', include('users.urls', namespace='users')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]