@echo off
echo ============================================
echo  Установка зависимостей для Equipment Monitor
echo ============================================
echo.

echo [1/3] Создание виртуального окружения...
py -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/3] Установка Python пакетов...
py -m pip install -r requirements.txt

echo.
echo [3/3] Готово!
echo.
echo Далее выполните:
echo   1. Убедитесь, что MySQL запущен
echo   2. Создайте БД: CREATE DATABASE equipment_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo   3. setup.bat (настройка Django)
echo   4. run_server.bat (запуск сервера)
echo.
pause
