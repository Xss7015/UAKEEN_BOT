import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, ENVIRONMENT
from handlers import Handlers
from web_server import web_server

logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "dev" else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    logger.info(f"🚀 Запускаем бота в режиме {ENVIRONMENT}...")
    
    # Запускаем веб-сервер
    await web_server.start()
    
    # Запускаем бота
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")