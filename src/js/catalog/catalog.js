// Функция для открытия и закрытия модального окна (Форма "Новая запись")
async function toggleNewRecModal() {
    const modalRec = document.getElementById('newRecModal');
    const openModalButton = document.getElementById('open-newRec-modal');
    const closeModalButton = document.getElementById('close-newRec-modal');

    // Открываем/закрываем модальное окно
    modalRec.classList.toggle('hidden');
    await fetchSelectOptions(); // Подгружаем данные для выпадающих списков

    // Обработчик закрытия модального окна для крестика
    closeModalButton.addEventListener('click', () => {
        modalRec.classList.add('hidden');
    });

    // Закрытие модального окна при клике вне его
    modalRec.addEventListener('click', (event) => {
        if (event.target === modalRec) {
            modalRec.classList.add('hidden');
        }
    });

    // Закрытие модального окна по нажатию Esc
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !modalRec.classList.contains('hidden')) {
            modalRec.classList.add('hidden');
            openModalButton.blur(); // Снимаем фокус с кнопки
        }
    });
}

// Функция для открытия и закрытия модального окна (Форма "Изменить запись")
async function toggleEditModal(row = null) {
    const modal = document.getElementById('editmodal');
    const closeModalButton = document.getElementById('close-editRec-modal');
    const modalContent = modal.querySelector('.modal-content'); // Основной контент модального окна
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
        // document.getElementById("elementTypeOfReproduction").value = typeOfReproduction; Эти ребята тут : async function loadSelectOptions
        // document.getElementById("elementBasicUnit").value = basicUnit; Эти ребята тут : async function loadSelectOptions

        // Обновляем action формы
        const form = document.getElementById("editForm");
        form.action = url;

        // Загружаем опции для выпадающих списков
        await loadSelectOptions(typeOfReproduction, basicUnit);

    }

    // Открываем/закрываем модальное окно
    modal.classList.toggle('hidden');

    // Обработчик закрытия модального окна для крестика
    closeModalButton.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // Закрытие при клике вне модального окна
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
    // Закрытие при нажатии Esc
    document.addEventListener('keydown', function escKey(event) {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
            document.removeEventListener('keydown', escKey); // Убираем обработчик
        }
    });
}

// "Изменить запись"
document.getElementById("editForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    const form = event.target;
    const formData = new FormData(form);
    const actionUrl = form.action;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
            },
        });

        if (response.ok) {
            const responseData = await response.json();
            if (responseData.status === "success") {
                toggleEditModal(); // Закрываем модальное окно

                // Обновляем строку таблицы
                updateTableRow(responseData.data);
            }
        } else if (response.status === 403) {
            const errorHtml = await response.text();
            showModal(errorHtml); // Отображаем модальное окно
        } else {
            const errorData = await response.json();
            alert("Ошибка при обновлении записи: " + JSON.stringify(errorData));
        }
    } catch (error) {
        console.error("Ошибка отправки формы:", error);
        alert("Произошла ошибка при отправке формы.");
    }
});

// "Добавить запись"
document.getElementById("newRecordForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    const form = event.target;
    const formData = new FormData(form); // Собираем данные формы
    const actionUrl = form.action; // URL для отправки
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // CSRF-токен

    try {
        const response = await fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
            },
        });

        if (response.ok) {
            const responseData = await response.json();
            if (responseData.status === "success") {
                toggleNewRecModal(); // Закрываем модальное окно
                refreshTable();
            } else {
                alert("Ошибка: " + responseData.message); // Обрабатываем сообщение об ошибке
            }
        } else if (response.status === 403) {
            const errorHtml = await response.text(); // Предполагаем, что сервер возвращает HTML модального окна
            showModal(errorHtml); // Отображаем модальное окно
        } else {
            const errorData = await response.json();
            alert("Ошибка при создании записи: " + JSON.stringify(errorData)); // Обработка ошибок
        }
    } catch (error) {
        console.error("Ошибка отправки формы:", error);
        alert("Произошла ошибка при отправке формы.");
    }
});

// Для заполнения выпадающих списков в окне "Изменить запись"
async function loadSelectOptions(selectedReproduction, selectedBasicUnit) {
    const reproductionSelect = document.getElementById("elementTypeOfReproduction");
    const basicUnitSelect = document.getElementById("elementBasicUnit");

    // Очищаем текущие опции
    reproductionSelect.innerHTML = '';
    basicUnitSelect.innerHTML = '';

    try {
        const response = await fetch('getSelectOptions/');
        // const response = await fetch('/');
        const data = await response.json();

        // Заполняем список "Вид воспроизводства"
        data.reproduction_choices.forEach(choice => {
            const option = document.createElement('option');
            option.value = choice.reproduction;
            option.text = choice.name;
            if (choice.name === selectedReproduction) {
                option.selected = true;
            }
            reproductionSelect.appendChild(option);
        });

        // Заполняем список "Единица измерения"
        data.basic_units.forEach(unit => {
            const option = document.createElement('option');
            option.value = unit.db_id;
            option.text = unit.name;
            if (unit.name === selectedBasicUnit) {
                option.selected = true;
            }
            basicUnitSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Ошибка загрузки опций:", error);
        alert("Не удалось загрузить данные для выпадающих списков.");
    }
}

// Для заполнения выпадающих списков в окне "Новая запись"
async function fetchSelectOptions() {
    try {
        const response = await fetch('getSelectOptions/');

        const data = await response.json();

        // Обработка данных для поля "Вид воспроизводства"
        const reproductionSelect = document.getElementById('elementTypeOfReproductionNewRec');
        reproductionSelect.innerHTML = ''; // Очистка текущих опций
        data.reproduction_choices.forEach((choice) => {
            const option = document.createElement('option');
            option.value = choice.reproduction; // Значение для отправки
            option.textContent = choice.name; // Текст для отображения
            reproductionSelect.appendChild(option);
        });

        // Обработка данных для поля "Единица измерения"
        const basicUnitSelect = document.getElementById('elementBasicUnitNewRec');
        basicUnitSelect.innerHTML = ''; // Очистка текущих опций
        data.basic_units.forEach((unit) => {
            const option = document.createElement('option');
            option.value = unit.db_id; // Значение для отправки
            option.textContent = unit.name; // Текст для отображения
            basicUnitSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки данных для выпадающих списков:', error);
    }
}