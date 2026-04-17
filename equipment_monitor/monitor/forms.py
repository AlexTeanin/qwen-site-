from django import forms
from .models import Report, ProblemType

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