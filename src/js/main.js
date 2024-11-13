// Слушатель для каждого элемента таблицы, чтобы отслеживать клики
document.querySelectorAll('tbody tr').forEach(item => {item.addEventListener('contextmenu', handleCellClick);});

// Слушатель для каждого элемента таблицы, чтобы отслеживать клики
// {#document.querySelectorAll('tbody tr').forEach(item => {item.addEventListener('click', toggleEditModal);});#}

// Меню по нажатию ПКМ на запись в таблице
function handleCellClick(event) {
    // Отменяем стандартное контекстное меню правой кнопки мыши
    event.preventDefault();

    // Получите координаты клика
    const x = event.clientX;
    const y = event.clientY;

    const modal = document.getElementById('actionModal');

    modal.style.left = `${x}px`;
    modal.style.top = `${y}px`;
    modal.style.position = 'absolute';
    modal.classList.remove('hidden');

    // Добавьте обработчики для кнопок
    document.getElementById('editRecord').onclick = () => {
        if (confirm('Изменить?')) {
            window.location.href = `/edit/${recordId}/`;}
    };
    document.getElementById('deleteRecord').onclick = () => {
        if (confirm('Вы уверены, что хотите удалить эту запись?')) {
            window.location.href = `/delete/${recordId}/`;}
    };
}

// Функции для закрытия меню по нажатию ПКМ
function setupModalListeners(modalId) {
    const modal = document.getElementById(modalId);
    const closeButton = modal.querySelector('.close-modal');

    // Функция закрытия модального окна
    function closeModal() {
        modal.classList.add('hidden');
    }

    // Закрытие при клике вне области модального окна
    document.addEventListener('click', (event) => {
        if (!modal.classList.contains('hidden') && !modal.contains(event.target)) {
            closeModal();
        }
    });

    // Закрытие по нажатию клавиши ESC
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    // Закрытие по кнопке внутри модального окна
    closeButton.addEventListener('click', closeModal);
}

// Инициализация обработчиков для модального окна с ID 'actionModal'
setupModalListeners('actionModal');

// Функция для открытия и закрытия модального окна (Форма "Добавить запись")
function toggleModal() {
    const modal = document.getElementById('modal');
    modal.classList.toggle('hidden');
}

// Функция для открытия и закрытия модального окна (Форма "Изменить запись")
function toggleEditModal(row = null) {
    const modal = document.getElementById('editmodal');

    if (row) {
        // Получаем данные из атрибутов data-*
        const id = row.getAttribute('data-id');
        const fieldCode = row.getAttribute('data-field-code');
        const name = row.getAttribute('data-name');
        const typeOfReproduction = row.getAttribute('data-type-of-reproduction');
        const basicUnit = row.getAttribute('data-basic-unit');
        const url = row.getAttribute('data-url'); // Получаем URL из атрибута

        // Заполняем поля модального окна
        document.getElementById("elementId").value = id;
        document.getElementById("elementFieldCode").value = fieldCode;
        document.getElementById("elementName").value = name;
        document.getElementById("elementTypeOfReproduction").value = typeOfReproduction;
        document.getElementById("elementBasicUnit").value = basicUnit;

        // Обновляем action формы
        const form = document.getElementById("editForm");
        form.action = url;
    }

    // Открываем/закрываем модальное окно
    modal.classList.toggle('hidden');
}

document.getElementById("editForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    const form = event.target;
    const formData = new FormData(form);
    const actionUrl = form.action;

    try {
        const response = await fetch(actionUrl, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            toggleEditModal(); // Закрываем модальное окно
            window.location.reload(); // Обновляем страницу
            alert("Запись успешно обновлена!");


        } else {
            const errorData = await response.json();
            alert("Ошибка при обновлении записи: " + JSON.stringify(errorData));
        }
    }
    catch (error) {
        console.error("Ошибка отправки формы:", error);
        alert("Произошла ошибка при отправке формы.");
    }
});

// Сортировка по нажатию на имя столбца
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