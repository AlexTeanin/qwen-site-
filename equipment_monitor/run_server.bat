@echo off
echo ============================================
echo  Запуск сервера Equipment Monitor
echo ============================================
echo.

call venv\Scripts\activate.bat

echo Сервер доступен по адресу: http://localhost:8000
echo Для подключения с других устройств: http://ВАШ_IP:8000
echo.
echo Нажмите Ctrl+C для остановки сервера
echo.

py manage.py runserver 0.0.0.0:8000
