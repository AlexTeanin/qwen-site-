import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equipment_monitor.settings')
django.setup()

from django.conf import settings
from monitor.models import Section, Equipment, ProblemType

def run_update():
    print("🚀 Начинаем обновление проекта...")

    # 1. Добавляем участки
    sections_list = [
        "Лазерная резка", "Гибка", "Сварка", "Сборка (1 конвейер)",
        "Сборка (2 конвейер)", "Сборка (Вытяжки и подставки)",
        "Сборка (16/20 уровней)", "Сборка (Двери)", "Сборка (Системы самоочистки)"
    ]
    
    sections_map = {}
    for name in sections_list:
        s, created = Section.objects.get_or_create(name=name)
        if created:
            print(f"✅ Участок добавлен: {name}")
        sections_map[name] = s

    # 2. Добавляем оборудование для Лазерной резки
    laser_section = sections_map["Лазерная резка"]
    equipment_list = [
        "Prima Power Platino 1530",
        "TokaGama Mark TG-GL-1530-150вт-R",
        "Компрессор REMEZA"
    ]
    
    for eq_name in equipment_list:
        eq, created = Equipment.objects.get_or_create(name=eq_name, section=laser_section)
        if created:
            print(f"✅ Оборудование добавлено: {eq_name}")

    # 3. Добавляем типы проблем
    problems = [
        # Для лазера
        "Пробой линзы", "Загрязнение оптики", "Сбой фокусировки", 
        "Неисправность ЧПУ", "Падение давления газа", "Обрыв кабеля",
        # Для компрессора
        "Утечка воздуха", "Перегрев компрессора", "Низкое давление в сети",
        "Шум/Вибрация", "Ошибка контроллера", "Загрязнение фильтра",
        # Общие
        "Механическая поломка", "Требуется настройка", "Отсутствие питания",
        "Программная ошибка", "Износ расходников"
    ]
    
    for p_name in problems:
        p, created = ProblemType.objects.get_or_create(name=p_name)
        if created:
            print(f"✅ Тип проблемы добавлен: {p_name}")

    print("\n🎉 База данных успешно обновлена!")
    print("Теперь нужно обновить код моделей и форм.")

if __name__ == '__main__':
    run_update()