from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
import json
import xlsxwriter
from io import BytesIO
from datetime import datetime

from .models import Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction
from .forms import PayrollForm, PayrollDetailForm
from employees.models import Employee, Position
from attendance.models import AttendanceSummary, DailyAttendance


@login_required
@require_POST
def calculate_tax_api(request, employee_id):
	"""API để tính thuế TNCN cho nhân viên"""
	try:
		employee = get_object_or_404(Employee, pk=employee_id)
		data = json.loads(request.body)
		gross_income = Decimal(str(data.get('gross_income', 0)))

		# Tính thu nhập tính thuế
		taxable_income = employee.calculate_taxable_income(gross_income)

		# Tính thuế TNCN
		income_tax = employee.calculate_income_tax(gross_income)

		# Tính lương thực lĩnh
		net_salary = gross_income - income_tax

		return JsonResponse({
			'gross_income': float(gross_income),
			'taxable_income': float(taxable_income),
			'income_tax': float(income_tax),
			'net_salary': float(net_salary)
		})
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=400)


@login_required
def payroll_list(request):
    """Hiển thị danh sách bảng lương"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # Lấy danh sách bảng lương
    payrolls = Payroll.objects.all()

    # Lọc theo từ khóa tìm kiếm
    if search_query:
        payrolls = payrolls.filter(
            Q(name__icontains=search_query) |
            Q(position__name__icontains=search_query)
        )

    # Lọc theo trạng thái
    if status_filter:
        payrolls = payrolls.filter(status=status_filter)

    # Phân trang
    paginator = Paginator(payrolls, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'payroll/payroll_list.html', context)


@login_required
def process_attendance_data(payroll, attendance_summary):
    """
    Xử lý dữ liệu từ bảng chấm công để tạo chi tiết lương
    """
    # Lấy danh sách nhân viên từ bảng chấm công
    employees = Employee.objects.filter(position=attendance_summary.position)

    # Số công chuẩn
    standard_workdays = getattr(attendance_summary, 'standard_workdays', 22) or 24

    # Tính lương cho từng nhân viên
    for employee in employees:
        # Lấy lương cơ bản từ thông tin nhân viên
        basic_salary = getattr(employee, 'basic_salary', 0) or 0

        # Tìm dữ liệu chấm công của nhân viên
        try:
            from attendance.models import EmployeeAttendance
            employee_attendance = EmployeeAttendance.objects.filter(
                employee=employee,
                attendance_summary=attendance_summary
            ).first()
        except Exception:
            employee_attendance = None

        # Nếu có dữ liệu chấm công
        if employee_attendance:
            actual_workdays = employee_attendance.workdays
            unpaid_leave = employee_attendance.unpaid_leave
            attendance_ratio = employee_attendance.total_paid_days / standard_workdays if standard_workdays > 0 else 0
        else:
            # Nếu không có dữ liệu chấm công, giả định làm đủ công
            actual_workdays = standard_workdays
            unpaid_leave = 0
            attendance_ratio = 1.0

        # Tính lương theo ngày công
        from decimal import Decimal
        gross_salary = int(basic_salary * Decimal(str(attendance_ratio)))

        # Tính các khoản khấu trừ (giả định 10% tổng thu nhập)
        deductions_amount = int(gross_salary * Decimal('0.1'))

        # Tính lương thực lĩnh
        net_salary = gross_salary - deductions_amount

        # Debug: In ra giá trị để kiểm tra
        print(f"Employee: {employee.full_name}")
        print(f"Basic salary: {basic_salary}")
        print(f"Gross salary: {gross_salary}")
        print(f"Deductions: {deductions_amount}")
        print(f"Net salary: {net_salary}")

        # Tạo chi tiết lương - không sử dụng deduction_data nếu không có cột
        try:
            # Kiểm tra xem có cột deduction_data không
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("PRAGMA table_info(payroll_payrolldetail);")
            columns = [col[1] for col in cursor.fetchall()]

            if 'deduction_data' in columns:
                # Nếu có cột deduction_data
                deduction_data = {
                    'deductions': [
                        {
                            'name': 'Bảo hiểm xã hội',
                            'amount': 8,
                            'is_percentage': True,
                            'value': int(gross_salary * Decimal('0.08'))
                        },
                        {
                            'name': 'Bảo hiểm y tế',
                            'amount': 1.5,
                            'is_percentage': True,
                            'value': int(gross_salary * Decimal('0.015'))
                        },
                        {
                            'name': 'Bảo hiểm thất nghiệp',
                            'amount': 1,
                            'is_percentage': True,
                            'value': int(gross_salary * Decimal('0.01'))
                        }
                    ]
                }

                payroll_detail = PayrollDetail.objects.create(
                    payroll=payroll,
                    employee=employee,
                    basic_salary=basic_salary,
                    attendance_ratio=attendance_ratio,
                    standard_workdays=standard_workdays,
                    actual_workdays=actual_workdays,
                    unpaid_leave=unpaid_leave,
                    gross_salary=gross_salary,
                    deduction_amount=deductions_amount,
                    net_salary=net_salary,  # Đảm bảo net_salary được lưu
                    deduction_data=deduction_data
                )
            else:
                # Nếu không có cột deduction_data
                payroll_detail = PayrollDetail.objects.create(
                    payroll=payroll,
                    employee=employee,
                    basic_salary=basic_salary,
                    attendance_ratio=attendance_ratio,
                    standard_workdays=standard_workdays,
                    actual_workdays=actual_workdays,
                    unpaid_leave=unpaid_leave,
                    gross_salary=gross_salary,
                    deduction_amount=deductions_amount,
                    net_salary=net_salary  # Đảm bảo net_salary được lưu
                )
        except Exception as e:
            # Nếu có lỗi, thử tạo không có deduction_data
            print(f"Error creating payroll detail: {str(e)}")
            payroll_detail = PayrollDetail.objects.create(
                payroll=payroll,
                employee=employee,
                basic_salary=basic_salary,
                attendance_ratio=attendance_ratio,
                standard_workdays=standard_workdays,
                actual_workdays=actual_workdays,
                unpaid_leave=unpaid_leave,
                gross_salary=gross_salary,
                deduction_amount=deductions_amount,
                net_salary=net_salary  # Đảm bảo net_salary được lưu
            )


@login_required
def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.user = request.user  # Gán người dùng hiện tại cho trường user
            payroll.save()

            # Xử lý dữ liệu từ bảng chấm công nếu có
            attendance_summary = form.cleaned_data.get('attendance_summary')
            if attendance_summary:
                # Gọi hàm xử lý dữ liệu từ bảng chấm công
                process_attendance_data(payroll, attendance_summary)

            messages.success(request, 'Bảng lương đã được tạo thành công.')
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm()

    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Tạo bảng lương mới'
    })



@login_required
def payroll_detail(request, pk):
	"""Xem chi tiết bảng lương"""
	payroll = get_object_or_404(Payroll, pk=pk)
	details = PayrollDetail.objects.filter(payroll=payroll)



	context = {
		'payroll': payroll,
		'details': details,
	}

	return render(request, 'payroll/payroll_detail.html', context)


@login_required
def payroll_update(request, pk):
    """Cập nhật bảng lương"""
    payroll = get_object_or_404(Payroll, pk=pk)




    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bảng lương "{payroll.name}" đã được cập nhật')
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm(instance=payroll)

    context = {
        'form': form,
        'payroll': payroll,
        'title': 'Cập nhật bảng lương',

    }

    return render(request, 'payroll/payroll_form.html', context)


@login_required
def payroll_employee_detail(request, payroll_id, detail_id):
	"""Xem chi tiết lương của nhân viên"""
	payroll = get_object_or_404(Payroll, pk=payroll_id)
	detail = get_object_or_404(PayrollDetail, pk=detail_id, payroll=payroll)

	# Lấy danh sách khấu trừ
	deductions = PayrollDeduction.objects.filter(payroll_detail=detail)

	# Lấy danh sách phụ cấp
	allowances = PayrollAllowance.objects.filter(payroll_detail=detail)

	context = {
		'payroll': payroll,
		'detail': detail,
		'deductions': deductions,
		'allowances': allowances,
	}

	return render(request, 'payroll/payroll_employee_detail.html', context)


@login_required
def calculate_payroll(request):
	from .forms import CalculatePayrollForm

	if request.method == 'POST':
		form = CalculatePayrollForm(request.POST)
		if form.is_valid():
			attendance_summary = form.cleaned_data['attendance_summary']
			payroll_name = form.cleaned_data['payroll_name']

			# Tạo bảng lương mới
			payroll = Payroll.objects.create(
				user=request.user, # ✅ thêm dòng này
				name=payroll_name,
				month=attendance_summary.start_date.month if hasattr(attendance_summary,
				                                                     'start_date') and attendance_summary.start_date else timezone.now().month,
				year=attendance_summary.start_date.year if hasattr(attendance_summary,
				                                                   'start_date') and attendance_summary.start_date else timezone.now().year,
				position=attendance_summary.position,
				status='draft'
			)

			# Xử lý dữ liệu từ bảng chấm công
			process_attendance_data(payroll, attendance_summary)

			# Đánh dấu bảng chấm công đã được chuyển tính lương
			try:
				attendance_summary.transferred = True
				attendance_summary.save()
			except AttributeError:
				pass

			messages.success(request, 'Đã tính lương thành công từ bảng chấm công.')
			return redirect('payroll_detail', pk=payroll.pk)
	else:
		form = CalculatePayrollForm()

	return render(request, 'payroll/calculate_payroll.html', {
		'form': form,
		'title': 'Tính lương'
	})


@login_required
def export_payroll(request, pk):
	"""Xuất bảng lương ra file Excel"""
	payroll = get_object_or_404(Payroll, pk=pk)

	# Xử lý xuất file Excel (sẽ triển khai sau)
	messages.info(request, 'Chức năng xuất bảng lương đang được phát triển')
	return redirect('payroll_detail', pk=payroll.pk)


@login_required
def transfer_to_payroll(request, attendance_summary_id):
	"""Chuyển dữ liệu từ bảng chấm công tổng hợp sang tính lương"""
	attendance_summary = get_object_or_404(AttendanceSummary, pk=attendance_summary_id)

	# Kiểm tra xem bảng chấm công đã được chuyển sang tính lương chưa
	if attendance_summary.transferred:
		messages.warning(request, 'Bảng chấm công này đã được chuyển sang tính lương trước đó')
		return redirect('attendance_summary_detail', pk=attendance_summary_id)

	if request.method == 'POST':
		# Tạo tên bảng lương mặc định
		month = attendance_summary.start_date.month if attendance_summary.start_date else timezone.now().month
		year = attendance_summary.start_date.year if attendance_summary.start_date else timezone.now().year
		payroll_name = f"Bảng lương tháng {month}/{year} - {attendance_summary.name}"

		# Tạo bảng lương mới
		payroll = Payroll.objects.create(
			user=request.user,  # ✅ thêm dòng này,
			name=payroll_name,
			month=month,
			year=year,
			position=attendance_summary.position,
			attendance_summary=attendance_summary,
			status='draft'
		)

		# Lấy danh sách nhân viên từ bảng chấm công
		employee_attendances = attendance_summary.employee_attendances.all()

		# Tính lương cho từng nhân viên
		for employee_attendance in employee_attendances:
			employee = employee_attendance.employee

			# Lấy số công chuẩn từ bảng chấm công
			standard_workdays = attendance_summary.standard_workdays

			# Lấy số công thực tế và số ngày nghỉ không lương
			actual_workdays = employee_attendance.workdays
			unpaid_leave = employee_attendance.unpaid_leave

			# Tính tỷ lệ hưởng lương
			attendance_ratio = employee_attendance.total_paid_days / standard_workdays if standard_workdays > 0 else 0

			# Lấy lương cơ bản từ thông tin nhân viên
			basic_salary = employee.basic_salary or 0

			# Tính lương theo ngày công
			gross_salary = int(basic_salary * attendance_ratio)

			# Tính các khoản khấu trừ (giả định 10% tổng thu nhập)
			deductions_amount = int(gross_salary * Decimal('0.1'))

			# Tính lương thực lĩnh
			net_salary = gross_salary - deductions_amount

			# Tạo chi tiết lương
			payroll_detail = PayrollDetail.objects.create(
				payroll=payroll,
				employee=employee,
				basic_salary=basic_salary,
				attendance_ratio=attendance_ratio,
				standard_workdays=standard_workdays,
				actual_workdays=actual_workdays,
				unpaid_leave=unpaid_leave,
				gross_salary=gross_salary,
				deduction_amount=deductions_amount,
				net_salary=net_salary
			)



		# Đánh dấu bảng chấm công đã được chuyển tính lương
		attendance_summary.transferred = True
		attendance_summary.save()

		messages.success(request,
		                 f'Đã chuyển dữ liệu từ bảng chấm công "{attendance_summary.name}" sang bảng lương thành công')
		return redirect('payroll_detail', pk=payroll.pk)

	context = {
		'attendance_summary': attendance_summary,
	}

	return render(request, 'payroll/transfer_to_payroll.html', context)


@login_required
def disable_payroll(request, pk):
    """Vô hiệu hóa bảng lương"""
    payroll = get_object_or_404(Payroll, pk=pk)



    if request.method == 'POST':
        payroll.status = 'disabled'
        payroll.save()
        messages.success(request, f'Bảng lương "{payroll.name}" đã được vô hiệu hóa')
        return redirect('payroll_list')

    context = {
        'payroll': payroll,
    }

    return render(request, 'payroll/payroll_disable.html', context)


@login_required
def export_payroll_excel(request, pk):
	"""Xuất bảng lương ra file Excel"""
	payroll = get_object_or_404(Payroll, pk=pk)
	details = PayrollDetail.objects.filter(payroll=payroll)

	# Tạo file Excel trong bộ nhớ
	output = BytesIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet("Bảng lương")

	# Định dạng
	header_format = workbook.add_format({
		'bold': True,
		'bg_color': '#2980b9',
		'color': 'white',
		'align': 'center',
		'valign': 'vcenter',
		'border': 1
	})

	cell_format = workbook.add_format({
		'border': 1,
		'align': 'left',
		'valign': 'vcenter'
	})

	number_format = workbook.add_format({
		'border': 1,
		'align': 'right',
		'valign': 'vcenter',
		'num_format': '#,##0'
	})

	percent_format = workbook.add_format({
		'border': 1,
		'align': 'right',
		'valign': 'vcenter',
		'num_format': '0.00%'
	})

	# Thiết lập độ rộng cột
	worksheet.set_column('A:A', 5)  # STT
	worksheet.set_column('B:B', 30)  # Họ tên
	worksheet.set_column('C:C', 15)  # Mã nhân viên
	worksheet.set_column('D:D', 15)  # Lương cơ bản
	worksheet.set_column('E:E', 15)  # Số công chuẩn
	worksheet.set_column('F:F', 15)  # Số công thực tế
	worksheet.set_column('G:G', 15)  # Nghỉ không lương
	worksheet.set_column('H:H', 15)  # Tỷ lệ hưởng lương
	worksheet.set_column('I:I', 15)  # Tổng thu nhập
	worksheet.set_column('J:J', 15)  # Khấu trừ
	worksheet.set_column('K:K', 15)  # Thực lĩnh

	# Tiêu đề bảng lương
	worksheet.merge_range('A1:K1', f"BẢNG LƯƠNG: {payroll.name}", header_format)
	worksheet.merge_range('A2:K2', f"Tháng {payroll.month}/{payroll.year} - {payroll.position.name}", header_format)

	# Tiêu đề cột
	headers = [
		"STT", "Họ tên", "Mã NV", "Lương cơ bản", "Công chuẩn",
		"Công thực tế", "Nghỉ không lương", "Tỷ lệ hưởng",
		"Tổng thu nhập", "Khấu trừ", "Thực lĩnh"
	]

	for col, header in enumerate(headers):
		worksheet.write(3, col, header, header_format)

	# Dữ liệu
	row = 4
	for i, detail in enumerate(details, 1):
		worksheet.write(row, 0, i, cell_format)  # STT
		worksheet.write(row, 1, detail.employee.full_name, cell_format)  # Họ tên
		worksheet.write(row, 2, detail.employee.employee_id, cell_format)  # Mã NV
		worksheet.write(row, 3, detail.basic_salary, number_format)  # Lương cơ bản
		worksheet.write(row, 4, detail.standard_workdays, cell_format)  # Công chuẩn
		worksheet.write(row, 5, detail.actual_workdays, cell_format)  # Công thực tế
		worksheet.write(row, 6, detail.unpaid_leave, cell_format)  # Nghỉ không lương
		worksheet.write(row, 7, detail.attendance_ratio, percent_format)  # Tỷ lệ hưởng
		worksheet.write(row, 8, detail.gross_salary, number_format)  # Tổng thu nhập
		worksheet.write(row, 9, detail.deduction_amount, number_format)  # Khấu trừ
		worksheet.write(row, 10, detail.net_salary, number_format)  # Thực lĩnh
		row += 1

	# Tổng cộng
	worksheet.merge_range(f'A{row + 1}:G{row + 1}', "TỔNG CỘNG", header_format)
	worksheet.write(row + 1, 8, f'=SUM(I5:I{row})', number_format)
	worksheet.write(row + 1, 9, f'=SUM(J5:J{row})', number_format)
	worksheet.write(row + 1, 10, f'=SUM(K5:K{row})', number_format)

	# Thông tin người tạo
	worksheet.merge_range(f'A{row + 3}:K{row + 3}', f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
	                      cell_format)

	workbook.close()

	# Thiết lập response
	output.seek(0)
	filename = f"Bang_luong_{payroll.month}_{payroll.year}_{payroll.position.name}.xlsx"

	response = HttpResponse(
		output,
		content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	)
	response['Content-Disposition'] = f'attachment; filename="{filename}"'

	return response


@login_required
def payroll_employee_detail(request, payroll_id, detail_id):
	"""Xem chi tiết lương của nhân viên"""
	payroll = get_object_or_404(Payroll, pk=payroll_id)
	detail = get_object_or_404(PayrollDetail, pk=detail_id, payroll=payroll)

	# Lấy danh sách khấu trừ
	deductions = PayrollDeduction.objects.filter(payroll_detail=detail)

	# Lấy danh sách phụ cấp
	allowances = PayrollAllowance.objects.filter(payroll_detail=detail)

	context = {
		'payroll': payroll,
		'detail': detail,
		'deductions': deductions,
		'allowances': allowances,
	}

	return render(request, 'payroll/payroll_employee_detail.html', context)

@login_required
def activate_payroll(request, pk):
    """Kích hoạt bảng lương đã vô hiệu hóa"""
    payroll = get_object_or_404(Payroll, pk=pk)





    if request.method == 'POST':
        # Đặt lại trạng thái là nháp
        payroll.status = 'draft'
        payroll.save()
        messages.success(request, f'Bảng lương "{payroll.name}" đã được kích hoạt lại')
        return redirect('payroll_detail', pk=payroll.pk)

    context = {
        'payroll': payroll,

    }

    return render(request, 'payroll/payroll_activate.html', context)

@login_required
def export_payroll_excel(request, pk):
	"""Xuất bảng lương ra file Excel"""
	payroll = get_object_or_404(Payroll, pk=pk)
	details = PayrollDetail.objects.filter(payroll=payroll)

	# Tạo file Excel trong bộ nhớ
	output = BytesIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet("Bảng lương")

	# Định dạng
	header_format = workbook.add_format({
		'bold': True,
		'bg_color': '#2980b9',
		'color': 'white',
		'align': 'center',
		'valign': 'vcenter',
		'border': 1
	})

	cell_format = workbook.add_format({
		'border': 1,
		'align': 'left',
		'valign': 'vcenter'
	})

	number_format = workbook.add_format({
		'border': 1,
		'align': 'right',
		'valign': 'vcenter',
		'num_format': '#,##0'
	})

	percent_format = workbook.add_format({
		'border': 1,
		'align': 'right',
		'valign': 'vcenter',
		'num_format': '0.00%'
	})

	# Thiết lập độ rộng cột
	worksheet.set_column('A:A', 5)  # STT
	worksheet.set_column('B:B', 30)  # Họ tên
	worksheet.set_column('C:C', 15)  # Mã nhân viên
	worksheet.set_column('D:D', 15)  # Lương cơ bản
	worksheet.set_column('E:E', 15)  # Số công chuẩn
	worksheet.set_column('F:F', 15)  # Số công thực tế
	worksheet.set_column('G:G', 15)  # Nghỉ không lương
	worksheet.set_column('H:H', 15)  # Tỷ lệ hưởng lương
	worksheet.set_column('I:I', 15)  # Tổng thu nhập
	worksheet.set_column('J:J', 15)  # Khấu trừ
	worksheet.set_column('K:K', 15)  # Thực lĩnh

	# Tiêu đề bảng lương
	worksheet.merge_range('A1:K1', f"BẢNG LƯƠNG: {payroll.name}", header_format)
	worksheet.merge_range('A2:K2', f"Tháng {payroll.month}/{payroll.year} - {payroll.position.name}", header_format)

	# Tiêu đề cột
	headers = [
		"STT", "Họ tên", "Mã NV", "Lương cơ bản", "Công chuẩn",
		"Công thực tế", "Nghỉ không lương", "Tỷ lệ hưởng",
		"Tổng thu nhập", "Khấu trừ", "Thực lĩnh"
	]

	for col, header in enumerate(headers):
		worksheet.write(3, col, header, header_format)

	# Dữ liệu
	row = 4
	for i, detail in enumerate(details, 1):
		worksheet.write(row, 0, i, cell_format)  # STT
		worksheet.write(row, 1, detail.employee.full_name, cell_format)  # Họ tên

		# Sửa lỗi: Kiểm tra xem employee có thuộc tính employee_id không
		employee_id = getattr(detail.employee, 'employee_id', '') or getattr(detail.employee, 'id',
		                                                                     str(detail.employee.pk))
		worksheet.write(row, 2, employee_id, cell_format)  # Mã NV

		worksheet.write(row, 3, detail.basic_salary, number_format)  # Lương cơ bản
		worksheet.write(row, 4, detail.standard_workdays, cell_format)  # Công chuẩn
		worksheet.write(row, 5, detail.actual_workdays, cell_format)  # Công thực tế
		worksheet.write(row, 6, detail.unpaid_leave, cell_format)  # Nghỉ không lương
		worksheet.write(row, 7, detail.attendance_ratio, percent_format)  # Tỷ lệ hưởng
		worksheet.write(row, 8, detail.gross_salary, number_format)  # Tổng thu nhập
		worksheet.write(row, 9, detail.deduction_amount, number_format)  # Khấu trừ
		worksheet.write(row, 10, detail.net_salary, number_format)  # Thực lĩnh
		row += 1

	# Tổng cộng
	worksheet.merge_range(f'A{row + 1}:G{row + 1}', "TỔNG CỘNG", header_format)
	worksheet.write(row + 1, 8, f'=SUM(I5:I{row})', number_format)
	worksheet.write(row + 1, 9, f'=SUM(J5:J{row})', number_format)
	worksheet.write(row + 1, 10, f'=SUM(K5:K{row})', number_format)

	# Thông tin người tạo
	worksheet.merge_range(f'A{row + 3}:K{row + 3}', f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
	                      cell_format)

	workbook.close()

	# Thiết lập response
	output.seek(0)
	filename = f"Bang_luong_{payroll.month}_{payroll.year}_{payroll.position.name}.xlsx"

	response = HttpResponse(
		output,
		content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	)
	response['Content-Disposition'] = f'attachment; filename="{filename}"'

	return response

@login_required
def payroll_detail(request, pk):
    """Xem chi tiết bảng lương"""
    payroll = get_object_or_404(Payroll, pk=pk)
    details = PayrollDetail.objects.filter(payroll=payroll)

    context = {
        'payroll': payroll,
        'details': details,
    }

    return render(request, 'payroll/payroll_detail.html', context)

