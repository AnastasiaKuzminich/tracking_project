import sqlite3
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# Пути
DB_PATH = "clicks.db"
IMAGE_PATH = "screenshot.png"

# Получаем клики и оригинальные размеры экрана
def get_clicks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT x, y, screen_width, screen_height FROM clicks")  # Предполагаем, что ты их хранишь
    clicks = cursor.fetchall()
    conn.close()
    return clicks

def show_heatmap():
    img = Image.open(IMAGE_PATH)
    img_width, img_height = img.size

    click_data = get_clicks()
    xs, ys = [], []

    for x, y, sw, sh in click_data:
        # Масштабируем координаты под размер изображения
        scale_x = img_width / sw
        scale_y = img_height / sh
        xs.append(x * scale_x)
        ys.append(img_height - y * scale_y)  # Инвертируем y

    # Создаем тепловую карту
    plt.figure(figsize=(10, 8))
    plt.imshow(img)
    sns.kdeplot(x=xs, y=ys, cmap="Reds", fill=True, alpha=0.5, bw_adjust=0.5, levels=100, thresh=0.05)
    plt.title("Тепловая карта кликов")
    plt.axis("off")
    plt.show()

show_heatmap()
