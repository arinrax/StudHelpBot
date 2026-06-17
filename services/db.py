import os
import sqlite3

DB_PATH = os.path.join("data", "vkr_archive.db")


def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"База данных не найдена: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
