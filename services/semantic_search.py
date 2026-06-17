import json
import os
import pickle

import numpy as np
from sentence_transformers import SentenceTransformer

from services.db import get_db_connection
from utils.logger import logger


class SemanticSearch:
    def __init__(self):
        self.model = None
        self.topic_vectors = None
        self.topics_metadata = []
        self.index_loaded = False

    def _get_model(self):
        if self.model is None:
            logger.info("Загрузка SBERT модели")
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logger.info("Модель загружена")
        return self.model

    def _get_data_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        return os.path.join(project_root, "data")

    def build_index(self):
        logger.info("Построение семантического индекса тем")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT topic, supervisor, direction, degree, defense_year
        FROM student_works
        WHERE topic IS NOT NULL
        """
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            logger.warning("База данных пуста")
            return
        self.topics_metadata = [
            {
                "topic": row["topic"],
                "supervisor": row["supervisor"],
                "direction": row["direction"],
                "degree": row["degree"],
                "defense_year": row["defense_year"],
            }
            for row in rows
        ]

        model = self._get_model()
        topics = [row["topic"] for row in rows]

        self.topic_vectors = model.encode(
            topics,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        self.index_loaded = True
        logger.info(f"Индекс построен: {len(self.topic_vectors)} тем векторизовано")

        self._save_index()

    def _save_index(self):
        data_dir = self._get_data_dir()

        with open(os.path.join(data_dir, "topic_vectors.pkl"), "wb") as f:
            pickle.dump(self.topic_vectors, f)

        with open(
            os.path.join(data_dir, "topics_metadata.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.topics_metadata, f, ensure_ascii=False, indent=2)
        logger.info("Индекс сохранён на диск")

    def load_index(self):
        data_dir = self._get_data_dir()
        vectors_path = os.path.join(data_dir, "topic_vectors.pkl")
        metadata_path = os.path.join(data_dir, "topics_metadata.json")

        if os.path.exists(vectors_path) and os.path.exists(metadata_path):
            logger.info("Загрузка сохранённого индекса")

            with open(vectors_path, "rb") as f:
                self.topic_vectors = pickle.load(f)

            with open(metadata_path, "r", encoding="utf-8") as f:
                self.topics_metadata = json.load(f)

            self.index_loaded = True
            logger.info(f"Загружено {len(self.topic_vectors)} векторов")
            return True
        else:
            logger.info("Индекс не найден, строю новый")
            self.build_index()
            return False

    def search(self, query, top_k=5, threshold=0.3):
        if not self.index_loaded:
            self.load_index()

        logger.debug(f"Семантический поиск: '{query}' (top_k={top_k})")

        model = self._get_model()
        query_vector = model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        )
        similarities = np.dot(self.topic_vectors, query_vector.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if similarities[idx] >= threshold:
                result = self.topics_metadata[idx].copy()
                result["similarity"] = float(similarities[idx])
                results.append(result)

        logger.info(f"Найдено {len(results)} результатов по запросу '{query}'")
        return results


semantic_search_instance = SemanticSearch()


def search_topics_semantic(keyword, limit=5):
    results = semantic_search_instance.search(keyword, top_k=limit)

    if not results:
        return f"По запросу «{keyword}» ничего не найдено"

    result_text = f"Найдено {len(results)} работ по смыслу:\n\n"
    for i, item in enumerate(results, 1):
        result_text += f"{i}. {item['topic']}\n"
        result_text += f"   {item['supervisor']}\n"
        result_text += f"   {item['direction']}\n"
        result_text += f"   Сходство: {item['similarity']:.2f}\n\n"

    return result_text.strip()
