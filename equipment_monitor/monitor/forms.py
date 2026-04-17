from django import forms
from .models import Report, ProblemType, ChecklistTemplate, ChecklistItem, DailyChecklist, ChecklistResult

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        # Оставлены только существующие поля модели
        fields = ['equipment', 'problem_type', 'downtime_start', 'description', 'photo']
        widgets = {
            'downtime_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'problem_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сортировка выпадающих списков
        self.fields['equipment'].queryset = self.fields['equipment'].queryset.order_by('section__name', 'name')
        self.fields['problem_type'].queryset = ProblemType.objects.filter(is_active=True).order_by('name')
        
        # Добавляем подписи для полей
        self.fields['equipment'].label = "Оборудование"
        self.fields['problem_type'].label = "Тип проблемы"
        self.fields['downtime_start'].label = "Время начала простоя"
        self.fields['description'].label = "Описание"
        self.fields['photo'].label = "Фотография проблемы"

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = DailyChecklist
        fields = []

class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = None  # Будет установлено динамически
        fields = ['email_host', 'email_port', 'email_use_tls', 'email_host_user', 'email_host_password', 'admin_email', 'is_active']
        widgets = {
            'email_host': forms.TextInput(attrs={'class': 'form-control'}),
            'email_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'email_use_tls': forms.CheckboxInput(),
            'email_host_user': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_host_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'admin_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }
