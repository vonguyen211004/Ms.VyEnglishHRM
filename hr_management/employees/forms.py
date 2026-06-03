from django import forms
from .models import Employee, Contract, WorkHistory, SalaryHistory, Department, Position
from django.utils.translation import gettext_lazy as _


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'code', 'first_name', 'last_name', 'gender', 'date_of_birth', 'id_number',
            'phone', 'email', 'address', 'position', 'join_date', 'is_active',
            'education_level', 'degree', 'major', 'graduation_year', 'graduation_place',
            'faculty', 'ranking', 'basic_salary'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '100000'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1950', 'max': '2050'}),
        }
        labels = {
            'code': _('Mã nhân viên'),
            'first_name': _('Tên'),
            'last_name': _('Họ'),
            'gender': _('Giới tính'),
            'date_of_birth': _('Ngày sinh'),
            'id_number': _('Số CMND/CCCD'),
            'phone': _('Số điện thoại'),
            'email': _('Email'),
            'address': _('Địa chỉ'),
            'position': _('Vị trí công việc'),
            'join_date': _('Ngày vào làm'),
            'is_active': _('Đang làm việc'),
            'education_level': _('Trình độ đào tạo'),
            'degree': _('Bằng cấp'),
            'major': _('Chuyên ngành'),
            'graduation_year': _('Năm tốt nghiệp'),
            'graduation_place': _('Nơi đào tạo'),
            'faculty': _('Khoa'),
            'ranking': _('Xếp loại'),
            'basic_salary': _('Lương cơ bản (VNĐ)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm placeholder và các thuộc tính khác
        self.fields['code'].widget.attrs.update({'placeholder': 'Ví dụ: NV001'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Nhập tên'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Nhập họ'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Nhập số điện thoại'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Nhập email'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Nhập địa chỉ'})
        self.fields['id_number'].widget.attrs.update({'placeholder': 'Nhập số CMND/CCCD'})
        self.fields['degree'].widget.attrs.update({'placeholder': 'Ví dụ: Cử nhân Anh ngữ'})
        self.fields['major'].widget.attrs.update({'placeholder': 'Ví dụ: Ngôn ngữ Anh'})
        self.fields['basic_salary'].widget.attrs.update({'placeholder': 'Ví dụ: 10000000'})

        # Thêm placeholder cho các trường mới
        self.fields['graduation_year'].widget.attrs.update({'placeholder': 'Ví dụ: 2020'})
        self.fields['graduation_place'].widget.attrs.update({'placeholder': 'Ví dụ: Đại học Quốc gia Hà Nội'})
        self.fields['faculty'].widget.attrs.update({'placeholder': 'Ví dụ: Khoa Ngoại ngữ'})
        self.fields['ranking'].widget.attrs.update({'placeholder': 'Ví dụ: Giỏi, Khá, Trung bình'})


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'contract_name', 'contract_type',
            'department', 'position', 'work_form',
            'sign_date', 'start_date', 'end_date',
            'basic_salary', 'insurance_salary', 'is_active'
        ]
        widgets = {
            'sign_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_number': forms.TextInput(attrs={'placeholder': 'HD0000001'}),
            'contract_name': forms.TextInput(attrs={'placeholder': 'Hợp đồng lao động'}),
            'basic_salary': forms.NumberInput(attrs={'placeholder': '0'}),
            'insurance_salary': forms.NumberInput(attrs={'placeholder': '0'}),
        }


class ContractFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tìm kiếm theo số hợp đồng, tên nhân viên...',
            'class': 'form-control'
        })
    )
    contract_type = forms.ChoiceField(
        required=False,
        choices=[('', '-- Tất cả loại hợp đồng --')] + list(Contract.CONTRACT_TYPES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        required=False,
        queryset=Department.objects.filter(is_active=True),
        empty_label='-- Tất cả đơn vị --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Từ ngày'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Đến ngày'
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', '-- Tất cả trạng thái --'),
            ('active', 'Đang hiệu lực'),
            ('expiring', 'Sắp hết hạn'),
            ('inactive', 'Hết hiệu lực')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class WorkHistoryForm(forms.ModelForm):
    class Meta:
        model = WorkHistory
        fields = ['company', 'position', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SalaryHistoryForm(forms.ModelForm):
    class Meta:
        model = SalaryHistory
        fields = ['employee', 'effective_date', 'old_salary', 'new_salary', 'reason']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }
