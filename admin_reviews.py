import json
from utils.database import reviews_db

def admin_menu():
    while True:
        print("\n" + "="*50)
        print("📋 АДМИН-ПАНЕЛЬ ДЛЯ УПРАВЛЕНИЯ ОТЗЫВАМИ")
        print("="*50)
        print("1. 📊 Показать статистику")
        print("2. ⏳ Показать отзывы на модерации")
        print("3. ✅ Одобрить отзыв")
        print("4. ❌ Отклонить отзыв")
        print("5. 📝 Показать все отзывы")
        print("6. 🗑️ Удалить отзыв")
        print("7. 📄 Экспорт отзывов в JSON")
        print("8. 🔄 Инициализировать примеры отзывов")
        print("0. 🔙 Выход")
        print("="*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            show_statistics()
        elif choice == "2":
            show_pending_reviews()
        elif choice == "3":
            approve_review()
        elif choice == "4":
            reject_review()
        elif choice == "5":
            show_all_reviews()
        elif choice == "6":
            delete_review()
        elif choice == "7":
            export_reviews()
        elif choice == "8":
            init_default_reviews()
        elif choice == "0":
            print("Выход из админ-панели.")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

def show_statistics():
    stats = reviews_db.get_statistics()
    
    print("\n📊 СТАТИСТИКА ОТЗЫВОВ")
    print("-" * 30)
    print(f"Всего отзывов: {stats['total']}")
    print(f"Одобрено: {stats['approved']}")
    print(f"На модерации: {stats['pending']}")
    print(f"Отклонено: {stats['rejected']}")
    print(f"Средняя оценка: {stats['average_rating']}/5 ⭐")
    
    if stats['visa_types']:
        print("\n📋 Распределение по типам виз:")
        for visa_type, count in stats['visa_types'].items():
            print(f"  • {visa_type}: {count}")

def show_pending_reviews():
    pending_reviews = reviews_db.get_reviews(status="pending")
    
    if not pending_reviews:
        print("\n✅ Нет отзывов на модерации.")
        return
    
    print(f"\n⏳ ОТЗЫВЫ НА МОДЕРАЦИИ ({len(pending_reviews)})")
    print("-" * 50)
    
    for review in pending_reviews:
        print(f"\nID: #{review['id']}")
        print(f"Имя: {review['name']}")
        print(f"Оценка: {'⭐' * review['rating']} ({review['rating']}/5)")
        if review.get('visa_type'):
            print(f"Тип визы: {review['visa_type']}")
        if review.get('username'):
            print(f"Telegram: @{review['username']}")
        print(f"Дата: {review['created_at'][:10]}")
        print(f"Текст: {review['text'][:100]}...")
        print("-" * 30)

def approve_review():
    try:
        review_id = int(input("Введите ID отзыва для одобрения: "))
    except ValueError:
        print("❌ Неверный ID.")
        return
    
    review = reviews_db.get_review(review_id)
    
    if not review:
        print(f"❌ Отзыв с ID #{review_id} не найден.")
        return
    
    if review['status'] == 'approved':
        print("✅ Этот отзыв уже одобрен.")
        return
    
    if reviews_db.update_review_status(review_id, "approved"):
        print(f"✅ Отзыв #{review_id} успешно одобрен!")
    else:
        print(f"❌ Ошибка при одобрении отзыва #{review_id}.")

def reject_review():
    try:
        review_id = int(input("Введите ID отзыва для отклонения: "))
    except ValueError:
        print("❌ Неверный ID.")
        return
    
    review = reviews_db.get_review(review_id)
    
    if not review:
        print(f"❌ Отзыв с ID #{review_id} не найден.")
        return
    
    if review['status'] == 'rejected':
        print("❌ Этот отзыв уже отклонен.")
        return
    
    if reviews_db.update_review_status(review_id, "rejected"):
        print(f"✅ Отзыв #{review_id} отклонен.")
    else:
        print(f"❌ Ошибка при отклонении отзыва #{review_id}.")

def show_all_reviews():
    all_reviews = reviews_db.get_reviews(status="approved", limit=None)
    pending = reviews_db.get_reviews(status="pending", limit=None)
    rejected = reviews_db.get_reviews(status="rejected", limit=None)
    
    print(f"\n📝 ВСЕ ОТЗЫВЫ")
    print(f"Одобрено: {len(all_reviews)} | На модерации: {len(pending)} | Отклонено: {len(rejected)}")
    print("-" * 50)
    
    status_map = {"approved": "✅", "pending": "⏳", "rejected": "❌"}
    
    for review in all_reviews + pending + rejected:
        status_icon = status_map.get(review['status'], '❓')
        print(f"\n{status_icon} ID: #{review['id']} | {review['name']} | {'⭐' * review['rating']}")
        print(f"  Статус: {review['status']} | Дата: {review['created_at'][:10]}")
        if review.get('visa_type'):
            print(f"  Визы: {review['visa_type']}")
        print(f"  Текст: {review['text'][:80]}...")

def delete_review():
    try:
        review_id = int(input("Введите ID отзыва для удаления: "))
    except ValueError:
        print("❌ Неверный ID.")
        return
    
    review = reviews_db.get_review(review_id)
    
    if not review:
        print(f"❌ Отзыв с ID #{review_id} не найден.")
        return
    
    confirm = input(f"Вы уверены что хотите удалить отзыв #{review_id} от {review['name']}? (да/нет): ").lower()
    
    if confirm == 'да' or confirm == 'д' or confirm == 'y' or confirm == 'yes':
        if reviews_db.delete_review(review_id):
            print(f"✅ Отзыв #{review_id} удален.")
        else:
            print(f"❌ Ошибка при удалении отзыва #{review_id}.")
    else:
        print("❌ Удаление отменено.")

def export_reviews():
    import os
    from datetime import datetime
    
    filename = f"reviews_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open("data/reviews.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Отзывы экспортированы в файл: {filename}")
    print(f"📁 Путь: {os.path.abspath(filename)}")

if __name__ == "__main__":

    admin_menu()
