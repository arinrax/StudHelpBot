import telebot
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

print("Бот запущен. Жду сообщений")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! 🎓\n\n"
                          "Скоро я научусь:\n"
                          "Подбирать темы для курсовых\n"
                          "Искать информацию в базе работ\n"
                          "Прогнозировать оценки\n\n"
                          "Жди обновлений")
bot.infinity_polling()