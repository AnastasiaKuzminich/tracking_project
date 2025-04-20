document.addEventListener('DOMContentLoaded', () => {
    // DOMContentLoaded	запускает код после полной загрузки страницы
    // Получаем id операции из URL (?id=...)
    const urlParams = new URLSearchParams(window.location.search);
    const operationId = urlParams.get('id');

    // Если нет operation_id — не продолжаем
    if (!operationId) return;

    // для прекращения отслеживания после клика по важной кнопке/ссылке
    let trackingStopped = false;

    // Получаем текущую дату и время в формате ISO (например, 2025-04-20T12:34:56.789Z)
    function getCurrentTimestamp() {
        return new Date().toISOString();
    }

    // Общая функция для отправки данных на сервер
    async function sendData(url, data) {
        if (trackingStopped) return;

        try {
            await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        } catch (err) {
            console.error("Ошибка при отправке данных:", err);
        }
    }

    // Отправка события захода на сайт
    sendData('/track/visit', {
        operation_id: operationId,
        timestamp: getCurrentTimestamp()
    });

    // Клики по странице
    document.addEventListener('click', (e) => {
        if (trackingStopped) return;

        const siteWidth = document.documentElement.clientWidth;
        const siteHeight = document.documentElement.clientHeight;

        const clickX = e.clientX;
        const clickY = e.clientY;

        const text = (e.target.innerText || "").toLowerCase();

        // Ключевые кнопки и ссылки
        const importantWords = [
            'войти', 'войти по эцп', 'отправить заявку', 'зарегистрироваться',
            'отправить', 'сохранить', 'сменить пароль', 'забыли пароль?',
            'не помню логин или пароль', 'регистрация', 'вход через мси'
        ];

        const isImportant = importantWords.some(word => text.includes(word));

        if (isImportant) {
            // Событие нажатия важной кнопки — остановка всего трекинга
            trackingStopped = true;
            sendData('/track/button_click', {
                operation_id: operationId,
                timestamp: getCurrentTimestamp(),
                button_text: text
            });
        }

        // Отправка клика (даже если важный — он попадёт в базу "clicks", но только один раз)
        sendData('/track/click', {
            operation_id: operationId,
            timestamp: getCurrentTimestamp(),
            x: clickX,
            y: clickY,
            site_width: siteWidth,
            site_height: siteHeight
        });
    });

    //  Ввод в поля
    document.addEventListener('input', (e) => {
        if (trackingStopped) return;

        const el = e.target;
        if (!(el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement)) return;

        sendData('/track/input', {
            operation_id: operationId,
            timestamp: getCurrentTimestamp(),
            input_class: el.className,
            value: el.value
        });
    });
});
