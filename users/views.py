import json

from django.contrib.auth import login as auth_login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.http import JsonResponse

from users.forms import CustomUserCreationForm, UserLoginForm
from users.models import CustomUser
from my_ol import settings
from .utils import send_sms

User = get_user_model()

def user_logout(request):
    logout(request)
    # Получаем URL предыдущей страницы и перенаправляем пользователя туда
    referer_url = request.META.get('HTTP_REFERER', 'users:login')  # 'users:login' - если нет реферера
    return redirect(referer_url)

def login(request):
    if request.method == "POST":
        send_type = request.POST.get('send_type')
        auth_process = request.POST.get('auth_process')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # Очистка номера телефона
        if phone_number:
            phone_number = str(phone_number).strip()

        print(request.POST)
        # Проверка на совпадение email и phone_number с записями в БД
        if send_type == 'email':
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Пользователь с таким email не найден.'},
                                    status=400)
        else:
            if not User.objects.filter(phone_number=phone_number).exists():
                print(f"Запрос: {User.objects.filter(phone_number=phone_number).query}")
                print(f"Телефон: {phone_number}")
                return JsonResponse(
                    {'status': 'error', 'message': 'Пользователь с таким номером телефона не найден.'},
                    status=400)

        form = UserLoginForm(request.POST)
        if form.is_valid():
            # Генерация 6-значного кода
            # verification_code = get_random_string(length=6, allowed_chars='0123456789')
            verification_code = '000000'

            # Сохранение данных пользователя в сессию
            request.session['verification_code'] = verification_code
            request.session['auth_process'] = auth_process
            request.session['send_type'] = send_type
            request.session['user_data'] = form.cleaned_data
            request.session.set_expiry(90)  # Код действует 1.5 минуты

            if send_type == 'sms':
                # Отправка кода по SMS
                message = f"Ваш код подтверждения: {verification_code}"
                send_sms(phone_number, message)
            elif send_type == 'email':
                print(f"Получатель письма: {email}")
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
            return JsonResponse(
                {'status': 'error', 'message': 'Пожалуйста, проверьте правильность введенных данных.'},
                status=400)
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html',{'form': form})

def signup(request):
    if request.method == 'POST':

        # Получаем данные из запроса
        send_type = request.POST.get('send_type')  # Получаем тип отправки
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        auth_process = request.POST.get('auth_process')


        # Проверка на совпадение email и phone_number с записями в БД
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Пользователь с таким email уже зарегистрирован.'},status=400)
        if User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'status': 'error', 'message': 'Пользователь с таким номером телефона уже зарегистрирован.'},status=400)

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Генерация 6-значного кода
            verification_code = get_random_string(length=6, allowed_chars='0123456789')

            # Сохранение данных пользователя в сессию
            request.session['verification_code'] = verification_code
            request.session['auth_process'] = auth_process
            request.session['user_data'] = form.cleaned_data
            request.session.set_expiry(90)  # Код действует 1.5 минуты

            if send_type == 'sms':
                # Отправка кода по SMS
                message = f"Ваш код подтверждения: {verification_code}"
                send_sms(phone_number, message)
            elif send_type == 'email':
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
        form = UserLoginForm()

    # Если форма была запрашиваема через GET (для первого отображения)
    return render(request, 'users/login.html', {'form': form})

def verify_code(request):
    if request.method == 'POST':
        user_code = request.POST.get('verification_code')
        session_code = request.session.get('verification_code')
        auth_process = request.session.get('auth_process')
        send_type = request.session.get('send_type')

        if not session_code:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errorType': 'expired',  # Передаём статус "expired"
                    'error': 'Срок действия кода истек.'
                }, status=400)
            messages.error(request, 'Срок действия кода истек. Регистрация отменена.')

            return redirect('users:login')

        if str(user_code).strip() == str(session_code).strip():
            user_data = request.session.get('user_data')
            print(auth_process)
            if user_data:
                if auth_process == 'False':  # Создание нового пользователя
                    user = CustomUser.objects.create_user(
                        username=user_data['email'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        phone_number=user_data['phone_number'],
                    )

                    # Очистка сессии
                    request.session.flush()

                    # Авторизация пользователя
                    auth_login(request, user)
                    request.session.set_expiry(0)  # Не ограничиваем время сессии
                    print(f"Пользователь авторизован: {request.user.first_name}, {request.user.email}")

                    return JsonResponse({
                        'success': True,
                        'message': 'Код подтверждён. Регистрация завершена.',
                    }, status=200)

                elif auth_process  == 'True':  # Авторизация существующего пользователя
                    try:
                        if send_type == 'email':
                            print(send_type)
                            user = CustomUser.objects.get(email=user_data['email'])
                            auth_login(request, user)
                            request.session.set_expiry(0)  # Не ограничиваем время сессии
                        elif send_type == 'sms':
                            user = CustomUser.objects.get(phone_number=user_data['phone_number'])
                            auth_login(request, user)
                            request.session.set_expiry(0)  # Не ограничиваем время сессии

                        print(f"Пользователь авторизован: {request.user.first_name}, {request.user.email}")

                        return JsonResponse({
                            'success': True,
                            'message': 'Код подтверждён. Авторизация завершена.',
                        }, status=200)
                    except CustomUser.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'Пользователь не найден. Попробуйте снова.'
                        }, status=400)

        return JsonResponse({
            'success': False,
            'error': 'Неверный код. Попробуйте снова.'
        }, status=400)

    return render(request, 'users/login.html')

def resend_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        send_type = data.get('send_type')
        auth_process = data.get('auth_process')
        email = data.get('email')
        phone_number = data.get('phone_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Генерация нового кода
        verification_code = get_random_string(length=6, allowed_chars='0123456789')

        # Обновляем код в сессии
        request.session['auth_process'] = auth_process
        request.session['send_type'] = send_type
        request.session['verification_code'] = verification_code
        request.session.set_expiry(90)  # Код действует 10 минут

        print(auth_process)

        if not request.session.get('user_data'):
            request.session['user_data'] = {
                'email': email,
                'phone_number': phone_number,
                'first_name': first_name,
                'last_name': last_name,
            }

        if send_type == 'sms':
            message = f"Ваш новый код подтверждения: {verification_code}"
            send_sms(phone_number, message)
        elif send_type == 'email':
            send_mail(
                subject="Ваш новый код подтверждения",
                message=f"Ваш новый код: {verification_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

        return JsonResponse({'status': 'success', 'message': 'Новый код подтверждения отправлен.'})

    return JsonResponse({'status': 'error', 'message': 'Невалидный запрос.'}, status=400)

def check_code_status(request):
    # Получаем код из сессии
    session_code = request.session.get('verification_code')

    if not session_code:
        # Если кода нет в сессии, он истёк
        return JsonResponse({'codeExpired': True})

    # Если код существует, он действителен
    return JsonResponse({'codeExpired': False})