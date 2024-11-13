from django.urls import path
from users import views
from django.contrib.auth import views as auth_views
from users.views import login, signup

app_name = 'users'

urlpatterns = [
    # path('', users, name='index'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
