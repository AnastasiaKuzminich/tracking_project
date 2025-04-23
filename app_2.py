from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

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
def connect_track():
    conn = sqlite3.connect("track.db", timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


db_emails_path = r"D:\my_distant\coding\my_emails_2.db"


def connect_my_emails_2():
    conn = sqlite3.connect(db_emails_path, timeout=10, check_same_thread=False)
    return conn


# Инициализация базы данных
def init_db():
    with connect_track() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS general_oper (
            operation_id TEXT PRIMARY KEY,
            entry_date DATETIME,
            entry_time DATETIME,
            button_click_date DATETIME,
            button_click_time DATETIME,
            button_type TEXT
        )"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS clicks (
            operation_id TEXT,
            click_date DATETIME,
            click_time DATETIME,
            click_x INTEGER,
            click_y INTEGER,
            site_width INTEGER,
            site_height INTEGER
        )"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS inputs (
            operation_id TEXT,
            input_date DATETIME,
            input_time DATETIME,
            input_class TEXT,
            input_value TEXT
        )"""
        )


init_db()


@app.route("/track/visit", methods=["POST"])
def track_visit():
    data = request.get_json()
    print("Получен /track/visit:", data)

    if not data or "operation_id" not in data:
        print("Нет operation_id!")
        return jsonify({"error": "Missing operation_id"}), 400

    operation_id = data["operation_id"]
    timestamp = datetime.now()
    date = timestamp.date().isoformat()
    time = timestamp.time().strftime("%H:%M:%S")

    try:
        with sqlite3.connect("track.db") as conn1:
            cursor = conn1.cursor()
            cursor.execute(
                "INSERT INTO general_oper (operation_id, entry_date, entry_time) VALUES (?, ?, ?)",
                (operation_id, date, time),
            )
            with connect_my_emails_2() as conn2:
                cursor = conn2.cursor()
                cursor.execute(
                    "SELECT 1 FROM registration WHERE sending_id = ? LIMIT 1",
                    (operation_id,),
                )
                result = cursor.fetchone()

                if result:
                    print("Значение найдено!")
                    cursor.execute(
                        "UPDATE registration SET entry_date = ?, entry_time = ? WHERE sending_id = ?",
                        (date, time, operation_id),
                    )
                else:
                    print("Значение не найдено.")

            print("Сохранили в general_oper:", operation_id, timestamp)
        return jsonify({"status": "visit tracked"})
    except Exception as e:
        print("Ошибка при сохранении:", e)
        return jsonify({"error": "DB error"}), 500


@app.route("/track/click", methods=["POST"])
def track_click():
    data = request.get_json()
    operation_id = data["operation_id"]
    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", ""))

    date_iso = timestamp.date().isoformat()
    time_iso = timestamp.time().strftime("%H:%M:%S")
    click_x = data["x"]
    click_y = data["y"]
    site_width = data["site_width"]
    site_height = data["site_height"]

    with connect_track() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT button_click_time FROM general_oper WHERE operation_id = ?",
            (operation_id,),
        )
        button_click_time = cursor.fetchone()

        if button_click_time and button_click_time["button_click_time"]:

            return jsonify({"status": "ignored"}), 200

        cursor.execute(
            """INSERT INTO clicks (operation_id, click_date, click_time, click_x, click_y, site_width, site_height) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                operation_id,
                date_iso,
                time_iso,
                click_x,
                click_y,
                site_width,
                site_height,
            ),
        )
    print("Сохраняем клик")

    return jsonify({"status": "success"}), 200


@app.route("/track/input", methods=["POST"])
def track_input():
    data = request.get_json()
    operation_id = data["operation_id"]

    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", ""))

    date_iso = timestamp.date().isoformat()
    time_iso = timestamp.time().strftime("%H:%M:%S")
    input_class = data["input_class"]
    input_value = data["value"]

    with connect_track() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT button_click_time FROM general_oper WHERE operation_id = ?",
            (operation_id,),
        )
        button_click_time = cursor.fetchone()

        if button_click_time and button_click_time["button_click_time"]:

            return jsonify({"status": "ignored"}), 200

        cursor.execute(
            """INSERT INTO inputs (operation_id, input_date, input_time, input_class, input_value) 
                        VALUES (?, ?, ?, ?, ?)""",
            (operation_id, date_iso, time_iso, input_class, input_value),
        )

    print("Сохраняем ввод")

    return jsonify({"status": "success"}), 200


@app.route("/track/button_click", methods=["POST"])
def track_button_click():
    data = request.get_json()
    operation_id = data.get("operation_id")
    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", ""))
    date_iso = timestamp.date().isoformat()
    time_iso = timestamp.time().strftime("%H:%M:%S")
    button_text = data.get("button_text")

    if not operation_id:
        return jsonify({"error": "No operation ID"}), 400

    with connect_track() as conn1:
        cursor = conn1.cursor()

        cursor.execute(
            "SELECT button_type FROM general_oper WHERE operation_id = ?",
            (operation_id,),
        )
        row = cursor.fetchone()

        if row and row["button_type"]:

            return jsonify({"stop_tracking": True})  # уже кликали — стоп

        # первый клик — сохраняем
        cursor.execute(
            """
            UPDATE OR IGNORE general_oper
            SET button_click_date = ?, button_click_time = ?, button_type = ?
            WHERE operation_id = ?
        """,
            (date_iso, time_iso, button_text, operation_id),
        )

        cursor.execute(
            """
            INSERT INTO clicks (operation_id, click_date, click_time, click_x, click_y, site_width, site_height)
            VALUES (?, ?, ?, NULL, NULL, NULL, NULL)
        """,
            (operation_id, date_iso, time_iso),
        )

    with connect_my_emails_2() as conn2:
        cursor = conn2.cursor()
        cursor.execute(
            """
            UPDATE registration
            SET failed_date = ?, failed_time = ?
            WHERE sending_id = ?
        """,
            (date_iso, time_iso, operation_id),
        )

    return jsonify({"stop_tracking": True})


if __name__ == "__main__":
    app.run(debug=True)
