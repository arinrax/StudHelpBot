from sentence_transformers import SentenceTransformer, util

print("Загрузка модели")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

print("Модель загружена\n")

sentences = [
    "Искусственный интеллект меняет мир.",
    "Машинное обучение меняет нашу реальность.",
    "Я люблю есть пиццу по пятницам.",
]

print("Преобразование")
embeddings = model.encode(sentences)

cos_scores = util.cos_sim(embeddings[0], embeddings)[0]

print(f'Фраза 1: "{sentences[0]}"')

for i in range(len(sentences)):
    score = cos_scores[i].item()
    print(f'Сравнение с фразой {i+1}: "{sentences[i]}"')
    print(f"Похожесть: {score:.4f} (от 0 до 1)")
    print()
