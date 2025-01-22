//JSON и проверка полей формы авторизации
document.addEventListener('DOMContentLoaded', function () {
    const authForm = document.getElementById('auth-code-form');
    const registerForm = document.getElementById('reg-code-form');
    const fieldsAuthSMS = authForm.querySelectorAll('[name="auth_contact_input_number"]');
    const fieldsAuthEmail = authForm.querySelectorAll('[name="email"]');
    const smsAuthButton = document.getElementById('auth-send-code-sms');
    const emailAuthButton = document.getElementById('auth-send-code-email');
    const phoneAuthInput = document.getElementById('contact_input_number_login');
    const emailAuthInput = document.getElementById('email_auth');

    const authModal = document.getElementById('auth-form');

    const modalCode = document.getElementById('modal-code');
    const authButtons = document.getElementById('auth-header');
    const modalContent = document.getElementById('login-modal-content');
    const modalContactInfo = document.getElementById('modalContactInfo');
    const modalContactInfoMethods = document.getElementById('modalContactInfoMethods');


    // Установка начального значения и блокировка удаления +7
    setupPhoneInput(phoneAuthInput);

    // Форматирование номера телефона
    setupPhoneFormatting(phoneAuthInput);

    // Проверка валидности поля ввода номера телефона
    fieldsAuthSMS.forEach(field => {
        field.addEventListener('input', () => {
            checkFormValidity(fieldsAuthSMS, phoneAuthInput, null, smsAuthButton, null);
        });
    });

    // Проверка валидности поля email
    const checkFormValidityEmail = () => {
        let isValid = true;

        fieldsAuthEmail.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });

        // Проверка корректности email

        if (!isValidEmail(emailAuthInput.value.trim())) {
            isValid = false;
        }

        // Активируем или деактивируем кнопку отправки кода по SMS
        emailAuthButton.disabled = !isValid;
        emailAuthButton.classList.toggle('opacity-50', !isValid);
        emailAuthButton.classList.toggle('bg-gray-400', !isValid);
        emailAuthButton.classList.toggle('bg-emerald-500', isValid);
        emailAuthButton.classList.toggle('text-gray-700', isValid);
        emailAuthButton.classList.toggle('hover:bg-emerald-400', isValid);
    };

    // Обработчик для проверки поля ввода email на каждом изменении поля
    fieldsAuthEmail.forEach(field => {
        field.addEventListener('input', checkFormValidityEmail);
    });

    // Функция отправки данных
    function sendCodeAuth(sendType, authProcess) {
        const formData = new FormData(authForm);
        formData.append('send_type', sendType); // Добавляем тип отправки (SMS или Email)
        formData.append('auth_process', authProcess);
        const rawPhoneValue = phoneAuthInput.value.replace(/\s+/g, '');
        formData.set('phone_number', rawPhoneValue); // Устанавливаем отформатированный номер

        const loginUrl = authForm.getAttribute('data-login-url');

        // Сохраняем данные, которые понадобятся для повторной отправки
        localStorage.setItem('sendType', sendType);
        localStorage.setItem('authProcess', authProcess);
        localStorage.setItem('phoneNumber', rawPhoneValue);
        localStorage.setItem('email', document.getElementById('email_auth').value);


        fetch(loginUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                authForm.classList.add('hidden');
                registerForm.classList.add('hidden');
                authButtons.classList.add('hidden');
                modalCode.classList.remove('hidden');
                modalContent.style.height = '250px';
                if (sendType === 'sms' || sendType === 'email') {
                    localStorage.setItem('authInProgress', 'true'); // Авторизация
                    localStorage.removeItem('registrationInProgress'); // Удаляем состояние регистрации
                } else {
                    localStorage.setItem('registrationInProgress', 'true'); // Регистрация
                    localStorage.removeItem('authInProgress'); // Удаляем состояние авторизации
                }
                // Обновляем содержимое модального окна
                const contactInfo = sendType === 'sms' ? rawPhoneValue : document.getElementById('email_auth').value; // Получаем номер телефона или email
                const contactMethod = sendType === 'sms' ? 'номер' : 'почту'; // Определяем метод отправки

                modalContactInfo.textContent = `Код отправлен на ${contactMethod}`;
                modalContactInfoMethods.textContent = `${contactInfo}`;

            } else {
                alert(data.message || 'Произошла ошибка');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при отправке кода.');
        });
    }

    // Обработчики кнопок
    smsAuthButton.addEventListener('click', function (e) {
        e.preventDefault();
        sendCodeAuth('sms', 'True');

    });

    emailAuthButton.addEventListener('click', function (e) {
        e.preventDefault();
        sendCodeAuth('email','True');
    });

});