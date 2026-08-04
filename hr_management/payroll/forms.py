from django import forms
from django.db.models import Q
from attendance.models import MonthlyTimesheet
from .models import Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['name', 'monthly_timesheet', 'status']
        labels = {
            'name': 'Tên bảng lương',
            'monthly_timesheet': 'Bảng công tháng',
            'status': 'Trạng thái',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_timesheet': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filters = Q(status='locked', transferred=False)
        if self.instance and self.instance.pk and self.instance.monthly_timesheet_id:
            filters |= Q(pk=self.instance.monthly_timesheet_id)
        self.fields['monthly_timesheet'].queryset = MonthlyTimesheet.objects.filter(filters).select_related('position').order_by('-year', '-month', 'position__code')
        self.fields['monthly_timesheet'].required = False


class PayrollDetailForm(forms.ModelForm):
    class Meta:
        model = PayrollDetail
        fields = [
            'basic_salary', 'standard_workdays', 'actual_workdays',
            'unpaid_leave',

        ]



class PayrollAllowanceForm(forms.ModelForm):
    class Meta:
        model = PayrollAllowance
        fields = ['name', 'amount', 'is_percentage']

class PayrollDeductionForm(forms.ModelForm):
    class Meta:
        model = PayrollDeduction
        fields = ['name', 'amount', 'is_percentage']
