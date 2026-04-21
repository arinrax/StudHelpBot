import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "search_topics_keyword",
            "description": "Поиск тем курсовых работ в базе данных по ключевому слову. Используй, когда пользователь просит подобрать тему или спрашивает про конкретную область.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Ключевое слово для поиска"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


def process_llm_response(user_message: str) -> str:
    messages = [
        {"role": "system",
         "content": "Ты умный помощник студента. Используй доступные инструменты, чтобы помочь с выбором темы."},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=messages,
            tools=tools_definition,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"LLM вызвала инструмент: {function_name} с аргументами: {function_args}")

            from tools import search_topics_keyword

            if function_name == "search_topics":
                db_results = search_topics_keyword(function_args.get("keyword", ""))
                tool_response = json.dumps(db_results, ensure_ascii=False)
            else:
                tool_response = "Инструмент не найден"

            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_response
            })

            second_response = client.chat.completions.create(
                model="qwen2.5:7b",
                messages=messages
            )
            return second_response.choices[0].message.content

        return response_message.content

    except Exception as e:
        return f"Ошибка: {e}"
