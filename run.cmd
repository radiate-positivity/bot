@echo off
chcp 65001 > nul
echo Запуск Telegram бота
echo.

cd /d "C:\Users\79873\OneDrive\Рабочий стол\ebla_bot"

echo Используем Python Launcher (py.exe)
py --version
echo.

if exist venv (
    echo Виртуальное окружение найдено
    call venv\Scripts\activate.bat
) else (
    echo Создаем виртуальное окружение...
    py -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo Устанавливаем зависимости...
pip install aiogram python-dotenv
echo.

echo Запуск бота...
python main.py

echo.
pause