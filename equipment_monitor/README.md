# Мониторинг оборудования

Система учёта неисправностей и ТО оборудования.

## Быстрый старт

### 1. Установите зависимости

```
install.bat
```

### 2. Создайте базу данных MySQL

```sql
CREATE DATABASE equipment_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Настройте подключение к БД

Откройте `equipment_monitor/settings.py` и укажите параметры MySQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'equipment_monitor',
        'USER': 'root',       # ваш пользователь MySQL
        'PASSWORD': 'your_password',  # ваш пароль MySQL
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Примените миграции и заполните данными

```
setup.bat
```

### 5. Запустите сервер

```
run_server.bat
```

Откройте браузер: `http://localhost:8000`

## Данные для входа

| Роль | Логин | Пароль |
|------|-------|--------|
| Руководитель | admin | admin123 |
| Пользователь | ivanov | user123 |

## Доступ с телефона

Сервер запускается на `0.0.0.0:8000`, поэтому с телефона подключайтесь по:
`http://ВАШ_IP_АДРЕС:8000`

Узнайте IP командой: `ipconfig`

## Настройка email уведомлений

В `settings.py` измените:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
ADMIN_EMAIL = 'admin@company.com'
```

## Функционал

- **Авторизация** — логин + пароль (хеширование Django)
- **Создание отчёта** — выбор участка → оборудование → тип проблемы → критичность → комментарий
- **Уведомления** — email руководителю при создании отчёта
- **Дашборд руководителя** — все отчёты, статистика, управление статусами
- **Фильтрация** — по участку, статусу, критичности
- **Адаптивный дизайн** — работает на телефоне

## Структура

```
equipment_monitor/
├── equipment_monitor/   # Django проект
│   └── settings.py      # Настройки
├── monitor/             # Приложение
│   ├── models.py        # Модели (Section, Equipment, Report...)
│   ├── views.py         # Представления
│   ├── forms.py         # Формы
│   └── management/      # Команды (seed_data)
├── templates/monitor/   # HTML шаблоны
├── db/                  # Папка для файлов БД (если SQLite)
├── install.bat          # Установка зависимостей
├── setup.bat            # Настройка Django
└── run_server.bat       # Запуск сервера
```
