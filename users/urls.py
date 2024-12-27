from django.urls import path
from users.views import login, signup, verify_code, resend_code, check_code_status, user_logout

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('verify_code/', verify_code, name='verify_code'),
    path('resend_code/', resend_code, name='resend_code'),
    path('check-code-status/', check_code_status, name='check_code_status'),
]
