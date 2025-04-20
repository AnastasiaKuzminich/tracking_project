import sqlite3

conn = sqlite3.connect("tracking.db")
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS user_actions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    event_type TEXT,
    timestamp TEXT,
    site TEXT,
    page TEXT,
    x INTEGER,
    y INTEGER,
    scroll_position INTEGER,
    field_name TEXT,
    input_value TEXT)"""
)
conn.commit()
conn.close()
