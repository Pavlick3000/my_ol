from django.urls import path
from users.views import login, signup, verify_code

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('verify_code/', verify_code, name='verify_code'),
]
