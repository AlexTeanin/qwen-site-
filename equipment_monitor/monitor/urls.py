from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-report/', views.create_report, name='create_report'),
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/update-status/', views.update_report_status, name='update_report_status'),
    path('api/equipment/', views.api_equipment, name='api_equipment'),
]
