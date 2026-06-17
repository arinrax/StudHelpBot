from .db import get_db_connection
from .semantic_search import search_topics_semantic as _search_topics_semantic


def search_topics_keyword(keyword, limit=5):
    semantic_result = _search_topics_semantic(keyword, limit)
    if "ничего не найдено" not in semantic_result:
        return semantic_result

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

    result = f"Найдено {len(results)} работ (по точному совпадению):\n\n"
    for i, row in enumerate(results, 1):
        result += f"{i}. {row['topic']}\n"
        result += f"   {row['supervisor']}\n"
        result += f"   {row['direction']}\n"
    return result.strip()


def get_supervisor_topics(supervisor_name, limit=3):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT topic, direction, defense_year
    FROM student_works
    WHERE supervisor LIKE ?
    ORDER BY defense_year DESC
    LIMIT ?
    """
    cursor.execute(query, (f"%{supervisor_name}%", limit))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"Работы научного руководителя «{supervisor_name}» не найдены"
    result = f"Темы работ {supervisor_name} (последние {len(rows)}):\n\n"
    for i, row in enumerate(rows, 1):
        result += f"{i}. {row['topic']}\n"
        result += f"   Направление: {row['direction']}\n"
        result += f"   Год защиты: {row['defense_year']}\n\n"
    return result.strip()


def get_supervisor_stats(supervisor_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT COUNT(*) as count, AVG(grade) as avg_grade
    FROM student_works
    WHERE supervisor LIKE ?
    """,
        (f"%{supervisor_name}%",),
    )
    stats = cursor.fetchone()

    cursor.execute(
        """
    SELECT topic, defense_year
    FROM student_works
    WHERE supervisor LIKE ?
    ORDER BY defense_year DESC
    LIMIT 3
    """,
        (f"%{supervisor_name}%",),
    )
    recent_topics = cursor.fetchall()
    conn.close()

    if not stats or stats["count"] == 0:
        return f"Информация о научном руководителе «{supervisor_name}» не найдена"

    result = f"Статистика по {supervisor_name}:\n\n"
    result += f"• Всего работ: {stats['count']}\n"
    if stats["avg_grade"]:
        result += f"• Средняя оценка: {stats['avg_grade']:.2f}\n"

    if recent_topics:
        result += "\nПоследние темы:\n"
        for i, topic in enumerate(recent_topics, 1):
            result += f"{i}. {topic['topic']} ({topic['defense_year']})\n"

    return result.strip()


def get_random_topic():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT topic, supervisor, direction, degree
    FROM student_works
    ORDER BY RANDOM()
    LIMIT 1
    """
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        return "База данных пуста"

    return (
        f"Случайная тема:\n\n"
        f"{result['topic']}\n"
        f"{result['supervisor']}\n"
        f"{result['direction']}\n"
        f"{result['degree']}"
    )


def find_similar_topics(topic_text, limit=3):
    words = topic_text.split()[:3]
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = " OR ".join(["topic LIKE ?"] * len(words))
    query = f"""
    SELECT topic, supervisor, direction
    FROM student_works
    WHERE ({conditions}) AND topic NOT LIKE ?
    LIMIT ?
    """

    params = [f"%{word}%" for word in words] + [f"%{topic_text}%", limit]
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    if not results:
        return "Похожие темы не найдены"

    result = f"Похожие темы:\n\n"
    for i, row in enumerate(results, 1):
        result += f"{i}. {row['topic']}\n"
        result += f"   {row['supervisor']}\n\n"
    return result.strip()
