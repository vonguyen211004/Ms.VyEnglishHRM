from datetime import datetime
from decimal import Decimal
from io import BytesIO
import json

import xlsxwriter
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from attendance.models import AttendanceSummary, MonthlyTimesheet
from attendance.utils import calculate_gross_salary, get_attendance_summary_data, get_monthly_timesheet_data
from employees.models import Employee
from .forms import PayrollForm
from .models import Payroll, PayrollAllowance, PayrollDeduction, PayrollDetail


def _money(value):
    return int(Decimal(str(value or 0)))


def _deduction_for(gross_salary):
    return int(Decimal(str(gross_salary or 0)) * Decimal('0.1'))


def _timesheet_source(payroll):
    return payroll.monthly_timesheet or payroll.attendance_summary


def process_attendance_data(payroll, source):
    """Create payroll details from a locked MonthlyTimesheet or legacy AttendanceSummary."""
    if isinstance(source, MonthlyTimesheet):
        if payroll.monthly_timesheet_id is None:
            payroll.monthly_timesheet = source
            payroll.month = source.month
            payroll.year = source.year
            payroll.position = source.position
            payroll.save(update_fields=['monthly_timesheet', 'month', 'year', 'position'])
        rows = get_monthly_timesheet_data(source)
        period_end = source.end_date
    else:
        if payroll.attendance_summary_id is None:
            payroll.attendance_summary = source
            payroll.save(update_fields=['attendance_summary'])
        rows = get_attendance_summary_data(source)
        period_end = getattr(source, 'end_date', None)

    for row in rows:
        employee = row['employee']
        salary_data = calculate_gross_salary(employee, row, period_end)
        gross_salary = _money(salary_data['gross_salary'])
        deduction_amount = _deduction_for(gross_salary)
        income_tax = _money(employee.calculate_income_tax(gross_salary))

        PayrollDetail.objects.update_or_create(
            payroll=payroll,
            employee=employee,
            defaults={
                'basic_salary': salary_data['base_amount'],
                'attendance_ratio': max(Decimal('0'), min(Decimal('1'), Decimal(str(row.get('attendance_ratio', 0))))),
                'standard_workdays': row.get('standard_work_days') or row.get('standard_teaching_hours') or 0,
                'actual_workdays': row.get('actual_workdays') or row.get('teaching_paid_hours') or 0,
                'unpaid_leave': row.get('unpaid_leave') or 0,
                'reward_amount': 0,
                'discipline_amount': 0,
                'gross_salary': gross_salary,
                'deduction_amount': deduction_amount,
                'income_tax': income_tax,
                'note': (
                    f"salary_type={salary_data['salary_type']}; "
                    f"timesheet_type={getattr(source, 'timesheet_type', 'legacy')}; "
                    f"worked_hours={row.get('worked_hours', 0)}; "
                    f"teaching_hours={row.get('teaching_paid_hours', 0)}"
                ),
            },
        )


@login_required
@require_POST
def calculate_tax_api(request, employee_id):
    try:
        employee = get_object_or_404(Employee, pk=employee_id)
        data = json.loads(request.body)
        gross_income = Decimal(str(data.get('gross_income', 0)))
        income_tax = employee.calculate_income_tax(gross_income)
        return JsonResponse({
            'gross_income': float(gross_income),
            'taxable_income': float(employee.calculate_taxable_income(gross_income)),
            'income_tax': float(income_tax),
            'net_salary': float(gross_income - income_tax),
        })
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)


@login_required
def payroll_list(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    source_filter = request.GET.get('source', '')

    payrolls = Payroll.objects.select_related('position', 'monthly_timesheet').order_by('-year', '-month', '-created_at')
    if search_query:
        payrolls = payrolls.filter(
            Q(name__icontains=search_query) |
            Q(position__name__icontains=search_query) |
            Q(monthly_timesheet__name__icontains=search_query)
        )
    if status_filter:
        payrolls = payrolls.filter(status=status_filter)
    if source_filter:
        payrolls = payrolls.filter(monthly_timesheet__timesheet_type=source_filter)

    page_obj = Paginator(payrolls, 10).get_page(request.GET.get('page'))
    return render(request, 'payroll/payroll_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'source_filter': source_filter,
        'source_choices': MonthlyTimesheet.TIMESHEET_TYPE_CHOICES,
    })


@login_required
def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            timesheet = form.cleaned_data.get('monthly_timesheet')
            if not timesheet:
                messages.warning(request, 'Vui lòng chọn bảng công tháng đã khóa để tạo bảng lương.')
                return redirect('payroll_create')

            payroll = form.save(commit=False)
            payroll.user = request.user
            payroll.created_by = request.user
            payroll.monthly_timesheet = timesheet
            payroll.month = timesheet.month
            payroll.year = timesheet.year
            payroll.position = timesheet.position
            if not payroll.name:
                payroll.name = f'Bảng lương {timesheet.get_timesheet_type_display().lower()} tháng {timesheet.month}/{timesheet.year} - {timesheet.position.name}'
            payroll.save()
            process_attendance_data(payroll, timesheet)
            timesheet.transferred = True
            timesheet.status = 'transferred'
            timesheet.save(update_fields=['transferred', 'status', 'updated_at'])
            messages.success(request, 'Đã tạo bảng lương từ bảng công tháng.')
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm()

    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Tạo bảng lương từ bảng công',
    })


@login_required
def payroll_update(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)
        if form.is_valid():
            updated = form.save(commit=False)
            source = form.cleaned_data.get('monthly_timesheet') or payroll.monthly_timesheet
            if source:
                updated.monthly_timesheet = source
                updated.month = source.month
                updated.year = source.year
                updated.position = source.position
            updated.save()
            if source:
                process_attendance_data(updated, source)
            messages.success(request, f'Đã cập nhật bảng lương "{updated.name}".')
            return redirect('payroll_detail', pk=updated.pk)
    else:
        form = PayrollForm(instance=payroll)

    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'payroll': payroll,
        'title': 'Cập nhật bảng lương',
    })


@login_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll.objects.select_related('position', 'monthly_timesheet'), pk=pk)
    details = PayrollDetail.objects.filter(payroll=payroll).select_related('employee', 'employee__position')
    source = _timesheet_source(payroll)
    return render(request, 'payroll/payroll_detail.html', {
        'payroll': payroll,
        'details': details,
        'source': source,
        'is_teaching': getattr(source, 'timesheet_type', '') == 'teaching',
        'is_operations': getattr(source, 'timesheet_type', '') == 'operations',
    })


@login_required
def payroll_employee_detail(request, payroll_id, detail_id):
    payroll = get_object_or_404(Payroll, pk=payroll_id)
    detail = get_object_or_404(PayrollDetail.objects.select_related('employee', 'employee__position'), pk=detail_id, payroll=payroll)
    return render(request, 'payroll/payroll_employee_detail.html', {
        'payroll': payroll,
        'detail': detail,
        'deductions': PayrollDeduction.objects.filter(payroll_detail=detail),
        'allowances': PayrollAllowance.objects.filter(payroll_detail=detail),
        'source': _timesheet_source(payroll),
    })


@login_required
def calculate_payroll(request):
    messages.info(request, 'Vui lòng tạo bảng lương từ bảng công tháng đã khóa để dữ liệu lương khớp với chấm công mới.')
    return redirect('attendance:attendance_summary')


@login_required
def transfer_to_payroll(request, attendance_summary_id):
    timesheet = MonthlyTimesheet.objects.filter(pk=attendance_summary_id).first()
    if timesheet:
        if timesheet.transferred:
            messages.warning(request, 'Bảng công này đã được chuyển tính lương trước đó.')
            return redirect('attendance:attendance_summary_view', id=timesheet.id)
        if timesheet.status != 'locked':
            messages.warning(request, 'Chỉ được chuyển tính lương sau khi khóa bảng công.')
            return redirect('attendance:attendance_summary_view', id=timesheet.id)

        payroll = Payroll.objects.create(
            user=request.user,
            created_by=request.user,
            name=f'Bảng lương {timesheet.get_timesheet_type_display().lower()} tháng {timesheet.month}/{timesheet.year} - {timesheet.position.name}',
            month=timesheet.month,
            year=timesheet.year,
            position=timesheet.position,
            monthly_timesheet=timesheet,
            status='draft',
        )
        process_attendance_data(payroll, timesheet)
        timesheet.transferred = True
        timesheet.status = 'transferred'
        timesheet.save(update_fields=['transferred', 'status', 'updated_at'])
        messages.success(request, 'Đã chuyển bảng công tháng sang bảng lương.')
        return redirect('payroll_detail', pk=payroll.pk)

    legacy_summary = get_object_or_404(AttendanceSummary, pk=attendance_summary_id)
    messages.warning(request, 'Bảng công tổng hợp cũ không còn nằm trong workflow tính lương mới.')
    return redirect('attendance:attendance_summary')


@login_required
def disable_payroll(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        payroll.status = 'disabled'
        payroll.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Đã vô hiệu hóa bảng lương "{payroll.name}".')
        return redirect('payroll_list')
    return render(request, 'payroll/payroll_disable.html', {'payroll': payroll})


@login_required
def activate_payroll(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        payroll.status = 'draft'
        payroll.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Đã kích hoạt lại bảng lương "{payroll.name}".')
        return redirect('payroll_detail', pk=payroll.pk)
    return render(request, 'payroll/payroll_activate.html', {'payroll': payroll})


@login_required
def export_payroll(request, pk):
    messages.info(request, 'Chức năng xuất bảng lương đang dùng file Excel.')
    return redirect('export_payroll_excel', pk=pk)


@login_required
def export_payroll_excel(request, pk):
    payroll = get_object_or_404(Payroll.objects.select_related('position', 'monthly_timesheet'), pk=pk)
    details = PayrollDetail.objects.filter(payroll=payroll).select_related('employee')

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Bảng lương")
    header_format = workbook.add_format({'bold': True, 'bg_color': '#2980b9', 'color': 'white', 'align': 'center', 'border': 1})
    cell_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
    number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0'})
    percent_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '0.00%'})

    headers = [
        "STT", "Họ tên", "Mã NV", "Lương cơ bản", "Công/Giờ chuẩn",
        "Công/Giờ tính lương", "Nghỉ không lương", "Tỷ lệ hưởng",
        "Tổng thu nhập", "Thuế TNCN", "Khấu trừ khác", "Thực lĩnh"
    ]
    worksheet.merge_range('A1:L1', f"BẢNG LƯƠNG: {payroll.name}", header_format)
    worksheet.merge_range('A2:L2', f"Tháng {payroll.month}/{payroll.year} - {payroll.position.name}", header_format)
    for col, header in enumerate(headers):
        worksheet.write(3, col, header, header_format)
        worksheet.set_column(col, col, 18)

    row = 4
    for index, detail in enumerate(details, 1):
        worksheet.write(row, 0, index, cell_format)
        worksheet.write(row, 1, detail.employee.full_name, cell_format)
        worksheet.write(row, 2, detail.employee.code, cell_format)
        worksheet.write(row, 3, detail.basic_salary, number_format)
        worksheet.write(row, 4, detail.standard_workdays, cell_format)
        worksheet.write(row, 5, detail.actual_workdays, cell_format)
        worksheet.write(row, 6, detail.unpaid_leave, cell_format)
        worksheet.write(row, 7, detail.attendance_ratio, percent_format)
        worksheet.write(row, 8, detail.gross_salary, number_format)
        worksheet.write(row, 9, detail.income_tax, number_format)
        worksheet.write(row, 10, detail.deduction_amount, number_format)
        worksheet.write(row, 11, detail.net_salary, number_format)
        row += 1

    worksheet.merge_range(f'A{row + 1}:H{row + 1}', "TỔNG CỘNG", header_format)
    worksheet.write(row + 1, 8, f'=SUM(I5:I{row})', number_format)
    worksheet.write(row + 1, 9, f'=SUM(J5:J{row})', number_format)
    worksheet.write(row + 1, 10, f'=SUM(K5:K{row})', number_format)
    worksheet.write(row + 1, 11, f'=SUM(L5:L{row})', number_format)
    worksheet.merge_range(f'A{row + 3}:L{row + 3}', f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}", cell_format)
    workbook.close()

    output.seek(0)
    filename = f"Bang_luong_{payroll.month}_{payroll.year}_{payroll.position.code}.xlsx"
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
