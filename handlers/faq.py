from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.text_data import FAQ_DATA

router = Router()

def get_faq_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📋 EB-1A", 
            callback_data="faq_category:eb1a"
        ),
        InlineKeyboardButton(
            text="🎭 O-1 Visa", 
            callback_data="faq_category:o1"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔬 EB-2 NIW", 
            callback_data="faq_category:niw"
        )
        InlineKeyboardButton(
            text="🔙 Главное меню", 
            callback_data="faq_back_to_menu"
        )
    )
    
    return builder.as_markup()

def get_faq_category_keyboard(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    category_data = FAQ_DATA.get(category, {})
    
    if "questions" in category_data:
        for q_key, q_data in category_data["questions"].items():
            question_text = q_data['text']
            if len(question_text) > 40:
                question_text = question_text[:37] + "..."
            
            builder.row(
                InlineKeyboardButton(
                    text=f"❔ {question_text}",
                    callback_data=f"faq_question:{category}:{q_key}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к категориям",
            callback_data="faq_back_to_categories"
        ),
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="faq_back_to_menu"
        )
    )
    
    return builder.as_markup()

@router.message(F.text == "❓ Частые вопросы (FAQ)")
async def show_faq_menu(message: Message):
    menu_text = """
📚 <b>Частые вопросы (FAQ)</b>

Выберите категорию вопросов:
"""
    
    await message.answer(
        text=menu_text,
        reply_markup=get_faq_main_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("faq_category:"))
async def process_faq_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    category_data = FAQ_DATA.get(category, {})
    
    if not category_data:
        await callback.answer("Категория не найдена")
        return
    
    title = category_data.get("title", "Категория")
    questions_count = len(category_data.get("questions", {}))
    
    text = f"""
{title}

В этой категории {questions_count} вопросов.
Выберите интересующий вопрос:
    """
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_faq_category_keyboard(category),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("faq_question:"))
async def process_faq_question(callback: CallbackQuery):
    _, category, question_key = callback.data.split(":")
    
    category_data = FAQ_DATA.get(category, {})
    question_data = category_data.get("questions", {}).get(question_key, {})
    
    if not question_data:
        await callback.answer("Вопрос не найден")
        return
    
    question_text = question_data.get("text", "")
    answer_text = question_data.get("answer", "")
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к вопросам",
            callback_data=f"faq_category:{category}"
        ),
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="faq_back_to_menu"
        )
    )
    
    text = f"""
<b>❔ Вопрос:</b> {question_text}

{answer_text}

<i>Эта информация носит ознакомительный характер.</i>
    """
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "faq_back_to_categories")
async def back_to_faq_categories(callback: CallbackQuery):
    menu_text = """
📚 <b>Частые вопросы (FAQ)</b>

Выберите категорию вопросов:
"""
    
    await callback.message.edit_text(
        text=menu_text,
        reply_markup=get_faq_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "faq_back_to_menu")
async def back_to_main_menu(callback: CallbackQuery):
    from handlers.start import get_main_keyboard
    
    welcome_text = """
🤖 <b>Добро пожаловать!</b>

Я — бот-ассистент компании <b>Clever Solutions</b>. 
Помогу вам с PR активностями и предварительной оценкой шансов на получение виз.
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

@router.message(Command("faq"))
async def cmd_faq(message: Message):
    menu_text = """
📚 <b>Частые вопросы (FAQ)</b>

Выберите категорию вопросов:
"""
    
    await message.answer(
        text=menu_text,
        reply_markup=get_faq_main_keyboard(),
        parse_mode="HTML"

    )
