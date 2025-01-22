// Функция перерисовки таблицы после обновления данных
function renderTable(data) {
    const tbody = document.querySelector('#productTable tbody');
    tbody.innerHTML = ''; // Очищаем текущие строки

    data.forEach(product => {
        const row = document.createElement('tr');
        row.className = 'cursor-pointer hover:text-red-400';
        row.dataset.id = product.id;
        row.dataset.fieldCode = product.field_code;
        row.dataset.name = product.name;
        row.dataset.typeOfReproduction = product.type_of_reproduction;
        row.dataset.basicUnit = product.basic_unit;
        row.dataset.url = product.url;
        row.onclick = () => toggleEditModal(row);

        row.innerHTML = `
            <td class="font-light">${product.id}</td>
            <td>${product.field_code}</td>
            <td class="font-medium">${product.name}</td>
            <td>${product.type_of_reproduction}</td>
            <td>${product.basic_unit}</td>
        `;
        tbody.appendChild(row);
    });
}

// Функция обновления данных таблицы
async function updateTable(recordId = null) {
    // Генерация уникального параметра для предотвращения кеширования
    const timestamp = new Date().getTime();
    const url = recordId
        ? `/catalog/update_table/?id=${recordId}&_=${timestamp}`
        : `/catalog/update_table/?_=${timestamp}`;

    const response = await fetch(url, { cache: "no-store" });

    if (!response.ok) {
        console.error('Error fetching data:', response.statusText);
        return;
    }

    const data = await response.json();
    console.log("Received data:", data);
    renderTable(data.data);
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

