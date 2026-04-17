from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Section, Equipment, ProblemType, Report, UserProfile, ChecklistTemplate, ChecklistItem, DailyChecklist, ChecklistResult, Favorite, EmailSettings, BackupLog

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    actions = ['delete_selected']
    list_editable = ['name']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'section', 'is_active']
    list_filter = ['section', 'is_active']
    search_fields = ['name']
    list_editable = ['name', 'is_active']
    actions = ['delete_selected']

@admin.register(ProblemType)
class ProblemTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['name', 'is_active']
    actions = ['delete_selected']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'section']
    list_filter = ['role', 'section']
    search_fields = ['user__username']

@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'section', 'is_active', 'created_at']
    list_filter = ['section', 'is_active']
    search_fields = ['name']
    list_editable = ['name', 'is_active']
    filter_horizontal = []  # Можно добавить если будут ManyToMany поля

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'template', 'text', 'order', 'is_active']
    list_filter = ['template', 'is_active']
    search_fields = ['text']
    list_editable = ['text', 'order', 'is_active']

@admin.register(DailyChecklist)
class DailyChecklistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'section', 'template', 'date', 'status', 'created_at']
    list_filter = ['status', 'date', 'section']
    search_fields = ['user__username', 'template__name']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(ChecklistResult)
class ChecklistResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'daily_checklist', 'item', 'is_completed', 'completed_at']
    list_filter = ['is_completed']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'content_type', 'get_favorite_name', 'added_at']
    list_filter = ['content_type', 'user']
    
    def get_favorite_name(self, obj):
        if obj.content_type == 'equipment' and obj.equipment:
            return obj.equipment.name
        elif obj.content_type == 'checklist' and obj.checklist_template:
            return obj.checklist_template.name
        return '-'
    get_favorite_name.short_description = 'Название'

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'email_host_user', 'admin_email', 'email_host', 'email_port', 'is_active', 'updated_at']
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        # Разрешаем создать только одну запись настроек
        return not EmailSettings.objects.exists()

@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'backup_path', 'backup_type', 'status', 'created_at', 'error_message']
    list_filter = ['backup_type', 'status']
    readonly_fields = ['created_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment', 'problem_type', 'status', 'downtime_start', 'created_at', 'created_by']
    list_filter = ['status', 'problem_type', 'equipment__section']
    search_fields = ['description', 'equipment__name']
    readonly_fields = ['created_at', 'resolved_at', 'resolved_by', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # При создании
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
