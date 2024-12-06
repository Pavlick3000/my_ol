from django.urls import path
from users.views import login, signup

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
]
