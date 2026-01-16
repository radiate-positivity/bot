from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PR_SPECIALIST_USERNAME, PR_SPECIALIST_EMAIL
from utils.text_data import SERVICES_TEXTS, CONTACT_TEXTS

router = Router()

def get_services_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["eb1a"],
            callback_data="service_detail:eb1a"
        ),
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["o1"],
            callback_data="service_detail:o1"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["niw"],
            callback_data="service_detail:niw"
        ),
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["combo"],
            callback_data="service_detail:combo"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["consultation"],
            callback_data="service_detail:consultation"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text=SERVICES_TEXTS["buttons"]["contact"],
            callback_data="service_contact"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="service_back_to_menu"
        )
    )
    
    return builder

@router.message(F.text == "💼 Услуги и стоимость")
async def services_handler(message: Message):
    services_text = f"{SERVICES_TEXTS['main_title']}\n\n{SERVICES_TEXTS['main_text']}"
    
    keyboard_builder = get_services_keyboard()
    
    await message.answer(
        text=services_text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("service_detail:"))
async def service_detail(callback: CallbackQuery):
    service_type = callback.data.split(":")[1]
    
    service_data = SERVICES_TEXTS["details"].get(service_type, {})
    
    if not service_data:
        await callback.answer("Услуга не найдена")
        return
    
    text = f"{service_data['title']}\n\n{service_data['text']}"
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📞 Заказать эту услугу",
            callback_data="service_contact"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к услугам",
            callback_data="service_back_to_list"
        )
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "service_back_to_list")
async def back_to_services_list(callback: CallbackQuery):
    await services_handler(callback.message)
    await callback.answer()

@router.callback_query(F.data == "service_contact")
async def service_contact(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать в Telegram",
            url="https://t.me/OlgaMar_pr"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к услугам",
            callback_data="service_back_to_list"
        )
    )
    
    await callback.message.edit_text(
        text=CONTACT_TEXTS["contact_order"],
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "service_back_to_menu")
async def service_back_to_menu(callback: CallbackQuery):
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
