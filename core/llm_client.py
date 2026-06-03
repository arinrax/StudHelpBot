import json
from openai import OpenAI

from services.db_tools import search_topics_keyword
from services.predictor import predict_grade
from .agent_config import SYSTEM_PROMPT, tools_definition


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120.0,
)


def process_response(user_message):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
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

            if function_name == "search_topics_keyword":
                db_results = search_topics_keyword(function_args.get("keyword", ""))
                tool_response = json.dumps(db_results, ensure_ascii=False)

            elif function_name == "predict_grade":
                tool_response = predict_grade(
                    topic=function_args.get("topic", ""),
                    supervisor=function_args.get("supervisor", ""),
                    diploma_avg=function_args.get("diploma_avg"),
                )

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
