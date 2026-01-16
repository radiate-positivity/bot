from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PR_SPECIALIST_USERNAME, PR_SPECIALIST_EMAIL
from utils.text_data import CONTACT_TEXTS

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
    contact_text = f"{CONTACT_TEXTS['main_title']}\n\n{CONTACT_TEXTS['intro']}"
    
    contacts = []
    
    if PR_SPECIALIST_USERNAME and PR_SPECIALIST_USERNAME != "@username_specialist":
        contacts.append(f"• <b>Telegram:</b> {PR_SPECIALIST_USERNAME}")
    
    if PR_SPECIALIST_EMAIL and PR_SPECIALIST_EMAIL != "partner@firma.com":
        contacts.append(f"• <b>Email:</b> {PR_SPECIALIST_EMAIL}")
    
    if not contacts:
        contact_text += f"\n\n{CONTACT_TEXTS['no_contacts']}"
    else:
        contact_text += "\n\n" + "\n".join(contacts)
        contact_text += f"\n\n{CONTACT_TEXTS['work_hours']}"
    
    keyboard_builder = get_contact_keyboard()
    
    await message.answer(
        text=contact_text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "contact_schedule")
async def schedule_consultation(callback: CallbackQuery):
    schedule_text = f"{CONTACT_TEXTS['schedule_title']}\n\n{CONTACT_TEXTS['schedule_text']}"
    
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
    from utils.text_data import START_TEXTS
    
    await callback.message.answer(
        text=START_TEXTS["welcome"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.answer()
