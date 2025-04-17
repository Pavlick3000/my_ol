// Функция для открытия и закрытия модального окна (Форма "Просмотр Заказ покупателя")
async function toggleOrderModal(row = null, modalHorizontalOffset = '350px', modalVerticalOffset = '-145px') {
    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // внутренний div модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loader = document.getElementById('loading-spinner'); // Лоадер

    const orderId = row.dataset.id;

    // Настройки размеров модального окна
    const modalWidth = '800px';
    const modalHeight = '450px';

    try {
        // Показать лоадер перед загрузкой данных
        loader.classList.remove('hidden');

        const response = await fetch(`/orders/orderDetails/${orderId}/`);
        const data = await response.json();

        // Заполнение шапки
        document.getElementById('order-number-display').textContent = data.number;
        document.getElementById('order-date-display').textContent = data.date_of_formation;
        document.getElementById('order-buyer-display').textContent = data.buyer;
        // document.getElementById('order-total-display').textContent = data.total;
        document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 });


        // Очистка и заполнение таблицы
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';

        data.items.forEach((item, index) => {
            const row = document.createElement('tr');
            const formattedTotal = parseFloat(item.total).toLocaleString('ru-RU', {
                maximumFractionDigits: 2,
                minimumFractionDigits: 0 // убираем нули после запятой, если их нет
            });

            row.innerHTML = `
                <td class="px-2 py-1">${item.line_number}</td>
                <td class="px-2 py-1">${item.name}</td>
                <td class="px-2 py-1 text-right">${item.quantity}</td>
                <td class="px-2 py-1 text-right">${formattedTotal}</td>
            `;
            tableBody.appendChild(row);
        });

        // Показать модалку
        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Ошибка при загрузке деталей заказа:', error);
    } finally {
        // Скрыть лоадер после завершения
        loader.classList.add('hidden');
    }

    // Применяем размеры к модальному окну
    if (modalContent) {
        modalContent.style.width = modalWidth;
        modalContent.style.height = modalHeight;
        modalContent.style.maxHeight = '90vh';
        modalContent.style.overflowY = 'auto';
        modalContent.style.position = 'absolute';
        modalContent.style.left = `calc(50% + ${modalHorizontalOffset})`;
        modalContent.style.top = `calc(50% + ${modalVerticalOffset})`;
        modalContent.style.transform = 'translate(-50%, -50%)';
    }

    // Обработчики закрытия модального окна
    closeModalButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (event) => {
        if (event.target === modal) modal.classList.add('hidden');
    });
    document.addEventListener('keydown', function escKey(event) {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
            document.removeEventListener('keydown', escKey);
        }
    });
}
