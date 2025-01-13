//JSON и проверка полей формы авторизации
document.addEventListener('DOMContentLoaded', function () {
    const authForm = document.getElementById('auth-code-form');
    const fieldsAuthSMS = authForm.querySelectorAll('[name="auth_contact_input_number"]');
    const fieldsAuthEmail = authForm.querySelectorAll('[name="emailAuth"]');
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

});