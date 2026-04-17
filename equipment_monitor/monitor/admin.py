from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Section, Equipment, ProblemType, Report, UserProfile

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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment', 'problem_type', 'status', 'downtime_start', 'created_at']
    list_filter = ['status', 'problem_type', 'equipment__section']
    search_fields = ['description', 'equipment__name']
    readonly_fields = ['created_at', 'resolved_at', 'resolved_by']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'section']
    list_filter = ['role', 'section']
