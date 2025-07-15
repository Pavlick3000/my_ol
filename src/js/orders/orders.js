const orderCache = {};

// Универсальная функция-загрузчик (для применения в нескольких функция, чтобы избежать дублирование кода)
async function fetchOrderDetails(orderId, refresh = false) {
    if (!refresh && orderCache[orderId]) {
        return orderCache[orderId]; // используем локальный кэш
    }

    try {
        let url = `/orders/orderDetails/${orderId}/`;
        if (refresh) {
            url += `?refresh=1&t=${Date.now()}`; // обойти HTTP-кэш
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Ошибка при загрузке данных заказа');

        const data = await response.json();

        orderCache[orderId] = data; // сохраняем в кэш
        return data;
        // console.log(result.data);  // ← данные заказа
        // console.log(result.items_data);
    } catch (error) {
        console.error('Ошибка загрузки данных заказа:', error);
        return null;
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

// Открытие модального окна с составом "Заказа покупателя"
async function toggleOrderModal(row = null, orderData = null) {

    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // Основной контейнер модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loaderOpen = document.getElementById('loading-spinner');

    const orderId = row.dataset.id;

    modal.dataset.orderId = orderId; // Сохраняем ID заказа в модальном окне

    // Настройки размеров
    // const modalHorizontalOffset = '-450px';
    const modalVerticalOffset = '-380px';
    const modalWidth = '900px';
    const minModalHeight = '350px'; // Минимальная высота модального окна

    // Позиционирование (фиксируем верхнюю границу)
    modalContent.style.width = modalWidth;
    modalContent.style.minHeight = minModalHeight; // Устанавливаем минимальную высоту
    modalContent.style.position = 'absolute';
    // modalContent.style.left = `calc(50% + ${modalHorizontalOffset})`;
    modalContent.style.left = '50%';
    modalContent.style.top = `calc(50% + ${modalVerticalOffset})`;
    modalContent.style.transform = 'translate(-50%, 0)';
    modalContent.style.maxHeight = '780px';

    loaderOpen.classList.remove('hidden');

    let data = orderData;

        if (!data) {
            data = await fetchOrderDetails(orderId); // запрос делается только если данных нет
            // console.log('data:', data);
        }
        if (!data) return;

    document.getElementById('order-number-display').textContent = data.number;
    document.getElementById('order-date-display').textContent = data.date_of_formation;
    document.getElementById('order-buyer-display').textContent = data.buyer;
    document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU');

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

    // loader.classList.remove('hidden');
    modal.classList.remove('hidden');

    // Обработчики закрытия
    closeModalButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => e.target === modal && modal.classList.add('hidden'));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && modal.classList.add('hidden'));

    loaderOpen.classList.add('hidden');
    // Загрузка данных заказа
    await loadProductTab(orderId, loaderOpen, data);

    // Загружаем дерево только при первом открытии вкладки
    const treeContainer = document.getElementById('specs-tree-container');
    treeContainer.innerHTML = ''; // очистить старое

    if (treeContainer.innerHTML.trim() === '') {
        try {
            // await loadSpecsTree(orderId);
        } catch (error) {
            console.error('Ошибка при загрузке дерева спецификации:', error);
        }
    }

}

// Загрузка данных заказа - вкладка "Товары"
async function loadProductTab(orderId, loaderOpen, data) {
    try {
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';

        const fragment = document.createDocumentFragment();

        data.items.forEach(item => {
            const itemRow = document.createElement('tr');
            itemRow.className = 'hover:text-emerald-500';
            itemRow.dataset.itemId = item.id;
            itemRow.dataset.itemName = item.name;
            itemRow.dataset.key = item.key;
            itemRow.dataset.key_material = item.key_material;
            itemRow.dataset.id_for_filter_material = item.id_for_filter_material;
            itemRow.innerHTML = `
                <td class="text-sm px-2 py-1 text-center">${item.id}</td>
                <td class="text-sm px-2 py-1 text-center">${item.line_number}</td>
                <td class="text-sm px-2 py-1">${item.name}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.quantity).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.price).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.amount).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.total).toLocaleString('ru-RU')}</td>
            `;

            const specToggleBtn = document.createElement('button');
            specToggleBtn.textContent = '▸';
            specToggleBtn.className = 'ml-2 text-emerald-600 hover:text-emerald-800';
            specToggleBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const specRow = document.getElementById(`spec-for-${item.id}`);
                const isHidden = specRow.classList.contains('hidden');
                if (isHidden) {
                    await loadSpecsForItem(orderId, item.id);
                } else {
                    specRow.classList.add('hidden');
                }
            });

            itemRow.querySelector('td:nth-child(1)').appendChild(specToggleBtn);
            fragment.appendChild(itemRow);

            const specRow = document.createElement('tr');
            specRow.id = `spec-for-${item.id}`;
            specRow.className = 'hidden';
            specRow.innerHTML = `
                <td colspan="7" class="bg-gray-50">
                    <div id="spec-container-${item.id}" class="ml-4 text-sm text-gray-700" data-loaded="false">
                        <!-- Сюда будет загружено дерево -->
                    </div>
                </td>
            `;
            fragment.appendChild(specRow);
        });

        tableBody.appendChild(fragment);

        const maxLineNumber = data.items.length > 0
            ? Math.max(...data.items.map(item => item.line_number))
            : 0;
        document.getElementById('max-line-number').textContent = maxLineNumber;

    } catch (error) {
        // Можно убрать или обработать иначе, если нужно
    }
}

// Загрузка дерева
async function loadSpecsForItem(orderId, itemId) {
    const specContainer = document.getElementById(`spec-container-${itemId}`);
    const specRow = document.getElementById(`spec-for-${itemId}`);

    if (!specContainer || !specRow) {
        return;
    }

    specRow.classList.remove('hidden');

    if (specContainer.dataset.loaded === 'true') {
        return;
    }

    try {
        const response = await fetch(`/orders/get_spec_tree_by_item/${orderId}/${itemId}/`);

        if (!response.ok) throw new Error('Ошибка при получении спецификации');

        const data = await response.json();

        specContainer.innerHTML = '';
        await renderSpecTree(data.items, specContainer, 0);
        specContainer.dataset.loaded = 'true';

    } catch (error) {
        specContainer.innerHTML = '<p class="text-red-500">Ошибка загрузки</p>';
    }
}

// Отрисовка дерева
async function renderSpecTree(items, parentElement, level = 0) {
    if (!items || items.length === 0) {
        const p = document.createElement('p');
        p.className = 'text-gray-500 text-sm italic';
        p.textContent = 'Нет данных для отображения.';
        parentElement.appendChild(p);
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'space-y-2';

    items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'spec-node';

        const div = document.createElement('div');
        div.className = `ml-${level * 4} text-xs bg-gray-50 flex justify-between p-1 rounded`;

        const spanLeft = document.createElement('span');
        spanLeft.className = 'flex items-center gap-2';

        if (item.children && item.children.length > 0) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'toggle-node text-emerald-600 hover:text-emerald-800';
            toggleBtn.type = 'button';
            toggleBtn.textContent = '▸';
            toggleBtn.onclick = () => {
                const childrenContainer = li.querySelector('.children-container');
                if (childrenContainer.classList.contains('hidden')) {
                    childrenContainer.classList.remove('hidden');
                    toggleBtn.textContent = '▾';
                } else {
                    childrenContainer.classList.add('hidden');
                    toggleBtn.textContent = '▸';
                }
            };
            spanLeft.appendChild(toggleBtn);
        } else {
            const placeholder = document.createElement('span');
            placeholder.className = 'inline-block w-4';
            spanLeft.appendChild(placeholder);
        }

        const nameSpan = document.createElement('span');
        nameSpan.textContent = item.ComponentName || '(без названия)';
        spanLeft.appendChild(nameSpan);

        const rightSpan = document.createElement('span');
        rightSpan.className = 'text-right text-xs text-gray-600';
        rightSpan.textContent = `${parseFloat(item.TotalQuantity)} ${item.basic_unit || ''}`;

        div.appendChild(spanLeft);
        div.appendChild(rightSpan);
        li.appendChild(div);

        if (item.children && item.children.length > 0) {
            const childrenDiv = document.createElement('div');
            childrenDiv.className = 'children-container ml-4 hidden';
            renderSpecTree(item.children, childrenDiv, level + 1);
            li.appendChild(childrenDiv);
        }

        ul.appendChild(li);
    });

    parentElement.appendChild(ul);
}






