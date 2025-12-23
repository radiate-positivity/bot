# main.py - минимальная версия
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Импортируем и регистрируем ВСЕ роутеры
    from handlers.start import router as start_router
    from handlers.faq import router as faq_router
    from handlers.quiz import router as quiz_router
    from handlers.contact import router as contact_router
    from handlers.services import router as services_router
    from handlers.reviews import router as reviews_router
    from handlers.add_review import router as add_review_router
    from handlers.admin import router as admin_router
    
    dp.include_router(start_router)
    dp.include_router(faq_router)
    dp.include_router(quiz_router)
    dp.include_router(contact_router)
    dp.include_router(services_router)
    dp.include_router(reviews_router)
    dp.include_router(add_review_router)
    dp.include_router(admin_router)
    
    print(f"✅ Admin роутер зарегистрирован")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
