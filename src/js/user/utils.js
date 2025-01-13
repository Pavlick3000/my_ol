// Функция проверки номера телефона (возвращает true, если номер валиден)
function validatePhoneNumber(inputElement) {
    const rawValue = inputElement.value.replace(/\D/g, ''); // Удаляем всё кроме цифр
    return rawValue.length === 11; // Длина должна быть ровно 11 цифр
}

// Установка начального значения и блокировка удаления +7
function setupPhoneInput(inputElement) {
    // Установка начального значения
    inputElement.value = '+7 ';
    // Блокировка удаления +7
    inputElement.addEventListener('keydown', function (e) {
        if (inputElement.selectionStart < 3 && e.key === 'Backspace') {
            e.preventDefault(); // Блокируем удаление +7
        }
    });
}

// Универсальная функция для форматирования телефона
function formatPhoneNumber(value) {
    let formatted = '+7 ';
    if (value.length > 1) formatted += value.substring(1, 4);
    if (value.length > 4) formatted += ' ' + value.substring(4, 7);
    if (value.length > 7) formatted += ' ' + value.substring(7, 9);
    if (value.length > 9) formatted += ' ' + value.substring(9, 11);
    return formatted.trim();
}

// Универсальный обработчик для форматирования номера телефона
function setupPhoneFormatting(inputElement) {
    inputElement.addEventListener('input', function () {
        const rawValue = inputElement.value.replace(/\D/g, ''); // Удаляем всё кроме цифр
        const formattedValue = formatPhoneNumber(rawValue); // Форматируем номер
        inputElement.value = formattedValue; // Обновляем значение
    });
}

// Проверка поля email с использованием регулярного выражения
function isValidEmail(email) {
    var pattern = new RegExp(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$/);
    return pattern.test(email);
}

// Универсальная функция для проверки валидности формы
function checkFormValidity(fields, phoneInput= null, emailField = null, smsButton= null, emailButton = null) {
    let isValid = true;

    // Проверка заполненности всех полей
    fields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
        }
    });

    // Проверка корректности номера телефона
    if (!validatePhoneNumber(phoneInput)) {
        isValid = false;
    }

    // Если есть поле для email, проверяем его
    if (emailField && !isValidEmail(emailField.value.trim())) {
        isValid = false;
    }

    // Активируем или деактивируем кнопки в зависимости от валидности
    if (smsButton) {
        smsButton.disabled = !isValid;
        smsButton.classList.toggle('opacity-50', !isValid);
        smsButton.classList.toggle('bg-gray-400', !isValid);
        smsButton.classList.toggle('bg-emerald-500', isValid);
        smsButton.classList.toggle('text-gray-700', isValid);
        smsButton.classList.toggle('hover:bg-emerald-400', isValid);
    }

    if (emailButton) {
        emailButton.disabled = !isValid;
        emailButton.classList.toggle('opacity-50', !isValid);
        emailButton.classList.toggle('text-gray-700', isValid);
        emailButton.classList.toggle('hover:text-emerald-500', isValid);
    }
}