from datetime import date, datetime, timedelta

from django import forms
from django.db.models import Q

from employees.models import Employee, Position
from .models import (
    AttendanceAdjustment,
    AttendanceRecord,
    AttendanceSummary,
    Course,
    DailyAttendance,
    ClassSession,
    MonthlyTimesheet,
    StaffSchedule,
    WorkShift,
)


WEEKDAY_CHOICES = [
    ('0', 'Thứ 2'),
    ('1', 'Thứ 3'),
    ('2', 'Thứ 4'),
    ('3', 'Thứ 5'),
    ('4', 'Thứ 6'),
    ('5', 'Thứ 7'),
    ('6', 'Chủ nhật'),
]

TEACHER_POSITION_FILTER = (
    Q(position__name__icontains='giảng viên') |
    Q(position__name__icontains='giao vien') |
    Q(position__name__icontains='teacher') |
    Q(position__name__icontains='lecturer') |
    Q(position__name__icontains='instructor') |
    Q(position__code__icontains='GV') |
    Q(contracts__is_active=True, contracts__position__name__icontains='giảng viên') |
    Q(contracts__is_active=True, contracts__position__name__icontains='giao vien') |
    Q(contracts__is_active=True, contracts__position__name__icontains='teacher') |
    Q(contracts__is_active=True, contracts__position__name__icontains='lecturer') |
    Q(contracts__is_active=True, contracts__position__name__icontains='instructor') |
    Q(contracts__is_active=True, contracts__position__code__icontains='GV')
)

ASSISTANT_POSITION_FILTER = (
    Q(position__name__icontains='trợ giảng') |
    Q(position__name__icontains='tro giang') |
    Q(position__name__icontains='assistant') |
    Q(position__name__icontains='teaching assistant') |
    Q(position__code__icontains='TG') |
    Q(contracts__is_active=True, contracts__position__name__icontains='trợ giảng') |
    Q(contracts__is_active=True, contracts__position__name__icontains='tro giang') |
    Q(contracts__is_active=True, contracts__position__name__icontains='assistant') |
    Q(contracts__is_active=True, contracts__position__name__icontains='teaching assistant') |
    Q(contracts__is_active=True, contracts__position__code__icontains='TG')
)


def teaching_employee_queryset(role='teaching'):
    role_filter = TEACHER_POSITION_FILTER
    if role == 'assistant':
        role_filter = ASSISTANT_POSITION_FILTER

    return (
        Employee.objects
        .filter(is_active=True)
        .filter(role_filter)
        .select_related('position')
        .distinct()
        .order_by('code')
    )


class BootstrapFormMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                continue
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault('class', 'form-select')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class WorkShiftForm(BootstrapFormMixin, forms.ModelForm):
    late_grace_minutes = forms.IntegerField(
        label="Cho phép đi muộn (phút)",
        min_value=0,
        initial=5,
        help_text="Số phút sau giờ bắt đầu ca vẫn được tính là đúng giờ.",
    )
    class Meta:
        model = WorkShift
        fields = [
            'name', 'code', 'start_time', 'end_time', 'break_minutes', 'work_hours', 'work_days',
        ]
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'break_minutes': forms.NumberInput(attrs={'step': '5', 'min': '0'}),
            'work_hours': forms.NumberInput(attrs={'step': '0.1', 'readonly': 'readonly'}),
            'work_days': forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_hours'].required = False
        if self.instance and self.instance.pk:
            self.fields['late_grace_minutes'].initial = self._minutes_between(
                self.instance.start_time,
                self.instance.check_in_end,
                default=5,
            )
        self._apply_bootstrap()

    @staticmethod
    def _time_plus_minutes(value, minutes):
        anchor = datetime.combine(date(2000, 1, 1), value)
        return (anchor + timedelta(minutes=int(minutes))).time()

    @staticmethod
    def _time_minus_minutes(value, minutes):
        anchor = datetime.combine(date(2000, 1, 1), value)
        return (anchor - timedelta(minutes=int(minutes))).time()

    @staticmethod
    def _minutes_between(start, end, default=0):
        if not start or not end:
            return default
        start_dt = datetime.combine(date(2000, 1, 1), start)
        end_dt = datetime.combine(date(2000, 1, 1), end)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        return max(0, int((end_dt - start_dt).total_seconds() // 60))

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        break_minutes = cleaned_data.get('break_minutes') or 0

        if start_time and end_time:
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            if end_minutes < start_minutes:
                end_minutes += 24 * 60
            shift_minutes = end_minutes - start_minutes
            if break_minutes >= shift_minutes:
                self.add_error('break_minutes', 'Thời gian nghỉ phải nhỏ hơn thời lượng ca.')
            else:
                cleaned_data['work_hours'] = round((shift_minutes - int(break_minutes)) / 60, 2)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        late_grace = self.cleaned_data.get('late_grace_minutes') or 0

        instance.work_hours = self.cleaned_data.get('work_hours') or 0
        instance.check_in_start = instance.start_time
        instance.check_in_end = self._time_plus_minutes(instance.start_time, late_grace)
        instance.check_out_start = instance.end_time
        instance.check_out_end = instance.end_time

        # Legacy fields are kept in the database but no longer configured per
        # shift in the workflow. Policies should live outside the shift template.
        instance.has_break = bool(instance.break_minutes)
        instance.normal_day_coefficient = 1
        instance.rest_day_coefficient = 2
        instance.holiday_coefficient = 3
        instance.deduct_if_no_check_in = False
        instance.deduct_if_no_check_out = False
        instance.apply_to_all = False

        if commit:
            instance.save()
            instance.employees.clear()
        return instance


class StaffScheduleForm(BootstrapFormMixin, forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True).select_related('position').order_by('code'),
        label="Nhân viên",
    )
    work_shift = forms.ModelChoiceField(
        queryset=WorkShift.objects.all().order_by('code'),
        label="Ca làm",
    )
    start_date = forms.DateField(label="Từ ngày", widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label="Đến ngày", widget=forms.DateInput(attrs={'type': 'date'}))
    weekdays = forms.MultipleChoiceField(
        label="Ngày trong tuần",
        choices=WEEKDAY_CHOICES,
        initial=['0', '1', '2', '3', '4', '5'],
        widget=forms.CheckboxSelectMultiple,
    )
    expected_work_days = forms.DecimalField(
        label="Công dự kiến mỗi ca",
        max_digits=4,
        decimal_places=2,
        initial=1,
        widget=forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '2'}),
    )
    note = forms.CharField(label="Ghi chú", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Ngày bắt đầu không thể sau ngày kết thúc.")
        return cleaned_data


class CourseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'level', 'start_date', 'end_date', 'is_active', 'note']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class ClassSessionForm(BootstrapFormMixin, forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True).order_by('code'),
        label="Lớp/Khóa học",
    )
    teacher = forms.ModelChoiceField(
        queryset=teaching_employee_queryset('teacher'),
        label="Giáo viên",
    )
    assistant = forms.ModelChoiceField(
        queryset=teaching_employee_queryset('assistant'),
        label="Trợ giảng",
        required=False,
    )
    start_date = forms.DateField(label="Từ ngày", widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label="Đến ngày", widget=forms.DateInput(attrs={'type': 'date'}))
    weekdays = forms.MultipleChoiceField(
        label="Ngày trong tuần",
        choices=WEEKDAY_CHOICES,
        initial=['0', '2', '4'],
        widget=forms.CheckboxSelectMultiple,
    )
    start_time = forms.TimeField(label="Giờ bắt đầu", widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(label="Giờ kết thúc", widget=forms.TimeInput(attrs={'type': 'time'}))
    room = forms.CharField(label="Phòng học", required=False)
    expected_hours = forms.DecimalField(
        label="Số giờ tính lương dự kiến",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0,
        max_value=24,
        widget=forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '24'}),
        help_text="Nhập số giờ, ví dụ 1.5 hoặc 2. Không nhập đơn giá tiền lương ở ô này.",
        error_messages={
            'max_value': "Số giờ tính lương không được lớn hơn 24.",
            'min_value': "Số giờ tính lương không được âm.",
        },
    )
    note = forms.CharField(label="Ghi chú", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = teaching_employee_queryset('teacher')
        self.fields['assistant'].queryset = teaching_employee_queryset('assistant')
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Ngày bắt đầu không thể sau ngày kết thúc.")
        if start_time and end_time and start_time == end_time:
            raise forms.ValidationError("Giờ bắt đầu và kết thúc không được trùng nhau.")
        if start_date and end_date:
            selected_weekdays = {int(day) for day in cleaned_data.get('weekdays') or []}
            current_date = start_date
            has_matching_day = False
            while current_date <= end_date:
                if current_date.weekday() in selected_weekdays:
                    has_matching_day = True
                    break
                current_date += timedelta(days=1)
            if selected_weekdays and not has_matching_day:
                self.add_error('weekdays', "Khoảng ngày đã chọn không có ngày nào khớp với thứ trong tuần.")
        return cleaned_data


class DailyAttendanceForm(BootstrapFormMixin, forms.Form):
    attendance_status = forms.ChoiceField(choices=DailyAttendance.ATTENDANCE_STATUS_CHOICES, required=True)
    check_in_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    check_out_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    paid_work_days = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        initial=1,
        required=True,
        widget=forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '2'}),
    )
    actual_work_days = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        initial=1,
        required=True,
        widget=forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '2'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class MonthlyTimesheetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MonthlyTimesheet
        fields = ['month', 'year', 'timesheet_type', 'position', 'name']
        widgets = {
            'month': forms.NumberInput(attrs={'min': '1', 'max': '12'}),
            'year': forms.NumberInput(attrs={'min': '2020', 'max': '2100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['position'].queryset = Position.objects.filter(is_active=True).order_by('code')
        self._apply_bootstrap()


class AttendanceAdjustmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AttendanceAdjustment
        fields = ['employee', 'adjustment_type', 'value', 'reason']
        widgets = {
            'value': forms.NumberInput(attrs={'step': '0.25'}),
            'reason': forms.TextInput(attrs={'placeholder': 'Nhập lý do điều chỉnh'}),
        }

    def __init__(self, *args, **kwargs):
        position = kwargs.pop('position', None)
        super().__init__(*args, **kwargs)
        employees = Employee.objects.filter(is_active=True).order_by('code')
        if position:
            employees = employees.filter(position=position)
        self.fields['employee'].queryset = employees
        self._apply_bootstrap()


# Legacy forms kept so old imports do not break while the UI is moved away from
# AttendanceRecord/AttendanceSummary.
class AttendanceRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['name', 'start_date', 'end_date', 'positions', 'attendance_type', 'apply_to_all_shifts', 'work_shifts']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class AttendanceSummaryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AttendanceSummary
        fields = ['name', 'position', 'attendance_records']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


EmployeeScheduleForm = StaffScheduleForm


class TransferAttendanceForm(forms.Form):
    monthly_timesheet = forms.ModelChoiceField(
        queryset=MonthlyTimesheet.objects.filter(transferred=False).order_by('-year', '-month'),
        label="Bảng công tháng",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
