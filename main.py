import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("🔄 Запуск бота...")
    
    try:
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher(storage=MemoryStorage())
        
        print("📋 Импорт роутеров...")
        
        # Импортируем и регистрируем ВСЕ роутеры
        try:
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
            print(f"🔄 Все роутеры зарегистрированы")
            
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
            sys.exit(1)
        
        # Удаляем вебхук и начинаем polling
        print("🔄 Удаляю вебхук...")
        await bot.delete_webhook(drop_pending_updates=True)
        
        bot_info = await bot.get_me()
        print(f"✅ Бот запущен: @{bot_info.username} (ID: {bot_info.id})")
        print(f"📱 Бот готов к работе!")
        print(f"➡️ Отправьте команду /testadmin для проверки")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.session.close()
        print("🛑 Бот остановлен")

if __name__ == "__main__":
    # Проверяем, что нет других запусков
    import os
    import socket
    
    try:
        # Проверка на дублирующий запуск
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8080))
        
        if result == 0:
            print("⚠️ Возможно, бот уже запущен!")
            print("Остановите все процессы и запустите заново.")
            choice = input("Продолжить? (y/n): ")
            if choice.lower() != 'y':
                sys.exit(1)
        
        sock.close()
    except:
        pass
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
