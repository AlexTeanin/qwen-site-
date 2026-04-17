-- Скрипт создания базы данных
-- Выполните в MySQL:
--   mysql -u root -p < create_db.sql

CREATE DATABASE IF NOT EXISTS equipment_monitor 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON equipment_monitor.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Database equipment_monitor created!' AS Result;
