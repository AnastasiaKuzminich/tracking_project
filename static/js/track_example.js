const operationId = new URLSearchParams(window.location.search).get("id"); //window.location.search--так часть ссылки после вопросительного знака
let trackingActive = true;

const sendToServer = async (endpoint, data) => {
  await fetch(`http://localhost:5000/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
};

// отслеживание входа
window.addEventListener("load", () => {
  sendToServer("log_operation", {
    operation_id: operationId,
    event: "enter"
  });
});

// Клик
document.addEventListener("click", (e) => {
  if (!trackingActive) return;

  const element = e.target;
  const x = e.clientX;
  const y = e.clientY;

  // Если нажали на "конечную" кнопку
  if (["отправить данные", "забыл пароль"].includes(target.innerText.toLowerCase())) {
    sendToServer("log_operation", {
      operation_id: operationId,
      event: "exit"
    });

    alert("проиграл");
    trackingActive = false;
    return;
  }

  sendToServer("log_click", {
    operation_id: operationId,
    x,
    y,
    timestamp: new Date().toISOString()
  });
});

// Ввод текста
document.addEventListener("input", (e) => {
  if (!trackingActive) return;

  const inputValue = e.data;
  if (inputValue) {
    sendToServer("log_input", {
      operation_id: operationId,
      char: inputValue,
      timestamp: new Date().toISOString()
    });
  }
});
document.addEventListener('input', (e) => {
  if (e.target.tagName === 'INPUT') {
      sendEvent({
          event_type: 'input',
          field_name: e.target.name,
          input_value: e.target.value
      });
  }
});