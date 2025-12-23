from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.database import reviews_db
from config import REVIEWS_CHANNEL_ID, REVIEWS_CHANNEL_LINK

router = Router()

def init_default_reviews():
    try:
        from utils.text_data import DEFAULT_REVIEWS
        existing_reviews = reviews_db.get_reviews(status="approved", limit=1)
        if not existing_reviews:
            print("🔧 Инициализация базы отзывов...")
            for review in DEFAULT_REVIEWS:
                reviews_db.add_review(
                    name=review["name"],
                    text=review["text"],
                    rating=review["rating"],
                    visa_type=review["visa_type"],
                    status=review["status"]
                )
            print("✅ База отзывов инициализирована с примерами")
    except Exception as e:
        print(f"⚠️ Ошибка при инициализации отзывов: {e}")

def get_reviews_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    if REVIEWS_CHANNEL_ID and REVIEWS_CHANNEL_ID != "@your_reviews_channel":
        if REVIEWS_CHANNEL_LINK and REVIEWS_CHANNEL_LINK != "https://t.me/your_reviews_channel":
            channel_link = REVIEWS_CHANNEL_LINK
        else:
            channel_link = f"https://t.me/{REVIEWS_CHANNEL_ID.replace('@', '')}"
        
        builder.row(
            InlineKeyboardButton(
                text="📢 Перейти в канал с отзывами",
                url=channel_link
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="⭐ Читать отзывы",
            callback_data="reviews_examples"
        ),
        InlineKeyboardButton(
            text="📊 Статистика",
            callback_data="reviews_stats"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📝 Оставить отзыв",
            callback_data="reviews_add"
        ),
        InlineKeyboardButton(
            text="🔍 Поиск по типу визы",
            callback_data="reviews_search"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="reviews_back_to_menu"
        )
    )
    
    return builder

@router.message(F.text == "📈 Отзывы и кейсы")
async def reviews_handler(message: Message):
    stats = reviews_db.get_statistics()
    
    reviews_text = f"""
📈 <b>Отзывы и кейсы</b>

Здесь вы можете ознакомиться с отзывами наших клиентов и реальными кейсами успешного получения виз.

<b>Наша статистика:</b>
• Всего отзывов: {stats['total']}
• Одобрено: {stats['approved']}
• На модерации: {stats['pending']}
• Средняя оценка: {stats['average_rating']}/5 ⭐

"""

    if REVIEWS_CHANNEL_ID and REVIEWS_CHANNEL_ID != "@your_reviews_channel":
        reviews_text += f"""
<b>Наш канал с отзывами:</b> {REVIEWS_CHANNEL_ID}

В канале мы публикуем:
✅ Реальные отзывы клиентов
✅ Подробные кейсы успеха  
✅ Обновления по процессам
✅ Полезные статьи и советы
"""
    else:
        reviews_text += """
<b>Канал с отзывами:</b> В процессе настройки
"""

    reviews_text += """

Выберите раздел для подробной информации:
"""
    
    keyboard_builder = get_reviews_keyboard()
    
    await message.answer(
        text=reviews_text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "reviews_examples")
async def reviews_examples(callback: CallbackQuery):
    approved_reviews = reviews_db.get_reviews(status="approved", limit=10)
    
    if not approved_reviews:
        examples_text = """
⭐ <b>Отзывы</b>

Пока нет одобренных отзывов. Будьте первым, кто оставит отзыв!
"""
    else:
        examples_text = f"""
⭐ <b>Отзывы наших клиентов</b>

Показано: {len(approved_reviews)} из {len(reviews_db.get_reviews(status='approved'))} отзывов

"""
        
        for i, review in enumerate(approved_reviews, 1):
            stars = "⭐" * review["rating"]
            examples_text += f"""
<b>{i}. {review['name']}</b> {stars}
"""
            if review.get("visa_type"):
                examples_text += f"<i>Визы: {review['visa_type']}</i>\n"
            
            review_text = review["text"]
            if len(review_text) > 200:
                review_text = review_text[:197] + "..."
            
            examples_text += f"{review_text}\n"
            examples_text += "─" * 30 + "\n"
    
    builder = InlineKeyboardBuilder()
    
    if approved_reviews:
        builder.row(
            InlineKeyboardButton(
                text="📝 Оставить отзыв",
                callback_data="reviews_add"
            ),
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="reviews_stats"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔍 Поиск по типу визы",
            callback_data="reviews_search"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к отзывам",
            callback_data="reviews_back"
        )
    )
    
    await callback.message.edit_text(
        text=examples_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "reviews_stats")
async def reviews_stats(callback: CallbackQuery):
    stats = reviews_db.get_statistics()
    
    stats_text = f"""
📊 <b>Статистика отзывов</b>

<b>Общая статистика:</b>
• Всего отзывов: {stats['total']}
• Одобрено: {stats['approved']}
• На модерации: {stats['pending']}
• Отклонено: {stats['rejected']}
• Средняя оценка: <b>{stats['average_rating']}/5</b> ⭐

"""
    
    if stats["visa_types"]:
        stats_text += "<b>Распределение по типам виз:</b>\n"
        for visa_type, count in stats["visa_types"].items():
            percentage = (count / stats["approved"] * 100) if stats["approved"] > 0 else 0
            stats_text += f"• {visa_type}: {count} ({percentage:.1f}%)\n"
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⭐ Читать отзывы",
            callback_data="reviews_examples"
        ),
        InlineKeyboardButton(
            text="📝 Оставить отзыв",
            callback_data="reviews_add"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к отзывам",
            callback_data="reviews_back"
        )
    )
    
    await callback.message.edit_text(
        text=stats_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "reviews_search")
async def reviews_search(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    all_reviews = reviews_db.get_reviews(status="approved")
    visa_types = set()
    
    for review in all_reviews:
        if review.get("visa_type"):
            visa_types.add(review["visa_type"])
    
    visa_types = sorted(list(visa_types))
    
    if not visa_types:
        search_text = """
🔍 <b>Поиск отзывов по типу визы</b>

Пока нет отзывов с указанным типом визы.
"""
    else:
        search_text = """
🔍 <b>Поиск отзывов по типу визы</b>

Выберите тип визы для просмотра отзывов:
"""
        
        for visa_type in visa_types:
            count = len([r for r in all_reviews if r.get("visa_type") == visa_type])
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{visa_type} ({count})",
                    callback_data=f"reviews_filter:{visa_type}"
                )
            )
    
    builder.row(
        InlineKeyboardButton(
            text="⭐ Все отзывы",
            callback_data="reviews_examples"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к отзывам",
            callback_data="reviews_back"
        )
    )
    
    await callback.message.edit_text(
        text=search_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("reviews_filter:"))
async def reviews_filter(callback: CallbackQuery):
    visa_type = callback.data.split(":")[1]
    
    filtered_reviews = reviews_db.get_reviews(status="approved", visa_type=visa_type)
    
    if not filtered_reviews:
        filter_text = f"""
🔍 <b>Отзывы для визы: {visa_type}</b>

Пока нет отзывов для этого типа визы.
"""
    else:
        filter_text = f"""
🔍 <b>Отзывы для визы: {visa_type}</b>

Найдено: {len(filtered_reviews)} отзывов

"""
        
        for i, review in enumerate(filtered_reviews, 1):
            stars = "⭐" * review["rating"]
            filter_text += f"""
<b>{i}. {review['name']}</b> {stars}
"""
            
            review_text = review["text"]
            if len(review_text) > 150:
                review_text = review_text[:147] + "..."
            
            filter_text += f"{review_text}\n"
            filter_text += "─" * 30 + "\n"
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔍 Другие категории",
            callback_data="reviews_search"
        ),
        InlineKeyboardButton(
            text="⭐ Все отзывы",
            callback_data="reviews_examples"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к отзывам",
            callback_data="reviews_back"
        )
    )
    
    await callback.message.edit_text(
        text=filter_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "reviews_cases")
async def reviews_cases(callback: CallbackQuery):
    cases_text = """
📊 <b>Подробные кейсы успеха</b>

<b>Кейс 1: Молодой ученый с ограниченными публикациями</b>
• <b>Профиль:</b> PhD в биоинформатике, 3 года опыта
• <b>Проблема:</b> Всего 5 публикаций, 30 цитирований
• <b>Решение:</b> Акцент на рецензировании (15+ работ), рекомендации от нобелевских лауреатов, доказательство влияния на область через патенты
• <b>Результат:</b> EB-1A одобрен за 3 месяца без RFE

<b>Кейс 2: Артист без формального образования</b>
• <b>Профиль:</b> Музыкант, самоучка, 10 лет карьеры
• <b>Проблема:</b> Нет диплома, мало документации
• <b>Решение:</b> Сбор медиа-упоминаний (50+), призы с международных конкурсов, рекомендации от известных музыкантов, видео-портфолио
• <b>Результат:</b> O-1 виза одобрена, сейчас на гастролях в США

<b>Кейс 3: IT-специалист без научных публикаций</b>
• <b>Профиль:</b> Senior разработчик, 8 лет опыта
• <b>Проблема:</b> Нет академического бэкграунда
• <b>Решение:</b> Доказательство национального интереса через open-source проекты (10k+ stars на GitHub), рекомендации от CTO крупных компаний, доказательство экономического impact
• <b>Результат:</b> NIW одобрен, получил грин-карту через 8 месяцев

<b>Кейс 4: Врач из страны с ограниченными ресурсами</b>
• <b>Профиль:</b> Хирург, 15 лет опыта
• <b>Проблема:</b> Публикации в локальных журналах
• <b>Решение:</b> Доказательство уникальных методик, спасшие жизни в сложных условиях, рекомендации от международных медицинских ассоциаций
• <b>Результат:</b> EB-1A одобрен как 'лицо с исключительными способностями в медицине'

<b>Кейс 5: Предприниматель в нишевой области</b>
• <b>Профиль:</b> Основатель стартапа в агротехнологиях
• <b>Проблема:</b> Бизнес не приносил прибыль первые 3 года
• <b>Решение:</b> Доказательство инновационности через патенты, гранты от правительственных программ, признание в профессиональном сообществе
• <b>Результат:</b> EB-1A одобрен как 'выдающийся предприниматель'

<b>Наш подход:</b>
1. Глубокий анализ сильных сторон
2. Стратегический выбор критериев
3. Качественная подготовка каждого документа
4. Постоянная коммуникация с клиентом
"""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📞 Обсудить мой кейс",
            callback_data="reviews_consult"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к отзывам",
            callback_data="reviews_back"
        )
    )
    
    await callback.message.edit_text(
        text=cases_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "reviews_consult")
async def reviews_consult(callback: CallbackQuery):
    from config import PR_SPECIALIST_USERNAME
    telegram_username = PR_SPECIALIST_USERNAME if PR_SPECIALIST_USERNAME and PR_SPECIALIST_USERNAME != "@username_specialist" else "visa_expert"
    telegram_username = telegram_username.replace('@', '')
    
    consult_text = """
📞 <b>Обсудить мой кейс</b>

Хотите обсудить вашу ситуацию с учетом нашего опыта?

<b>Что мы предлагаем:</b>
• Бесплатная первичная консультация (30 мин)
• Анализ вашего профиля
• Рекомендации по стратегии
• Предварительная оценка шансов

<b>Как подготовиться к консультации:</b>
1. Подготовьте краткое резюме (1-2 страницы)
2. Список публикаций, наград, достижений
3. Информацию об образовании и опыте работы
4. Конкретные вопросы, которые вас волнуют

<b>Контакты для записи:</b>
• Telegram: @visa_expert
• Email: consult@visasuccess.com
• Телефон: +1 (123) 456-7890

<b>Наши специалисты:</b>
• Юристы с 10+ лет опыта в иммиграционном праве
• Эксперты по научным и творческим визам
• Носители русского и английского языков

<b>Первые шаги к успеху начинаются здесь!</b>
"""
    
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Записаться на консультацию",
            url=f"https://t.me/{telegram_username}?text=Хочу обсудить мой кейс"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к кейсам",
            callback_data="reviews_cases"
        )
    )
    
    await callback.message.edit_text(
        text=consult_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "reviews_back")
async def reviews_back(callback: CallbackQuery):
    await reviews_handler(callback.message)
    await callback.answer()

@router.callback_query(F.data == "reviews_back_to_menu")
async def reviews_back_to_menu(callback: CallbackQuery):
    from handlers.start import get_main_keyboard
    
    welcome_text = """
🤖 <b>Добро пожаловать!</b>

Я — бот-ассистент компании <b>VisaSuccess</b>. 
Помогу вам с предварительной оценкой шансов на получение виз.

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