import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from handlers import Handlers
from web_server import web_server
from config import BOT_TOKEN, ENVIRONMENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info(f"🚀 Запускаем бота в режиме {ENVIRONMENT}...")
    
    # Запускаем веб-сервер
    await web_server.start()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    Handlers(dp)
    
    logger.info("✅ Бот успешно запущен!")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()
        await web_server.stop()

if __name__ == "__main__":
    asyncio.run(main())