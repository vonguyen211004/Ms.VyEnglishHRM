from django.db import models
import datetime
from django.utils import timezone  # Thêm import này
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from decimal import Decimal


# Phòng ban
class Department(models.Model):
    code = models.CharField("Mã phòng ban", max_length=20, unique=True) 
    # verbose_name="Mã phòng ban": hiển thị trong Django Admin hoặc Form
    # max_length=20: tối đa 20 ký tự
    name = models.CharField("Tên phòng ban", max_length=100)
    is_active = models.BooleanField("Đang hoạt động", default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


# Vị trí công việc
class Position(models.Model):
    code = models.CharField("Mã vị trí công việc", max_length=20, unique=True)
    name = models.CharField("Tên vị trí công việc", max_length=100)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    # on_delete=models.SET_NULL: nếu đối tượng được tham chiếu bị xóa
    # thì không xóa object này, chỉ bỏ liên kết với đối tượng được tham chiếu đó.
    # (
    # position vẫn tồn tại nhưng trường department sẽ được đặt thành NULL
    # )
    
    # null=True: cho phép trường này có giá trị NULL trong DB
    # blank=True: cho phép trường này có thể để trống trong FORM (không bắt buộc nhập)
    is_active = models.BooleanField("Đang hoạt động", default=True)

    def save(self, *args, **kwargs):
        # Tự động tạo mã vị trí nếu không được cung cấp
        if not self.code:
            # Lấy 2-3 chữ cái đầu tiên của tên vị trí và chuyển thành viết hoa
            prefix = ''.join(word[0] for word in self.name.split()[:3]).upper()

            # Tìm mã vị trí cuối cùng có cùng tiền tố
            from django.db.models import Max
            last_code = Position.objects.filter(code__startswith=prefix).aggregate(Max('code'))['code__max']

            if last_code:
                # Trích xuất số từ mã cuối cùng và tăng lên 1
                try:
                    last_num = int(last_code[len(prefix):])
                    self.code = f"{prefix}{last_num + 1:03d}"
                except ValueError:
                    self.code = f"{prefix}001"
            else:
                self.code = f"{prefix}001"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Employee(models.Model):
    GENDER_CHOICES = (
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    )

    EDUCATION_LEVEL_CHOICES = (
        ('high_school', 'Trung học phổ thông'),
        ('college', 'Cao đẳng'),
        ('university', 'Đại học'),
        ('master', 'Thạc sĩ'),
        ('phd', 'Tiến sĩ'),
    )

    # Thông tin cơ bản
    code = models.CharField(_("Mã nhân viên"), max_length=20, unique=True)
    first_name = models.CharField(_("Tên"), max_length=50)
    last_name = models.CharField(_("Họ"), max_length=50)
    full_name = models.CharField(_("Họ và tên"), max_length=100, blank=True)
    gender = models.CharField(_("Giới tính"), max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(_("Ngày sinh"))
    id_number = models.CharField(_("Số CMND/CCCD"), max_length=20, blank=True, null=True)

    # Thông tin liên hệ
    phone = models.CharField(_("Số điện thoại"), max_length=20)
    email = models.EmailField(_("Email"), blank=True, null=True)
    address = models.CharField(_("Địa chỉ"), max_length=255, blank=True, null=True)

    # Thông tin công việc
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, verbose_name=_("Vị trí công việc"))
    join_date = models.DateField(_("Ngày vào làm"))
    is_active = models.BooleanField(_("Đang làm việc"), default=True)

    # Thông tin bằng cấp và trình độ
    education_level = models.CharField(_("Trình độ đào tạo"), max_length=20, choices=EDUCATION_LEVEL_CHOICES,
                                       blank=True, null=True)
    degree = models.CharField(_("Bằng cấp"), max_length=100, blank=True, null=True)
    major = models.CharField(_("Chuyên ngành"), max_length=100, blank=True, null=True)
    graduation_year = models.IntegerField(_("Năm tốt nghiệp"), blank=True, null=True)
    graduation_place = models.CharField(_("Nơi đào tạo"), max_length=200, blank=True, null=True)
    faculty = models.CharField(_("Khoa"), max_length=100, blank=True, null=True)
    ranking = models.CharField(_("Xếp loại"), max_length=50, blank=True, null=True)

    # Thời gian tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Luôn cập nhật full_name mỗi khi lưu, không chỉ khi nó trống
        self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)

    def get_current_contract(self, on_date=None):
        on_date = on_date or timezone.now().date()
        return self.contracts.filter(
            is_active=True,
            start_date__lte=on_date,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=on_date)
        ).select_related('position', 'department').order_by('-start_date', '-id').first()

    def get_salary_basis(self, on_date=None):
        contract = self.get_current_contract(on_date)
        if contract:
            return contract.get_salary_basis()

        salary_history = self.salary_histories.filter(
            effective_date__lte=on_date or timezone.now().date()
        ).order_by('-effective_date').first()

        return {
            'contract': None,
            'salary_type': 'monthly' if salary_history else 'none',
            'amount': salary_history.new_salary if salary_history else Decimal('0'),
            'insurance_salary': Decimal('0'),
        }

    def sync_from_current_contract(self, on_date=None, save=True):
        contract = self.get_current_contract(on_date)
        if not contract:
            return False

        changed_fields = []
        if contract.position_id and self.position_id != contract.position_id:
            self.position = contract.position
            changed_fields.append('position')

        if not self.is_active:
            self.is_active = True
            changed_fields.append('is_active')

        if save and changed_fields:
            self.save(update_fields=changed_fields + ['full_name', 'updated_at'])

        return bool(changed_fields)

    def calculate_taxable_income(self, gross_income):
        gross_income = Decimal(str(gross_income or 0))
        return max(Decimal('0'), gross_income - Decimal('11000000'))

    def calculate_income_tax(self, gross_income):
        taxable_income = self.calculate_taxable_income(gross_income)
        brackets = [
            (Decimal('5000000'), Decimal('0.05')),
            (Decimal('10000000'), Decimal('0.10')),
            (Decimal('18000000'), Decimal('0.15')),
            (Decimal('32000000'), Decimal('0.20')),
            (Decimal('52000000'), Decimal('0.25')),
            (Decimal('80000000'), Decimal('0.30')),
        ]
        tax = Decimal('0')
        previous_cap = Decimal('0')
        for cap, rate in brackets:
            if taxable_income <= previous_cap:
                break
            taxable_part = min(taxable_income, cap) - previous_cap
            tax += taxable_part * rate
            previous_cap = cap
        if taxable_income > previous_cap:
            tax += (taxable_income - previous_cap) * Decimal('0.35')
        return tax.quantize(Decimal('1'))

    def __str__(self):
        return f"{self.code} - {self.full_name}"

    class Meta:
        verbose_name = _("Nhân viên")
        verbose_name_plural = _("Nhân viên")
        ordering = ['code']


class Contract(models.Model):
    SALARY_TYPES = (
        ('monthly', 'Lương tháng'),
        ('daily', 'Lương theo ngày công'),
        ('shift', 'Lương theo ca'),
        ('hourly', 'Lương theo giờ'),
        ('commission', 'Hoa hồng/doanh số'),
        ('none', 'Không áp dụng lương cơ bản'),
    )

    CONTRACT_TYPES = (
        ('probation', 'Thử việc'),
        ('definite', 'Xác định thời hạn'),
        ('indefinite', 'Không xác định thời hạn'),
    )

    WORK_FORMS = (
        ('fulltime', 'Toàn thời gian'),
        ('parttime', 'Bán thời gian'),
        ('shift', 'Theo ca'),
        ('contractor', 'Cộng tác viên'),
        ('remote', 'Từ xa'),
        ('hybrid', 'Kết hợp'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts', verbose_name="Nhân viên")
    contract_number = models.CharField("Số hợp đồng", max_length=20, unique=True)
    contract_name = models.CharField("Tên hợp đồng", max_length=200, blank=True, null=True)
    contract_type = models.CharField("Loại hợp đồng", max_length=20, choices=CONTRACT_TYPES)
    work_form = models.CharField("Hình thức làm việc", max_length=20, choices=WORK_FORMS, default='fulltime',
                                 blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='department_contracts', verbose_name="Đơn vị ký hợp đồng")
    start_date = models.DateField("Ngày có hiệu lực")
    end_date = models.DateField("Ngày kết thúc", null=True, blank=True)
    sign_date = models.DateField("Ngày ký", null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, related_name='employee_contracts',
                                 verbose_name="Vị trí công việc")
    salary_type = models.CharField("Loại lương", max_length=20, choices=SALARY_TYPES, default='monthly')
    basic_salary = models.DecimalField("Mức lương / Đơn giá tính lương", max_digits=12, decimal_places=0, blank=True, null=True)
    insurance_salary = models.DecimalField("Lương đóng bảo hiểm", max_digits=12, decimal_places=0, default=0)
    file = models.FileField("File hợp đồng", upload_to='contracts/', blank=True, null=True)
    is_active = models.BooleanField("Đang hiệu lực", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    def __str__(self):
        return f"{self.contract_number} - {self.employee.full_name}"

    class Meta:
        verbose_name = "Hợp đồng"
        verbose_name_plural = "Hợp đồng"
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        # Kiểm tra và chuyển đổi end_date nếu là chuỗi
        if self.end_date and isinstance(self.end_date, str):
            try:
                from datetime import datetime
                self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            except ValueError:
                # Nếu không thể chuyển đổi, giữ nguyên giá trị và bỏ qua việc so sánh
                pass

        # Kiểm tra và cập nhật trạng thái is_active dựa trên end_date
        if self.end_date and not isinstance(self.end_date, str) and self.end_date <= timezone.now().date():
            self.is_active = False

        # Nếu là hợp đồng không xác định thời hạn, xóa ngày kết thúc
        if self.contract_type == 'indefinite':
            self.end_date = None

        super().save(*args, **kwargs)

        if self.is_active_status:
            self.employee.sync_from_current_contract()

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.contract_type != 'indefinite' and not self.end_date:
            errors['end_date'] = "Hop dong thu viec/xac dinh thoi han can co ngay ket thuc."

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = "Ngay ket thuc khong duoc truoc ngay hieu luc."

        if self.salary_type in {'monthly', 'daily', 'shift', 'hourly'} and not self.basic_salary:
            errors['basic_salary'] = "Kieu luong nay can co so tien tinh luong."

        if self.basic_salary is not None and self.basic_salary < 0:
            errors['basic_salary'] = "Luong khong duoc am."

        if self.insurance_salary is not None and self.insurance_salary < 0:
            errors['insurance_salary'] = "Luong dong bao hiem khong duoc am."

        if self.is_active and self.employee_id and self.start_date:
            overlap_end = self.end_date or datetime.date.max
            overlapping_contracts = Contract.objects.filter(
                employee_id=self.employee_id,
                is_active=True,
                start_date__lte=overlap_end,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=self.start_date)
            )
            if self.pk:
                overlapping_contracts = overlapping_contracts.exclude(pk=self.pk)
            if overlapping_contracts.exists():
                errors['start_date'] = "Nhan vien da co hop dong dang hieu luc trung thoi gian."

        if errors:
            raise ValidationError(errors)

    def get_salary_basis(self):
        return {
            'contract': self,
            'salary_type': self.salary_type,
            'amount': self.basic_salary or Decimal('0'),
            'insurance_salary': self.insurance_salary or Decimal('0'),
        }

    @property
    def is_active_status(self):
        """Kiểm tra trạng thái hoạt động của hợp đồng dựa trên ngày kết thúc"""
        if not self.is_active:
            return False
        today = timezone.now().date()
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and not isinstance(self.end_date, str) and self.end_date <= today:
            return False
        return True


class WorkHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_histories')
    company = models.CharField("Công ty", max_length=100)
    position = models.CharField("Vị trí", max_length=100)
    start_date = models.DateField("Ngày bắt đầu")
    end_date = models.DateField("Ngày kết thúc", null=True, blank=True)
    description = models.TextField("Mô tả công việc", blank=True, null=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.company}"


class SalaryHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_histories')
    effective_date = models.DateField("Ngày hiệu lực")
    old_salary = models.DecimalField("Lương cũ", max_digits=12, decimal_places=0)
    new_salary = models.DecimalField("Lương mới", max_digits=12, decimal_places=0)
    reason = models.TextField("Lý do thay đổi")

    def __str__(self):
        return f"{self.employee.full_name} - {self.effective_date}"
