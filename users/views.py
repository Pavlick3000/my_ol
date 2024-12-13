from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.http import JsonResponse

from my_ol import settings
from users.forms import CustomUserCreationForm
from users.models import CustomUser

def login(request):
    return render(request, 'users/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Генерация 6-значного кода
            verification_code = get_random_string(length=6, allowed_chars='0123456789')

            # Сохранение данных пользователя в сессию
            request.session['verification_code'] = verification_code
            request.session['user_data'] = form.cleaned_data
            request.session.set_expiry(600)  # Код действует 10 минут

            # Отправка кода на почту
            email = form.cleaned_data['email']
            send_mail(
                subject="Ваш код подтверждения",
                message=f"Ваш код: {verification_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            # Ответ в формате JSON, чтобы показать модальное окно с кодом
            return JsonResponse({'status': 'success', 'message': 'Код подтверждения отправлен на вашу почту.'})
        else:
            # Если форма невалидна, возвращаем ошибку
            return JsonResponse({'status': 'error', 'message': 'Пожалуйста, проверьте правильность введенных данных.'},
                                status=400)
    else:
        form = CustomUserCreationForm()

    # Если форма была запрашиваема через GET (для первого отображения)
    return render(request, 'users/login.html', {'form': form})

def verify_code(request):
    if request.method == 'POST':
        user_code = request.POST.get('verification_code')
        session_code = request.session.get('verification_code')

        if not session_code:
            messages.error(request, 'Срок действия кода истек. Пожалуйста, зарегистрируйтесь снова.')
            return redirect('users:signup')

        if user_code == session_code:
            user_data = request.session.get('user_data')
            if user_data:
                CustomUser.objects.create_user(
                    username=user_data['email'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone_number=user_data['phone_number'],
                )
                request.session.flush()  # Очистка сессии
                messages.success(request, "Вы успешно зарегистрированы!")
                return redirect('catalog:index')
        else:
            messages.error(request, 'Неверный код. Попробуйте снова.')

    return render(request, 'users/login.html')