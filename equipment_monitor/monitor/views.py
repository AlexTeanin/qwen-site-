from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import os
from .models import Section, Equipment, ProblemType, Report, UserProfile, ChecklistTemplate, ChecklistItem, DailyChecklist, ChecklistResult, Favorite, EmailSettings, BackupLog
from .forms import ReportForm

def is_manager(user):
    try:
        return hasattr(user, 'profile') and user.profile.role == 'manager'
    except (UserProfile.DoesNotExist, AttributeError):
        return False

def get_email_settings():
    email_settings = EmailSettings.objects.filter(is_active=True).first()
    if email_settings:
        return {
            'EMAIL_HOST': email_settings.email_host,
            'EMAIL_PORT': email_settings.email_port,
            'EMAIL_USE_TLS': email_settings.email_use_tls,
            'EMAIL_HOST_USER': email_settings.email_host_user,
            'EMAIL_HOST_PASSWORD': email_settings.email_host_password,
            'ADMIN_EMAIL': email_settings.admin_email,
        }
    return None

def send_report_notification(report):
    try:
        email_settings = get_email_settings()
        if not email_settings:
            return
        old_settings = {}
        for key, value in email_settings.items():
            old_settings[key] = getattr(settings, key, None)
            setattr(settings, key, value)
        subject = f"Неисправность: {report.equipment.name} - {report.problem_type.name}"
        message = f"Новый отчёт о неисправности\n\nОборудование: {report.equipment.name}\nУчасток: {report.equipment.section.name}\nТип проблемы: {report.problem_type.name}\nОписание: {report.description}\nНачало простоя: {report.downtime_start}\nСоздал: {report.created_by.username if report.created_by else 'Пользователь'}\nДата: {report.created_at}\n\nПросмотр: http://localhost:8000/reports/{report.id}/"
        email = EmailMessage(subject, message, email_settings['EMAIL_HOST_USER'], [email_settings['ADMIN_EMAIL']])
        if report.photo and os.path.exists(report.photo.path):
            max_size = 10 * 1024 * 1024
            if os.path.getsize(report.photo.path) <= max_size:
                email.attach_file(report.photo.path)
        email.send(fail_silently=True)
        for key, value in old_settings.items():
            if value is not None:
                setattr(settings, key, value)
    except Exception:
        pass

@login_required
def home(request):
    context = {'sections': Section.objects.all()}
    today = timezone.now().date()
    user_checklists = DailyChecklist.objects.filter(user=request.user, date=today)
    context['today_checklists'] = user_checklists
    favorites = Favorite.objects.filter(user=request.user)
    context['favorite_equipment'] = [f.equipment for f in favorites if f.content_type == 'equipment' and f.equipment]
    context['favorite_checklists'] = [f.checklist_template for f in favorites if f.content_type == 'checklist' and f.checklist_template]
    if is_manager(request.user):
        reports = Report.objects.select_related('equipment', 'problem_type').all()[:50]
        context['reports'] = reports
        context['is_manager'] = True
        context['new_count'] = reports.filter(status='new').count()
        context['in_progress_count'] = reports.filter(status='in_progress').count()
    else:
        reports = Report.objects.filter(created_by=request.user).select_related('equipment', 'problem_type')[:20]
        context['reports'] = reports
        context['is_manager'] = False
    return render(request, 'monitor/home.html', context)

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            send_report_notification(report)
            messages.success(request, 'Отчёт успешно создан!')
            return redirect('home')
        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
    else:
        form = ReportForm()
    context = {'form': form, 'sections': Section.objects.all()}
    return render(request, 'monitor/create_report.html', context)

@login_required
def reports_list(request):
    reports = Report.objects.select_related('equipment', 'problem_type', 'created_by').all()
    status = request.GET.get('status')
    section = request.GET.get('section')
    if status:
        reports = reports.filter(status=status)
    if section:
        reports = reports.filter(equipment__section_id=section)
    return render(request, 'monitor/reports_list.html', {'reports': reports, 'sections': Section.objects.all()})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, 'monitor/report_detail.html', {'report': report})

@login_required
@require_http_methods(["POST"])
def update_report_status(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    new_status = request.POST.get('status')
    if new_status and new_status in dict(Report._meta.get_field('status').choices):
        report.status = new_status
        if new_status == 'resolved':
            report.resolved_at = timezone.now()
            report.resolved_by = request.user
        report.save()
        messages.success(request, f'Статус изменён на "{report.get_status_display()}"')
    return redirect('report_detail', report_id=report.id)

@require_http_methods(["GET"])
@login_required
def api_equipment(request):
    section_id = request.GET.get('section_id')
    if section_id:
        equipment = Equipment.objects.filter(section_id=section_id, is_active=True).values('id', 'name')
    else:
        equipment = Equipment.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse(list(equipment), safe=False)

@login_required
def checklists(request):
    user = request.user
    today = timezone.now().date()
    if is_manager(user):
        templates = ChecklistTemplate.objects.filter(is_active=True).select_related('section')
    else:
        user_profile = getattr(user, 'profile', None)
        if user_profile and user_profile.section:
            templates = ChecklistTemplate.objects.filter(section=user_profile.section, is_active=True).select_related('section')
        else:
            templates = ChecklistTemplate.objects.none()
    today_checklists = DailyChecklist.objects.filter(user=user, date=today).select_related('template')
    today_checklist_ids = [c.template_id for c in today_checklists]
    available_templates = [t for t in templates if t.id not in today_checklist_ids]
    context = {'templates': templates, 'today_checklists': today_checklists, 'available_templates': available_templates}
    return render(request, 'monitor/checklists.html', context)

@login_required
def start_checklist(request, template_id):
    template = get_object_or_404(ChecklistTemplate, id=template_id, is_active=True)
    today = timezone.now().date()
    existing = DailyChecklist.objects.filter(user=request.user, template=template, date=today).first()
    if existing:
        messages.info(request, 'Вы уже начали этот чек-лист сегодня')
        return redirect('checklist_detail', checklist_id=existing.id)
    daily_checklist = DailyChecklist.objects.create(user=request.user, section=template.section, template=template, date=today, status='red')
    items = ChecklistItem.objects.filter(template=template, is_active=True).order_by('order')
    for item in items:
        ChecklistResult.objects.create(daily_checklist=daily_checklist, item=item)
    update_checklist_status(daily_checklist)
    return redirect('checklist_detail', checklist_id=daily_checklist.id)

@login_required
def checklist_detail(request, checklist_id):
    daily_checklist = get_object_or_404(DailyChecklist, id=checklist_id, user=request.user)
    if request.method == 'POST':
        result_ids = request.POST.getlist('results')
        all_completed = True
        any_completed = False
        for result in daily_checklist.results.all():
            if str(result.id) in result_ids:
                if not result.is_completed:
                    result.is_completed = True
                    result.completed_at = timezone.now()
                    result.save()
                any_completed = True
            else:
                result.is_completed = False
                result.completed_at = None
                result.save()
                all_completed = False
        update_checklist_status(daily_checklist)
        if all_completed:
            daily_checklist.completed_at = timezone.now()
            daily_checklist.save()
            messages.success(request, 'Чек-лист полностью выполнен!')
        elif any_completed:
            messages.info(request, 'Чек-лист частично выполнен')
        else:
            messages.warning(request, 'Ни один пункт не отмечен')
        return redirect('checklist_detail', checklist_id=daily_checklist.id)
    context = {'daily_checklist': daily_checklist, 'items': daily_checklist.results.select_related('item').order_by('item__order')}
    return render(request, 'monitor/checklist_detail.html', context)

def update_checklist_status(daily_checklist):
    total = daily_checklist.results.count()
    if total == 0:
        daily_checklist.status = 'red'
        return
    completed = daily_checklist.results.filter(is_completed=True).count()
    if completed == 0:
        daily_checklist.status = 'red'
    elif completed == total:
        daily_checklist.status = 'green'
        daily_checklist.completed_at = timezone.now()
    else:
        daily_checklist.status = 'yellow'
    daily_checklist.save()

@login_required
def checklist_history(request):
    user = request.user
    days_to_show = 90
    cutoff_date = timezone.now().date() - timedelta(days=days_to_show)
    checklists = DailyChecklist.objects.filter(user=user, date__gte=cutoff_date).select_related('template', 'section').order_by('-date')
    context = {'checklists': checklists, 'days_to_show': days_to_show}
    return render(request, 'monitor/checklist_history.html', context)

@login_required
def toggle_favorite(request, content_type, object_id):
    user = request.user
    if content_type == 'equipment':
        obj = get_object_or_404(Equipment, id=object_id)
        favorite, created = Favorite.objects.get_or_create(user=user, content_type='equipment', equipment=obj)
        if not created:
            favorite.delete()
            messages.success(request, f'Оборудование "{obj.name}" удалено из избранного')
        else:
            messages.success(request, f'Оборудование "{obj.name}" добавлено в избранное')
    elif content_type == 'checklist':
        obj = get_object_or_404(ChecklistTemplate, id=object_id)
        favorite, created = Favorite.objects.get_or_create(user=user, content_type='checklist', checklist_template=obj)
        if not created:
            favorite.delete()
            messages.success(request, f'Чек-лист "{obj.name}" удалён из избранного')
        else:
            messages.success(request, f'Чек-лист "{obj.name}" добавлен в избранное')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def favorites(request):
    user = request.user
    favorites_qs = Favorite.objects.filter(user=user).select_related('equipment', 'checklist_template')
    favorite_equipment = [f.equipment for f in favorites_qs if f.content_type == 'equipment' and f.equipment]
    favorite_checklists = [f.checklist_template for f in favorites_qs if f.content_type == 'checklist' and f.checklist_template]
    context = {'favorite_equipment': favorite_equipment, 'favorite_checklists': favorite_checklists}
    return render(request, 'monitor/favorites.html', context)

@login_required
def settings_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ только для администраторов')
        return redirect('home')
    email_settings = EmailSettings.objects.first()
    if request.method == 'POST':
        if not email_settings:
            email_settings = EmailSettings()
        email_settings.email_host = request.POST.get('email_host', 'smtp.gmail.com')
        email_settings.email_port = int(request.POST.get('email_port', 587))
        email_settings.email_use_tls = request.POST.get('email_use_tls') == 'on'
        email_settings.email_host_user = request.POST.get('email_host_user', '')
        if request.POST.get('email_host_password'):
            email_settings.email_host_password = request.POST.get('email_host_password')
        email_settings.admin_email = request.POST.get('admin_email', '')
        email_settings.is_active = request.POST.get('is_active') == 'on'
        email_settings.save()
        messages.success(request, 'Настройки сохранены')
        return redirect('settings')
    context = {'email_settings': email_settings}
    return render(request, 'monitor/settings.html', context)

@login_required
def backup_now(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ только для администраторов')
        return redirect('home')
    import zipfile
    from datetime import datetime
    backup_dir = r'\\f12\exchange\Production\data base'
    project_dir = settings.BASE_DIR
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        if not os.path.exists(backup_dir):
            backup_dir = os.path.join(project_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, backup_filename)
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            db_path = os.path.join(project_dir, 'db', 'db.sqlite3')
            if os.path.exists(db_path):
                zipf.write(db_path, 'db/db.sqlite3')
            media_path = os.path.join(project_dir, 'media')
            if os.path.exists(media_path):
                for root, dirs, files in os.walk(media_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_dir)
                        zipf.write(file_path, arcname)
        BackupLog.objects.create(backup_path=backup_path, backup_type='full', status='success')
        messages.success(request, f'Бэкап успешно создан: {backup_path}')
    except Exception as e:
        BackupLog.objects.create(backup_path='', backup_type='full', status='failed', error_message=str(e))
        messages.error(request, f'Ошибка создания бэкапа: {str(e)}')
    return redirect('settings')

@login_required
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'monitor/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
