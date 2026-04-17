from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Этот импорт обязателен!
from datetime import timedelta

class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'
        ordering = ['name']

class ProblemType(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип проблемы'
        verbose_name_plural = 'Типы проблем'

class Equipment(models.Model):
    name = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='equipment_list')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.section.name})"

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('manager', 'Руководитель'), ('user', 'Пользователь')])
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class ChecklistTemplate(models.Model):
    """Шаблон чек-листа для участка"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='checklist_templates', verbose_name="Участок")
    name = models.CharField(max_length=200, verbose_name="Название чек-листа")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return f"{self.name} ({self.section.name})"
    
    class Meta:
        verbose_name = 'Шаблон чек-листа'
        verbose_name_plural = 'Шаблоны чек-листов'
        ordering = ['section__name', 'name']

class ChecklistItem(models.Model):
    """Пункт шаблона чек-листа"""
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name='items', verbose_name="Шаблон")
    text = models.TextField(verbose_name="Текст пункта")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    def __str__(self):
        return f"{self.template.name} - {self.text[:50]}"
    
    class Meta:
        verbose_name = 'Пункт чек-листа'
        verbose_name_plural = 'Пункты чек-листов'
        ordering = ['template', 'order']

class DailyChecklist(models.Model):
    """Ежедневный чек-лист пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="Участок")
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, verbose_name="Шаблон")
    date = models.DateField(default=timezone.now, verbose_name="Дата")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
    
    # Статус: green - все выполнено, yellow - частично, red - не выполнено
    status = models.CharField(max_length=10, choices=[
        ('green', 'Выполнен'),
        ('yellow', 'Частично выполнен'),
        ('red', 'Не выполнен')
    ], default='red', verbose_name="Статус")
    
    class Meta:
        verbose_name = 'Ежедневный чек-лист'
        verbose_name_plural = 'Ежедневные чек-листы'
        unique_together = ['user', 'template', 'date']
        ordering = ['-date', 'section__name']

class ChecklistResult(models.Model):
    """Результат выполнения пункта чек-листа"""
    daily_checklist = models.ForeignKey(DailyChecklist, on_delete=models.CASCADE, related_name='results', verbose_name="Чек-лист")
    item = models.ForeignKey(ChecklistItem, on_delete=models.CASCADE, verbose_name="Пункт")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнен")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время выполнения")
    
    class Meta:
        verbose_name = 'Результат пункта'
        verbose_name_plural = 'Результаты пунктов'
        unique_together = ['daily_checklist', 'item']

class Favorite(models.Model):
    """Избранное: оборудование и чек-листы"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    content_type = models.CharField(max_length=20, choices=[
        ('equipment', 'Оборудование'),
        ('checklist', 'Чек-лист')
    ], verbose_name="Тип")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Оборудование")
    checklist_template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Чек-лист")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    
    def __str__(self):
        if self.content_type == 'equipment' and self.equipment:
            return f"{self.user.username} - {self.equipment.name}"
        elif self.content_type == 'checklist' and self.checklist_template:
            return f"{self.user.username} - {self.checklist_template.name}"
        return f"{self.user.username} - избранное"
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'content_type', 'equipment', 'checklist_template']

class EmailSettings(models.Model):
    """Настройки email для отправки уведомлений"""
    email_host = models.CharField(max_length=100, default='smtp.gmail.com', verbose_name="SMTP сервер")
    email_port = models.IntegerField(default=587, verbose_name="Порт")
    email_use_tls = models.BooleanField(default=True, verbose_name="Использовать TLS")
    email_host_user = models.EmailField(verbose_name="Логин email")
    email_host_password = models.CharField(max_length=100, verbose_name="Пароль приложения")
    admin_email = models.EmailField(verbose_name="Email получателя")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    def __str__(self):
        return f"Настройки email: {self.email_host_user}"
    
    class Meta:
        verbose_name = 'Настройки email'
        verbose_name_plural = 'Настройки email'

class BackupLog(models.Model):
    """Лог бэкапов"""
    backup_path = models.CharField(max_length=500, verbose_name="Путь к бэкапу")
    backup_type = models.CharField(max_length=20, choices=[
        ('database', 'База данных'),
        ('files', 'Файлы'),
        ('full', 'Полный')
    ], verbose_name="Тип бэкапа")
    status = models.CharField(max_length=20, choices=[
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
        ('in_progress', 'В процессе')
    ], default='in_progress', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    error_message = models.TextField(blank=True, verbose_name="Ошибка")
    
    class Meta:
        verbose_name = 'Лог бэкапа'
        verbose_name_plural = 'Логи бэкапов'
        ordering = ['-created_at']

class Report(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="Оборудование")
    problem_type = models.ForeignKey(ProblemType, on_delete=models.CASCADE, verbose_name="Тип проблемы")
    description = models.TextField(verbose_name="Описание проблемы", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания отчёта")

    # Новые поля
    downtime_start = models.DateTimeField(verbose_name="Время начала простоя", default=timezone.now)
    photo = models.ImageField(upload_to='reports_photos/', null=True, blank=True, verbose_name="Фото проблемы", 
                              max_length=500)  # Увеличили max_length для пути

    status = models.CharField(max_length=20, choices=[
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решено')
    ], default='new', verbose_name="Статус")

    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Время устранения")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_reports', verbose_name="Создал")

    def __str__(self):
        return f"Отчёт #{self.id} - {self.equipment.name}"

    class Meta:
        verbose_name = 'Отчёт о проблеме'
        verbose_name_plural = 'Отчёты о проблемах'
        ordering = ['-created_at']
