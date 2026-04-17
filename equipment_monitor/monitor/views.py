from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Section, Equipment, ProblemType, Report, UserProfile
from .forms import ReportForm

def is_manager(user):
    """Проверка, является ли пользователь руководителем"""
    try:
        return hasattr(user, 'profile') and user.profile.role == 'manager'
    except (UserProfile.DoesNotExist, AttributeError):
        return False


def send_report_notification(report):
    """Отправка email уведомления о новом отчёте"""
    try:
        subject = f"Неисправность: {report.equipment.name} - {report.problem_type.name}"
        message = (
            f"Новый отчёт о неисправности\n\n"
            f"Оборудование: {report.equipment.name}\n"
            f"Участок: {report.equipment.section.name}\n"
            f"Тип проблемы: {report.problem_type.name}\n"
            f"Описание: {report.description}\n"
            f"Начало простоя: {report.downtime_start}\n"
            f"Создал: {report.created_by.username if hasattr(report, 'created_by') and report.created_by else 'Пользователь'}\n"
            f"Дата: {report.created_at}\n\n"
            f"Просмотр: http://localhost:8000/reports/{report.id}/"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass  # Тихо игнорируем ошибки email


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный логин или пароль')

    return render(request, 'monitor/login.html')


def logout_view(request):
    """Выход"""
    logout(request)
    return redirect('login')


@login_required
def home(request):
    """Главная страница"""
    if is_manager(request.user):
        # Руководитель видит все отчёты
        reports = Report.objects.select_related('equipment', 'problem_type').all()[:50]
        context = {
            'reports': reports,
            'is_manager': True,
            'new_count': reports.filter(status='new').count(),
            'in_progress_count': reports.filter(status='in_progress').count(),
        }
    else:
        # Пользователь видит свои отчёты
        reports = Report.objects.filter(created_by=request.user).select_related('equipment', 'problem_type')[:20]
        context = {
            'reports': reports,
            'is_manager': False,
        }

    context['sections'] = Section.objects.all()
    return render(request, 'monitor/home.html', context)


@login_required
def create_report(request):
    """Создание отчёта о неисправности"""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user  # Добавляем создателя
            report.save()

            # Отправляем уведомление руководителю
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
    """Список всех отчётов"""
    reports = Report.objects.select_related('equipment', 'problem_type', 'created_by').all()

    # Фильтры
    status = request.GET.get('status')
    severity = request.GET.get('severity')
    section = request.GET.get('section')

    if status:
        reports = reports.filter(status=status)
    if severity:
        reports = reports.filter(severity=severity)
    if section:
        reports = reports.filter(equipment__section_id=section)

    return render(request, 'monitor/reports_list.html', {
        'reports': reports,
        'sections': Section.objects.all(),
    })


@login_required
def report_detail(request, report_id):
    """Детали отчёта"""
    report = get_object_or_404(Report, id=report_id)
    return render(request, 'monitor/report_detail.html', {'report': report})


@login_required
@require_http_methods(["POST"])
def update_report_status(request, report_id):
    """Обновление статуса отчёта"""
    report = get_object_or_404(Report, id=report_id)
    new_status = request.POST.get('status')

    if new_status and new_status in dict(Report.STATUS_CHOICES):
        report.status = new_status
        report.save()
        messages.success(request, f'Статус изменён на "{report.get_status_display()}"')

    return redirect('report_detail', report_id=report.id)


@require_http_methods(["GET"])
@login_required
def api_equipment(request):
    """API: получить оборудование по участку"""
    section_id = request.GET.get('section_id')
    if section_id:
        equipment = Equipment.objects.filter(section_id=section_id).values('id', 'name')
    else:
        equipment = Equipment.objects.all().values('id', 'name')
    return JsonResponse(list(equipment), safe=False)
