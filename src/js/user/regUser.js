document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('reg-code-form');
    const smsButton = document.getElementById('send-code-sms');
    const emailButton = document.getElementById('send-code-email');
    const email = document.getElementById('email');
    const fields = registerForm.querySelectorAll('[name="first_name"], [name="last_name"], [name="email"], [name="contact_input_number"]');
    const phoneInput = document.querySelector('[data-real-name="phone_number"]');
    const authForm = document.getElementById('auth-form');
    const modalCode = document.getElementById('modal-code');
    const authButtons = document.getElementById('auth-header');
    const modalContent = document.getElementById('login-modal-content');
    const modalContactInfo = document.getElementById('modalContactInfo');
    const modalContactInfoMethods = document.getElementById('modalContactInfoMethods');

    // Установка начального значения и блокировка удаления +7
    setupPhoneInput(phoneInput);

    // Форматирование номера телефона
    setupPhoneFormatting(phoneInput);

    // Проверка валидности формы
    fields.forEach(field => {
        field.addEventListener('input', () => {
            checkFormValidity(fields, phoneInput, email, smsButton, emailButton);
        });
    });

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
                                fetch('/users/resend_code/', { // TODO избавиться от хардкода
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