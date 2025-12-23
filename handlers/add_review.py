from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.database import reviews_db

router = Router()

class ReviewStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_text = State()
    waiting_for_rating = State()
    waiting_for_visa_type = State()
    waiting_for_confirmation = State()

def get_rating_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    for i in range(1, 6):
        stars = "⭐" * i
        builder.row(
            InlineKeyboardButton(
                text=f"{stars} ({i}/5)",
                callback_data=f"review_rating:{i}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    return builder

def get_visa_type_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    visa_types = [
        ("EB-1A", "📋 EB-1A"),
        ("O-1", "🎭 O-1 Visa"),
        ("NIW", "🔬 EB-2 NIW"),
        ("EB-1A + NIW", "🔄 Комбо-пакет"),
        ("Другое", "📝 Другая виза")
    ]
    
    for visa_id, visa_text in visa_types:
        builder.row(
            InlineKeyboardButton(
                text=visa_text,
                callback_data=f"review_visa:{visa_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="⏭️ Пропустить",
            callback_data="review_visa:skip"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    return builder

def get_confirmation_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Отправить отзыв",
            callback_data="review_confirm"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="✏️ Изменить имя",
            callback_data="review_edit_name"
        ),
        InlineKeyboardButton(
            text="✏️ Изменить текст",
            callback_data="review_edit_text"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="⭐ Изменить оценку",
            callback_data="review_edit_rating"
        ),
        InlineKeyboardButton(
            text="📋 Изменить визу",
            callback_data="review_edit_visa"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    return builder

@router.message(Command("addreview"))
@router.callback_query(F.data == "reviews_add")
async def start_review_process(callback: CallbackQuery, state: FSMContext):
    init_default_reviews()
    
    await state.set_state(ReviewStates.waiting_for_name)
    
    text = """
📝 <b>Добавление отзыва</b>

Мы ценим ваше мнение! Ваш отзыв поможет другим сделать правильный выбор.

<b>Введите ваше имя (или псевдоним):</b>
<i>Можно использовать имя и профессию, например: "Алексей, ученый"</i>
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    if isinstance(callback, CallbackQuery):
        await callback.message.edit_text(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
    else:
        await callback.answer(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

@router.message(ReviewStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите имя (минимум 2 символа):")
        return
    
    if len(name) > 100:
        await message.answer("❌ Имя слишком длинное. Введите имя (максимум 100 символов):")
        return
    
    await state.update_data(name=name)
    data = await state.get_data()
    
    if data.get("text"):
        await state.set_state(ReviewStates.waiting_for_confirmation)
        await show_confirmation_message(message, state)
    else:
        await state.set_state(ReviewStates.waiting_for_text)
        
        text = """
✏️ <b>Введите текст отзыва:</b>

Расскажите о вашем опыте:
• Какие услуги получали
• Что понравилось/можно улучшить  
• Результаты (если можно делиться)
• Рекомендации другим

<i>Минимум 20 символов, максимум 1000 символов</i>
"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="↩️ Назад",
                callback_data="review_back_to_confirmation"
            ),
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="review_cancel"
            )
        )
        
        await message.answer(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

@router.message(ReviewStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    review_text = message.text.strip()
    
    if len(review_text) < 20:
        await message.answer("❌ Текст слишком короткий. Минимум 20 символов:")
        return
    
    if len(review_text) > 1000:
        await message.answer("❌ Текст слишком длинный. Максимум 1000 символов:")
        return
    
    await state.update_data(text=review_text)
    data = await state.get_data()
    
    if data.get("rating"):
        await state.set_state(ReviewStates.waiting_for_confirmation)
        await show_confirmation_message(message, state)
    else:
        await state.set_state(ReviewStates.waiting_for_rating)
        
        text = """
⭐ <b>Оцените нашу работу:</b>

Выберите оценку от 1 до 5 звезд:
"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="↩️ Назад",
                callback_data="review_back_to_confirmation"
            )
        )
        
        keyboard = get_rating_keyboard()
        keyboard.attach(builder)
        
        await message.answer(
            text=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("review_rating:"), StateFilter(ReviewStates.waiting_for_rating))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split(":")[1])
    
    await state.update_data(rating=rating)
    await state.set_state(ReviewStates.waiting_for_visa_type)
    
    text = """
📋 <b>Выберите тип визы (опционально):</b>

Если вы получали нашу помощь с конкретной визой, выберите ее:
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="review_back_to_confirmation"
        )
    )
    
    keyboard = get_visa_type_keyboard()
    keyboard.attach(builder)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("review_visa:"), StateFilter(ReviewStates.waiting_for_visa_type))
async def process_visa_type(callback: CallbackQuery, state: FSMContext):
    visa_type = callback.data.split(":")[1]
    
    if visa_type == "skip":
        visa_type = ""
    
    await state.update_data(visa_type=visa_type)
    await state.set_state(ReviewStates.waiting_for_confirmation)
    
    data = await state.get_data()
    
    stars = "⭐" * data["rating"]
    
    confirmation_text = f"""
✅ <b>Проверьте ваш отзыв:</b>

<b>Имя:</b> {data['name']}
<b>Оценка:</b> {stars} ({data['rating']}/5)
"""
    
    if data.get("visa_type"):
        confirmation_text += f"<b>Тип визы:</b> {data['visa_type']}\n"
    
    confirmation_text += f"""
<b>Текст отзыва:</b>
{data['text']}

<b>Отзыв будет отправлен на модерацию.</b>
После проверки он появится в общем списке.
"""
    
    await callback.message.edit_text(
        text=confirmation_text,
        reply_markup=get_confirmation_keyboard().as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_edit_name", StateFilter(ReviewStates.waiting_for_confirmation))
async def edit_name(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    
    await state.set_state(ReviewStates.waiting_for_name)
    await state.update_data(**current_data)
    
    text = """
✏️ <b>Введите новое имя:</b>
    
<i>Текущие данные сохранятся</i>
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад к проверке",
            callback_data="review_back_to_confirmation"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_edit_text", StateFilter(ReviewStates.waiting_for_confirmation))
async def edit_text(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    
    await state.set_state(ReviewStates.waiting_for_text)
    await state.update_data(**current_data)
    
    text = """
✏️ <b>Введите новый текст отзыва:</b>
    
<i>Текущие данные сохранятся</i>
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад к проверке",
            callback_data="review_back_to_confirmation"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="review_cancel"
        )
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_edit_rating", StateFilter(ReviewStates.waiting_for_confirmation))
async def edit_rating(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    
    await state.set_state(ReviewStates.waiting_for_rating)
    await state.update_data(**current_data)
    
    text = """
⭐ <b>Выберите новую оценку:</b>
    
<i>Текущие данные сохранятся</i>
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад к проверке",
            callback_data="review_back_to_confirmation"
        )
    )
    
    keyboard = get_rating_keyboard()
    keyboard.attach(builder)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_edit_visa", StateFilter(ReviewStates.waiting_for_confirmation))
async def edit_visa(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    
    await state.set_state(ReviewStates.waiting_for_visa_type)
    await state.update_data(**current_data)
    
    text = """
📋 <b>Выберите тип визы:</b>
    
<i>Текущие данные сохранятся</i>
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="↩️ Назад к проверке",
            callback_data="review_back_to_confirmation"
        )
    )
    
    keyboard = get_visa_type_keyboard()
    keyboard.attach(builder)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_back_to_confirmation")
async def back_to_confirmation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReviewStates.waiting_for_confirmation)
    
    data = await state.get_data()
    
    stars = "⭐" * data["rating"]
    
    confirmation_text = f"""
✅ <b>Проверьте ваш отзыв:</b>

<b>Имя:</b> {data['name']}
<b>Оценка:</b> {stars} ({data['rating']}/5)
"""
    
    if data.get("visa_type"):
        confirmation_text += f"<b>Тип визы:</b> {data['visa_type']}\n"
    
    confirmation_text += f"""
<b>Текст отзыва:</b>
{data['text']}

<b>Отзыв будет отправлен на модерацию.</b>
После проверки он появится в общем списке.
"""
    
    await callback.message.edit_text(
        text=confirmation_text,
        reply_markup=get_confirmation_keyboard().as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

async def show_confirmation_message(message: Message, state: FSMContext):
    data = await state.get_data()
    
    stars = "⭐" * data["rating"]
    
    confirmation_text = f"""
✅ <b>Проверьте ваш отзыв:</b>

<b>Имя:</b> {data['name']}
<b>Оценка:</b> {stars} ({data['rating']}/5)
"""
    
    if data.get("visa_type"):
        confirmation_text += f"<b>Тип визы:</b> {data['visa_type']}\n"
    
    confirmation_text += f"""
<b>Текст отзыва:</b>
{data['text']}

<b>Отзыв будет отправлен на модерацию.</b>
После проверки он появится в общем списке.
"""
    
    await message.answer(
        text=confirmation_text,
        reply_markup=get_confirmation_keyboard().as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "review_confirm", StateFilter(ReviewStates.waiting_for_confirmation))
async def confirm_review(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    review_id = reviews_db.add_review(
        name=data["name"],
        text=data["text"],
        rating=data["rating"],
        visa_type=data.get("visa_type", ""),
        status="pending",
        user_id=callback.from_user.id,
        username=callback.from_user.username
    )
    
    await state.clear()
    
    try:
        from config import ADMIN_ID
        if ADMIN_ID and ADMIN_ID != 0:
            print(f"🔔 Отправка уведомления админу на ID: {ADMIN_ID}")
            
            stars = "⭐" * data["rating"]
            admin_text = f"""
🔔 <b>НОВЫЙ ОТЗЫВ НА МОДЕРАЦИЮ</b>

<b>ID:</b> #{review_id}
<b>От:</b> {data['name']}
<b>Username:</b> @{callback.from_user.username if callback.from_user.username else 'нет'}
<b>User ID:</b> {callback.from_user.id}
<b>Оценка:</b> {stars} ({data['rating']}/5)
"""
            
            if data.get("visa_type"):
                admin_text += f"<b>Тип визы:</b> {data['visa_type']}\n"
            
            preview_text = data['text'][:200] + "..." if len(data['text']) > 200 else data['text']
            admin_text += f"\n<b>Текст:</b>\n{preview_text}"
            
            admin_builder = InlineKeyboardBuilder()
            admin_builder.row(
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"admin_approve:{review_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"admin_reject:{review_id}"
                )
            )
            admin_builder.row(
                InlineKeyboardButton(
                    text="📝 Показать полный текст",
                    callback_data=f"admin_show_full:{review_id}"
                )
            )
            
            try:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_text,
                    reply_markup=admin_builder.as_markup(),
                    parse_mode="HTML"
                )
                print(f"✅ Уведомление отправлено админу {ADMIN_ID}")
            except Exception as e:
                print(f"❌ Ошибка отправки сообщения админу: {e}")
        else:
            print("⚠️ ADMIN_ID не настроен в config.py")
    except ImportError:
        print("⚠️ ADMIN_ID не найден в config.py")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления админу: {e}")
    
    success_text = f"""
✅ <b>Отзыв успешно отправлен!</b>

ID отзыва: #{review_id}

<b>Что дальше:</b>
1. Ваш отзыв отправлен на модерацию
2. Мы проверим его в течение 24 часов
3. После одобрения он появится в общем списке
4. Вы получите уведомление

<b>Благодарим за отзыв!</b> 💫
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📊 Посмотреть другие отзывы",
            callback_data="reviews_examples"
        ),
        InlineKeyboardButton(
            text="🏠 В главное меню",
            callback_data="reviews_back_to_menu"
        )
    )
    
    await callback.message.edit_text(
        text=success_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "review_cancel")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    from handlers.start import get_main_keyboard
    
    text = """
❌ <b>Добавление отзыва отменено</b>

Вы всегда можете оставить отзыв позже через меню "Отзывы и кейсы".
"""
    
    await callback.message.edit_text(
        text=text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()

