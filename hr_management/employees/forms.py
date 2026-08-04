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
            'faculty', 'ranking'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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

        # Thêm placeholder cho các trường mới
        self.fields['graduation_year'].widget.attrs.update({'placeholder': 'Ví dụ: 2020'})
        self.fields['graduation_place'].widget.attrs.update({'placeholder': 'Ví dụ: Đại học Quốc gia Hà Nội'})
        self.fields['faculty'].widget.attrs.update({'placeholder': 'Ví dụ: Khoa Ngoại ngữ'})
        self.fields['ranking'].widget.attrs.update({'placeholder': 'Ví dụ: Giỏi, Khá, Trung bình'})


    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number') or None
        if id_number:
            exists = Employee.objects.filter(id_number=id_number)
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise forms.ValidationError("So CMND/CCCD da ton tai.")
        return id_number

    def clean_email(self):
        email = self.cleaned_data.get('email') or None
        if email:
            exists = Employee.objects.filter(email__iexact=email)
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise forms.ValidationError("Email da duoc su dung cho nhan vien khac.")
        return email


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'contract_name', 'contract_type',
            'department', 'position', 'work_form',
            'sign_date', 'start_date', 'end_date',
            'salary_type', 'basic_salary', 'insurance_salary', 'file', 'is_active'
        ]
        labels = {
            'salary_type': _('Loại lương'),
            'basic_salary': _('Mức lương / Đơn giá tính lương'),
            'insurance_salary': _('Lương đóng bảo hiểm'),
            'file': _('File hợp đồng'),
            'work_form': _('Hình thức làm việc'),
        }
        widgets = {
            'sign_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_number': forms.TextInput(attrs={'placeholder': 'HD0000001'}),
            'contract_name': forms.TextInput(attrs={'placeholder': 'Hợp đồng lao động'}),
            'basic_salary': forms.NumberInput(attrs={'placeholder': '0', 'step': '1000'}),
            'insurance_salary': forms.NumberInput(attrs={'placeholder': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['basic_salary'].required = False
        self._sync_salary_requirement()

    def _sync_salary_requirement(self):
        salary_type = self.data.get('salary_type') or getattr(self.instance, 'salary_type', 'monthly')
        salary_type = salary_type or 'monthly'
        requires_amount = salary_type in {'monthly', 'daily', 'shift', 'hourly'}
        self.fields['basic_salary'].required = requires_amount

    def clean(self):
        cleaned_data = super().clean()
        salary_type = cleaned_data.get('salary_type') or 'monthly'
        basic_salary = cleaned_data.get('basic_salary')
        if salary_type in {'monthly', 'daily', 'shift', 'hourly'} and not basic_salary:
            self.add_error('basic_salary', 'Vui lòng nhập mức lương/đơn giá tính lương.')
        return cleaned_data


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
        choices=[('', 'Tất cả')] + list(Contract.CONTRACT_TYPES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        required=False,
        queryset=Department.objects.filter(is_active=True),
        empty_label='Tất cả',
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
            ('', 'Tất cả'),
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
