from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)


@app.route("/site_1")
def page1():
    return render_template("site_1.html")


@app.route("/site_2.1")
def page2_1():
    return render_template("site_2.1.html")


@app.route("/site_2.2")
def page2_2():
    return render_template("site_2.2.html")


@app.route("/site_2.3")
def page2_3():
    return render_template("site_2.3.html")


@app.route("/site_3.1")
def page3_1():
    return render_template("site_3.1.html")


@app.route("/site_3.2")
def page3_2():
    return render_template("site_3.2.html")


@app.route("/site_3.3")
def page3_3():
    return render_template("site_3.3.html")


@app.route("/site_3.5")
def page3_5():
    return render_template("site_3.5.html")


@app.route("/site_4.1")
def page4_1():
    return render_template("site_4.1.html")


@app.route("/site_4.2")
def page4_2():
    return render_template("site_4.2.html")


@app.route("/site_4.3")
def page4_3():
    return render_template("site_4.3.html")


@app.route("/site_5.1")
def page5_1():
    return render_template("site_5.1.html")


@app.route("/site_6.1")
def page6_1():
    return render_template("site_6.1.html")


@app.route("/site_7.1")
def page7_1():
    return render_template("site_7.1.html")


@app.route("/site_8.1")
def page8_1():
    return render_template("site_8.1.html")


@app.route("/site_9.1")
def page9_1():
    return render_template("site_9.1.html")


@app.route("/site_10.1")
def page10_1():
    return render_template("site_10.1.html")


@app.route("/site_11.1")
def page11_1():
    return render_template("site_11.1.html")


# Функция для подключения к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect("track.db")
    conn.row_factory = sqlite3.Row
    return conn


# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS general_oper (
        operation_id TEXT PRIMARY KEY,
        entry_time TEXT,
        button_click_time TEXT,
        button_type TEXT
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS clicks (
        operation_id TEXT,
        click_time TEXT,
        click_x INTEGER,
        click_y INTEGER,
        site_width INTEGER,
        site_height INTEGER
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS inputs (
        operation_id TEXT,
        input_time TEXT,
        input_class TEXT,
        input_value TEXT
    )"""
    )

    conn.commit()
    conn.close()


init_db()


@app.route("/track/visit", methods=["POST"])
def track_visit():
    data = request.get_json()
    print("Получен /track/visit:", data)

    if not data or "operation_id" not in data:
        print("Нет operation_id!")
        return jsonify({"error": "Missing operation_id"}), 400

    operation_id = data["operation_id"]
    timestamp = datetime.now().isoformat()

    try:
        with sqlite3.connect("track.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO general_oper (operation_id, entry_time) VALUES (?, ?)",
                (operation_id, timestamp),
            )
            conn.commit()
            print("Сохранили в general_oper:", operation_id, timestamp)
        return jsonify({"status": "visit tracked"})
    except Exception as e:
        print("Ошибка при сохранении:", e)
        return jsonify({"error": "DB error"}), 500


@app.route("/track/click", methods=["POST"])
def track_click():
    data = request.get_json()
    operation_id = data["operation_id"]
    timestamp = data["timestamp"]
    click_x = data["x"]
    click_y = data["y"]
    site_width = data["site_width"]
    site_height = data["site_height"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT button_click_time FROM general_oper WHERE operation_id = ?",
        (operation_id,),
    )
    button_click_time = cursor.fetchone()

    if button_click_time and button_click_time["button_click_time"]:
        conn.close()
        return jsonify({"status": "ignored"}), 200

    cursor.execute(
        """INSERT INTO clicks (operation_id, click_time, click_x, click_y, site_width, site_height) 
                      VALUES (?, ?, ?, ?, ?, ?)""",
        (operation_id, timestamp, click_x, click_y, site_width, site_height),
    )
    conn.commit()
    conn.close()
    print("Сохраняем клик")

    return jsonify({"status": "success"}), 200


@app.route("/track/input", methods=["POST"])
def track_input():
    data = request.get_json()
    operation_id = data["operation_id"]
    timestamp = data["timestamp"]
    input_class = data["input_class"]
    input_value = data["value"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT button_click_time FROM general_oper WHERE operation_id = ?",
        (operation_id,),
    )
    button_click_time = cursor.fetchone()

    if button_click_time and button_click_time["button_click_time"]:
        conn.close()
        return jsonify({"status": "ignored"}), 200

    cursor.execute(
        """INSERT INTO inputs (operation_id, input_time, input_class, input_value) 
                      VALUES (?, ?, ?, ?)""",
        (operation_id, timestamp, input_class, input_value),
    )
    conn.commit()
    conn.close()
    print("Сохраняем ввод")

    return jsonify({"status": "success"}), 200


@app.route("/track/button_click", methods=["POST"])
def track_button_click():
    data = request.get_json()
    operation_id = data.get("operation_id")
    timestamp = data.get("timestamp")
    button_text = data.get("button_text")

    if not operation_id:
        return jsonify({"error": "No operation ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT button_type FROM general_oper WHERE operation_id = ?", (operation_id,)
    )
    row = cursor.fetchone()

    if row and row["button_type"]:
        conn.close()
        return jsonify({"stop_tracking": True})  # уже кликали — стоп

    # первый клик — сохраняем
    cursor.execute(
        """
        UPDATE OR IGNORE general_oper
        SET button_click_time = ?, button_type = ?
        WHERE operation_id = ?
    """,
        (timestamp, button_text, operation_id),
    )

    cursor.execute(
        """
        INSERT INTO clicks (operation_id, click_time, click_x, click_y, site_width, site_height)
        VALUES (?, ?, NULL, NULL, NULL, NULL)
    """,
        (operation_id, timestamp),
    )

    conn.commit()
    conn.close()

    return jsonify({"stop_tracking": True})


if __name__ == "__main__":
    app.run(debug=True)
