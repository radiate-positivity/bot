from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.quiz_texts import QUIZ_TEXTS

router = Router()

class QuizStates(StatesGroup):
    waiting_for_start = State()
    publications = State()
    citations = State()
    reviews = State()
    membership = State()
    media = State()
    awards = State()
    waiting_for_results = State()

def get_quiz_keyboard(options_list, question_num, total_questions):
    builder = InlineKeyboardBuilder()
    
    for option in options_list:
        builder.row(
            InlineKeyboardButton(
                text=option["text"],
                callback_data=f"quiz_answer:{option['score']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить квиз",
            callback_data="quiz_cancel"
        )
    )
    
    return builder.as_markup()

def get_start_quiz_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Начать оценку",
            callback_data="quiz_start"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Вернуться в меню",
            callback_data="quiz_back_to_menu"
        )
    )
    
    return builder.as_markup()

@router.message(F.text == "📊 Пройти оценку шансов")
async def start_quiz_command(message: Message, state: FSMContext):
    await state.set_state(QuizStates.waiting_for_start)
    
    await message.answer(
        text=QUIZ_TEXTS["start"]["text"],
        reply_markup=get_start_quiz_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "quiz_start", StateFilter(QuizStates.waiting_for_start))
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        quiz_score=0,
        current_question=0,
        answers={},
        message_id=callback.message.message_id
    )
    
    question_data = QUIZ_TEXTS["questions"][0]
    
    await state.set_state(QuizStates.publications)
    
    await callback.message.edit_text(
        text=f"1/{len(QUIZ_TEXTS['questions'])}\n\n{question_data['text']}",
        reply_markup=get_quiz_keyboard(question_data["options"], 1, len(QUIZ_TEXTS["questions"])),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data.startswith("quiz_answer:"), StateFilter(
    QuizStates.publications,
    QuizStates.citations,
    QuizStates.reviews,
    QuizStates.membership,
    QuizStates.media,
    QuizStates.awards
))
async def process_quiz_answer(callback: CallbackQuery, state: FSMContext):
    score = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    current_q = data.get("current_question", 0)
    quiz_score = data.get("quiz_score", 0)
    answers = data.get("answers", {})
    
    quiz_score += score
    answers[current_q] = score
    
    await state.update_data(
        quiz_score=quiz_score,
        answers=answers,
        current_question=current_q + 1
    )
    
    next_q = current_q + 1
    if next_q < len(QUIZ_TEXTS["questions"]):
        question_data = QUIZ_TEXTS["questions"][next_q]
        
        state_mapping = {
            0: QuizStates.publications,
            1: QuizStates.citations,
            2: QuizStates.reviews,
            3: QuizStates.membership,
            4: QuizStates.media,
            5: QuizStates.awards
        }
        
        next_state = state_mapping.get(next_q, QuizStates.waiting_for_results)
        await state.set_state(next_state)
        
        await callback.message.edit_text(
            text=f"{next_q + 1}/{len(QUIZ_TEXTS['questions'])}\n\n{question_data['text']}",
            reply_markup=get_quiz_keyboard(question_data["options"], next_q + 1, len(QUIZ_TEXTS["questions"])),
            parse_mode="HTML"
        )
    else:
        await state.set_state(QuizStates.waiting_for_results)
        await show_quiz_results_final(callback, quiz_score, state)
    
    await callback.answer()

async def show_quiz_results_final(callback: CallbackQuery, total_score: int, state: FSMContext):
    result_category = "low"
    
    if total_score >= 26:
        result_category = "high"
    elif total_score >= 11:
        result_category = "medium"
    
    result_data = QUIZ_TEXTS["results"][result_category]
    
    await state.update_data(final_score=total_score)
    
    result_text = f"{result_data['title']}\n\n{result_data['text']}\n\n<b>Ваш балл: {total_score}/40</b>\n{QUIZ_TEXTS['disclaimer']}"
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="👨‍💼 Записаться на консультацию",
            callback_data="quiz_consultation"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔄 Пройти квиз заново",
            callback_data="quiz_restart"
        ),
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="quiz_back_to_menu"
        )
    )
    
    await callback.message.edit_text(
        text=result_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "quiz_cancel")
async def cancel_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="quiz_back_to_menu"
        )
    )
    
    await callback.message.edit_text(
        text="❌ Квиз отменен.",
        reply_markup=builder.as_markup()
    )
    
    await callback.answer()

@router.callback_query(F.data == "quiz_back_to_menu")
async def back_to_menu_from_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
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

@router.callback_query(F.data == "quiz_restart")
async def restart_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(QuizStates.waiting_for_start)
    
    await callback.message.edit_text(
        text=QUIZ_TEXTS["start"]["text"],
        reply_markup=get_start_quiz_keyboard(),
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.callback_query(F.data == "quiz_consultation")
async def request_consultation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_score = data.get("final_score", 0)
    
    if quiz_score == 0:
        quiz_score = data.get("quiz_score", 0)
    
    consultation_text = QUIZ_TEXTS["consultation_text"].format(score=quiz_score)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="quiz_back_to_menu"
        )
    )
    
    await callback.message.edit_text(
        text=consultation_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()
