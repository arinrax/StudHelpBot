import os

from dotenv import load_dotenv

from bot.bot import bot
from utils.logger import logger

load_dotenv()

if __name__ == "__main__":
    logger.info("Запуск бота")
    logger.info(f"Рабочая папка: {os.getcwd()}")

    try:
        logger.info("Запуск polling")
        bot.infinity_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise
