const orderCache = {};
let fullSpecsData = []; // глобально храним все строки

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

// Открытие модального окна с составом "Заказа покупателя"
async function toggleOrderModal(row = null, orderData = null) {
    const modal = document.getElementById('ordermodal');
    const modalContent = modal.querySelector('div'); // Основной контейнер модального окна
    const closeModalButton = document.getElementById('close-orders-modal');
    const loaderOpen = document.getElementById('loading-spinner');

    const orderId = row.dataset.id;

    modal.dataset.orderId = orderId; // Сохраняем ID заказа в модальном окне

    // Настройки размеров
    const modalHorizontalOffset = '-450px';
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

    loaderOpen.classList.remove('hidden');

    let data = orderData;

        if (!data) {
            data = await fetchOrderDetails(orderId); // запрос делается только если данных нет
            console.log('data:', data);
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
    // modal.addEventListener('click', (e) => e.target === modal && modal.classList.add('hidden'));
    // document.addEventListener('keydown', (e) => e.key === 'Escape' && modal.classList.add('hidden'));

    loaderOpen.classList.add('hidden');
    // Загрузка данных заказа
    await loadProductTab(orderId, loaderOpen, data);
    // console.log('[loadMaterialsTab] orderId:', order.id);
    await loadMaterialsTab(orderId, data);
    await loadSpecsData(orderId);
}

// Открытие модального окна с содержимым "спецификаций номенклатуры"\"список комплектующих"
async function toggleSecondModal(itemId, itemName, key) {
    const modalSecond = document.getElementById('specsModal');
    const modalSecondContent = modalSecond.querySelector('div');
    const closeSecondModalButton = document.getElementById('close-specs-modal');
    const loader = document.getElementById('modal-inner-loader');

    const modalHorizontalOffset = '460px';
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

// Открытие модального окна с "Материалами"
async function toggleMaterialModal() {
  const materialModal = document.getElementById('materialModal');
  const modalContent = materialModal.querySelector('div');

  // Настройки размеров
    const modalHorizontalOffset = '460px';
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


  // Активируем модальное окно
  materialModal.classList.remove('hidden');
  materialModal.classList.add('pointer-events-none'); // Отключаем события для всего окна
  modalContent.classList.add('pointer-events-auto'); // Включаем события для содержимого
}

// Закрытие модального окна с "Материалами"
function closeMaterialModal() {
  const materialModal = document.getElementById('materialModal');
  materialModal.classList.add('hidden');
  materialModal.classList.remove('pointer-events-none');
  const modalContent = materialModal.querySelector('div');
  modalContent.classList.remove('pointer-events-auto');
}

// Обработчик модального окна с "Материалами"
document.addEventListener("DOMContentLoaded", function() {
  // Открытие по кнопке
  document.getElementById("right-arrow-btn").addEventListener("click", toggleMaterialModal);

  // Закрытие
  document.getElementById("close-material-modal").addEventListener("click", closeMaterialModal);

});

// Загрузка данных заказа - вкладка "Товары"
async function loadProductTab(orderId, loaderOpen, data) {

    try {
        const tableBody = document.getElementById('order-items-table');
        tableBody.innerHTML = '';
        data.items.forEach(item => {
            const itemRow = document.createElement('tr');
            itemRow.className = 'cursor-pointer hover:text-emerald-500';
            itemRow.dataset.itemId = item.id;
            itemRow.dataset.itemName = item.name;
            itemRow.dataset.key = item.key;
            itemRow.dataset.key_material = item.key_material;
            itemRow.dataset.id_for_filter_material = item.id_for_filter_material;
            itemRow.innerHTML = `
                <td class="text-sm px-2 py-1">${item.line_number}</td>
                <td class="text-sm px-2 py-1">${item.name}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.quantity).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.price).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.amount).toLocaleString('ru-RU')}</td>
                <td class="text-sm px-2 py-1 text-right">${parseFloat(item.total).toLocaleString('ru-RU')}</td>
            `;
            itemRow.addEventListener('click', function () {
                const { itemId, itemName, key, key_material } = this.dataset;
                toggleSecondModal(itemId, itemName, key, key_material);
            });
            tableBody.appendChild(itemRow);
        });

        // Максимальный номер строки
        const maxLineNumber = data.items.length > 0
            ? Math.max(...data.items.map(item => item.line_number))
            : 0;
        document.getElementById('max-line-number').textContent = maxLineNumber;

        // Загрузка материалов
        loadMaterialsCount(orderId, data);
    } catch (error) {
        console.error('Ошибка:', error);
    } finally {
        // loaderOpen.classList.add('hidden');
    }
}

// Загрузка и отображение агрегированной номенклатуры - вкладка "Материалы"
async function loadMaterialsTab(orderId, data) {
    const materialsTabContent = document.getElementById('materials-tab');
    const loader = document.getElementById('materials-loader');
    const table = document.getElementById('materials-table');

    try {
        loader.classList.remove('hidden');
        table.classList.add('hidden');

        // Собираем все спецификации товаров
        const allMaterials = [];
        const materialPromises = [];


        for (const item of data.items) {
            materialPromises.push(
                fetch(`/orders/specsDetails/${item.id}/?key=${item.key}&key_material=${item.key_material}&id_for_filter_material=${item.id_for_filter_material}`)

                    .then(response => response.json())
                    .then(specData => {
                        if (specData.specs && specData.specs.length > 0) {
                            const multiplier = specData.use_quantity_multiplier === false ? 1 : parseFloat(item.quantity); // конструкция для умножения на единицу, если попался товар или материал
                            specData.specs.forEach(spec => {
                                allMaterials.push({
                                    name: spec.name,
                                    quantity: parseFloat(spec.quantity) * multiplier,
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
        materialsTableBody.innerHTML = '';
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
        table.classList.remove('hidden');
    }
}

// Прелоадер значения количество строк - вкладка "Материалы"
async function loadMaterialsCount(orderId, data) {
    const lineCounter = document.getElementById('materials-line-number');

    try {
        // Показываем индикатор загрузки
        lineCounter.textContent = '...';

        // Собираем все спецификации товаров
        const materialPromises = data.items.map(item =>
            fetch(`/orders/specsDetails/${item.id}/?key=${item.key}&key_material=${item.key_material}&id_for_filter_material=${item.id_for_filter_material}`)
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

// Обработчик кнопки "Обновить"
document.getElementById('refresh-order-btn').addEventListener('click', async () => {
    const orderId = document.getElementById('ordermodal').dataset.orderId;
    const loader = document.getElementById('loading-spinner');
    loader.classList.remove('hidden');

    const data = await fetchOrderDetails(orderId, true);
    if (!data) return;

    // Обновляем "шапку"
    document.getElementById('order-number-display').textContent = data.number;
    document.getElementById('order-date-display').textContent = data.date_of_formation;
    document.getElementById('order-buyer-display').textContent = data.buyer;
    document.getElementById('order-total-display').textContent = data.total.toLocaleString('ru-RU');

    // Перезагружаем вкладки
    await loadProductTab(orderId, loader, data);     // передаём данные, если хотим избежать повторного fetch
    await loadMaterialsTab(orderId, data);           // тоже самое
    updateOrderRowInTable(orderId, data);

    loader.classList.add('hidden');
});

// Для обновления записи, при открытии которой была нажата кнопка "обновить" внутри модального окна
function updateOrderRowInTable(orderId, data) {
    const row = document.querySelector(`tr[data-id="${orderId}"]`);
    if (!row) return;

    const cells = row.querySelectorAll('td');
    if (cells.length < 7) return;

    // Обновляем значения
    cells[2].textContent = data.number;
    cells[3].textContent = data.buyer;
    cells[4].textContent = formatNumber(data.total);

}
function formatNumber(value) {
    return Number(value).toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}


// Запуска обработчиков для отрисовка таблицы и списка фильтров вкладки "Материалы"
function loadSpecsData(orderId) {
    fetch(`/orders/specsDetailsSQL/${orderId}/`)
        .then(response => response.json())
        .then(data => {
            fullSpecsData = data.data || [];
            renderSpecsTable(fullSpecsData);
            renderCategoryDropdown(fullSpecsData, orderId);
        })
        .catch(error => console.error('Ошибка загрузки данных:', error));
}

// Отрисовка выпадающего списка во вкладке "Материалы"
function renderCategoryDropdown(data, orderId) {
    const container = document.getElementById('category-buttons');
    container.innerHTML = '';

    const uniqueCategories = [...new Set(data.map(item => item.CategoryName).filter(Boolean))];

    // Обёртка с относительным позиционированием
    const wrapper = document.createElement('div');
    wrapper.className = 'relative inline-block text-left z-50'; // z-50 для приоритета

    // Кнопка для открытия списка
    const button = document.createElement('button');
    button.textContent = 'Категория';
    button.className = 'inline-flex justify-center w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50';
    button.id = 'dropdown-button';

    // Выпадающее меню
    const menu = document.createElement('div');
    menu.className = `
    absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5
    hidden transition-opacity duration-150 overflow-y-auto scrollbar-custom
`;
    function adjustDropdownHeight() {
    const rect = button.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom - 95; // отступ от края
    menu.style.maxHeight = `${spaceBelow}px`;
}
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-orientation', 'vertical');
    menu.setAttribute('aria-labelledby', 'dropdown-button');

    // Опция "Все"
    const allOption = document.createElement('a');
    allOption.href = '#';
    allOption.textContent = 'Все';
    allOption.className = 'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100';
    allOption.onclick = (e) => {
        e.preventDefault();
        renderSpecsTable(fullSpecsData);
        menu.classList.add('hidden');
    };
    menu.appendChild(allOption);

    // Остальные категории
    uniqueCategories.forEach(category => {
        const item = document.createElement('a');
        item.href = '#';
        item.textContent = category;
        item.className = 'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100';
        item.onclick = (e) => {
            e.preventDefault();
            const filtered = fullSpecsData.filter(row => row.CategoryName === category);
            renderSpecsTable(filtered);
            menu.classList.add('hidden');
        };
        menu.appendChild(item);
    });

    // Открытие/закрытие
    button.onclick = (e) => {
        e.preventDefault();
        adjustDropdownHeight();
        menu.classList.toggle('hidden');
    };

    // Закрытие по клику вне
    document.addEventListener('click', (e) => {
        if (!wrapper.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });

    wrapper.appendChild(button);
    wrapper.appendChild(menu);
    container.appendChild(wrapper);
}

// Отрисовка таблицы во вкладке "Материалы"
function renderSpecsTable(data) {
    const tableBody = document.getElementById('specs-tab-table-body');
    tableBody.innerHTML = '';

    data.forEach((row, index)=> {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="text-sm px-2 py-1 text-gray-700 text-center">${index + 1}</td>
            <td class="text-sm px-2 py-1 text-gray-700">${row.ComponentName}</td>
            <td class="text-sm px-2 py-1 text-center">${parseFloat(row.TotalQuantity)}</td>
            <td class="text-sm px-2 py-1 text-center">${row.basic_unit}</td>
            <td class="text-sm px-2 py-1 text-gray-700 text-center">${row.CategoryName}</td>
            <td class="text-sm px-2 py-1 text-gray-700 text-center">${row.CategoryParentName}</td>
        `;
        tableBody.appendChild(tr);
    });
}



