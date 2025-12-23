import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск бота...")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    logger.info("Регистрация обработчиков...")
    
    try:
        from handlers.start import router as start_router
        from handlers.faq import router as faq_router
        from handlers.quiz import router as quiz_router
        from handlers.contact import router as contact_router
        from handlers.services import router as services_router
        from handlers.reviews import router as reviews_router
        from handlers.add_review import router as add_review_router
        
        dp.include_router(start_router)
        dp.include_router(faq_router)
        dp.include_router(quiz_router)
        dp.include_router(contact_router)
        dp.include_router(services_router)
        dp.include_router(reviews_router)
        dp.include_router(add_review_router)
        
        logger.info("Роутеры зарегистрированы: start, faq, quiz, contact, services, reviews, add_review")
        
    except ImportError as e:
        logger.error(f"Ошибка импорта обработчиков: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    try:
        from handlers.admin import router as admin_router
        dp.include_router(admin_router)
        logger.info("Роутер admin зарегистрирован")
    except ImportError as e:
        logger.warning(f"Не удалось загрузить admin роутер: {e}")
    except Exception as e:
        logger.error(f"Ошибка при регистрации admin роутера: {e}")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен и готов к работе!")
        logger.info(f"Бот: @{bot_info.username} (ID: {bot_info.id})")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
