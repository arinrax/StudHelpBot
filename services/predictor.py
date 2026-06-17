import os

import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODEL_PATH = os.path.join(DATA_DIR, "grade_predictor.pkl")
PCA_PATH = os.path.join(DATA_DIR, "pca_grade.pkl")


if os.path.exists(MODEL_PATH) and os.path.exists(PCA_PATH):
    model = joblib.load(MODEL_PATH)
    pca = joblib.load(PCA_PATH)
    sbert = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    ready = True
else:
    model = pca = sbert = None
    ready = False
    print("Модель или PCA не найдены")


def predict_grade(topic, supervisor, diploma_avg):
    if not ready:
        return "Прогноз временно недоступен"
    try:
        topic_vec = sbert.encode([topic], normalize_embeddings=True)
        topic_pca = pca.transform(topic_vec)[0]

        input_data = pd.DataFrame(
            [
                {
                    "supervisor": supervisor,
                    "diploma_avg": float(diploma_avg),
                    "topic_0": topic_pca[0],
                    "topic_1": topic_pca[1],
                    "topic_2": topic_pca[2],
                }
            ]
        )

        pred = model.predict(input_data)[0]
        proba = model.predict_proba(input_data)[0]
        classes = model.classes_
        confidence = proba[list(classes).index(pred)] * 100

        return f"Прогноз: {pred}/5\nУверенность: {confidence:.1f}%\nНа основе темы, научрука и среднего балла ({diploma_avg})."
    except Exception as e:
        return f"Ошибка прогноза: {type(e).__name__}"
