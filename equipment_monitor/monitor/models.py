from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Этот импорт обязателен!

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

class Report(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="Оборудование")
    problem_type = models.ForeignKey(ProblemType, on_delete=models.CASCADE, verbose_name="Тип проблемы")
    description = models.TextField(verbose_name="Описание проблемы", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания отчёта")

    # Новые поля
    downtime_start = models.DateTimeField(verbose_name="Время начала простоя", default=timezone.now)
    photo = models.ImageField(upload_to='reports_photos/', null=True, blank=True, verbose_name="Фото проблемы")

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