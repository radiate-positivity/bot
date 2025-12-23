from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
    builder.row(
        KeyboardButton(text="📈 Отзывы и кейсы"),
        KeyboardButton(text="ℹ️ О боте")
    )
    
    return builder.as_markup(resize_keyboard=True, persistent=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = """
🤖 <b>Добро пожаловать!</b>

Я — бот-ассистент компании <b>VisaSuccess</b>. 
Помогу вам с предварительной оценкой шансов на получение виз:

• <b>EB-1A</b> — для лиц с исключительными способностями
• <b>O-1</b> — для лиц с выдающимися способностями
• <b>EB-2 NIW</b> — национальный интерес

Выберите интересующий вас раздел👇
    """
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📚 <b>Доступные команды:</b>

/start — Главное меню
/help — Эта справка

👆 Вы также можете использовать кнопки меню ниже для навигации.

<b>Важно:</b> Информация, предоставляемая ботом, носит ознакомительный характер и не является юридической консультацией.
    """
    
    await message.answer(
        text=help_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(lambda message: message.text == "ℹ️ О боте")
async def about_bot(message: Message):
    about_text = """
ℹ️ <b>О боте</b>

Этот бот создан для предварительной оценки шансов на получение виз:
• EB-1A (Extraordinary Ability)
• O-1 (Individuals with Extraordinary Ability)
• EB-2 NIW (National Interest Waiver)

<b>Дисклеймер:</b>
Вся информация, предоставляемая ботом, носит ознакомительный характер. 
Для получения юридической консультации обратитесь к специалисту.

Версия бота: 1.0
Разработчик: Ваша компания
    """
    await message.answer(text=about_text, parse_mode="HTML")