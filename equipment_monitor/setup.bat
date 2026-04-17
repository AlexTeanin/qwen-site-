@echo off
echo ============================================
echo  Настройка Django проекта
echo ============================================
echo.

call venv\Scripts\activate.bat

echo [1/4] Применение миграций Django...
py manage.py migrate

echo.
echo [2/4] Создание начальных данных...
py manage.py seed_data

echo.
echo [3/4] Сбор статических файлов...
py manage.py collectstatic --noinput

echo.
echo [4/4] Готово!
echo.
echo Для запуска сервера выполните: run_server.bat
echo.
echo Данные для входа:
echo   Руководитель: admin / admin123
echo   Пользователь: ivanov / user123
echo.
pause
