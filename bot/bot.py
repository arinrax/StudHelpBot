import telebot
import os
from dotenv import load_dotenv
from core.llm_client import process_response

load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
print("Бот запущен")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name or "друг"
    text = (
        f"Привет, {name}!\n"
        "Я твой помощник по ВКР.\n"
        "Напиши мне ключевое слово, "
        "и я подберу тему, посмотрев в архив работ."
    )
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    loading = bot.reply_to(message, "Думаю...")

    try:
        answer = process_response(message.text)
        bot.edit_message_text(
            chat_id=loading.chat.id,
            message_id=loading.message_id,
            text=answer,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=loading.chat.id,
            message_id=loading.message_id,
            text=f"Ошибка: {e}"
        )

