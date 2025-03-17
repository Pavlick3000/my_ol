function formatQnt(qnt) {
    if (qnt == null) {
        return '0';
    }
    // Округляем до 3 знаков после запятой и удаляем лишние нули
    let formattedQnt = parseFloat(qnt).toFixed(3).replace(/\.?0+$/, '');

    // Разделяем целую часть и дробную часть (если есть)
    let [integerPart, decimalPart] = formattedQnt.split('.');

    // Форматируем целую часть с разделением на тысячи
    integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

    // Если есть дробная часть, добавляем её обратно
    return decimalPart ? `${integerPart}.${decimalPart}` : integerPart;
}

// Функция для получения CSRF-токена_
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для очистки поля поиска
function clearInput(searchInputId, filterFunction) {
    document.getElementById(searchInputId).value = ""; // Очищаем поле поиска
    filterFunction(); // Вызываем переданную функцию фильтрации
}

// Функция обновления данных таблицы при изменении записей
function updateTableRow(updatedProduct) {
    // Найти строку по data-id
    const row = document.querySelector(`tr[data-id="${updatedProduct.id}"]`);

    if (row) {
        // Форматируем значение qnt
        const formattedQnt = formatQnt(updatedProduct.qnt);

        // Обновляем текст в ячейках таблицы
        row.querySelector('td:nth-child(2)').textContent = updatedProduct.field_code;
        row.querySelector('td:nth-child(3)').textContent = updatedProduct.name;
        row.querySelector('td:nth-child(4)').textContent = updatedProduct.type_of_reproduction;
        row.querySelector('td:nth-child(5)').textContent = updatedProduct.basic_unit;
        row.querySelector('td:nth-child(6)').textContent = formattedQnt;

        // Обновляем атрибуты data-* в строке таблицы
        row.setAttribute('data-field-code', updatedProduct.field_code);
        row.setAttribute('data-name', updatedProduct.name);
        row.setAttribute('data-type-of-reproduction', updatedProduct.type_of_reproduction);
        row.setAttribute('data-basic-unit', updatedProduct.basic_unit);
        row.setAttribute('data-qnt', updatedProduct.qnt);

    }
}

// Функция для обновления содержимого таблицы при добавлении новой записи.
async function refreshTable() {
    try {
        const currentPage = new URLSearchParams(window.location.search).get("page") || 1;
        const searchQuery = new URLSearchParams(window.location.search).get("search") || "";

        // Генерация уникального параметра для предотвращения кеширования
        const timestamp = new Date().getTime();
        const url = `/catalog/?search=${encodeURIComponent(searchQuery)}&page=${currentPage}&_=${timestamp}`;

        const response = await fetch(url, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });

        if (response.ok) {
            const responseData = await response.json();
            updateTable(responseData.data);
        }
    } catch (error) {
        console.error("Ошибка обновления таблицы:", error);
    }
}

// Функция для обновления строк в таблице при добавлении новой записи.
function updateTable(data) {
    const tableBody = document.querySelector("#productTable tbody");
    tableBody.innerHTML = ""; // Очищаем старые данные

    data.forEach((product) => {
        const row = document.createElement("tr");
        row.className = "cursor-pointer hover:text-red-400";
        row.setAttribute("data-id", product.id);
        row.setAttribute("data-field-code", product.field_code);
        row.setAttribute("data-name", product.name);
        row.setAttribute("data-type-of-reproduction", product.type_of_reproduction);
        row.setAttribute("data-basic-unit", product.basic_unit);
        row.setAttribute("data-qnt", product.qnt);
        row.setAttribute("data-url", product.url);
        row.setAttribute("onclick", "toggleEditModal(this)");

        // Форматируем qnt с помощью formatQnt
        const formattedQnt = formatQnt(product.qnt);

        row.innerHTML = `
            <td class="font-light">${product.id}</td>
            <td>${product.field_code}</td>
            <td class="font-medium">${product.name}</td>
            <td class="text-center">${product.type_of_reproduction}</td>
            <td class="text-center">${product.basic_unit}</td>
            <td class="text-center">${formattedQnt}</td>
        `;

        tableBody.appendChild(row);
    });
}




