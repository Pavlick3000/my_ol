async function toggleOrderModal(row = null, modalHorizontalOffset = '450px', modalVerticalOffset = '-380px') {
    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // Основной контейнер модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loader = document.getElementById('loading-spinner');

    const orderId = row.dataset.id;

    // Настройки размеров
    const modalWidth = '900px';
    const minModalHeight = '350px'; // Минимальная высота модального окна

    try {
        loader.classList.remove('hidden');
        const response = await fetch(`/orders/orderDetails/${orderId}/`);
        const data = await response.json();

        // Заполнение данных
        document.getElementById('order-number-display').textContent = data.number;
        document.getElementById('order-date-display').textContent = data.date_of_formation;
        document.getElementById('order-buyer-display').textContent = data.buyer;
        document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU');

        // Заполнение таблицы
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';
        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'cursor-pointer hover:text-emerald-500';
            row.innerHTML = `
                <td class="text-sm px-2 py-1">${item.line_number}</td>
                <td class="text-sm px-2 py-1">${item.name}</td>                
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.quantity).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.price).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.amount).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.total).toLocaleString('ru-RU')}</td>
            `;
            tableBody.appendChild(row);
        });

        // Позиционирование (фиксируем верхнюю границу)
        const topPosition = `calc(50% + ${modalVerticalOffset})`;

        modalContent.style.width = modalWidth;
        modalContent.style.minHeight = minModalHeight; // Устанавливаем минимальную высоту
        modalContent.style.position = 'absolute';
        modalContent.style.left = `calc(50% + ${modalHorizontalOffset})`;
        modalContent.style.top = topPosition;
        modalContent.style.transform = 'translate(-50%, 0)';

        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Ошибка:', error);
    } finally {
        loader.classList.add('hidden');
    }

    // Обработчики закрытия
    closeModalButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => e.target === modal && modal.classList.add('hidden'));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && modal.classList.add('hidden'));
}