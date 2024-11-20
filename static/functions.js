let times = new Map();
let days = new Map();
let currentId = null; // Переменная для хранения id редактируемой ячейки

document.querySelectorAll('td.time').forEach(td => {
    td.ondblclick = function () {
        const existingInput = this.querySelector('input');
        if (existingInput) {
            existingInput.focus();
            return;
        }
        currentId = this.parentElement.id; // Получаем id редактируемой строки
        const input = document.createElement('input');
        input.value = this.innerText; // Сохраняем текст в input
        const previousValue = input.value
        console.log('previousValue', previousValue)
        this.textContent = ''; // Очищаем содержимое td
        this.appendChild(input); // Добавляем input в td
        input.focus(); // Устанавливаем фокус на input
        input.onblur = () => saveValue(event, previousValue, input.value);
    };
});

// Функция для сохранения значения
function saveValue(event, previousValue, value) {
    const parentTd = event.target.parentElement;
    console.log('value2', previousValue, value)
    if (previousValue === value) {
        console.log("Значение не изменилось, ничего не сохраняем.");
        return; // Если значение не изменилось, выходим
    }

    if (isValid(value)) {
        parentTd.textContent = value; // Передаем данные в td
        times.set(currentId, value); // Используем currentId, чтобы сохранить значение
        console.log(times);
    } else {
        showError('Некорректный ввод! Введите время в формате чч:мм-чч:мм');
        parentTd.querySelector('input').focus(); // Возвращаем пользователя к редактированию
    }
}

// Функция проверки на валидность
function isValid(value) {
    const regex = /^\d{2}\:\d{2}\-\d{2}\:\d{2}$/;
    return regex.test(value);
}

// Функция для отображения ошибки
function showError(message) {
    const error = document.createElement('div');
    error.style.color = 'red';
    error.innerText = message;
    document.body.appendChild(error);

    // Удаляем сообщение через 2 секунды
    setTimeout(() => {
        document.body.removeChild(error);
    }, 2000);
}

// перенос строки
$(function() {
    $("#sortable-table").sortable({
        items: "tr:not(:first-child)", // не сортируем заголовок
        cursor: "move",
        update: function(event, ui) {
            // Собираем новый порядок строк
            let sortedIDs = $("#sortable-table tbody tr.lesson").map(function() {
              return { id: this.id, day: $(this).data('day') };
              }).get();
        console.log(sortedIDs);
},
start: function (event, ui) {
    // Сохраняем исходный day перед началом сортировки
    ui.item.data('initial-day', ui.item.data('day'));
},
stop: function (event, ui) {
    // Обновляем атрибут data-day после завершения сортировки
    let oldDay = ui.item.data('initial-day');
    let newDay = ui.item.closest('tbody').data('day');
    // Проверяем если строка была перемещена на другой день
    if (oldDay !== newDay) {
        ui.item.data('day', newDay);
        currentId=ui.item.attr('id')
        days.set(currentId, newDay);
    }
}
    });
    $("#sortable-table tbody").disableSelection();
});

$(document).ready(function() {
    $('#send-button').on('click', function() {
        // Преобразуем данные из Map в объект
        const timesData = {};
        times.forEach((value, key) => {
            timesData[key] = value;
        });

        const daysData = {};
        days.forEach((value, key) => {
            daysData[key] = value;
        });

        // Отправляем данные на сервер с помощью AJAX
        $.ajax({
            url: '/update-lesson',
            method: 'put',
            contentType: 'application/json',
            data: JSON.stringify({ times: timesData, days: daysData }),
            success: function(response) {
                console.log('Данные успешно отправлены:', response);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Ошибка при отправке данных:', textStatus, errorThrown);
            }
        });
    });
});
