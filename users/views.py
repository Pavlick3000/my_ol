from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.core.mail import send_mail
import random

from django.contrib.auth.models import User

def send_verification_code(user, method):
    code = random.randint(100000, 999999)
    user.profile.verification_code = code
    user.profile.save()
    if method == 'email':
        send_mail(
            'Код подтверждения',
            f'Ваш код: {code}',
            'noreply@example.com',
            [user.email],
        )
    elif method == 'sms':
        # Логика отправки SMS
        print(f'Отправка SMS на {user.profile.phone_number}: {code}')

def signup(request):
    # if request.method == 'POST':
    #     form = RegistrationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         method = request.POST.get('method', 'email')  # email или sms
    #         send_verification_code(user, method)
    #         return redirect('verify', user_id=user.id)
    # else:
    #     form = RegistrationForm()
    return render(request, 'users/signup.html')
    # , {'form': form})

def login(request):
    context = {
        'title': 'Авторизация',

    }
    return render(request, 'users/login.html', context)