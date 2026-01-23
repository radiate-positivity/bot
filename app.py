import asyncio
import logging
import os
import threading
import time
import requests
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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

from handlers.start import router as start_router
from handlers.faq import router as faq_router
from handlers.quiz import router as quiz_router
from handlers.contact import router as contact_router
from handlers.services import router as services_router

def start_keep_alive():
    def ping():
        service_name = os.environ.get('RENDER_SERVICE_NAME', 'your-bot-name')
        while True:
            try:
                requests.get(f"https://{service_name}.onrender.com/health", timeout=5)
                logger.info(f"[Keep-alive] Ping sent")
            except Exception as e:
                logger.warning(f"[Keep-alive] Ping failed: {e}")
            time.sleep(280)
    
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()
    return thread

async def on_startup(bot: Bot):
    webhook_url = f"https://{os.environ.get('RENDER_SERVICE_NAME', 'your-bot-name')}.onrender.com/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logger.info("Webhook удален")

async def main():
    logger.info("Запуск бота на вебхуках...")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(start_router)
    dp.include_router(faq_router)
    dp.include_router(quiz_router)
    dp.include_router(contact_router)
    dp.include_router(services_router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    keep_alive_thread = start_keep_alive()
    
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    webhook_requests_handler.register(app, path="/webhook")
    
    async def health(request):
        return web.Response(text="OK")
    
    app.router.add_get("/health", health)
    
    port = int(os.environ.get("PORT", 5000))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"Сервер запущен на порту {port}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")
