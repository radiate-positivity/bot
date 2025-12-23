import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения.")

REVIEWS_CHANNEL_ID = "@your_reviews_channel"
REVIEWS_CHANNEL_LINK = "https://t.me/your_reviews_channel"

PR_SPECIALIST_USERNAME = "@username_specialist"
PR_SPECIALIST_EMAIL = "partner@firma.com"
PR_SPECIALIST_PHONE = "+1234567890"