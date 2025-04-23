document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const operationId = urlParams.get('id');
    if (!operationId) {
        console.error("Отсутствует operationId в URL");
        return;
    }
    function getCurrentTimestamp() {
        // ISO-совместимое локальное время по Минску
        const now = new Date();
        const localTime = now.toLocaleString("sv-SE", { timeZone: "Europe/Minsk" }).replace(" ", "T");
        return localTime;
    }

    let trackingStopped = localStorage.getItem("trackingStopped_" + operationId) === "true";
    console.log("Tracking started. Tracking stopped:", trackingStopped);

    /* function getCurrentTimestamp() {
        return new Date().toISOString();
    } */

    async function sendData(url, data) {
        if (trackingStopped) {
            console.log("Отправка данных остановлена, трекинг завершён.");
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            // Если это важная кнопка — проверяем ответ сервера
            if (url.includes("/track/button_click") && response.ok) {
                const result = await response.json();
                if (result.stop_tracking === true) {
                    trackingStopped = true;
                    localStorage.setItem("trackingStopped_" + operationId, "true");  // Сохраняем, что трекинг остановлен
                    console.log("Трекинг остановлен по ответу сервера.");
                }
            }

        } catch (err) {
            console.error("Ошибка при отправке данных:", err);
        }
    }

    // 1. Событие захода
    sendData('/track/visit', {
        operation_id: operationId,
        timestamp: getCurrentTimestamp()
    });

    // 2. Клики
    document.addEventListener('click', (e) => {
        if (trackingStopped) return;
    
        // Получаем элемент, по которому кликнули
        const clickedElement = e.target;
    
        // Проверка, является ли элемент кнопкой или ссылкой
        if (clickedElement.tagName.toLowerCase() === 'button' || clickedElement.tagName.toLowerCase() === 'a') {
            // Если это кнопка или ссылка, обрабатываем как важную кнопку
            const text = (clickedElement.innerText || "").toLowerCase();
            const siteWidth = document.documentElement.clientWidth;
            const siteHeight = document.documentElement.clientHeight;
    
            const clickX = e.clientX;
            const clickY = e.clientY;
    
            const importantWords = [
                'войти', 'войти по эцп', 'отправить заявку', 'зарегистрироваться',
                'отправить', 'сохранить', 'сменить пароль', 'забыли пароль?',
                'не помню логин или пароль', 'регистрация', 'вход через мси'
            ];
    
            // Проверка, является ли клик важной кнопкой
            const isImportant = importantWords.some(word => text.includes(word));
    
            if (isImportant) {
                sendData('/track/button_click', {
                    operation_id: operationId,
                    timestamp: getCurrentTimestamp(),
                    button_text: text
                });
            }
    
            // Отправка клика для кнопки или ссылки
            sendData('/track/click', {
                operation_id: operationId,
                timestamp: getCurrentTimestamp(),
                x: clickX,
                y: clickY,
                site_width: siteWidth,
                site_height: siteHeight
            });
        } else {
            // Это клик по тексту или другим элементам, не кнопке и не ссылке
            // В таком случае, сохраняем как обычный клик в базу clicks
            const siteWidth = document.documentElement.clientWidth;
            const siteHeight = document.documentElement.clientHeight;
    
            const clickX = e.clientX;
            const clickY = e.clientY;
    
            sendData('/track/click', {
                operation_id: operationId,
                timestamp: getCurrentTimestamp(),
                x: clickX,
                y: clickY,
                site_width: siteWidth,
                site_height: siteHeight
            });
    
            console.log("Клик по тексту или не кнопке, записываем в базу clicks.");
        }
    });

    //  3. Ввод в поля
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
