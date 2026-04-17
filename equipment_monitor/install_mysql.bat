@echo off
echo ============================================
echo  Установка MySQL Server
echo ============================================
echo.
echo MySQL можно установить несколькими способами:
echo.
echo 1. MySQL Installer (рекомендуется)
echo    Скачайте с: https://dev.mysql.com/downloads/installer/
echo    Выберите "mysql-installer-community"
echo.
echo 2. XAMPP (проще, включает MySQL + phpMyAdmin)
echo    Скачайте с: https://www.apachefriends.org/
echo.
echo 3. MariaDB (совместимая замена MySQL)
echo    Скачайте с: https://mariadb.org/download/
echo.
echo После установки MySQL:
echo   1. Создайте базу данных:
echo      CREATE DATABASE equipment_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo.
echo   2. В файле settings.py укажите пароль MySQL:
echo      'PASSWORD': 'ваш_пароль',
echo.
echo   3. Запустите setup.bat, затем run_server.bat
echo.
pause
