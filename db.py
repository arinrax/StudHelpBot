import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/vkr_archive.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"База данных не найдена: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_topics_sample(limit: int = 5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT topic, supervisor FROM student_works LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    print("Тест подключения к бд")
    try:
        data = get_topics_sample(15)
        print(f"найдено записей: {len(data)}")
        for item in data:
            print(f"- {item['topic']} | {item['supervisor']}")
    except Exception as e:
        print(f"Ошибка БД: {e}")