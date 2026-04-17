from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/update_status/', views.update_report_status, name='update_report_status'),
    path('api/equipment/', views.api_equipment, name='api_equipment'),
    
    # Чек-листы
    path('checklists/', views.checklists, name='checklists'),
    path('checklists/start/<int:template_id>/', views.start_checklist, name='start_checklist'),
    path('checklists/<int:checklist_id>/', views.checklist_detail, name='checklist_detail'),
    path('checklists/history/', views.checklist_history, name='checklist_history'),
    
    # Избранное
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/<str:content_type>/<int:object_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # Настройки
    path('settings/', views.settings_view, name='settings'),
    path('settings/backup/', views.backup_now, name='backup_now'),
]
