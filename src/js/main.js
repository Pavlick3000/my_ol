// Сортировка по нажатию на имя столбца_
function sortTable(columnIndex) {
    const table = document.getElementById("productTable");
    let switching = true;
    let shouldSwitch, i;
    let dir = "asc";
    let switchCount = 0;

    while (switching) {
        switching = false;
        const rows = table.rows;
        for (i = 1; i < rows.length - 1; i++) {
            shouldSwitch = false;
            const x = rows[i].getElementsByTagName("TD")[columnIndex];
            const y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
            if (dir === "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir === "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchCount++;
        } else {
            if (switchCount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

// Функция для отображения модального окна с ошибкой о правах
function showModal(content) {
    // Создаем контейнер модального окна
    const modalContainer = document.createElement("div");
    modalContainer.innerHTML = content;
    document.body.appendChild(modalContainer);

    // Обработчик закрытия модального окна
    const closeModalButton = modalContainer.querySelector("#closeModal");
    if (closeModalButton) {
        closeModalButton.addEventListener("click", () => {
            modalContainer.remove();
        });
    }
}

// Функция подтверждения удаления
function confirmDeletion() {
    const elementId = document.getElementById("elementId").value;

    if (confirm("Вы уверены, что хотите удалить эту запись?")) {
        fetch(`/catalog/deleteRecord/${elementId}/`, { //TODO тут надо убрать хардкод!
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Получение CSRF-токена
            }
        })
        .then(async response => {
            if (response.ok) {
                // alert("Запись успешно удалена!");
                toggleEditModal();
                refreshTable(); // Обновляем таблицу
            } else if (response.status === 403) {
                const errorHtml = await response.text(); // Предполагаем, что сервер возвращает HTML модального окна
                showModal(errorHtml); // Отображаем модальное окно
            } else {
                alert("Ошибка при удалении записи.");
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Ошибка при удалении записи.");
        });
    }
}

// Поле поиск
function filterTable(searchInputId, fetchUrl, tableId) {
    let searchInput = document.getElementById(searchInputId).value.trim();

    fetch(`${fetchUrl}?search=${encodeURIComponent(searchInput)}`)
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, 'text/html');

            // Обновляем таблицу
            let newTableBody = doc.querySelector(`#${tableId} tbody`);
            document.querySelector(`#${tableId} tbody`).innerHTML = newTableBody.innerHTML;

            // Обновляем пагинацию
            let newPagination = doc.querySelector(".pagination");
            let paginationContainer = document.querySelector(".pagination");
            if (newPagination) {
                paginationContainer.innerHTML = newPagination.innerHTML;
            } else {
                paginationContainer.innerHTML = "";
            }
        })
        .catch(error => console.error('Ошибка поиска:', error));
}

// Использование функции для каталога: переменные для поля поиск
function filterTableByName() {
    filterTable("searchInput", "/catalog/", "productTable");
}

// Использование функции для заказов: переменные для поля поиск
function filterTableByNameOrders() {
    filterTable("searchInputOrders", "/orders/", "ordersTable");
}

