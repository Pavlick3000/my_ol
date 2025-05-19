// Функция для открытия модального окна с содержимым "Заказа покупателя"
async function toggleOrderModal(row = null) {
    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // Основной контейнер модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loader = document.getElementById('loading-spinner');

    const orderId = row.dataset.id;
    modal.dataset.orderId = orderId; // Сохраняем ID заказа в модальном окне

    // Настройки размеров
    const modalHorizontalOffset = '450px';
    const modalVerticalOffset = '-380px';
    const modalWidth = '900px';
    const minModalHeight = '350px'; // Минимальная высота модального окна

    // Позиционирование (фиксируем верхнюю границу)
    modalContent.style.width = modalWidth;
    modalContent.style.minHeight = minModalHeight; // Устанавливаем минимальную высоту
    modalContent.style.position = 'absolute';
    modalContent.style.left = `calc(50% + ${modalHorizontalOffset})`;
    modalContent.style.top = `calc(50% + ${modalVerticalOffset})`;
    modalContent.style.transform = 'translate(-50%, 0)';
    modalContent.style.maxHeight = '780px';

    try {
        // Вкладка "Товары" выбирается по умолчанию
        const productsTabBtn = document.querySelector('.tab-btn[data-tab="products-tab"]');

        // Удаляем border-transparent и добавляем border-emerald-500
        productsTabBtn.classList.remove('border-transparent');
        productsTabBtn.classList.add('border-emerald-500');

        // Деактивируем остальные вкладки
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.tab !== "products-tab") {
                btn.classList.remove('border-emerald-500');
                btn.classList.add('border-transparent');
            }
        });

        productsTabBtn.click(); // Переключаем на вкладку "Товары"

        loader.classList.remove('hidden');
        const response = await fetch(`/orders/orderDetails/${orderId}/`);
        const data = await response.json();

        // Заполнение данных "Шапка"
        document.getElementById('order-number-display').textContent = data.number;
        document.getElementById('order-date-display').textContent = data.date_of_formation;
        document.getElementById('order-buyer-display').textContent = data.buyer;
        document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU');

        // Заполнение таблицы
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';
        data.items.forEach(item => {
            const itemRow = document.createElement('tr');  // переименовано
            itemRow.className = 'cursor-pointer hover:text-emerald-500';
            itemRow.dataset.itemId = item.id;
            itemRow.dataset.itemName = item.name;
            itemRow.dataset.key = item.key;
            itemRow.innerHTML = `
                <td class="text-sm px-2 py-1">${item.line_number}</td>
                <td class="text-sm px-2 py-1">${item.name}</td>                
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.quantity).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.price).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.amount).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.total).toLocaleString('ru-RU')}</td>
            `;
            itemRow.addEventListener('click', function () {
                const itemId = this.dataset.itemId;
                const itemName = this.dataset.itemName;
                const key = this.dataset.key;
                toggleSecondModal(itemId, itemName, key); // передаётся напрямую
            });
            tableBody.appendChild(itemRow);
        });

        // Найти и вставить максимальный line_number, если записей нет, то выводим 0
        const maxLineNumber = data.items.length > 0
            ? Math.max(...data.items.map(item => item.line_number))
            : 0;

        document.getElementById('max-line-number').textContent = maxLineNumber;
        // Запускаем фоновую загрузку материалов
        loadMaterialsCount(orderId);

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

// Загрузка и отображение агрегированной номенклатуры во вкладке "Материалы"
async function loadMaterialsTab(orderId) {
    const materialsTabContent = document.getElementById('materials-tab');
    const loader = document.getElementById('modal-inner-loader');

    // const loader = document.getElementById('materials-loader');
    // const table = document.getElementById('materials-table');
    // const loader = document.getElementById('modal-table-loader');

    try {
        loader.classList.remove('hidden');
        // table.classList.add('hidden');

        // Загружаем детали заказа
        const orderResponse = await fetch(`/orders/orderDetails/${orderId}/`);
        const orderData = await orderResponse.json();

        // Собираем все спецификации товаров
        const allMaterials = [];
        const materialPromises = [];

        for (const item of orderData.items) {
            materialPromises.push(
                fetch(`/orders/specsDetails/${item.id}/?key=${item.key}`)
                    .then(response => response.json())
                    .then(specData => {
                        if (specData.specs && specData.specs.length > 0) {
                            const itemQuantity = parseFloat(item.quantity);
                            specData.specs.forEach(spec => {
                                allMaterials.push({
                                    name: spec.name,
                                    quantity: parseFloat(spec.quantity) * itemQuantity,
                                    unit: spec.basic_unit
                                });
                            });
                        }
                    })
                    .catch(error => {
                        console.error(`Ошибка загрузки спецификации для товара ${item.id}:`, error);
                    })
            );
        }

        // Ждем завершения всех запросов
        await Promise.all(materialPromises);

        // Группируем материалы по наименованию и единицам измерения
        const groupedMaterials = {};

        allMaterials.forEach(material => {
            const key = `${material.name}|${material.unit}`;
            if (!groupedMaterials[key]) {
                groupedMaterials[key] = {
                    name: material.name,
                    quantity: 0,
                    unit: material.unit
                };
            }
            groupedMaterials[key].quantity += material.quantity;
        });

        // Сортируем материалы по наименованию
        const sortedMaterials = Object.values(groupedMaterials)
            .sort((a, b) => a.name.localeCompare(b.name));

        // Заполняем таблицу
        const materialsTableBody = document.getElementById('materials-table-body');

        sortedMaterials.forEach((material, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="text-sm px-2 py-1 text-center">${index + 1}</td>
                <td class="text-sm px-2 py-1">${material.name}</td>
                <td class="text-sm px-2 py-1 text-right">${material.quantity.toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-center">${material.unit}</td>
            `;
            materialsTableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Ошибка загрузки материалов:', error);
        materialsTabContent.innerHTML = `
            <p class="text-sm text-red-500">Ошибка загрузки списка материалов: ${error.message}</p>
        `;
    } finally {
        loader.classList.add('hidden');
        // table.classList.remove('hidden');
    }
}

// Функция для открытия модального окна с содержимым "спецификаций номенклатуры"\"список комплектующих"
async function toggleSecondModal(itemId, itemName, key) {
    const modalSecond = document.getElementById('specsModal');
    const modalSecondContent = modalSecond.querySelector('div');
    const closeSecondModalButton = document.getElementById('close-specs-modal');
    const loader = document.getElementById('modal-inner-loader');

    const modalHorizontalOffset = '-460px';
    const modalVerticalOffset = '-380px';
    const modalWidth = '900px';
    const minModalHeight = '300px';

    modalSecondContent.style.width = modalWidth;
    modalSecondContent.style.minHeight = minModalHeight;
    modalSecondContent.style.position = 'absolute';
    modalSecondContent.style.left = `calc(50% + ${modalHorizontalOffset})`;
    modalSecondContent.style.top = `calc(50% + ${modalVerticalOffset})`;
    modalSecondContent.style.transform = 'translate(-50%, 0)';
    modalSecondContent.style.maxHeight = '780px';

    try {
        loader.classList.remove('hidden');
        const response = await fetch(`/orders/specsDetails/${itemId}/?key=${key}`);
        // const response = await fetch(endpoint);
        const data = await response.json();

        // Заполнение данных "Шапка"
        const titleElement = document.getElementById('specs-modal-title');
        titleElement.textContent = `${data.title_prefix}: ${itemName}`;

        // Заполнение таблицы
        const specsTableBody = document.getElementById('specs-table-body');
        specsTableBody.innerHTML = '';
        data.specs.forEach(spec => {
            const row = document.createElement('tr');
            row.innerHTML = `                
                <td class="px-2 py-1 text-center">${spec.line_number}</td>
                <td class="px-2 py-1">${spec.name}</td>
                <td class="px-2 py-1 text-center">${parseFloat(spec.quantity).toLocaleString('ru-RU')}</td>
                <td class="px-2 py-1 text-center">${spec.basic_unit}</td>
            `;
            specsTableBody.appendChild(row);
        });

        modalSecond.classList.remove('hidden');

    } catch (error) {
        console.error('Ошибка загрузки спецификаций:', error);
    } finally {
        loader.classList.add('hidden');
    }

    closeSecondModalButton.addEventListener('click', () => modalSecond.classList.add('hidden'));
    modalSecond.addEventListener('click', (e) => e.target === modalSecond && modalSecond.classList.add('hidden'));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && modalSecond.classList.add('hidden'));

}

// Обработчик клика по вкладке "Материалы"
document.querySelector('.tab-btn[data-tab="materials-tab"]').addEventListener('click', function() {
    const modal = document.getElementById('ordermodal');
    const orderId = modal.dataset.orderId; // Получаем сохраненный ID заказа
    const materialsTableBody = document.getElementById('materials-table-body');

    if (orderId) {
        materialsTableBody.innerHTML = '';
        loadMaterialsTab(orderId);
    }
});

// Прелоадер значения количество строк во вкладке "Материалы"
async function loadMaterialsCount(orderId) {
    const lineCounter = document.getElementById('materials-line-number');

    try {
        // Показываем индикатор загрузки
        lineCounter.textContent = '...';

        const orderResponse = await fetch(`/orders/orderDetails/${orderId}/`);
        const orderData = await orderResponse.json();

        // Собираем все спецификации товаров
        const materialPromises = orderData.items.map(item =>
            fetch(`/orders/specsDetails/${item.id}/?key=${item.key}`)
                .then(response => response.json())
                .catch(() => ({ specs: [] })) // В случае ошибки возвращаем пустой массив
        );

        const allSpecs = await Promise.all(materialPromises);

        // Считаем уникальные материалы
        const uniqueMaterials = new Set();
        allSpecs.forEach(specData => {
            specData.specs?.forEach(spec => {
                uniqueMaterials.add(`${spec.name}|${spec.basic_unit}`);
            });
        });

        // Обновляем счетчик
        lineCounter.textContent = uniqueMaterials.size;

    } catch (error) {
        console.error('Ошибка подсчета материалов:', error);
        lineCounter.textContent = '0';
    }
}

// Вкладки модального окна
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTabId = btn.dataset.tab;
        const targetContent = document.getElementById(targetTabId);

        // 1. Скрыть ВЕСЬ контент вкладок
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.add('hidden');
        });

        // 2. Показать только выбранную вкладку
        targetContent.classList.remove('hidden');

        // 3. Обновить подчеркивание (если ещё не сделано)
        document.querySelectorAll('.tab-btn').forEach(otherBtn => {
            otherBtn.classList.remove('border-emerald-500');
            otherBtn.classList.add('border-transparent');
        });

        btn.classList.remove('border-transparent');
        btn.classList.add('border-emerald-500');
    });
});