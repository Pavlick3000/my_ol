document.addEventListener('DOMContentLoaded', () => {
    const openModalButton = document.getElementById('open-login-modal');
    const closeModalButton = document.getElementById('close-login-modal');
    const modal = document.getElementById('login-modal');
    const phoneInput = document.getElementById('phone_number');

    openModalButton.addEventListener('click', () => {
        modal.classList.remove('hidden');

        // Очистка поля, если там есть данные
        phoneInput.value = '+7 ';

        // Устанавливаем фокус на поле ввода
        phoneInput.focus();

        // Перемещаем курсор в конец, если поле уже заполнено
        phoneInput.setSelectionRange(phoneInput.value.length, phoneInput.value.length);
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

    phoneInput.addEventListener('input', (event) => {
        const rawValue = phoneInput.value.replace(/\D/g, ''); // Удаляем все символы, кроме цифр
        const formattedValue = formatPhoneNumber(rawValue);
        phoneInput.value = formattedValue;
    });

    phoneInput.addEventListener('keydown', (event) => {
        // Запрещаем удаление +7 с помощью Backspace и Delete
        const cursorPosition = phoneInput.selectionStart;
        if ((event.key === 'Backspace' || event.key === 'Delete') && cursorPosition <= 3) {
            event.preventDefault();
        }
    });

    phoneInput.addEventListener('focus', () => {
        // Устанавливаем курсор в конец при фокусе
        phoneInput.setSelectionRange(phoneInput.value.length, phoneInput.value.length);
    });
});

/**
 * Форматирует номер телефона в формате +7 911 003 94 33
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
