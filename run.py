import subprocess
import sys
import os
import time

def main():
    print("Запуск EB-1A бота...")
    
    os.environ['BOT_TOKEN'] = BOT_TOKEN
    
    while True:
        try:
            print(f"Запуск: {time.strftime('%H:%M:%S')}")
            result = subprocess.run([sys.executable, "main.py"])
            
            if result.returncode != 0:
                print("Бот упал. Перезапуск через 5 сек...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\nОстановлено")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()