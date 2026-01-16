import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv('ADMIN_ID'))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения.")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден в переменных окружения.")

REVIEWS_CHANNEL_ID = "@visausa_eb1"
REVIEWS_CHANNEL_LINK = "https://t.me/visausa_eb1"

PR_SPECIALIST_USERNAME = "@OlgaMar_pr"
PR_SPECIALIST_EMAIL = "tvolga074@gmail.com"


