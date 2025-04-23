// Функция открытия окна
function openModal() {
  document.getElementById("myModal").classList.add("show");
}

// Открытие при нажатии на кнопку
document.getElementById("openModalBtn").onclick = function(event){
  event.preventDefault();
  openModal();
}

// Открытие при нажатии на ссылку
document.getElementById("openModalLink").onclick = function(event) {
  event.preventDefault(); // Чтобы страница не перезагружалась
  openModal();
};

// Закрытие окна
document.querySelector(".close").onclick = function() {
  document.getElementById("myModal").classList.remove("show");
};

// Закрытие при клике вне окна
window.onclick = function(event) {
  const modal = document.getElementById("myModal");
  if (event.target === modal) {
    modal.classList.remove("show");
  }
};
