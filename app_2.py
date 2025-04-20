from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Функция для подключения к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('track.db')
    conn.row_factory = sqlite3.Row  # Чтобы можно было обращаться к строкам по имени столбца
    return conn

# Функция для создания базы данных и таблиц (если их ещё нет)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу general_oper для записи операций
    cursor.execute('''CREATE TABLE IF NOT EXISTS general_oper (
        operation_id TEXT PRIMARY KEY,
        entry_time TEXT,
        button_click_time TEXT,
        button_type TEXT
    )''')
    
    # Создаем таблицу clicks для записи кликов
    cursor.execute('''CREATE TABLE IF NOT EXISTS clicks (
        operation_id TEXT,
        click_time TEXT,
        click_x INTEGER,
        click_y INTEGER,
        site_width INTEGER,
        site_height INTEGER
    )''')
    
    # Создаем таблицу inputs для записи ввода данных
    cursor.execute('''CREATE TABLE IF NOT EXISTS inputs (
        operation_id TEXT,
        input_time TEXT,
        input_class TEXT,
        input_value TEXT
    )''')
    
    conn.commit()
    conn.close()

# Инициализируем базу данных при старте сервера
init_db()

# Эндпоинт для записи данных о визите на сайт
@app.route('/track/visit', methods=['POST'])
def track_visit():
    data = request.get_json()
    operation_id = data['operation_id']
    timestamp = data['timestamp']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO general_oper (operation_id, entry_time) 
                      VALUES (?, ?)''', (operation_id, timestamp))
    conn.commit()
    conn.close()
    print('Сохраняем визит')
    return jsonify({'status': 'success'}), 200

# Эндпоинт для записи данных о клике
@app.route('/track/click', methods=['POST'])
def track_click():
    data = request.get_json()
    operation_id = data['operation_id']
    timestamp = data['timestamp']
    click_x = data['x']
    click_y = data['y']
    site_width = data['site_width']
    site_height = data['site_height']
    
    # Проверим, была ли уже нажата кнопка для этой операции
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT button_click_time FROM general_oper WHERE operation_id = ?', (operation_id,))
    button_click_time = cursor.fetchone()
    
    if button_click_time and button_click_time['button_click_time']:
        # Если кнопка уже нажата, не сохраняем клик
        conn.close()
        return jsonify({'status': 'success'}), 200
    
    # Сохраняем клик
    cursor.execute('''INSERT INTO clicks (operation_id, click_time, click_x, click_y, site_width, site_height) 
                      VALUES (?, ?, ?, ?, ?, ?)''', (operation_id, timestamp, click_x, click_y, site_width, site_height))
    conn.commit()
    conn.close()
    print('Сохраняем клик')
    
    return jsonify({'status': 'success'}), 200

# Эндпоинт для записи данных о вводе
@app.route('/track/input', methods=['POST'])
def track_input():
    data = request.get_json()
    operation_id = data['operation_id']
    timestamp = data['timestamp']
    input_class = data['input_class']
    input_value = data['value']
    
    # Проверим, была ли уже нажата кнопка для этой операции
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT button_click_time FROM general_oper WHERE operation_id = ?', (operation_id,))
    button_click_time = cursor.fetchone()
    
    if button_click_time and button_click_time['button_click_time']:
        # Если кнопка уже нажата, не сохраняем ввод
        conn.close()
        return jsonify({'status': 'success'}), 200
    
    # Сохраняем ввод
    cursor.execute('''INSERT INTO inputs (operation_id, input_time, input_class, input_value) 
                      VALUES (?, ?, ?, ?)''', (operation_id, timestamp, input_class, input_value))
    conn.commit()
    conn.close()
    print('Сохраняем ввод')
    
    return jsonify({'status': 'success'}), 200

# Эндпоинт для записи нажатия кнопки
@app.route('/track/button_click', methods=['POST'])
def track_button_click():
    data = request.get_json()
    operation_id = data['operation_id']
    timestamp = data['timestamp']
    button_text = data['button_text']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE general_oper SET button_click_time = ?, button_type = ? 
                      WHERE operation_id = ?''', (timestamp, button_text, operation_id))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
