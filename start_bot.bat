@echo off
echo =================================
echo ЗАПУСК TELEGRAM БОТА
echo =================================
echo.

cd /d "C:\Users\79873\Desktop\eb1a_bot"

if exist venv (
    echo Активируем виртуальное окружение...
    call venv\Scripts\activate.bat
) else (
    echo Создаем виртуальное окружение...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Устанавливаем зависимости...
    pip install aiogram python-dotenv
)

echo.
echo Проверяем наличие токена...
if not exist ".env" (
    echo ОШИБКА: Файл .env не найден!
    echo Создайте файл .env с токеном:
    echo BOT_TOKEN=ВАШ_ТОКЕН
    pause
    exit /b 1
)

echo.
echo Запускаем бота...
echo Если возникнут ошибки, проверьте:
echo 1. Токен в файле .env
echo 2. Файлы main.py и config.py
echo.
echo Для остановки бота нажмите Ctrl+C
echo =================================
echo.

python main.py

echo.
echo Бот остановлен
pause