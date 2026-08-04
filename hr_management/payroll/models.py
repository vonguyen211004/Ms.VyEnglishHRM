from django.db import models
from django.utils.translation import gettext_lazy as _
from employees.models import Employee, Position
from attendance.models import AttendanceSummary, MonthlyTimesheet
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User


def current_month():
	return timezone.now().month


def current_year():
	return timezone.now().year


class Payroll(models.Model):
	attendance_summary = models.ForeignKey(
		AttendanceSummary,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='payrolls',
		verbose_name="Bảng chấm công"
	)
	monthly_timesheet = models.ForeignKey(
		MonthlyTimesheet,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='payrolls',
		verbose_name="Bảng công tháng"
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, verbose_name="Tên bảng lương")
	code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã bảng lương")
	# Thêm các trường month và year nếu chưa có
	month = models.IntegerField(verbose_name="Tháng", default=current_month)
	year = models.IntegerField(verbose_name="Năm", default=current_year)
	position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Vị trí")
	status = models.CharField(
		max_length=20,
		choices=[
			('draft', 'Nháp'),
			('processing', 'Đang xử lý'),
			('approved', 'Đã duyệt'),
			('paid', 'Đã thanh toán'),
			('disabled', 'Vô hiệu hóa')
		],
		default='draft',
		verbose_name="Trạng thái"
	)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
	created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_payrolls',
	                               verbose_name="Người tạo")


	class Meta:
		verbose_name = "Bảng lương"
		verbose_name_plural = "Bảng lương"
		ordering = ['-created_at']

	def __str__(self):
		return self.name

	@property
	def source_type_display(self):
		if self.monthly_timesheet_id:
			return self.monthly_timesheet.get_timesheet_type_display()
		return "Bảng lương cũ"


class PayrollDetail(models.Model):
	payroll = models.ForeignKey(
		Payroll,
		on_delete=models.CASCADE,
		related_name='details',
		verbose_name=_("Bảng lương")
	)
	employee = models.ForeignKey(
		Employee,
		on_delete=models.CASCADE,
		verbose_name=_("Nhân viên")
	)
	basic_salary = models.DecimalField(
		_("Lương cơ bản"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	attendance_ratio = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('1.0000'),
	                                       verbose_name="Tỷ lệ hưởng lương")
	standard_workdays = models.FloatField(
		_("Số công chuẩn"),
		default=0.0
	)
	actual_workdays = models.FloatField(
		_("Số công thực tế"),
		default=0.0
	)
	unpaid_leave = models.FloatField(
		_("Số ngày nghỉ không lương"),
		default=0.0
	)
	# Thêm các trường bị thiếu
	reward_amount = models.DecimalField(
		_("Tiền thưởng"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	discipline_amount = models.DecimalField(
		_("Tiền phạt"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	gross_salary = models.DecimalField(
		_("Tổng thu nhập"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	deduction_amount = models.DecimalField(
		_("Tổng khấu trừ"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	net_salary = models.DecimalField(
		_("Thực lĩnh"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	# Thêm trường income_tax nếu chưa có
	income_tax = models.DecimalField(
		_("Thuế TNCN"),
		max_digits=12,
		decimal_places=0,
		default=0
	)
	note = models.TextField(_("Ghi chú"), blank=True, null=True)
	# Thêm trường để lưu thông tin khấu trừ dưới dạng JSON
	deduction_data = models.JSONField(default=dict, blank=True, null=True, verbose_name="Dữ liệu khấu trừ")

	def __str__(self):
		return f"{self.employee.full_name} - {self.payroll.name}"

	class Meta:
		verbose_name = _("Chi tiết lương")
		verbose_name_plural = _("Chi tiết lương")
		unique_together = ('payroll', 'employee')

	def save(self, *args, **kwargs):
		self.net_salary = (
				(self.gross_salary or Decimal('0')) -
				(self.deduction_amount or Decimal('0')) -
				(self.income_tax or Decimal('0')) +
				(self.reward_amount or Decimal('0')) -
				(self.discipline_amount or Decimal('0'))
		)
		super().save(*args, **kwargs)


class PayrollAllowance(models.Model):
	payroll_detail = models.ForeignKey(
		PayrollDetail,
		on_delete=models.CASCADE,
		related_name='allowances',
		verbose_name=_("Chi tiết lương")
	)
	name = models.CharField(_("Tên phụ cấp"), max_length=100)
	amount = models.FloatField(_("Giá trị"), default=0.0)
	is_percentage = models.BooleanField(_("Là phần trăm"), default=False)
	value = models.DecimalField(
		_("Số tiền"),
		max_digits=12,
		decimal_places=0,
		default=0
	)

	def __str__(self):
		return f"{self.name} - {self.payroll_detail.employee.full_name}"

	class Meta:
		verbose_name = _("Phụ cấp")
		verbose_name_plural = _("Phụ cấp")

class PayrollDeduction(models.Model):
    payroll_detail = models.ForeignKey(
        PayrollDetail,
        on_delete=models.CASCADE,
        related_name='deductions',
        verbose_name=_("Chi tiết lương")
    )
    name = models.CharField(_("Tên khấu trừ"), max_length=100)
    amount = models.FloatField(_("Giá trị"), default=0.0)
    is_percentage = models.BooleanField(_("Là phần trăm"), default=False)
    value = models.DecimalField(
        _("Số tiền"),
        max_digits=12,
        decimal_places=0,
        default=0
    )

    def __str__(self):
        return f"{self.name} - {self.payroll_detail.employee.full_name}"

    class Meta:
        verbose_name = _("Khấu trừ lương")
        verbose_name_plural = _("Khấu trừ lương")
