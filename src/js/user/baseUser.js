// Открытие и закрытие модального окна авторизации/регистрации;
// переключение между формами;
// состояние при открытии
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
    const emailButton = document.getElementById('email-link');
    const modalFooter = document.getElementById('footer-modal');

    // Обработчик открытия модального окна
    openModalButton.addEventListener('click', () => {
        modal.classList.remove('hidden');

        const registrationInProgress = localStorage.getItem('registrationInProgress') === 'true';
        const authInProgress = localStorage.getItem('authInProgress') === 'true';

        const handleCodeCheck = () => {
            fetch('/users/check-code-status/', { // TODO: убрать хардкод URL
                method: 'GET',
                credentials: 'include',
            })
                .then(response => response.json())
                .then(data => {
                    if (data.codeExpired) {
                        // Сброс процесса при истечении срока действия кода
                        localStorage.removeItem(registrationInProgress ? 'registrationInProgress' : 'authInProgress');
                        location.reload();
                    } else {
                        // Показываем ввод кода, если он действителен
                        updateModalView({
                            authButtonsHidden: true,
                            authFormHidden: true,
                            registerFormHidden: true,
                            modalCodeHidden: false,
                            modalFooterHidden: true,
                            modalHeight: '250px',
                        });
                    }
                });
        };

        if (registrationInProgress) {
            handleCodeCheck();
        } else if (authInProgress) {
            handleCodeCheck();
        } else {
            // Открыть форму авторизации по умолчанию
            updateModalView({
                authButtonsHidden: false,
                authFormHidden: false,
                registerFormHidden: true,
                modalCodeHidden: true,
                modalFooterHidden: true,
                modalHeight: '380px',
            });
            setActiveLink('auth-link', 'register-link');
            phoneInputLogin.focus();
        }
    });

    /**
     * Обновляет видимость элементов модального окна и его высоту.
     * @param {Object} options - Опции для обновления.
     */
    function updateModalView({
                                 authButtonsHidden,
                                 authFormHidden,
                                 registerFormHidden,
                                 modalCodeHidden,
                                 modalFooterHidden,
                                 modalHeight,
                             }) {
        toggleElementVisibility(authButtons, authButtonsHidden);
        toggleElementVisibility(authForm, authFormHidden);
        toggleElementVisibility(registerForm, registerFormHidden);
        toggleElementVisibility(modalCode, modalCodeHidden);
        toggleElementVisibility(modalFooter, modalFooterHidden);
        modalContent.style.height = modalHeight;
    }

    /**
     * Переключает видимость элемента.
     * @param {HTMLElement} element - Элемент для переключения.
     * @param {boolean} hidden - Флаг видимости.
     */
    function toggleElementVisibility(element, hidden) {
        if (hidden) {
            element.classList.add('hidden');
        } else {
            element.classList.remove('hidden');
        }
    }

    /**
     * Устанавливает активный линк в модальном окне.
     * @param {string} activeLinkId - ID активного линка.
     * @param {string} inactiveLinkId - ID неактивного линка.
     */
    function setActiveLink(activeLinkId, inactiveLinkId) {
        const activeLink = document.getElementById(activeLinkId);
        const inactiveLink = document.getElementById(inactiveLinkId);

        activeLink.classList.add('underline', 'underline-offset-4', 'decoration-gray-300');
        inactiveLink.classList.remove('underline', 'underline-offset-4', 'decoration-gray-300');
    }

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


    // Исходная высота модального окна
    // TODO по всему скрипту есть несколько мест где меняется высота окон,
    //  надо эти значения вынести в отдельные переменные, для дальнейше простоты внесения изменений - ищи по "modalContent.style.height"
    const initialHeight = '380px'; // Укажите вашу исходную высоту
    const expandedHeight = '540px'; // Увеличенная высота

    emailButton.addEventListener('click', () => {
        if (modalContent) {
            // Проверяем текущую высоту и переключаем её
            if (modalContent.style.height === expandedHeight) {
                modalContent.style.height = initialHeight; // Возвращаем к исходной высоте
                modalFooter.classList.add('hidden');
            } else {
                modalContent.style.height = expandedHeight; // Устанавливаем увеличенную высоту
                modalFooter.classList.remove('hidden');
            }
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
            modalFooter.classList.add('hidden');
            modalContent.style.height = '380px'; // Высота для авторизации
            document.getElementById('auth-link').classList.add('underline', "underline-offset-4", "decoration-gray-300");
            document.getElementById('register-link').classList.remove('underline', "underline-offset-4", "decoration-gray-300");
        }
    }

});

