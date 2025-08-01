const orderCache = {};
let activeTabLeftId = null;
let activeTabRightId = null;
let isItemSelected = false;
let currentOrderData = null;
let currentSelectedItemId = null;
let activeSelectedCategory = ''; // сохраняем выбранную категорию
let currentOrderId = null;
let currentPath = null;

// Переменные для сортировки таблицы "Материалы"
let currentSortField = 'ComponentName';
let currentSortDirection = 'asc'; // 'asc' | 'desc'
let allMaterialData = [];


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

    } catch (error) {
        console.error('Ошибка загрузки данных заказа:', error);
        return null;
    }
}

// Сортировка по выбранному полю и направлению
function sortItems(items) {
    return items.sort((a, b) => {
        const valA = currentSortField === 'TotalQuantity'
            ? parseFloat(a.TotalQuantity)
            : a.ComponentName.toLowerCase();

        const valB = currentSortField === 'TotalQuantity'
            ? parseFloat(b.TotalQuantity)
            : b.ComponentName.toLowerCase();

        if (valA < valB) return currentSortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

// Вкладки модального окна - левая колонка
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTabId = btn.dataset.tab;
        const targetContent = document.getElementById(targetTabId);
        activeTabLeftId = targetTabId;

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

        updateResetSelectButtonVisibility();

    });
});

// Вкладки модального окна - правая колонка
document.querySelectorAll('.second-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTabId = btn.dataset.tab;
        const targetContent = document.getElementById(targetTabId);
        activeTabRightId = targetTabId;

        // 1. Скрыть ВЕСЬ контент вкладок
        document.querySelectorAll('.second-tab-content').forEach(tab => {
            tab.classList.add('hidden');
        });

        // 2. Показать только выбранную вкладку
        targetContent.classList.remove('hidden');

        // 3. Обновить подчеркивание (если ещё не сделано)
        document.querySelectorAll('.second-tab-btn').forEach(otherBtn => {
            otherBtn.classList.remove('border-emerald-500');
            otherBtn.classList.add('border-transparent');
        });

        btn.classList.remove('border-transparent');
        btn.classList.add('border-emerald-500');

        updateResetFilterButtonVisibility();

    });
});

// Клик для кнопки "сбросить выделения"
document.getElementById('reset-select-btn').addEventListener('click', () => {
    const orderId = document.getElementById('ordermodal').dataset.orderId;
    const loaderMaterial = document.getElementById('materials-loader');
    const loaderOpen = document.getElementById('loading-spinner');

    // Удалить выделение
    clearSelectionHighlight();

    // Очистить фильтр категории
    currentSelectedItemId = null;
    currentPath = null;
    currentSortDirection = 'asc';
    currentSortField = 'ComponentName';
    resetCategoryFilter();

    // Для очистки поля поиска таблицы "материалы"
    clearInputMaterials('searchInputMaterials');

    if (!currentOrderData) {
        console.error('Данные заказа не сохранены');
        return;
    }

    loaderMaterial.classList.remove('hidden');
    loadProductTab(orderId, loaderOpen, currentOrderData);

});

// Изменение иконок сортировки
function updateSortIcons() {
    const iconName = document.getElementById('iconName');
    const iconQty = document.getElementById('iconQuantity');

    iconName.classList.add('hidden');
    iconQty.classList.add('hidden');

    if (currentSortField === 'ComponentName') {
        iconName.classList.remove('hidden');
        iconName.src = iconName.dataset[currentSortDirection === 'asc' ? 'iconAsc' : 'iconDesc'];
    } else if (currentSortField === 'TotalQuantity') {
        iconQty.classList.remove('hidden');
        iconQty.src = iconQty.dataset[currentSortDirection === 'asc' ? 'iconAsc' : 'iconDesc'];
    }
}

// Изменение иконки фильтра по категории
function updateFilterIcon() {
    const filterIcon = document.getElementById('FilterIcon');
    const defaultIcon = filterIcon.dataset.iconDefault;
    const onIcon = filterIcon.dataset.iconOn;

    if (activeSelectedCategory) {
        filterIcon.src = onIcon;
    } else {
        filterIcon.src = defaultIcon;
    }
}

// Функция сброса фильтра по категории
function resetCategoryFilter() {
    activeSelectedCategory = '';
    updateFilterIcon()

    document.getElementById('categoryDropdown')?.classList.add('hidden');
    document.getElementById('reset-filter-btn')?.classList.add('hidden');
    document.getElementById('selectedCategoryLabel').textContent = '';


    loadMaterialsTable(currentOrderId, currentSelectedItemId, currentPath, activeSelectedCategory).then(() => {
        filterMaterialsTable('searchInputMaterials', 'materials-table-body');
    });
}

// Функция для очистки выделения цветом
function clearSelectionHighlight() {
    document.querySelectorAll('[data-selected="true"]').forEach(el => {
        el.classList.remove('!bg-emerald-100');
        delete el.dataset.selected;
    });

    isItemSelected = false;
    updateResetSelectButtonVisibility(); // Обновляем видимость кнопки

}

// Функция для показа кнопки "сбросить выделения"
function updateResetSelectButtonVisibility() {
    const resetBtn = document.getElementById('reset-select-btn');
    if (activeTabLeftId === 'products-tab' && isItemSelected) {
        resetBtn.classList.remove('hidden');
    } else {
        resetBtn.classList.add('hidden');
    }

}

// Функция для показа кнопки "сбросить фильтр"
function updateResetFilterButtonVisibility() {
    const resetBtn = document.getElementById('reset-filter-btn');
    if (activeTabRightId === 'material-tab' && activeSelectedCategory) {
        resetBtn.classList.remove('hidden');
    } else {
        resetBtn.classList.add('hidden');
    }

}

// Открытие модального окна с составом "Заказа покупателя"
async function toggleOrderModal(row = null, orderData = null) {

    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // Основной контейнер модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loaderOpen = document.getElementById('loading-spinner');
    const loaderMaterial = document.getElementById('materials-loader');

    const orderId = row.dataset.id;
    currentOrderId = orderId;
    currentSortDirection = 'asc';
    currentSortField = 'ComponentName';

    modal.dataset.orderId = orderId; // Сохраняем ID заказа в модальном окне// document.getElementById('order-and-component-display').textContent = `#${orderId} / Компонент: -`;

    // Настройки размеров
    // const modalHorizontalOffset = '-450px';
    const modalVerticalOffset = '-380px';
    const modalWidth = '1680px';
    const minModalHeight = '350px'; // Минимальная высота модального окна

    // Позиционирование (фиксируем верхнюю границу)
    modalContent.style.width = modalWidth;
    modalContent.style.minHeight = minModalHeight; // Устанавливаем минимальную высоту
    modalContent.style.position = 'absolute';
    modalContent.style.left = '50%';
    modalContent.style.top = `calc(50% + ${modalVerticalOffset})`;
    modalContent.style.transform = 'translate(-50%, 0)';
    modalContent.style.maxHeight = '900px';

    loaderOpen.classList.remove('hidden');
    loaderMaterial.classList.remove('hidden');

    let data = orderData;

        if (!data) {
            data = await fetchOrderDetails(orderId); // запрос делается только если данных нет
        }
        if (!data) return;

        currentOrderData = data;

    document.getElementById('order-number-display').textContent = data.number;
    document.getElementById('order-date-display').textContent = data.date_of_formation;
    document.getElementById('order-buyer-display').textContent = data.buyer;
    document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU');

    // Активация вкладки "товары" в левой части окна
    // Вкладка "Товары" выбирается по умолчанию
    const productsTabBtn = document.querySelector('.tab-btn[data-tab="products-tab"]');
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

    // При открытии окна ни одна строка не выделена, указываем это в переменной и запускаем проверку для видимости кнопки "сбросить выделения"
    isItemSelected = false;
    activeSelectedCategory = '';
    document.getElementById('selectedCategoryLabel').textContent = '';
    document.getElementById('reset-filter-btn').classList.add('hidden');
    updateResetSelectButtonVisibility();


    // Активация вкладки "Дашборд" в правой части окна
    // Вкладка "Дашборд" выбирается по умолчанию
    const DashboardTabBtn = document.querySelector('.second-tab-btn[data-tab="material-tab"]');
    DashboardTabBtn.classList.remove('border-transparent');
    DashboardTabBtn.classList.add('border-emerald-500');

    document.querySelectorAll('.second-tab-btn').forEach(btn => {
        if (btn.dataset.tab !== "dashboard-tab") {
            btn.classList.remove('border-emerald-500');
            btn.classList.add('border-transparent');
        }
    });

    DashboardTabBtn.click(); // Переключаем на вкладку "Материалы"
    // Конец

    modal.classList.remove('hidden');

    // Обработчики закрытия
    closeModalButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => e.target === modal && modal.classList.add('hidden'));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && modal.classList.add('hidden'));

    // Закрытие выпадающего списка, на случай если окно было закрыто с развернутым списком.
    const dropdown = document.getElementById('categoryDropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }

    loaderOpen.classList.add('hidden');

    // Загрузка данных заказа
    await loadProductTab(orderId, loaderOpen, data); // левая часть - дерево
    await loadMaterialsTable(orderId, null, null); // правая часть - таблица материалов

}

// Загрузка данных заказа - вкладка "Товары"
async function loadProductTab(orderId, loaderOpen, data) {
    const loaderMaterial = document.getElementById('materials-loader');

    try {
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';

        const fragment = document.createDocumentFragment();

        data.items.forEach(item => {
            const itemRow = document.createElement('tr');
            itemRow.className = 'cursor-pointer parent-row product-row border-b border-gray-300 hover:text-emerald-500';
            itemRow.dataset.itemId = item.id;
            itemRow.dataset.itemName = item.name;
            itemRow.dataset.key = item.key;
            itemRow.dataset.key_material = item.key_material;
            itemRow.dataset.id_for_filter_material = item.id_for_filter_material;
            itemRow.innerHTML = `
<!--                <td class="text-sm px-2 py-1 text-center">${item.id}</td>-->
                <td class="text-sm px-2 py-1 text-center">${item.line_number}</td>
                <td class="text-sm px-2 py-1">${item.name}</td>
                <td class="text-sm px-2 py-1 text-center">${parseFloat(item.quantity).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-center">${parseFloat(item.price).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-center">${parseFloat(item.amount).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-center">${parseFloat(item.total).toLocaleString('ru-RU')}</td>
            `;

            // Добавляем обработчик клика на строку
            itemRow.addEventListener('click', () => {

                // Подсветка
                clearSelectionHighlight();
                itemRow.classList.add('!bg-emerald-100');
                itemRow.dataset.selected = 'true';

                // Указываем в переменной факт клика и запускаем проверку для видимости кнопки "сбросить выделения"
                isItemSelected = true;
                updateResetSelectButtonVisibility();

                currentSelectedItemId = item.id;
                currentPath = null;
                resetCategoryFilter(); // от сюда мы потом грузим саму таблицу

                loaderMaterial.classList.remove('hidden');

            });

            const specToggleBtn = document.createElement('button');
            specToggleBtn.textContent = '▸';
            specToggleBtn.className = 'ml-2 text-emerald-600 hover:text-emerald-800';
            specToggleBtn.addEventListener('click', async (e) => {
                // e.stopPropagation();
                const specRow = document.getElementById(`spec-for-${item.id}`);
                const isHidden = specRow.classList.contains('hidden');

                if (isHidden) {
                    await loadSpecsForItem(orderId, item.id);
                    specToggleBtn.textContent = '▾';
                } else {
                    specRow.classList.add('hidden');
                    specToggleBtn.textContent = '▸';
                }
            });

            itemRow.querySelector('td:nth-child(1)').appendChild(specToggleBtn);
            fragment.appendChild(itemRow);

            const specRow = document.createElement('tr');
            specRow.id = `spec-for-${item.id}`;
            specRow.className = 'hidden';
            specRow.innerHTML = `
                <td colspan="6" class=""> <!-- тут можно указать фон "за деревом" -->
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

        // Красим зеброй таблицу
        const itemRows = document.querySelectorAll('#order-items-table .product-row');
        itemRows.forEach((row, index) => {
            if (row.dataset.selected) return;
            row.classList.remove('bg-gray-50', 'bg-white');
            row.classList.add(index % 2 === 1 ? 'bg-gray-50' : 'bg-white');
        });

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
        const response = await fetch(`/orders/getSpecTreeByItem/${orderId}/${itemId}/`);

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
async function renderSpecTree(items, parentElement, level = 0, options = {}) {
    const defaultOptions = {
        baseIndent: 0,
        indentMultiplier: 1,
        indentUnit: 'px',
        showToggle: true,
        toggleClosed: '▸',
        toggleOpen: '▾',
        toggleSize: '10px',
        itemClass: '',
        containerClass: '',
        treeOffset: 22
    };

    options = { ...defaultOptions, ...options };

    if (!items || items.length === 0) {
        const p = document.createElement('p');
        p.className = 'text-gray-500 text-sm italic';
        p.textContent = 'Нет данных для отображения.';
        parentElement.appendChild(p);
        return;
    }

    const container = document.createElement('div');
    container.className = `${options.containerClass}`.trim();
    container.style.marginLeft = `${options.treeOffset}${options.indentUnit}`;

    items.forEach(item => {
        const nodeWrapper = document.createElement('div');
        nodeWrapper.className = `spec-node ${options.itemClass}`.trim();

        const node = document.createElement('div');
        node.className = 'text-xs bg-gray-100 flex justify-between p-1 text-gray-600 hover:text-emerald-500'; // классы для оформления дерева
        node.style.paddingLeft = `${level * options.baseIndent * options.indentMultiplier}${options.indentUnit}`;

        node.dataset.componentId = item.ComponentDbId;
        node.dataset.path = item.Path || '';

        // Добавляем cursor-pointer только если есть дети
        const hasChildren = item.children && item.children.length > 0;
        if (hasChildren) {
            node.classList.add('cursor-pointer');

            // Добавляем обработчик клика только для элементов с детьми
            node.addEventListener('click', (e) => {
                if (e.target.classList.contains('toggle-node')) return;

                // Удаляем подсветку со всех ранее выбранных
                document.querySelectorAll('.bg-emerald-100').forEach(el => el.classList.remove('bg-emerald-100'));

                // Подсветка
                clearSelectionHighlight();
                node.classList.add('!bg-emerald-100');
                node.dataset.selected = 'true';

                // Указываем в переменной факт клика по дереву и запускаем проверку для видимости кнопки "сбросить выделения"
                isItemSelected = true;
                updateResetSelectButtonVisibility();

                const path = node.dataset.path || '';

                currentPath = path;
                currentSelectedItemId = null;
                resetCategoryFilter(); // от сюда мы потом грузим саму таблицу

            });
        } else {
            // Стиль для элементов без детей
            node.classList.add('opacity-80');
        }

        const spanLeft = document.createElement('span');
        spanLeft.className = 'flex items-center gap-2';

        if (item.children && item.children.length > 0 && options.showToggle) {
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'toggle-node text-emerald-600';
            toggleBtn.type = 'button';
            toggleBtn.textContent = options.toggleClosed;
            toggleBtn.style.width = options.toggleSize;
            toggleBtn.style.minWidth = options.toggleSize;
            toggleBtn.onclick = () => {
                childrenContainer.classList.toggle('hidden');
                toggleBtn.textContent = childrenContainer.classList.contains('hidden')
                    ? options.toggleClosed
                    : options.toggleOpen;
            };
            spanLeft.appendChild(toggleBtn);
        } else if (options.showToggle) {
            const placeholder = document.createElement('span');
            placeholder.style.width = options.toggleSize;
            placeholder.style.minWidth = options.toggleSize;
            spanLeft.appendChild(placeholder);
        }

        const nameSpan = document.createElement('span');
        nameSpan.textContent = item.ComponentName || '(без названия)';
        spanLeft.appendChild(nameSpan);

        const spanRight = document.createElement('span');
        spanRight.className = 'text-right text-xs';
        spanRight.textContent = `${parseFloat(item.TotalQuantity)} ${item.basic_unit || ''}`;

        node.appendChild(spanLeft);
        node.appendChild(spanRight);
        nodeWrapper.appendChild(node);

        let childrenContainer = null;
        if (item.children && item.children.length > 0) {
            childrenContainer = document.createElement('div');
            childrenContainer.className = 'children-container hidden';
            childrenContainer.style.margin = '0';
            childrenContainer.style.padding = '0';
            renderSpecTree(item.children, childrenContainer, level + 1, options);
            nodeWrapper.appendChild(childrenContainer);
        }

        container.appendChild(nodeWrapper);
    });

    parentElement.appendChild(container);
}

// Таблица с материалами
async function loadMaterialsTable(orderId, itemId = null, path = '', selectedCategory = '') {
    const loaderMaterial = document.getElementById('materials-loader');
    const materialTableBody = document.getElementById('materials-table-body');
    const categoryDropdown = document.getElementById('categoryDropdown');

    loaderMaterial.classList.remove('hidden');
    materialTableBody.innerHTML = '';
    categoryDropdown.innerHTML = '';

    try {
        // Сбор query-параметров
        let endpoint = itemId
            ? `/orders/getFlatMaterials/${orderId}/item/${itemId}/`
            : `/orders/getFlatMaterials/${orderId}/`;

        const params = new URLSearchParams();
        if (path) params.set('path', path);
        if (selectedCategory) params.set('category', selectedCategory);

        if ([...params].length > 0) {
            endpoint += `?${params.toString()}`;
        }

        const response = await fetch(endpoint);
        const data = await response.json();
        allMaterialData = data.items;

        // Сортируем
        const sortedItems = sortItems(data.items);
        renderTable(sortedItems);

        // Обновляем иконки сортировки
        updateSortIcons();

        // Получение и отрисовка уникальных категорий
        const categories = Array.isArray(data.categories) ? data.categories : [];

        categories.forEach(category => {
            const option = document.createElement('div');
            option.className = 'cursor-pointer px-4 py-2 hover:bg-gray-100';
            option.dataset.category = category;
            option.textContent = category;
            categoryDropdown.appendChild(option);
        });

        // Навешиваем клики
        categoryDropdown.querySelectorAll('div[data-category]').forEach(item => {
            item.addEventListener('click', function () {
                selectedCategory = this.dataset.category;
                document.getElementById('categoryDropdown').classList.add('hidden');
                document.getElementById('reset-filter-btn').classList.remove('hidden');

                activeSelectedCategory = selectedCategory;
                updateFilterIcon();

                // Отображаем выбранную категорию
                const label = document.getElementById('selectedCategoryLabel');
                label.textContent = selectedCategory || '';

                const selectedRow = document.querySelector('.product-row[data-selected="true"]');
                const selectedItemId = selectedRow ? selectedRow.dataset.itemId : null;

                currentPath = path;

                loadMaterialsTable(currentOrderId, selectedItemId, path, selectedCategory).then(() => {
                    filterMaterialsTable('searchInputMaterials', 'materials-table-body');
                });
            });
        });

        const resetBtn = document.getElementById('reset-filter-btn');

        if (resetBtn) {
            resetBtn.addEventListener('click', resetCategoryFilter);
        }

    } catch (error) {
        materialTableBody.innerHTML = `<tr><td colspan="3" class="text-red-500">Ошибка загрузки</td></tr>`;
        console.error('Ошибка загрузки материалов:', error);
    } finally {
        loaderMaterial.classList.add('hidden');
    }
}

// Функция поиска таблицы "Материалы"
function filterMaterialsTable(inputId, tableBodyId) {
    const searchTerm = document.getElementById(inputId).value.toLowerCase();
    const rows = document.querySelectorAll(`#${tableBodyId} tr`);

    rows.forEach(row => {
        const componentName = row.children[0].textContent.toLowerCase(); // первая колонка
        row.style.display = componentName.includes(searchTerm) ? '' : 'none';
    });
}

// Слушатель поля поиск таблицы "Материалы"
document.getElementById('searchInputMaterials').addEventListener('input', function () {
    filterMaterialsTable('searchInputMaterials', 'materials-table-body');
});

// Слушатель кнопки "фильтр"
document.getElementById('CategoryFilterMaterials').addEventListener('click', function () {
    document.getElementById('categoryDropdown').classList.toggle('hidden');
});

// Слушатель кнопки сортировки поля "Наименование"
document.getElementById('sortByName').addEventListener('click', () => {
    if (currentSortField === 'ComponentName') {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortField = 'ComponentName';
        currentSortDirection = 'asc';
    }

    const sorted = sortItems(allMaterialData);
    renderTable(sorted);
    updateSortIcons();
    filterMaterialsTable('searchInputMaterials', 'materials-table-body');

});

// Слушатель кнопки сортировки поля "Кол-во"
document.getElementById('sortByQuantity').addEventListener('click', () => {
    if (currentSortField === 'TotalQuantity') {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortField = 'TotalQuantity';
        currentSortDirection = 'asc';
    }

    const sorted = sortItems(allMaterialData);
    renderTable(sorted);
    updateSortIcons();
    filterMaterialsTable('searchInputMaterials', 'materials-table-body');

});

// Функция отрисовки таблицы "Материалы" при сортировке
function renderTable(items) {
    const tbody = document.getElementById('materials-table-body');
    tbody.innerHTML = '';

    items.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'text-sm border-b';

        row.innerHTML = `
            <td class="px-2 py-1">${item.ComponentName}</td>
            <td class="px-2 py-1 text-center">${parseFloat(item.TotalQuantity).toLocaleString('ru-RU')}</td>
            <td class="px-2 py-1 text-center">${item.basic_unit}</td>
        `;

        tbody.appendChild(row);
    });
}
