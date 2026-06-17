import json

from openai import OpenAI

from services.db_tools import (
    find_similar_topics,
    get_random_topic,
    get_supervisor_stats,
    get_supervisor_topics,
    search_topics_keyword,
)
from services.predictor import predict_grade
from utils.logger import logger

from .agent_config import SYSTEM_PROMPT, tools_definition

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120.0,
)


def process_response(user_message):
    logger.info(f"Получен запрос: {user_message[:50]}")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=messages,
            tools=tools_definition,
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            logger.info(f"LLM вызвала инструмент: {function_name}")
            logger.debug(f"Аргументы: {function_args}")

            if function_name == "search_topics_keyword":
                tool_response = search_topics_keyword(function_args.get("keyword", ""))

            elif function_name == "get_supervisor_topics":
                tool_response = get_supervisor_topics(
                    function_args.get("supervisor", "")
                )

            elif function_name == "get_supervisor_stats":
                tool_response = get_supervisor_stats(
                    function_args.get("supervisor", "")
                )

            elif function_name == "get_random_topic":
                tool_response = get_random_topic()

            elif function_name == "find_similar_topics":
                tool_response = find_similar_topics(function_args.get("topic_text", ""))

            elif function_name == "predict_grade":
                tool_response = predict_grade(
                    topic=function_args.get("topic", ""),
                    supervisor=function_args.get("supervisor", ""),
                    diploma_avg=function_args.get("diploma_avg"),
                )

            else:
                tool_response = "Инструмент не найден"
                logger.warning(f"Неизвестный инструмент: {function_name}")

            messages.append(response_message)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_response,
                }
            )

            logger.debug("Отправляю второй запрос к LLM с результатом инструмента...")
            second_response = client.chat.completions.create(
                model="qwen2.5:7b", messages=messages
            )

            final_content = second_response.choices[0].message.content
            logger.info(f"Ответ сгенерирован ({len(final_content)} символов)")
            return final_content

        logger.info("Ответ без использования инструментов")
        return response_message.content

    except Exception as e:
        logger.error(f"Ошибка в LLM клиенте: {e}", exc_info=True)
        return f"Ошибка: {e}"
