from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from monitor.models import Section, Equipment, ProblemType, UserProfile


class Command(BaseCommand):
    help = 'Заполнить начальные данные (участки, оборудование, типы проблем, пользователей)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание начальных данных...')

        # === Участки ===
        sections_data = [
            {'name': 'Лазерная резка', 'description': 'Участок лазерной резки металла'},
            {'name': 'Гибка', 'description': 'Участок гибки металла'},
            {'name': 'Сварка', 'description': 'Участок сварочных работ'},
            {'name': 'Сборка (1 конвейер)', 'description': 'Сборочный конвейер 1'},
            {'name': 'Сборка (2 конвейер)', 'description': 'Сборочный конвейер 2'},
            {'name': 'Сборка (Вытяжки и подставки)', 'description': 'Сборка вытяжек и подставок'},
            {'name': 'Сборка (16/20 уровней)', 'description': 'Сборка шкафов 16/20 уровней'},
            {'name': 'Сборка (Двери)', 'description': 'Сборка дверей'},
            {'name': 'Сборка (Системы самоочистки)', 'description': 'Сборка систем самоочистки'},
            {'name': 'Цех №1', 'description': 'Основной производственный цех'},
            {'name': 'Цех №2', 'description': 'Цех сборки'},
            {'name': 'Склад сырья', 'description': 'Склад сырья и материалов'},
            {'name': 'Склад готовой продукции', 'description': 'Склад готовой продукции'},
            {'name': 'Компрессорная', 'description': 'Компрессорная станция'},
            {'name': 'Электрощитовая', 'description': 'Главная электрощитовая'},
        ]

        sections = {}
        for s in sections_data:
            obj, created = Section.objects.get_or_create(name=s['name'])
            sections[s['name']] = obj
            if created:
                self.stdout.write(f'  + Участок: {obj.name}')

        # === Оборудование ===
        equipment_data = {
            'Лазерная резка': [
                ('Prima Power Platino 1530', 'LP-001'),
                ('TokaGama Mark TG-GL-1530-150вт-R', 'LP-002'),
                ('Компрессор REMEZA', 'KO-001'),
            ],
            'Гибка': [
                ('Гибочный пресс 1', 'ГП-001'),
                ('Гибочный станок CNC', 'ГС-001'),
            ],
            'Сварка': [
                ('Сварочный аппарат 1', 'СВ-001'),
                ('Сварочный робот', 'СР-001'),
            ],
            'Сборка (1 конвейер)': [
                ('Конвейер сборки 1', 'СК1-001'),
            ],
            'Сборка (2 конвейер)': [
                ('Конвейер сборки 2', 'СК2-001'),
            ],
            'Сборка (Вытяжки и подставки)': [
                ('Линия вытяжек', 'ВТ-001'),
            ],
            'Сборка (16/20 уровней)': [
                ('Линия шкафов 16/20', 'ШК-001'),
            ],
            'Сборка (Двери)': [
                ('Линия дверей', 'ДВ-001'),
            ],
            'Сборка (Системы самоочистки)': [
                ('Линия самоочистки', 'СО-001'),
            ],
            'Цех №1': [
                ('Токарный станок 1', 'ТК-001'),
                ('Фрезерный станок 1', 'ФР-001'),
                ('Пресс гидравлический', 'ПР-001'),
                ('Конвейер линии 1', 'КН-001'),
            ],
            'Цех №2': [
                ('Сборочная линия 1', 'СЛ-001'),
                ('Сборочная линия 2', 'СЛ-002'),
                ('Упаковочный автомат', 'УА-001'),
            ],
            'Склад сырья': [
                ('Кран мостовой', 'КМ-001'),
                ('Тельфер 1', 'ТЛ-001'),
            ],
            'Склад готовой продукции': [
                ('Кран мостовой 2', 'КМ-002'),
                ('Штабелёр', 'ШТ-001'),
            ],
            'Компрессорная': [
                ('Компрессор 1', 'КВ-001'),
                ('Компрессор 2', 'КВ-002'),
                ('Сушилка воздушная', 'СВ-001'),
            ],
            'Электрощитовая': [
                ('Трансформатор 1', 'ТР-001'),
                ('Щит распределительный', 'ЩР-001'),
            ],
        }

        equipment_count = 0
        for section_name, items in equipment_data.items():
            section = sections[section_name]
            for name, inv_num in items:
                _, created = Equipment.objects.get_or_create(
                    name=name,
                    section=section
                )
                if created:
                    equipment_count += 1

        if equipment_count:
            self.stdout.write(f'  + Оборудование: {equipment_count} ед.')

        # === Типы проблем ===
        problem_types = [
            ('Проблемы с резкой/качеством', 'Проблемы с качеством реза, заусенцы, неточность'),
            ('Неисправность лазерной головы', 'Загрязнение, повреждение, калибровка'),
            ('Проблемы с ЧПУ', 'Ошибки программы, сбой контроллера'),
            ('Перегрев', 'Перегрев лазера, охлаждения'),
            ('Падение давления', 'Низкое давление воздуха'),
            ('Утечка воздуха', 'Утечки в системе пневматики'),
            ('Не запускается', 'Не запускается компрессор'),
            ('Перегрев двигателя', 'Перегрев двигателя компрессора'),
            ('Проблемы с осушителем', 'Неисправность осушителя воздуха'),
            ('Механическая неисправность', 'Износ, поломка деталей, вибрация, люфт'),
            ('Электрическая неисправность', 'Проблемы с проводкой, автоматами, датчиками'),
            ('Плановое ТО', 'Регулярное техническое обслуживание'),
            ('Гидравлика/пневматика', 'Утечки, падение давления'),
            ('Программное обеспечение', 'Ошибка ПО, сбой контроллера'),
            ('Другое', 'Иная причина'),
        ]

        for name, _ in problem_types:
            _, created = ProblemType.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'  + Тип проблемы: {name}')

        # === Пользователи ===
        users_data = [
            # username, password, role, email
            ('AGR', 'SASHa1', 'manager', 'a.grishin169@gmail.com'),
            ('admin', 'admin123', 'manager', 'admin@company.com'),
            ('ivanov', 'user123', 'user', 'ivanov@company.com'),
            ('petrov', 'user123', 'user', 'petrov@company.com'),
        ]

        for username, password, role, email in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                )
                UserProfile.objects.create(user=user, role=role)
                self.stdout.write(f'  + Пользователь: {username} ({role}) / пароль: {password}')

        self.stdout.write(self.style.SUCCESS('\nГотово!'))
        self.stdout.write(self.style.WARNING('\nДанные для входа:'))
        self.stdout.write('  Админ: AGR / SASHa1 (email: a.grishin169@gmail.com)')
        self.stdout.write('  Руководитель: admin / admin123')
        self.stdout.write('  Пользователь: ivanov / user123')
