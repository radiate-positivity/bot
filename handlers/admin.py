from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton 
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.database import reviews_db
from config import ADMIN_ID

router = Router()

async def check_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("moderation"))
async def moderation_list(message: Message):
    if not await check_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    pending_reviews = reviews_db.get_reviews(status="pending")
    
    if not pending_reviews:
        await message.answer("✅ Нет отзывов на модерации.")
        return
    
    text = f"📋 <b>Отзывы на модерации:</b> {len(pending_reviews)} шт.\n\n"
    
    builder = InlineKeyboardBuilder()
    
    for review in pending_reviews[:10]:
        stars = "⭐" * review["rating"]
        text += f"<b>#{review['id']}</b> - {review['name']} {stars}\n"
        text += f"<i>{review['text'][:50]}...</i>\n"
        text += "─" * 30 + "\n"
        
        builder.row(
            InlineKeyboardButton(
                text=f"👁️ #{review['id']}",
                callback_data=f"admin_view:{review['id']}"
            )
        )
    
    if len(pending_reviews) > 10:
        text += f"\n<i>И еще {len(pending_reviews) - 10} отзывов...</i>"
    
    builder.row(
        InlineKeyboardButton(
            text="📊 Статистика",
            callback_data="admin_stats"
        )
    )
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, bot: Bot):
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    action = callback.data
    
    if action.startswith("admin_approve:"):
        review_id = int(action.split(":")[1])
        if reviews_db.update_review_status(review_id, "approved"):
            review = reviews_db.get_review(review_id)
            if review and review.get("user_id"):
                try:
                    await bot.send_message(
                        chat_id=review["user_id"],
                        text=f"✅ Ваш отзыв #{review_id} был одобрен и опубликован!\n\nСпасибо за обратную связь!"
                    )
                except:
                    pass
            
            await callback.answer("✅ Отзыв одобрен")
            await callback.message.edit_text(
                text=f"✅ Отзыв #{review_id} одобрен и опубликован.",
                reply_markup=None
            )
        else:
            await callback.answer("❌ Отзыв не найден", show_alert=True)
    
    elif action.startswith("admin_reject:"):
        review_id = int(action.split(":")[1])
        if reviews_db.update_review_status(review_id, "rejected"):
            review = reviews_db.get_review(review_id)
            if review and review.get("user_id"):
                try:
                    await bot.send_message(
                        chat_id=review["user_id"],
                        text=f"❌ Ваш отзыв #{review_id} был отклонен модератором.\n\nПричина: не соответствует правилам публикации."
                    )
                except:
                    pass
            
            await callback.answer("❌ Отзыв отклонен")
            await callback.message.delete()
        else:
            await callback.answer("❌ Отзыв не найден", show_alert=True)
    
    elif action.startswith("admin_view:"):
        review_id = int(action.split(":")[1])
        review = reviews_db.get_review(review_id)
        
        if not review:
            await callback.answer("❌ Отзыв не найден", show_alert=True)
            return
        
        stars = "⭐" * review["rating"]
        text = f"""
📋 <b>Отзыв #{review_id}</b>

<b>Имя:</b> {review['name']}
<b>Оценка:</b> {stars} ({review['rating']}/5)
<b>Тип визы:</b> {review.get('visa_type', 'Не указан')}
<b>Статус:</b> {review['status']}
<b>Дата:</b> {review['created_at'][:10]}
<b>User ID:</b> {review.get('user_id', 'Не указан')}
<b>Username:</b> @{review.get('username', 'нет')}

<b>Текст отзыва:</b>
{review['text']}
"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="✅ Одобрить",
                callback_data=f"admin_approve:{review_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"admin_reject:{review_id}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin_back"
            )
        )
        
        await callback.message.edit_text(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        await callback.answer()
