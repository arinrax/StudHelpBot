from .db import get_db_connection


def search_topics_keyword(keyword, limit=5):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql_query = """
        SELECT topic, supervisor, direction, degree 
        FROM student_works 
        WHERE topic LIKE ? OR direction LIKE ?
        LIMIT ?
    """

    pattern = f"%{keyword}%"
    cursor.execute(sql_query, (pattern, pattern, limit))
    results = cursor.fetchall()
    conn.close()
    if not results:
        return f"По запросу «{keyword}» ничего не найдено"
    result = f"Найдено {len(results)} работ:\n\n"
    for i, row in enumerate(results, 1):
        result += f"{i}. {row['topic']}\n"
        result += f"   {row['supervisor']}\n"
        result += f"   {row['direction']}\n\n"
    return result.strip()


def get_supervisor_topics(supervisor_name, limit=3):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT topic, direction, defense_year 
        FROM student_works 
        WHERE supervisor LIKE ?
        LIMIT ?
    """
    cursor.execute(query, (f"%{supervisor_name}%", limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
