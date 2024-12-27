document.addEventListener('DOMContentLoaded', () => {
    const openModalButton = document.getElementById('open-login-modal');
    const closeModalButton = document.getElementById('close-login-modal');
    const modal = document.getElementById('login-modal');
    const phoneInputLogin = document.getElementById('contact_input_number_login');
    const authForm = document.getElementById('auth-form');
    const registerForm = document.getElementById('register-form');
    const modalCode = document.getElementById('modal-code'); // Форма ввода кода
    const modalContent = document.getElementById('login-modal-content');
    const authButtons = document.getElementById('auth-header'); // Контейнер с кнопками
    // const isCodeExpired = sessionStorage.getItem('isCodeExpired');

    // Обработчик открытия модального окна
    openModalButton.addEventListener('click', () => {
        modal.classList.remove('hidden');

        const registrationInProgress = localStorage.getItem('registrationInProgress');

        if (registrationInProgress === 'true') {
            fetch('/users/check-code-status/', {
                method: 'GET',
                credentials: 'include',
            })
                .then(response => response.json())
                .then(data => {
                    if (data.codeExpired) {
                        // Если пользователь так и не воспользовался повторной отправкой кода, то сбрасываем весь процесс регистрации.
                        // В будущем можно зациклить, чтобы можно было получать повторный код до бесконечности, но пока не до этого 27.12.24
                        localStorage.removeItem('registrationInProgress');
                        location.reload();
                    } else {
                        // Если код действителен, показываем ввод кода
                        authButtons.classList.add('hidden');
                        authForm.classList.add('hidden');
                        registerForm.classList.add('hidden');
                        modalCode.classList.remove('hidden');
                        modalContent.style.height = '250px';
                    }
                });
        } else {
            // По умолчанию открыть форму авторизации
            authButtons.classList.remove('hidden');
            authForm.classList.remove('hidden');
            document.getElementById('auth-link').classList.add('underline', "underline-offset-4", "decoration-gray-300");
            document.getElementById('register-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
            registerForm.classList.add('hidden');
            modalCode.classList.add('hidden');
            modalContent.style.height = '380px';
            phoneInputLogin.value = '+7 ';
            phoneInputLogin.focus();
        }
    });

    // Обработчик закрытия модального окна для крестика
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

    // Удаляем все символы, кроме цифр окно ЛОГИН
    phoneInputLogin.addEventListener('input', (event) => {
        const rawValue = phoneInputLogin.value.replace(/\D/g, '');
        const formattedValue = formatPhoneNumber(rawValue);
        phoneInputLogin.value = formattedValue;
    });

    // Запрещаем удаление +7 с помощью Backspace и Delete окно ЛОГИН
    phoneInputLogin.addEventListener('keydown', (event) => {
        const cursorPosition = phoneInputLogin.selectionStart;
        if ((event.key === 'Backspace' || event.key === 'Delete') && cursorPosition <= 3) {
            event.preventDefault();
        }
    });

    // Переключение между формами
    document.getElementById('register-link').addEventListener('click', () => toggleForm('register'));
    document.getElementById('auth-link').addEventListener('click', () => toggleForm('auth'));

    // Функция переключения между формами
    function toggleForm(formType) {
        if (formType === 'register') {
            authForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
            modalContent.style.height = '470px'; // Высота для регистрации
            document.getElementById('auth-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
            document.getElementById('register-link').classList.add('underline', "underline-offset-4", "decoration-gray-300");
        } else {
            registerForm.classList.add('hidden');
            authForm.classList.remove('hidden');
            modalContent.style.height = '380px'; // Высота для авторизации
            document.getElementById('auth-link').classList.add('underline', "underline-offset-4", "decoration-gray-300");
            document.getElementById('register-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
        }
    }

});

//JSON и проверка полей
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('email-code-form');
    const smsButton = document.getElementById('send-code-sms');
    const emailButton = document.getElementById('send-code-email');
    const fields = registerForm.querySelectorAll('[name="first_name"], [name="last_name"], [name="email"], [name="contact_input_number"]');
    const phoneInput = document.querySelector('[data-real-name="phone_number"]');
    const authForm = document.getElementById('auth-form');
    const modalCode = document.getElementById('modal-code');
    const authButtons = document.getElementById('auth-header');
    const modalContent = document.getElementById('login-modal-content');
    const modalContactInfo = document.getElementById('modalContactInfo');
    const modalContactInfoMethods = document.getElementById('modalContactInfoMethods');

    // Установка начального значения и блокировка удаления +7
    phoneInput.value = '+7 ';
    phoneInput.addEventListener('keydown', function (e) {
        if (phoneInput.selectionStart < 3 && e.key === 'Backspace') {
            e.preventDefault(); // Блокируем удаление +7
        }
    });

    // Форматирование номера телефона
    phoneInput.addEventListener('input', function (e) {
        const rawValue = phoneInput.value.replace(/\D/g, ''); // Удаляем всё кроме цифр
        const formattedValue = formatPhoneNumber(rawValue);
        phoneInput.value = formattedValue;

    });

    // Форматирование телефона в формате +7 000 000 00 00
    function formatPhoneNumber(value) {
        let formatted = '+7 ';
        if (value.length > 1) formatted += value.substring(1, 4);
        if (value.length > 4) formatted += ' ' + value.substring(4, 7);
        if (value.length > 7) formatted += ' ' + value.substring(7, 9);
        if (value.length > 9) formatted += ' ' + value.substring(9, 11);
        return formatted.trim();
    }

    // Обработчик проверки заполненности всех полей
    const checkFormValidity = () => {
        let isValid = true;

        fields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });

        // Проверка корректности email
        const emailField = document.getElementById('email');
        if (!isValidEmail(emailField.value.trim())) {
            isValid = false;
        }

        // Проверяем корректность номера телефона
        if (!validatePhoneNumber()) {
            isValid = false;
        }

        // Активируем или деактивируем кнопку отправки кода по email
        emailButton.disabled = !isValid;
        emailButton.classList.toggle('opacity-50', !isValid);
        emailButton.classList.toggle('text-gray-700', isValid);
        emailButton.classList.toggle('hover:text-emerald-500', isValid);


        // Активируем или деактивируем кнопку отправки кода по SMS
        smsButton.disabled = !isValid;
        smsButton.classList.toggle('opacity-50', !isValid);
        smsButton.classList.toggle('bg-gray-400', !isValid);
        smsButton.classList.toggle('bg-emerald-500', isValid);
        smsButton.classList.toggle('text-gray-700', isValid);
        smsButton.classList.toggle('hover:bg-emerald-400', isValid);
    };

    // Обработчик для проверки формы на каждом изменении поля
    fields.forEach(field => {
        field.addEventListener('input', checkFormValidity);
    });

    // Проверка поля email с использованием регулярного выражения
    function isValidEmail(email) {
        var pattern = new RegExp(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$/);
        return pattern.test(email);
    }

    // Проверка номера телефона (возвращает true, если номер валиден)
    function validatePhoneNumber() {
        const rawValue = phoneInput.value.replace(/\D/g, ''); // Удаляем всё кроме цифр
        return rawValue.length === 11; // Длина должна быть ровно 11 цифр
    }

    // Функция отправки данных
    function sendCode(sendType) {
        const formData = new FormData(registerForm);
        formData.append('send_type', sendType); // Добавляем тип отправки (SMS или Email)

        const rawPhoneValue = phoneInput.value.replace(/\s+/g, '');
        formData.set('phone_number', rawPhoneValue); // Устанавливаем отформатированный номер

        const signupUrl = registerForm.getAttribute('data-signup-url');

        // Сохраняем данные, которые понадобятся для повторной отправки
        localStorage.setItem('sendType', sendType);
        localStorage.setItem('phoneNumber', rawPhoneValue);
        localStorage.setItem('email', document.getElementById('email').value);
        localStorage.setItem('first_name', document.getElementById('first_name').value);
        localStorage.setItem('last_name', document.getElementById('last_name').value);


        fetch(signupUrl, {
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
                localStorage.setItem('registrationInProgress', 'true'); // фиксируем, что пользователю успешно отправлен код, чтобы при повторном нажатии "Вход" сразу попадать в окно ввода кода

                // Обновляем содержимое модального окна
                const contactInfo = sendType === 'sms' ? rawPhoneValue : document.getElementById('email').value; // Получаем номер телефона или email
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

    // Находим модальное окно и форму внутри него - для обработки события ввода неправильного кода
    const form = modalCode.querySelector('form'); // Находим первую форму внутри модального окна

    // Добавляем обработчик на форму ввода кода
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Предотвращаем стандартное поведение формы

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Успешная обработка
                    localStorage.removeItem('registrationInProgress'); // Процесс регистрации завершен
                    location.reload(); // Остаемся на той же странице, откуда начали регистрацию
                } else {
                    let errorMessageElement = document.getElementById('error-message');
                    const resendButton = document.getElementById('resend-button'); // Кнопка повторной отправки кода
                    const signupUrl = registerForm.getAttribute('data-signup-url');

                    if (errorMessageElement) {
                        // Показываем сообщение об ошибке
                        errorMessageElement.textContent = data.error;
                        errorMessageElement.classList.remove('hidden'); // Убираем скрытие

                        const form = document.getElementById('code-verification-form');
                        form.classList.add('error-expanded');
                        modalContent.style.height = '280px';

                        // Если ошибка связана с просроченным кодом
                        if (data.errorType === 'expired') {
                            modalContent.style.height = '310px';
                            // Показываем кнопку повторной отправки кода
                            resendButton.classList.remove('hidden');

                            resendButton.addEventListener('click', function resendHandler(e) {
                                e.preventDefault(); // Предотвращаем отправку формы

                                // Получаем данные из localStorage или формы
                                const sendType = localStorage.getItem('sendType');
                                const phoneNumber = localStorage.getItem('phoneNumber');
                                const email = localStorage.getItem('email');
                                const first_name = localStorage.getItem('first_name');
                                const last_name = localStorage.getItem('last_name');

                                // Проверяем, что все необходимые данные получены
                                if (!sendType || (!phoneNumber && sendType === 'sms') || (!email && sendType === 'email')) {
                                    alert('Недостаточно данных для повторной отправки кода.');
                                    return;
                                }

                                // Создаем запрос с данными
                                fetch('/users/resend_code/', {
                                    method: 'POST',
                                    body: JSON.stringify({
                                        send_type: sendType,
                                        email: email,
                                        phone_number: phoneNumber,
                                        first_name: first_name,
                                        last_name: last_name
                                    }),
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-Requested-With': 'XMLHttpRequest',
                                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Добавляем CSRF токен
                                    }
                                })
                                    .then(response => response.json())
                                    .then(resendData => {
                                        if (resendData.status === 'success') {
                                            alert('Код успешно отправлен повторно!');
                                            errorMessageElement.classList.add('hidden');
                                            modalContent.style.height = '250px';
                                            resendButton.classList.add('hidden'); // Скрываем кнопку после успешной отправки
                                        } else {
                                            alert('Не удалось отправить код. Попробуйте позже.');
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Ошибка при повторной отправке кода:', error);
                                        alert('Произошла ошибка. Попробуйте позже.');
                                    });

                                // Удаляем обработчик события после одного клика
                                resendButton.removeEventListener('click', resendHandler);
                            });
                        }

                        // Удаляем сообщение об ошибке и сбрасываем размер формы через 2.5 секунды (для неправильного пароля)
                        if (data.errorType !== 'expired') {
                            setTimeout(() => {
                                errorMessageElement.textContent = '';
                                errorMessageElement.classList.add('hidden'); // Скрываем сообщение
                                form.classList.remove('error-expanded'); // Убираем временное увеличение формы
                                modalContent.style.height = '250px';
                            }, 2500);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при проверке кода.');
            });
    });

    // Обработчики кнопок
    smsButton.addEventListener('click', function (e) {
        e.preventDefault();
        sendCode('sms');
    });

    emailButton.addEventListener('click', function (e) {
        e.preventDefault();
        sendCode('email');
    });

});
