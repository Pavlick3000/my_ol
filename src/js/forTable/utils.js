// Функция перерисовки таблицы после обновления данных
function renderTable(data) {
    console.log(data);
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
        row.dataset.qnt = product.qnt;
        row.dataset.url = product.url;
        row.onclick = () => toggleEditModal(row);

        // Заменяем значение qnt на 0, если оно null или undefined
        const qnt = product.qnt == null ? 0 : product.qnt;

        row.innerHTML = `
            <td class="font-light">${product.id}</td>
            <td>${product.field_code}</td>
            <td class="font-medium">${product.name}</td>
            <td class="text-center">${product.type_of_reproduction}</td>
            <td class="text-center">${product.basic_unit}</td>
            <td class="text-center">${qnt}</td> <!-- Используем qnt, замененный на 0, если оно null или undefined -->
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
    console.log("Received full response:", data);
    console.log("Received data:", data.data);
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

