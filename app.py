from flask import Flask, request, render_template

# Flask — главный класс для создания сервера
# request для получения данных из запросов (POST, GET)
# render_template(шаблон визуализации) — загружает HTML-шаблоны из папки templates
from flask_cors import CORS  # разрешение отправки запросов с других сайтов
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # чтобы сервер принимал запросы с любых других сайтов

DATABASE = os.path.join(os.getcwd(), "tracking.db")


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/page1")
def page1():
    return render_template("page1.html")


@app.route("/page2")
def page2():
    return render_template("page2.html")


@app.route("https://tracing-project.com/", methods=["POST"])
def track():
    data = request.get_json()
    db = get_db()

    db.execute(
        """
        INSERT INTO user_action (
            user_id, site, page, event_type, timestamp,
            x, y, scroll_position, field_name, input_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data.get("uid"),
            data.get("site"),
            data.get("page"),
            data.get("event_type"),
            data.get("timestamp"),
            data.get("x"),
            data.get("y"),
            data.get("scroll_position"),
            data.get("field_name"),
            data.get("input_value"),
        ),
    )

    db.commit()
    db.close()
    return "", 204  # успешно, но без содержимого


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway даёт свой порт
    app.run(host="0.0.0.0", port=port, debug=True)
