import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

class ReviewsDatabase:
    def __init__(self, file_path: str = "data/reviews.json"):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "reviews": [],
                    "settings": {
                        "next_id": 1,
                        "last_updated": datetime.now().isoformat()
                    }
                }, f, ensure_ascii=False, indent=2)
    
    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️ Файл {self.file_path} поврежден или не найден. Создаю новый...")
            
            if os.path.exists(self.file_path):
                backup_path = f"{self.file_path}.backup"
                try:
                    shutil.copy2(self.file_path, backup_path)
                    print(f"📁 Создана резервная копия: {backup_path}")
                except:
                    pass
            
            new_data = {
                "reviews": [],
                "settings": {
                    "next_id": 1,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            
            return new_data
        except Exception as e:
            print(f"❌ Неизвестная ошибка при загрузке данных: {e}")
            return {
                "reviews": [],
                "settings": {
                    "next_id": 1,
                    "last_updated": datetime.now().isoformat()
                }
            }
    
    def _save_data(self, data: Dict[str, Any]):
        try:
            data["settings"]["last_updated"] = datetime.now().isoformat()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка при сохранении данных: {e}")
            raise
    
    def add_review(self, 
                   name: str, 
                   text: str, 
                   rating: int, 
                   visa_type: str = "", 
                   status: str = "pending",
                   user_id: Optional[int] = None,
                   username: Optional[str] = None) -> int:
        data = self._load_data()
        
        review_id = data["settings"]["next_id"]
        
        review = {
            "id": review_id,
            "name": name,
            "text": text,
            "rating": rating,
            "visa_type": visa_type,
            "status": status,
            "user_id": user_id,
            "username": username,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        data["reviews"].append(review)
        data["settings"]["next_id"] += 1
        self._save_data(data)
        
        return review_id
    
    def get_reviews(self, 
                    status: str = "approved", 
                    limit: Optional[int] = None,
                    visa_type: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load_data()
        
        reviews = data["reviews"]
        
        filtered_reviews = [r for r in reviews if r["status"] == status]
        
        if visa_type:
            filtered_reviews = [r for r in filtered_reviews if r.get("visa_type") == visa_type]
        
        filtered_reviews.sort(key=lambda x: x["created_at"], reverse=True)
        
        if limit:
            filtered_reviews = filtered_reviews[:limit]
        
        return filtered_reviews
    
    def get_review(self, review_id: int) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        
        for review in data["reviews"]:
            if review["id"] == review_id:
                return review
        
        return None
    
    def update_review_status(self, review_id: int, status: str) -> bool:
        data = self._load_data()
        
        for review in data["reviews"]:
            if review["id"] == review_id:
                review["status"] = status
                review["updated_at"] = datetime.now().isoformat()
                self._save_data(data)
                return True
        
        return False
    
    def delete_review(self, review_id: int) -> bool:
        data = self._load_data()
        
        for i, review in enumerate(data["reviews"]):
            if review["id"] == review_id:
                data["reviews"].pop(i)
                self._save_data(data)
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        data = self._load_data()
        
        total = len(data["reviews"])
        approved = len([r for r in data["reviews"] if r["status"] == "approved"])
        pending = len([r for r in data["reviews"] if r["status"] == "pending"])
        rejected = len([r for r in data["reviews"] if r["status"] == "rejected"])
        
        approved_reviews = [r for r in data["reviews"] if r["status"] == "approved"]
        if approved_reviews:
            avg_rating = sum(r["rating"] for r in approved_reviews) / len(approved_reviews)
        else:
            avg_rating = 0
        
        visa_types = {}
        for review in approved_reviews:
            visa_type = review.get("visa_type", "Не указано")
            if visa_type in visa_types:
                visa_types[visa_type] += 1
            else:
                visa_types[visa_type] = 1
        
        return {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "average_rating": round(avg_rating, 1),
            "visa_types": visa_types
        }

reviews_db = ReviewsDatabase()