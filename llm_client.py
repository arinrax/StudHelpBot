from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

def ask_llm(user_message, system_prompt=None):
    if system_prompt is None:
        system_prompt = "Ты полезный ассистент. Отвечай кратко и по делу на русском языке."

    try:
        response = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка LLM: {e}"

if __name__ == "__main__":
    print("Тест qwen. Введите вопрос (или q):")
    while True:
        q = input("\nВы: ")
        if q.lower() in ("q", "exit"):
            break
        print(f"\nQwen: {ask_llm(q)}")