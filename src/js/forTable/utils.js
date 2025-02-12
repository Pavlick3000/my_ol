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

// Функция для получения CSRF-токена
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

function clearInput() {
        document.getElementById("searchInput").value = "";
        filterTableByName();  // Запускаем фильтрацию с пустым значением
    }

// Функция обновления данных таблицы
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





