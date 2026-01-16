from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import (
    PR_SPECIALIST_USERNAME, 
    PR_SPECIALIST_EMAIL
)

router = Router()

def get_contact_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    if PR_SPECIALIST_USERNAME and PR_SPECIALIST_USERNAME != "@username_specialist":
        builder.row(
            InlineKeyboardButton(
                text="💬 Написать в Telegram",
                url=f"https://t.me/{PR_SPECIALIST_USERNAME.replace('@', '')}"
            )
        )
    
    if PR_SPECIALIST_EMAIL and PR_SPECIALIST_EMAIL != "partner@firma.com":
        builder.row(
            InlineKeyboardButton(
                text="📧 Написать на email",
                url=f"mailto:{PR_SPECIALIST_EMAIL}"
            )
        )
    
    
    builder.row(
        InlineKeyboardButton(
            text="📅 Записаться на консультацию",
            callback_data="contact_schedule"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="contact_back_to_menu"
        )
    )
    
    return builder

@router.message(F.text == "👨‍💼 Связаться со специалистом")
async def contact_handler(message: Message):
    contact_text = f"""
📞 <b>Связь со специалистом</b>

Вы можете связаться с нами следующими способами:

"""
    
    contacts = []
    
    if PR_SPECIALIST_USERNAME and PR_SPECIALIST_USERNAME != "@username_specialist":
        contacts.append(f"• <b>Telegram:</b> {PR_SPECIALIST_USERNAME}")
    
    if PR_SPECIALIST_EMAIL and PR_SPECIALIST_EMAIL != "partner@firma.com":
        contacts.append(f"• <b>Email:</b> {PR_SPECIALIST_EMAIL}")
    
    if not contacts:
        contact_text += """
⚠️ <b>Контакты не настроены</b>

Для настройки контактов отредактируйте файл <code>config.py</code>:
1. PR_SPECIALIST_USERNAME - username специалиста в Telegram
2. PR_SPECIALIST_EMAIL - email специалиста
3. PR_SPECIALIST_PHONE - телефон специалиста
"""
    else:
        contact_text += "\n".join(contacts)
        contact_text += """

<b>Часы работы:</b>
Пн-Пт: 18:00-22:00 (МСК)

<b>Время ответа:</b>
• Telegram/Email: в течение 24 часов
"""
    
    keyboard_builder = get_contact_keyboard()
    
    await message.answer(
        text=contact_text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "contact_schedule")
async def schedule_consultation(callback: CallbackQuery):
    schedule_text = """
📅 <b>Запись на консультацию</b>

<b>Формат консультаций:</b>
1. <b>Первичная консультация</b> (15 мин) - бесплатно
   • Общая оценка ситуации
   • Рекомендации по стратегии
   
2. <b>Детальная консультация</b> (60 мин) - $250
   • Подробный разбор документов
   • Стратегия подготовки пакета
   • Ответы на все вопросы

<b>Для записи:</b>
1. Выберите удобное время (Пн-Пт: 18:00-22:00 (МСК))
2. Отправьте запрос через Telegram или email
3. Укажите удобный формат (видео/аудио звонок)
4. Приложите краткое описание ситуации
"""
    
    builder = InlineKeyboardBuilder()
    
    if PR_SPECIALIST_USERNAME and PR_SPECIALIST_USERNAME != "@username_specialist":
        builder.row(
            InlineKeyboardButton(
                text="💬 Записаться через Telegram",
                url=f"https://t.me/{PR_SPECIALIST_USERNAME.replace('@', '')}?text=Хочу записаться на консультацию"
            )
        )
    
    if PR_SPECIALIST_EMAIL and PR_SPECIALIST_EMAIL != "partner@firma.com":
        builder.row(
            InlineKeyboardButton(
                text="📧 Записаться по email",
                url=f"mailto:{PR_SPECIALIST_EMAIL}?subject=Запись на консультацию"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к контактам",
            callback_data="contact_back"
        )
    )
    
    await callback.message.edit_text(
        text=schedule_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "contact_back")
async def back_to_contacts(callback: CallbackQuery):
    await contact_handler(callback.message)
    await callback.answer()

@router.callback_query(F.data == "contact_back_to_menu")
async def contact_back_to_menu(callback: CallbackQuery):
    from handlers.start import get_main_keyboard
    
    welcome_text = """
🤖 <b>Добро пожаловать!</b>

Я — бот-ассистент компании <b>Clever Solutions</b>. 
Помогу вам с PR активностями и предварительной оценкой шансов на получение виз:
• EB-1A — для лиц с исключительными способностями (иммиграционная)
• O-1 — для лиц с исключительными способностями (неиммиграционная)
• EB-2 NIW — национальный интерес 

Выберите интересующий вас раздел👇
    """
    
    await callback.message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    
    try:
        await callback.message.delete()
    except:
        pass
    

    await callback.answer()
