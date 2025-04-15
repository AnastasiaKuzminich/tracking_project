const page = document.body.dataset.page;
const site = document.body.dataset.site;
const startTime = Date.now();

/* document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT') {
      sendEvent({
        event_type: 'input',
        field_name: e.target.name,
        input_value: e.target.value
      });
    }
  }); */

//e — это объект события
//e.target — это конкретный элемент, в который пользователь что-то вводит



// Слушатель кликов
document.addEventListener('click', (e) => {
    sendEvent({
        event_type: 'click',
        x: e.clientX,
        y: e.clientY
    });
});

// Слушатель ввода текста
document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT') {
        sendEvent({
            event_type: 'input',
            field_name: e.target.name,
            input_value: e.target.value
        });
    }
});

// Слушатель прокрутки
window.addEventListener('scroll', () => {
    sendEvent({
        event_type: 'scroll',
        scroll_position: window.scrollY
    });
});

/* // Периодически отправляем "время на странице"
setInterval(() => {
  const seconds = Math.floor((Date.now() - startTime) / 1000);
  sendEvent({
    event_type: 'time_spent',
    input_value: `${seconds} seconds`
  });
}, 10000); // Каждые 10 секунд */

// Когда пользователь уходит со страницы

window.addEventListener('beforeunload', () => {
    const seconds = Math.floor((Date.now() - startTime) / 1000);
    // закрытие вкладки, обновление страницы, переход на другой сайт
    // Отправляем финальное событие
    navigator.sendBeacon('/track', JSON.stringify({
        uid: uid,
        site: site,
        page: page,
        event_type: 'user_left',
        timestamp: new Date().toISOString(),
        input_value: `${seconds} seconds`
    }));
});




// Функция отправки события на сервер
function sendEvent(data) {
    fetch('/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            uid: uid,
            site: site,
            page: page,
            timestamp: new Date().toISOString(),
            ...data
        })
    });
}
