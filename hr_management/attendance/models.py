from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models

from employees.models import Employee, Position


class WorkShift(models.Model):
    """Reusable shift template for operational staff."""

    code = models.CharField(max_length=20, verbose_name="Mã ca")
    name = models.CharField(max_length=100, verbose_name="Tên ca làm việc")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu ca")
    check_in_start = models.TimeField(verbose_name="Chấm vào - Từ")
    check_in_end = models.TimeField(verbose_name="Chấm vào - Đến")
    end_time = models.TimeField(verbose_name="Giờ kết thúc ca")
    check_out_start = models.TimeField(verbose_name="Chấm ra - Từ")
    check_out_end = models.TimeField(verbose_name="Chấm ra - Đến")
    has_break = models.BooleanField(default=False, verbose_name="Có nghỉ giữa ca")
    break_minutes = models.PositiveIntegerField(default=0, verbose_name="Số phút nghỉ giữa ca")
    work_hours = models.FloatField(default=0, verbose_name="Giờ công")
    work_days = models.FloatField(default=1, verbose_name="Ngày công")
    normal_day_coefficient = models.FloatField(default=1, verbose_name="Hệ số ngày thường")
    rest_day_coefficient = models.FloatField(default=2, verbose_name="Hệ số ngày nghỉ")
    holiday_coefficient = models.FloatField(default=3, verbose_name="Hệ số ngày lễ")
    deduct_if_no_check_in = models.BooleanField(default=False, verbose_name="Trừ công nếu không có giờ vào")
    deduct_if_no_check_out = models.BooleanField(default=False, verbose_name="Trừ công nếu không có giờ ra")
    apply_to_all = models.BooleanField(default=False, verbose_name="Toàn đơn vị")
    employees = models.ManyToManyField(
        'employees.Employee',
        blank=True,
        verbose_name="Danh sách nhân viên"
    )

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

    class Meta:
        verbose_name = "Ca làm việc"
        verbose_name_plural = "Ca làm việc"


class EmployeeSchedule(models.Model):
    """Legacy roster model kept for old data."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_schedules',
        verbose_name="Nhân viên"
    )
    date = models.DateField(verbose_name="Ngày làm việc")
    work_shift = models.ForeignKey(
        WorkShift,
        on_delete=models.CASCADE,
        related_name='employee_schedules',
        verbose_name="Ca làm việc"
    )
    expected_work_days = models.FloatField(default=1, verbose_name="Số công dự kiến")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.work_shift.code}"

    class Meta:
        verbose_name = "Lịch làm việc cũ"
        verbose_name_plural = "Lịch làm việc cũ"
        ordering = ['-date', 'employee__code']
        unique_together = ('employee', 'date', 'work_shift')


class StaffSchedule(models.Model):
    """Operational staff roster: one employee, one date, one work shift."""

    STATUS_CHOICES = (
        ('planned', 'Đã xếp lịch'),
        ('cancelled', 'Đã hủy'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='staff_schedules',
        verbose_name="Nhân viên"
    )
    date = models.DateField(verbose_name="Ngày làm việc")
    work_shift = models.ForeignKey(
        WorkShift,
        on_delete=models.CASCADE,
        related_name='staff_schedules',
        verbose_name="Ca làm việc"
    )
    expected_work_days = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1,
        verbose_name="Công dự kiến"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Trạng thái")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.work_shift.code}"

    class Meta:
        verbose_name = "Lịch ca nhân viên vận hành"
        verbose_name_plural = "Lịch ca nhân viên vận hành"
        ordering = ['-date', 'employee__code']
        unique_together = ('employee', 'date', 'work_shift')


class Course(models.Model):
    """Class/course that owns recurring or one-off teaching sessions."""

    code = models.CharField(max_length=30, unique=True, verbose_name="Mã lớp/khóa học")
    name = models.CharField(max_length=200, verbose_name="Tên lớp/khóa học")
    level = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cấp độ")
    start_date = models.DateField(blank=True, null=True, verbose_name="Ngày bắt đầu")
    end_date = models.DateField(blank=True, null=True, verbose_name="Ngày kết thúc")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Lớp/Khóa học"
        verbose_name_plural = "Lớp/Khóa học"
        ordering = ['code']


class ClassSession(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Đã xếp lịch'),
        ('completed', 'Đã dạy'),
        ('cancelled', 'Đã hủy'),
        ('makeup', 'Dạy bù'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions', verbose_name="Lớp/Khóa học")
    date = models.DateField(verbose_name="Ngày học")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu")
    end_time = models.TimeField(verbose_name="Giờ kết thúc")
    room = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phòng học")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Trạng thái")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def planned_hours(self):
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        if end_minutes < start_minutes:
            end_minutes += 24 * 60
        return round((end_minutes - start_minutes) / 60, 2)

    def __str__(self):
        return f"{self.course.code} - {self.date} {self.start_time}-{self.end_time}"

    class Meta:
        verbose_name = "Buổi học"
        verbose_name_plural = "Buổi học"
        ordering = ['-date', 'start_time']


class TeacherAssignment(models.Model):
    ROLE_CHOICES = (
        ('teacher', 'Giáo viên'),
        ('assistant', 'Trợ giảng'),
        ('substitute', 'Dạy thay'),
    )

    class_session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Buổi học"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        verbose_name="Nhân sự"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher', verbose_name="Vai trò")
    expected_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Giờ dự kiến")
    pay_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1, verbose_name="Hệ số tính lương")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.expected_hours and self.class_session_id:
            self.expected_hours = self.class_session.planned_hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.class_session} - {self.role}"

    class Meta:
        verbose_name = "Phân công giảng dạy"
        verbose_name_plural = "Phân công giảng dạy"
        unique_together = ('class_session', 'employee', 'role')


class SessionAttendance(models.Model):
    STATUS_CHOICES = (
        ('taught', 'Đã dạy'),
        ('absent_excused', 'Nghỉ có phép'),
        ('absent_unexcused', 'Nghỉ không phép'),
        ('substituted', 'Có người dạy thay'),
        ('cancelled_by_center', 'Lớp hủy bởi trung tâm'),
        ('cancelled_by_teacher', 'Giáo viên hủy'),
        ('online', 'Dạy online'),
        ('makeup', 'Dạy bù'),
    )

    assignment = models.OneToOneField(
        TeacherAssignment,
        on_delete=models.CASCADE,
        related_name='attendance',
        verbose_name="Phân công"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='taught', verbose_name="Trạng thái")
    actual_start_time = models.TimeField(blank=True, null=True, verbose_name="Giờ bắt đầu thực tế")
    actual_end_time = models.TimeField(blank=True, null=True, verbose_name="Giờ kết thúc thực tế")
    paid_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Giờ tính lương")
    approved = models.BooleanField(default=False, verbose_name="Đã duyệt")
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.paid_hours and self.assignment_id and self.status in {'taught', 'online', 'makeup'}:
            self.paid_hours = self.assignment.expected_hours * self.assignment.pay_multiplier
        super().save(*args, **kwargs)

    @property
    def employee(self):
        return self.assignment.employee

    @property
    def class_session(self):
        return self.assignment.class_session

    def __str__(self):
        return f"{self.assignment.employee.full_name} - {self.assignment.class_session.date} - {self.status}"

    class Meta:
        verbose_name = "Chấm công buổi dạy"
        verbose_name_plural = "Chấm công buổi dạy"


class AttendanceRecord(models.Model):
    """Legacy detailed attendance sheet, hidden from the new user workflow."""

    ATTENDANCE_TYPE_CHOICES = (
        ('shift', 'Theo ca'),
        ('daily', 'Theo ngày'),
    )

    name = models.CharField(max_length=200, verbose_name="Tên bảng chấm công")
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES, verbose_name="Hình thức chấm công")
    positions = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Vị trí áp dụng")
    apply_to_all_shifts = models.BooleanField(default=False, verbose_name="Chọn tất cả ca")
    work_shifts = models.ManyToManyField(WorkShift, blank=True, verbose_name="Ca làm việc")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bảng chấm công chi tiết cũ"
        verbose_name_plural = "Bảng chấm công chi tiết cũ"
        ordering = ['-start_date']


class DailyAttendance(models.Model):
    """Attendance log for operational staff; legacy AttendanceRecord is optional."""

    ATTENDANCE_STATUS_CHOICES = (
        ('not_absent', 'Không nghỉ'),
        ('permitted_absence', 'Nghỉ có phép'),
        ('unpermitted_absence', 'Nghỉ không phép'),
        ('regime_absence', 'Nghỉ theo chế độ'),
    )

    attendance_record = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.CASCADE,
        related_name='daily_attendances',
        null=True,
        blank=True,
        verbose_name="Bảng chấm công cũ"
    )
    schedule = models.ForeignKey(
        EmployeeSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_attendances',
        verbose_name="Lịch làm việc cũ"
    )
    staff_schedule = models.ForeignKey(
        StaffSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_attendances',
        verbose_name="Lịch ca nhân viên"
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")
    date = models.DateField(verbose_name="Ngày chấm công")
    paid_work_days = models.FloatField(default=1, verbose_name="Số công hưởng lương")
    actual_work_days = models.FloatField(default=1, verbose_name="Số công đi làm thực tế")
    check_in_time = models.TimeField(null=True, blank=True, verbose_name="Giờ vào")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="Giờ ra")
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default='not_absent', verbose_name="Trạng thái nghỉ")
    work_shift = models.ForeignKey(WorkShift, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ca làm việc")

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    class Meta:
        verbose_name = "Chấm công nhân viên vận hành"
        verbose_name_plural = "Chấm công nhân viên vận hành"
        unique_together = ('attendance_record', 'employee', 'date')


class AttendanceSummary(models.Model):
    """Legacy summary sheet kept for old payroll records."""

    month = models.IntegerField(verbose_name="Tháng", default=1)
    year = models.IntegerField(verbose_name="Năm", default=2025)
    name = models.CharField(max_length=200, verbose_name="Tên bảng chấm công tổng hợp")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Vị trí áp dụng")
    attendance_records = models.ManyToManyField('AttendanceRecord', verbose_name="Danh sách bảng chấm công chi tiết")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField(default=False, verbose_name="Đã chuyển tính lương")
    standard_workdays = models.DecimalField(max_digits=5, decimal_places=2, default=24, verbose_name="Số công chuẩn")
    start_date = models.DateField(null=True, blank=True, verbose_name="Ngày bắt đầu")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bảng chấm công tổng hợp cũ"
        verbose_name_plural = "Bảng chấm công tổng hợp cũ"
        ordering = ['-created_at']

    @property
    def date_range(self):
        if self.start_date and self.end_date:
            return f"{self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"

        records = self.attendance_records.all()
        if records:
            start_date = min(record.start_date for record in records)
            end_date = max(record.end_date for record in records)
            return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        return "N/A"


class EmployeeAttendance(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, verbose_name="Nhân viên")
    attendance_summary = models.ForeignKey(
        AttendanceSummary,
        on_delete=models.CASCADE,
        related_name='employee_attendances',
        verbose_name="Bảng chấm công tổng hợp cũ"
    )
    workdays = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Số công làm việc")
    paid_leave = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Nghỉ có lương")
    unpaid_leave = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Nghỉ không lương")
    policy_leave = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Nghỉ chế độ")
    late_early_minutes = models.IntegerField(default=0, verbose_name="Đi muộn/về sớm (phút)")

    class Meta:
        verbose_name = "Chấm công nhân viên cũ"
        verbose_name_plural = "Chấm công nhân viên cũ"
        unique_together = ('employee', 'attendance_summary')

    @property
    def total_workdays(self):
        return self.workdays + self.paid_leave + self.policy_leave

    @property
    def total_paid_days(self):
        return self.workdays + self.paid_leave + self.policy_leave


class MonthlyTimesheet(models.Model):
    TIMESHEET_TYPE_CHOICES = (
        ('operations', 'Nhân viên vận hành'),
        ('teaching', 'Giáo viên/Trợ giảng'),
    )
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('locked', 'Đã khóa'),
        ('transferred', 'Đã chuyển lương'),
    )

    month = models.IntegerField(verbose_name="Tháng")
    year = models.IntegerField(verbose_name="Năm")
    name = models.CharField(max_length=200, verbose_name="Tên bảng công tháng")
    timesheet_type = models.CharField(
        max_length=20,
        choices=TIMESHEET_TYPE_CHOICES,
        default='operations',
        verbose_name="Loại bảng công"
    )
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Vị trí")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Trạng thái")
    transferred = models.BooleanField(default=False, verbose_name="Đã chuyển tính lương")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locked_at = models.DateTimeField(blank=True, null=True)
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='locked_timesheets'
    )

    @property
    def start_date(self):
        from datetime import date
        return date(self.year, self.month, 1)

    @property
    def end_date(self):
        next_month = (self.start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        return next_month - timedelta(days=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bảng công tháng"
        verbose_name_plural = "Bảng công tháng"
        ordering = ['-year', '-month', 'position__code']
        unique_together = ('month', 'year', 'position', 'timesheet_type')


class TimesheetApproval(models.Model):
    ACTION_CHOICES = (
        ('reviewed', 'Đã rà soát'),
        ('approved', 'Đã duyệt'),
        ('locked', 'Đã khóa'),
        ('reopened', 'Mở khóa'),
    )

    monthly_timesheet = models.ForeignKey(
        MonthlyTimesheet,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name="Bảng công tháng"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Hành động")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lịch sử duyệt bảng công"
        verbose_name_plural = "Lịch sử duyệt bảng công"
        ordering = ['-created_at']


class AttendanceAdjustment(models.Model):
    ADJUSTMENT_TYPES = (
        ('workday', 'Điều chỉnh ngày công'),
        ('hour', 'Điều chỉnh giờ dạy/làm'),
        ('paid_leave', 'Điều chỉnh nghỉ có lương'),
        ('unpaid_leave', 'Điều chỉnh nghỉ không lương'),
        ('note', 'Ghi chú'),
    )

    monthly_timesheet = models.ForeignKey(
        MonthlyTimesheet,
        on_delete=models.CASCADE,
        related_name='adjustments',
        verbose_name="Bảng công tháng"
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES, verbose_name="Loại điều chỉnh")
    value = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Giá trị")
    reason = models.TextField(verbose_name="Lý do")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Điều chỉnh công"
        verbose_name_plural = "Điều chỉnh công"
        ordering = ['-created_at']
