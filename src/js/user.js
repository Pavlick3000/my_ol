// Правила для модального окна авторизации/регистрации
document.addEventListener('DOMContentLoaded', () => {
    const openModalButton = document.getElementById('open-login-modal');
    const closeModalButton = document.getElementById('close-login-modal');
    const modal = document.getElementById('login-modal');
    const phoneInputLogin = document.getElementById('contact_input_number_login');
    const phoneInputRegister = document.getElementById('contact_input_number_register');

    openModalButton.addEventListener('click', () => {
        modal.classList.remove('hidden');


        // Очистка поля, если там есть данные
        phoneInputLogin.value = '+7 ';
        phoneInputRegister.value = '+7 ';

        // Устанавливаем фокус на поле ввода
        phoneInputLogin.focus();
        phoneInputRegister.focus();

        // Перемещаем курсор в конец, если поле уже заполнено
        phoneInputLogin.setSelectionRange(phoneInputLogin.value.length, phoneInputLogin.value.length);
        phoneInputRegister.setSelectionRange(phoneInputRegister.value.length, phoneInputRegister.value.length);
    });

    closeModalButton.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // Закрытие модального окна при клике вне его
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });

    // Закрытие модального окна по нажатию Esc
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
            openModalButton.blur(); // Снимаем фокус с кнопки
        }
    });

    phoneInputLogin.addEventListener('input', (event) => {
        const rawValue = phoneInputLogin.value.replace(/\D/g, ''); // Удаляем все символы, кроме цифр
        const formattedValue = formatPhoneNumber(rawValue);
        phoneInputLogin.value = formattedValue;
    });

    phoneInputRegister.addEventListener('input', (event) => {
        const rawValue = phoneInputRegister.value.replace(/\D/g, ''); // Удаляем все символы, кроме цифр
        const formattedValue = formatPhoneNumber(rawValue);
        phoneInputRegister.value = formattedValue;
    });

    phoneInputLogin.addEventListener('keydown', (event) => {
        // Запрещаем удаление +7 с помощью Backspace и Delete
        const cursorPosition = phoneInputLogin.selectionStart;
        if ((event.key === 'Backspace' || event.key === 'Delete') && cursorPosition <= 3) {
            event.preventDefault();
        }
    });

    phoneInputRegister.addEventListener('keydown', (event) => {
        // Запрещаем удаление +7 с помощью Backspace и Delete
        const cursorPosition = phoneInputRegister.selectionStart;
        if ((event.key === 'Backspace' || event.key === 'Delete') && cursorPosition <= 3) {
            event.preventDefault();
        }
    });

    phoneInputLogin.addEventListener('focus', () => {
        // Устанавливаем курсор в конец при фокусе
        phoneInputLogin.setSelectionRange(phoneInputLogin.value.length, phoneInputLogin.value.length);
    });

    phoneInputRegister.addEventListener('focus', () => {
        // Устанавливаем курсор в конец при фокусе
        phoneInputRegister.setSelectionRange(phoneInputRegister.value.length, phoneInputRegister.value.length);
    });
});

/**
 * Форматирует номер телефона в формате +7 ХХХ ХХХ ХХ ХХ
 * @param {string} value - Номер телефона без форматирования
 * @returns {string} - Отформатированный номер
 */
function formatPhoneNumber(value) {
    let formatted = '+7 ';
    if (value.length > 1) formatted += value.slice(1, 4) + ' ';
    if (value.length > 4) formatted += value.slice(4, 7) + ' ';
    if (value.length > 7) formatted += value.slice(7, 9) + ' ';
    if (value.length > 9) formatted += value.slice(9, 11);
    return formatted.trim();
}

//Событие Клика для открытия окна формы "Регистрация"
document.getElementById('register-link').addEventListener('click', function () {
        document.getElementById('auth-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
        document.getElementById('auth-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
        // registrationLink.classList.add("underline"
        this.classList.add('underline', "underline-offset-4", "decoration-gray-300");
    });

//Событие Клика для открытия окна формы "ЛогИн"
document.getElementById('auth-link').addEventListener('click', function () {
        document.getElementById('auth-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('register-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
        this.classList.add('underline', "underline-offset-4", "decoration-gray-300");
    });

//Изменение высоты окна Авторизация\Регистрация\Ввод кода
document.addEventListener('DOMContentLoaded', function() {
    const authLink = document.getElementById('auth-link');
    const registerLink = document.getElementById('register-link');
    const sendCodeButtonSms = document.getElementById('send-code-sms'); // Кнопка для перехода к вводу кода sms
    const sendCodeButtonEmail = document.getElementById('send-code-email'); // Кнопка для перехода к вводу кода email
    const authForm = document.getElementById('auth-form');
    const registerForm = document.getElementById('register-form');
    const modalCode = document.getElementById('modal-code'); // Форма ввода кода
    const modalContent = document.getElementById('login-modal-content');

    authLink.addEventListener('click', function() {
        registerForm.classList.add('hidden');
        modalCode.classList.add('hidden');
        authForm.classList.remove('hidden');
        modalContent.style.height = '380px'; // Высота для формы авторизации
    });

    registerLink.addEventListener('click', function() {
        authForm.classList.add('hidden');
        modalCode.classList.add('hidden');
        registerForm.classList.remove('hidden');
        modalContent.style.height = '470px'; // Высота для формы регистрации
    });

    sendCodeButtonSms.addEventListener('click', function() {
        authForm.classList.add('hidden');
        registerForm.classList.add('hidden');
        modalCode.classList.remove('hidden');
        modalContent.style.height = '240px'; // Высота для формы ввода кода после SMS
    });

    sendCodeButtonEmail.addEventListener('click', function() {
        authForm.classList.add('hidden');
        registerForm.classList.add('hidden');
        modalCode.classList.remove('hidden');
        modalContent.style.height = '240px'; // Высота для формы ввода кода после email
    });
});

//Событие Клика для открытия окна формы "Ввода кода"
document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const registerForm = document.getElementById('register-form');
    const modalCode = document.getElementById('modal-code');
    const authButtons = document.getElementById('auth-header'); // Контейнер с кнопками
    const sendCodeButtonSms = document.getElementById('send-code-sms'); // Кнопка Зарегистрироваться через SMS
    const sendCodeButtonEmail = document.getElementById('send-code-email'); // Кнопка Зарегистрироваться через Email

    // Показываем форму ввода кода и скрываем кнопки SMS
    sendCodeButtonSms.addEventListener('click', (event) => {
        authForm.classList.add('hidden');
        registerForm.classList.add('hidden');
        modalCode.classList.remove('hidden');
        authButtons.classList.add('hidden'); // Скрываем кнопки
    });
    // Показываем форму ввода кода и скрываем кнопки Email
    sendCodeButtonEmail.addEventListener('click', (event) => {
        authForm.classList.add('hidden');
        registerForm.classList.add('hidden');
        modalCode.classList.remove('hidden');
        authButtons.classList.add('hidden'); // Скрываем кнопки
    });
});

//JSON
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('email-code-form');
    const modalCode = document.getElementById('modal-code');
    const signupUrl = registerForm.getAttribute('data-signup-url');

    registerForm.addEventListener('submit', function (e) {
        e.preventDefault(); // Предотвращаем стандартное отправление формы

        const formData = new FormData(registerForm);

        fetch(signupUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Указываем, что это AJAX-запрос
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Скрыть текущую форму
                document.getElementById('register-form').classList.add('hidden');
                // Показать модальное окно
                modalCode.classList.remove('hidden');
            } else {
                alert(data.message || 'Произошла ошибка');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при регистрации.');
        });
    });
});