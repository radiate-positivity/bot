from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.text_data import START_TEXTS

router = Router()

def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="❓ Частые вопросы (FAQ)"),
        KeyboardButton(text="📊 Пройти оценку шансов")
    )
    builder.row(
        KeyboardButton(text="👨‍💼 Связаться со специалистом"),
        KeyboardButton(text="💼 Услуги и стоимость")
    )
    
    return builder.as_markup(resize_keyboard=True, persistent=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=START_TEXTS["welcome"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text=START_TEXTS["help"],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
