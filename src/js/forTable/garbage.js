// Слушатель для каждого элемента таблицы, чтобы отслеживать клики
document.querySelectorAll('tbody tr').forEach(item => {item.addEventListener('contextmenu', handleCellClick);});

// Инициализация обработчиков для модального окна с ID 'actionModal'
setupModalListeners('actionModal');

// Меню по нажатию ПКМ на запись в таблице
function handleCellClick(event) {
    // Отменяем стандартное контекстное меню правой кнопки мыши
    event.preventDefault();

    // Получите координаты клика
    const x = event.clientX;
    const y = event.clientY;

    const modal = document.getElementById('actionModal');

    modal.style.left = `${x}px`;
    modal.style.top = `${y}px`;
    modal.style.position = 'absolute';
    modal.classList.remove('hidden');

    // Добавьте обработчики для кнопок
    document.getElementById('editRecord').onclick = () => {
        if (confirm('Изменить?')) {
            window.location.href = `/edit/${recordId}/`;}
    };
    document.getElementById('deleteRecord').onclick = () => {
        if (confirm('Вы уверены, что хотите удалить эту запись?')) {
            window.location.href = `/delete/${recordId}/`;}
    };
}

// Функции для закрытия меню по нажатию ПКМ
function setupModalListeners(modalId) {
    const modal = document.getElementById(modalId);
    const closeButton = modal.querySelector('.close-modal');

    // Функция закрытия модального окна
    function closeModal() {
        modal.classList.add('hidden');
    }

    // Закрытие при клике вне области модального окна
    document.addEventListener('click', (event) => {
        if (!modal.classList.contains('hidden') && !modal.contains(event.target)) {
            closeModal();
        }
    });

    // Закрытие по нажатию клавиши ESC
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    // Закрытие по кнопке внутри модального окна
    closeButton.addEventListener('click', closeModal);
}