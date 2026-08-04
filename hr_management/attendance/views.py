from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from employees.models import Employee, Position
from payroll.models import Payroll, PayrollDetail
from .forms import (
    AttendanceAdjustmentForm,
    ClassSessionForm,
    CourseForm,
    DailyAttendanceForm,
    MonthlyTimesheetForm,
    StaffScheduleForm,
    WorkShiftForm,
)
from .models import (
    AttendanceAdjustment,
    AttendanceRecord,
    AttendanceSummary,
    ClassSession,
    Course,
    DailyAttendance,
    MonthlyTimesheet,
    SessionAttendance,
    StaffSchedule,
    TeacherAssignment,
    TimesheetApproval,
    WorkShift,
)
from .utils import calculate_gross_salary, get_attendance_summary_data, get_monthly_timesheet_data


def dashboard(request):
    return redirect('attendance:daily_attendance_form')


def _paginate(request, queryset, per_page=15):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def _month_end(year, month):
    start_date = datetime(year, month, 1).date()
    return (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


@login_required
def work_shift_list(request):
    page_obj = _paginate(request, WorkShift.objects.all().order_by('code'), 10)
    return render(request, 'attendance/work_shift_list.html', {
        'work_shifts': page_obj,
        'page_obj': page_obj,
    })


@login_required
def work_shift_form(request, id=None):
    work_shift = get_object_or_404(WorkShift, id=id) if id else None

    if request.method == 'POST':
        form = WorkShiftForm(request.POST, instance=work_shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã lưu ca làm việc.')
            return redirect('attendance:work_shift_list')
        messages.error(request, 'Dữ liệu ca làm việc chưa hợp lệ.')
    else:
        form = WorkShiftForm(instance=work_shift)

    return render(request, 'attendance/work_shift_form.html', {
        'form': form,
        'work_shift': work_shift,
    })


@login_required
def work_shift_detail(request, id):
    work_shift = get_object_or_404(WorkShift, id=id)
    return render(request, 'attendance/work_shift_detail.html', {'work_shift': work_shift})


@login_required
def work_shift_delete(request, id):
    work_shift = get_object_or_404(WorkShift, id=id)
    if request.method == 'POST':
        work_shift.delete()
        messages.success(request, 'Đã xóa ca làm việc.')
        return redirect('attendance:work_shift_list')
    work_shift.delete()
    messages.success(request, 'Đã xóa ca làm việc.')
    return redirect('attendance:work_shift_list')


@login_required
def schedule_list(request):
    selected_date = request.GET.get('date', '')
    employee_id = request.GET.get('employee', '')
    shift_id = request.GET.get('shift', '')

    schedules = StaffSchedule.objects.select_related('employee', 'employee__position', 'work_shift')
    if selected_date:
        try:
            schedules = schedules.filter(date=datetime.strptime(selected_date, '%Y-%m-%d').date())
        except ValueError:
            messages.warning(request, 'Ngày lọc không hợp lệ.')
    if employee_id:
        schedules = schedules.filter(employee_id=employee_id)
    if shift_id:
        schedules = schedules.filter(work_shift_id=shift_id)

    page_obj = _paginate(request, schedules, 15)
    return render(request, 'attendance/schedule_list.html', {
        'page_obj': page_obj,
        'schedules': page_obj,
        'employees': Employee.objects.filter(is_active=True).order_by('code'),
        'work_shifts': WorkShift.objects.all().order_by('code'),
        'selected_date': selected_date,
        'employee_filter': employee_id,
        'shift_filter': shift_id,
    })


@login_required
def schedule_form(request):
    if request.method == 'POST':
        form = StaffScheduleForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            work_shift = form.cleaned_data['work_shift']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            weekdays = {int(day) for day in form.cleaned_data['weekdays']}
            expected_work_days = form.cleaned_data['expected_work_days']
            note = form.cleaned_data['note']
            created_count = 0
            updated_count = 0
            current_date = start_date

            while current_date <= end_date:
                if current_date.weekday() in weekdays:
                    _, created = StaffSchedule.objects.update_or_create(
                        employee=employee,
                        date=current_date,
                        work_shift=work_shift,
                        defaults={
                            'expected_work_days': expected_work_days,
                            'status': 'planned',
                            'note': note,
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                current_date += timedelta(days=1)

            messages.success(request, f'Đã tạo {created_count} lịch và cập nhật {updated_count} lịch hiện có.')
            return redirect('attendance:schedule_list')
    else:
        form = StaffScheduleForm()

    work_shift_days = {
        str(shift.id): float(shift.work_days)
        for shift in WorkShift.objects.all()
    }
    return render(request, 'attendance/schedule_form.html', {
        'form': form,
        'work_shift_days': work_shift_days,
    })


@login_required
def schedule_delete(request, id):
    schedule = get_object_or_404(StaffSchedule, id=id)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Đã xóa lịch làm việc.')
        return redirect('attendance:schedule_list')
    return render(request, 'attendance/schedule_confirm_delete.html', {'schedule': schedule})


@login_required
def course_list(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    courses = Course.objects.all().order_by('code')
    if search_query:
        courses = courses.filter(Q(code__icontains=search_query) | Q(name__icontains=search_query))
    if status_filter == 'active':
        courses = courses.filter(is_active=True)
    elif status_filter == 'inactive':
        courses = courses.filter(is_active=False)

    page_obj = _paginate(request, courses, 15)
    return render(request, 'attendance/course_list.html', {
        'courses': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required
def course_form(request, id=None):
    course = get_object_or_404(Course, id=id) if id else None
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã lưu lớp/khóa học.')
            return redirect('attendance:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'attendance/course_form.html', {'form': form, 'course': course})


@login_required
def session_list(request):
    selected_date = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    sessions = ClassSession.objects.select_related('course').prefetch_related('assignments__employee')
    if selected_date:
        try:
            sessions = sessions.filter(date=datetime.strptime(selected_date, '%Y-%m-%d').date())
        except ValueError:
            messages.warning(request, 'Ngày lọc không hợp lệ.')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    page_obj = _paginate(request, sessions, 15)
    return render(request, 'attendance/session_list.html', {
        'sessions': page_obj,
        'page_obj': page_obj,
        'selected_date': selected_date,
        'status_filter': status_filter,
        'status_choices': ClassSession.STATUS_CHOICES,
    })


@login_required
def session_form(request):
    if request.method == 'POST':
        form = ClassSessionForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            teacher = form.cleaned_data['teacher']
            assistant = form.cleaned_data['assistant']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            weekdays = {int(day) for day in form.cleaned_data['weekdays']}
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            expected_hours = form.cleaned_data['expected_hours']
            created_count = 0
            current_date = start_date

            with transaction.atomic():
                while current_date <= end_date:
                    if current_date.weekday() in weekdays:
                        session = ClassSession.objects.create(
                            course=course,
                            date=current_date,
                            start_time=start_time,
                            end_time=end_time,
                            room=form.cleaned_data['room'],
                            note=form.cleaned_data['note'],
                        )
                        hours = expected_hours or Decimal(str(session.planned_hours))
                        TeacherAssignment.objects.create(
                            class_session=session,
                            employee=teacher,
                            role='teacher',
                            expected_hours=hours,
                        )
                        if assistant:
                            TeacherAssignment.objects.create(
                                class_session=session,
                                employee=assistant,
                                role='assistant',
                                expected_hours=hours,
                            )
                        created_count += 1
                    current_date += timedelta(days=1)

            messages.success(request, f'Đã tạo {created_count} buổi học.')
            return redirect('attendance:session_list')
        messages.error(request, 'Không thể tạo lịch buổi dạy. Vui lòng kiểm tra các lỗi trong form.')
    else:
        form = ClassSessionForm()

    return render(request, 'attendance/session_form.html', {'form': form})


@login_required
def daily_attendance_entry(request):
    selected_date_str = request.POST.get('selected_date') or request.GET.get('selected_date') or timezone.now().strftime('%Y-%m-%d')
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = timezone.now().date()

    staff_schedules = StaffSchedule.objects.filter(
        date=selected_date,
        status='planned',
    ).select_related('employee', 'employee__position', 'work_shift').order_by('employee__code', 'work_shift__start_time')
    assignments = TeacherAssignment.objects.filter(
        class_session__date=selected_date,
    ).select_related('employee', 'class_session', 'class_session__course').order_by('class_session__start_time')

    if request.method == 'POST':
        staff_ids = [key.split('_')[-1] for key in request.POST.keys() if key.startswith('staff_schedule_id_')]
        assignment_ids = [key.split('_')[-1] for key in request.POST.keys() if key.startswith('assignment_id_')]
        saved_staff = 0
        saved_teaching = 0

        with transaction.atomic():
            for schedule in staff_schedules.filter(id__in=staff_ids):
                form = DailyAttendanceForm(request.POST, prefix=f'staff_{schedule.id}')
                if not form.is_valid():
                    messages.warning(request, f'Dữ liệu của {schedule.employee.full_name} chưa hợp lệ.')
                    continue

                attendance, _ = DailyAttendance.objects.get_or_create(
                    staff_schedule=schedule,
                    employee=schedule.employee,
                    date=selected_date,
                    defaults={
                        'work_shift': schedule.work_shift,
                        'paid_work_days': float(schedule.expected_work_days),
                        'actual_work_days': float(schedule.expected_work_days),
                    },
                )
                attendance.work_shift = schedule.work_shift
                attendance.paid_work_days = form.cleaned_data['paid_work_days']
                attendance.actual_work_days = form.cleaned_data['actual_work_days']
                attendance.check_in_time = form.cleaned_data['check_in_time']
                attendance.check_out_time = form.cleaned_data['check_out_time']
                attendance.attendance_status = form.cleaned_data['attendance_status']
                attendance.save()
                saved_staff += 1

            for assignment in assignments.filter(id__in=assignment_ids):
                status = request.POST.get(f'assignment_{assignment.id}-status', 'taught')
                paid_hours = Decimal(request.POST.get(f'assignment_{assignment.id}-paid_hours') or assignment.expected_hours)
                note = request.POST.get(f'assignment_{assignment.id}-note', '')
                attendance, _ = SessionAttendance.objects.get_or_create(assignment=assignment)
                attendance.status = status
                attendance.paid_hours = paid_hours
                attendance.approved = True
                attendance.note = note
                attendance.save()
                saved_teaching += 1

        messages.success(request, f'Đã lưu {saved_staff} dòng ca vận hành và {saved_teaching} dòng buổi dạy.')
        return redirect(f'{request.path}?selected_date={selected_date:%Y-%m-%d}')

    staff_rows = []
    for schedule in staff_schedules:
        attendance = DailyAttendance.objects.filter(staff_schedule=schedule).first()
        staff_rows.append({
            'schedule': schedule,
            'employee': schedule.employee,
            'work_shift': schedule.work_shift,
            'check_in_time': attendance.check_in_time.strftime('%H:%M') if attendance and attendance.check_in_time else '',
            'check_out_time': attendance.check_out_time.strftime('%H:%M') if attendance and attendance.check_out_time else '',
            'attendance_status': attendance.attendance_status if attendance else 'not_absent',
            'paid_work_days': attendance.paid_work_days if attendance else schedule.expected_work_days,
            'actual_work_days': attendance.actual_work_days if attendance else schedule.expected_work_days,
        })

    teaching_rows = []
    for assignment in assignments:
        try:
            attendance = assignment.attendance
        except SessionAttendance.DoesNotExist:
            attendance = None
        teaching_rows.append({
            'assignment': assignment,
            'attendance': attendance,
            'status': attendance.status if attendance else 'taught',
            'paid_hours': attendance.paid_hours if attendance else assignment.expected_hours,
            'approved': attendance.approved if attendance else False,
            'note': attendance.note if attendance else '',
        })

    return render(request, 'attendance/daily_attendance_form.html', {
        'selected_date': selected_date,
        'employee_forms': staff_rows,
        'teaching_rows': teaching_rows,
        'session_status_choices': SessionAttendance.STATUS_CHOICES,
    })


@login_required
def attendance_summary(request):
    timesheet_type = request.GET.get('type', '')
    timesheets = MonthlyTimesheet.objects.select_related('position').order_by('-year', '-month', 'position__code')
    if timesheet_type:
        timesheets = timesheets.filter(timesheet_type=timesheet_type)
    page_obj = _paginate(request, timesheets, 10)
    return render(request, 'attendance/attendance_summary.html', {
        'attendance_summaries': page_obj,
        'timesheets': page_obj,
        'page_obj': page_obj,
        'positions': Position.objects.filter(is_active=True).order_by('code'),
        'timesheet_type': timesheet_type,
        'timesheet_type_choices': MonthlyTimesheet.TIMESHEET_TYPE_CHOICES,
    })


@login_required
def attendance_summary_form(request, id=None):
    timesheet = get_object_or_404(MonthlyTimesheet, id=id) if id else None
    if request.method == 'POST':
        form = MonthlyTimesheetForm(request.POST, instance=timesheet)
        if form.is_valid():
            timesheet = form.save(commit=False)
            if not timesheet.name:
                type_label = dict(MonthlyTimesheet.TIMESHEET_TYPE_CHOICES).get(timesheet.timesheet_type, 'Bảng công')
                timesheet.name = f'Bảng công {type_label.lower()} {timesheet.month}/{timesheet.year} - {timesheet.position.name}'
            timesheet.save()
            messages.success(request, 'Đã lưu bảng công tháng.')
            return redirect('attendance:attendance_summary_view', id=timesheet.id)
    else:
        initial = {}
        if not timesheet:
            today = timezone.now().date()
            initial = {'month': today.month, 'year': today.year}
        form = MonthlyTimesheetForm(instance=timesheet, initial=initial)
    return render(request, 'attendance/attendance_summary_form.html', {
        'form': form,
        'attendance_summary': timesheet,
        'timesheet': timesheet,
    })


@login_required
def attendance_summary_view(request, id):
    timesheet = get_object_or_404(MonthlyTimesheet.objects.select_related('position'), id=id)
    employee_data = get_monthly_timesheet_data(timesheet)
    adjustment_form = AttendanceAdjustmentForm(position=timesheet.position)
    return render(request, 'attendance/attendance_summary_view.html', {
        'attendance_summary': timesheet,
        'timesheet': timesheet,
        'employee_data': employee_data,
        'adjustment_form': adjustment_form,
        'is_operations': timesheet.timesheet_type == 'operations',
        'is_teaching': timesheet.timesheet_type == 'teaching',
    })


@login_required
@require_POST
def timesheet_add_adjustment(request, id):
    timesheet = get_object_or_404(MonthlyTimesheet, id=id)
    form = AttendanceAdjustmentForm(request.POST, position=timesheet.position)
    if form.is_valid():
        adjustment = form.save(commit=False)
        adjustment.monthly_timesheet = timesheet
        adjustment.created_by = request.user
        adjustment.save()
        messages.success(request, 'Đã thêm điều chỉnh công.')
    else:
        messages.error(request, 'Dữ liệu điều chỉnh chưa hợp lệ.')
    return redirect('attendance:attendance_summary_view', id=timesheet.id)


@login_required
@require_POST
def timesheet_lock(request, id):
    timesheet = get_object_or_404(MonthlyTimesheet, id=id)
    timesheet.status = 'locked'
    timesheet.locked_at = timezone.now()
    timesheet.locked_by = request.user
    timesheet.save(update_fields=['status', 'locked_at', 'locked_by', 'updated_at'])
    TimesheetApproval.objects.create(monthly_timesheet=timesheet, action='locked', created_by=request.user)
    messages.success(request, 'Đã khóa bảng công tháng.')
    return redirect('attendance:attendance_summary_view', id=timesheet.id)


@login_required
def attendance_summary_delete(request, id):
    timesheet = get_object_or_404(MonthlyTimesheet, id=id)
    timesheet.delete()
    messages.success(request, 'Đã xóa bảng công tháng.')
    return redirect('attendance:attendance_summary')


@login_required
def transfer_to_payroll(request, summary_id):
    timesheet = get_object_or_404(MonthlyTimesheet, pk=summary_id)
    if timesheet.transferred:
        messages.warning(request, 'Bảng công này đã được chuyển tính lương trước đó.')
        return redirect('attendance:attendance_summary_view', id=summary_id)
    if timesheet.status != 'locked':
        messages.warning(request, 'Chỉ được chuyển tính lương sau khi khóa bảng công.')
        return redirect('attendance:attendance_summary_view', id=summary_id)

    employee_data = get_monthly_timesheet_data(timesheet)
    if request.method == 'POST':
        payroll = Payroll.objects.create(
            user=request.user,
            name=f'Bảng lương {timesheet.get_timesheet_type_display().lower()} tháng {timesheet.month}/{timesheet.year} - {timesheet.position.name}',
            month=timesheet.month,
            year=timesheet.year,
            position=timesheet.position,
            monthly_timesheet=timesheet,
            status='draft',
            created_by=request.user,
        )
        for row in employee_data:
            employee = row['employee']
            salary_data = calculate_gross_salary(employee, row, timesheet.end_date)
            gross_salary = int(Decimal(str(salary_data['gross_salary'])))
            deduction_amount = int(Decimal(str(gross_salary)) * Decimal('0.1'))
            PayrollDetail.objects.create(
                payroll=payroll,
                employee=employee,
                basic_salary=salary_data['base_amount'],
                attendance_ratio=row.get('attendance_ratio', Decimal('0')),
                standard_workdays=row.get('standard_work_days', 0),
                actual_workdays=row.get('actual_workdays', 0),
                unpaid_leave=row.get('unpaid_leave', 0),
                gross_salary=gross_salary,
                deduction_amount=deduction_amount,
                note=f"salary_type={salary_data['salary_type']}; teaching_hours={row.get('teaching_paid_hours', 0)}",
            )
        timesheet.transferred = True
        timesheet.status = 'transferred'
        timesheet.save(update_fields=['transferred', 'status', 'updated_at'])
        messages.success(request, 'Đã chuyển bảng công tháng sang bảng lương.')
        return redirect('payroll_detail', pk=payroll.pk)

    return render(request, 'attendance/transfer_to_payroll.html', {
        'attendance_summary': timesheet,
        'timesheet': timesheet,
        'employee_data': employee_data,
        'is_operations': timesheet.timesheet_type == 'operations',
        'is_teaching': timesheet.timesheet_type == 'teaching',
    })


def attendance_summary_edit(request, id):
    return redirect('attendance:attendance_summary_edit_form', id=id)


def attendance_summary_list(request):
    return redirect('attendance:attendance_summary')


def attendance_list(request):
    return redirect('attendance:attendance_summary')


def attendance_dashboard(request):
    return redirect('attendance:daily_attendance_form')


def daily_attendance_form(request):
    return daily_attendance_entry(request)


# Legacy detailed-sheet endpoints are intentionally hidden from the new workflow.
def attendance_detail_list(request):
    return redirect('attendance:attendance_summary')


def attendance_detail_form(request, id=None):
    return redirect('attendance:attendance_summary')


def attendance_detail_delete(request, id):
    return redirect('attendance:attendance_summary')


def attendance_detail_view(request, id):
    return redirect('attendance:attendance_summary')


def attendance_detail_save(request):
    return redirect('attendance:attendance_summary')


def export_attendance_to_excel(request, record_id):
    return JsonResponse({'status': 'disabled', 'message': 'Bảng công chi tiết cũ đã được ẩn khỏi workflow mới.'})


def import_attendance_from_excel(request, record_id):
    return redirect('attendance:attendance_summary')


def get_attendance_detail(request, record_id, employee_id, date):
    return get_daily_attendance(request, record_id, employee_id, date)


def update_attendance_detail(request, record_id, employee_id, date):
    return update_daily_attendance(request, record_id, employee_id, date)


def get_daily_attendance(request, record_id, employee_id, date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        attendance = DailyAttendance.objects.filter(employee_id=employee_id, date=date).first()
        return JsonResponse({
            'paid_work_days': attendance.paid_work_days if attendance else 1,
            'actual_work_days': attendance.actual_work_days if attendance else 1,
            'check_in_time': attendance.check_in_time.strftime('%H:%M') if attendance and attendance.check_in_time else '',
            'check_out_time': attendance.check_out_time.strftime('%H:%M') if attendance and attendance.check_out_time else '',
            'attendance_status': attendance.attendance_status if attendance else 'not_absent',
        })
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)


def update_daily_attendance(request, record_id, employee_id, date_str):
    return JsonResponse({'status': 'disabled', 'message': 'Vui lòng chấm công ở màn hình Chấm công hôm nay.'})
