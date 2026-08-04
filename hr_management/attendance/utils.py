import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.shortcuts import get_object_or_404

from employees.models import Employee
from .models import (
    AttendanceAdjustment,
    AttendanceSummary,
    DailyAttendance,
    EmployeeSchedule,
    MonthlyTimesheet,
    SessionAttendance,
    StaffSchedule,
    TeacherAssignment,
)


logger = logging.getLogger(__name__)


def _working_days_without_sunday(start_date, end_date):
    total = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() != 6:
            total += 1
        current_date += timedelta(days=1)
    return total


def _minutes_late_or_early(attendance):
    if not attendance.work_shift:
        return 0

    minutes = 0
    if attendance.check_in_time and attendance.work_shift.check_in_end:
        check_in = (
            attendance.check_in_time.hour * 3600
            + attendance.check_in_time.minute * 60
            + attendance.check_in_time.second
        )
        allowed_check_in = (
            attendance.work_shift.check_in_end.hour * 3600
            + attendance.work_shift.check_in_end.minute * 60
            + attendance.work_shift.check_in_end.second
        )
        if check_in > allowed_check_in:
            minutes += (check_in - allowed_check_in) // 60

    if attendance.check_out_time and attendance.work_shift.check_out_start:
        check_out = (
            attendance.check_out_time.hour * 3600
            + attendance.check_out_time.minute * 60
            + attendance.check_out_time.second
        )
        allowed_check_out = (
            attendance.work_shift.check_out_start.hour * 3600
            + attendance.work_shift.check_out_start.minute * 60
            + attendance.work_shift.check_out_start.second
        )
        if check_out < allowed_check_out:
            minutes += (allowed_check_out - check_out) // 60

    return minutes


def _date_range_from_legacy_summary(attendance_summary):
    if attendance_summary.start_date and attendance_summary.end_date:
        return attendance_summary.start_date, attendance_summary.end_date

    records = attendance_summary.attendance_records.all()
    if records:
        return (
            min(record.start_date for record in records),
            max(record.end_date for record in records),
        )

    today = datetime.now().date()
    return today, today


def get_monthly_timesheet_data(monthly_timesheet_or_id):
    """Return payroll-ready rows for the new center-oriented attendance flow."""
    try:
        if isinstance(monthly_timesheet_or_id, (int, str)):
            timesheet = get_object_or_404(MonthlyTimesheet, id=monthly_timesheet_or_id)
        else:
            timesheet = monthly_timesheet_or_id

        start_date = timesheet.start_date
        end_date = timesheet.end_date
        is_operations = getattr(timesheet, 'timesheet_type', 'operations') == 'operations'
        is_teaching = getattr(timesheet, 'timesheet_type', 'operations') == 'teaching'
        employees = Employee.objects.filter(
            position=timesheet.position,
            is_active=True,
        ).select_related('position').order_by('code')

        rows = []
        for employee in employees:
            staff_schedules = StaffSchedule.objects.filter(
                employee=employee,
                date__range=[start_date, end_date],
                status='planned',
            ).select_related('work_shift')
            staff_attendances = DailyAttendance.objects.filter(
                employee=employee,
                date__range=[start_date, end_date],
                staff_schedule__isnull=False,
            ).select_related('work_shift', 'staff_schedule')
            if not is_operations:
                staff_schedules = StaffSchedule.objects.none()
                staff_attendances = DailyAttendance.objects.none()

            teaching_assignments = TeacherAssignment.objects.filter(
                employee=employee,
                class_session__date__range=[start_date, end_date],
            ).select_related('class_session', 'class_session__course')
            if not is_teaching:
                teaching_assignments = TeacherAssignment.objects.none()
            session_attendances = SessionAttendance.objects.filter(
                assignment__in=teaching_assignments,
            ).select_related('assignment', 'assignment__class_session')

            standard_staff_days = sum(Decimal(str(item.expected_work_days)) for item in staff_schedules)
            standard_teaching_hours = sum(Decimal(str(item.expected_hours)) for item in teaching_assignments)

            actual_workdays = Decimal('0')
            paid_workdays = Decimal('0')
            paid_leave = Decimal('0')
            policy_leave = Decimal('0')
            unpaid_leave = Decimal('0')
            normal_work_days = Decimal('0')
            rest_work_days = Decimal('0')
            worked_hours = Decimal('0')
            late_early_minutes = 0

            for attendance in staff_attendances:
                expected_days = Decimal(str(
                    attendance.staff_schedule.expected_work_days
                    if attendance.staff_schedule
                    else attendance.work_shift.work_days if attendance.work_shift
                    else 1
                ))

                if attendance.attendance_status == 'unpermitted_absence':
                    unpaid_leave += expected_days
                    late_early_minutes += _minutes_late_or_early(attendance)
                    continue

                if attendance.attendance_status == 'permitted_absence':
                    paid_leave += Decimal(str(attendance.paid_work_days))
                elif attendance.attendance_status == 'regime_absence':
                    policy_leave += Decimal(str(attendance.paid_work_days))
                else:
                    actual_workdays += Decimal(str(attendance.actual_work_days))
                    paid_workdays += Decimal(str(attendance.paid_work_days))

                    if attendance.work_shift:
                        coefficient = Decimal(str(
                            attendance.work_shift.rest_day_coefficient
                            if attendance.date.weekday() >= 5
                            else attendance.work_shift.normal_day_coefficient
                        ))
                        actual_days = Decimal(str(attendance.actual_work_days))
                        if attendance.date.weekday() >= 5:
                            rest_work_days += actual_days * coefficient
                        else:
                            normal_work_days += actual_days * coefficient
                        worked_hours += actual_days * Decimal(str(attendance.work_shift.work_hours or 0))

                late_early_minutes += _minutes_late_or_early(attendance)

            teaching_paid_hours = Decimal('0')
            teaching_unpaid_hours = Decimal('0')
            taught_sessions = Decimal('0')
            absent_teaching_sessions = Decimal('0')
            assigned_sessions = Decimal(str(teaching_assignments.count()))
            for attendance in session_attendances:
                expected_hours = Decimal(str(attendance.assignment.expected_hours))
                if attendance.status in {'taught', 'online', 'makeup'}:
                    teaching_paid_hours += Decimal(str(attendance.paid_hours))
                    taught_sessions += Decimal('1')
                elif attendance.status in {'absent_unexcused', 'cancelled_by_teacher'}:
                    teaching_unpaid_hours += expected_hours
                    absent_teaching_sessions += Decimal('1')
                elif attendance.status in {'absent_excused', 'cancelled_by_center', 'substituted'}:
                    teaching_paid_hours += Decimal(str(attendance.paid_hours))

            adjustments = AttendanceAdjustment.objects.filter(
                monthly_timesheet=timesheet,
                employee=employee,
            )
            for adjustment in adjustments:
                value = Decimal(str(adjustment.value))
                if adjustment.adjustment_type == 'workday':
                    if is_operations:
                        actual_workdays += value
                        paid_workdays += value
                elif adjustment.adjustment_type == 'hour':
                    if is_teaching:
                        teaching_paid_hours += value
                elif adjustment.adjustment_type == 'paid_leave':
                    if is_operations:
                        paid_leave += value
                elif adjustment.adjustment_type == 'unpaid_leave':
                    unpaid_leave += value

            if is_teaching:
                worked_hours += teaching_paid_hours
                paid_workdays += taught_sessions
                actual_workdays += taught_sessions
                unpaid_leave += absent_teaching_sessions

            paid_days = actual_workdays + paid_leave + policy_leave
            attendance_ratio = Decimal('0')
            if is_operations and standard_staff_days:
                attendance_ratio = paid_days / standard_staff_days
                attendance_ratio = max(Decimal('0'), min(Decimal('1'), attendance_ratio))
            elif is_teaching and standard_teaching_hours:
                attendance_ratio = teaching_paid_hours / standard_teaching_hours
                attendance_ratio = max(Decimal('0'), min(Decimal('1'), attendance_ratio))

            rows.append({
                'employee': employee,
                'standard_work_days': round(float(standard_staff_days), 2),
                'standard_teaching_hours': round(float(standard_teaching_hours), 2),
                'normal_work_days': round(float(normal_work_days), 2),
                'rest_work_days': round(float(rest_work_days), 2),
                'paid_leave': round(float(paid_leave), 2),
                'policy_leave': round(float(policy_leave), 2),
                'late_early_minutes': late_early_minutes,
                'unpaid_leave': round(float(unpaid_leave), 2),
                'actual_workdays': round(float(actual_workdays), 2),
                'paid_workdays': round(float(paid_workdays), 2),
                'worked_hours': round(float(worked_hours), 2),
                'teaching_paid_hours': round(float(teaching_paid_hours), 2),
                'teaching_unpaid_hours': round(float(teaching_unpaid_hours), 2),
                'assigned_sessions': round(float(assigned_sessions), 2),
                'taught_sessions': round(float(taught_sessions), 2),
                'attendance_ratio': attendance_ratio.quantize(Decimal('0.0001')),
            })

        return rows
    except Exception as exc:
        logger.error("Error while building monthly timesheet data: %s", exc)
        return []


def get_attendance_summary_data(attendance_summary_or_id):
    """Compatibility wrapper for old AttendanceSummary and new MonthlyTimesheet."""
    if isinstance(attendance_summary_or_id, MonthlyTimesheet):
        return get_monthly_timesheet_data(attendance_summary_or_id)

    if isinstance(attendance_summary_or_id, (int, str)):
        attendance_summary = get_object_or_404(AttendanceSummary, id=attendance_summary_or_id)
    else:
        attendance_summary = attendance_summary_or_id

    try:
        start_date, end_date = _date_range_from_legacy_summary(attendance_summary)
        attendance_records = attendance_summary.attendance_records.all()
        employees = Employee.objects.filter(
            position=attendance_summary.position,
            is_active=True,
        ).select_related('position')

        rows = []
        for employee in employees:
            schedules = EmployeeSchedule.objects.filter(
                employee=employee,
                date__range=[start_date, end_date],
            ).select_related('work_shift')
            daily_attendances = DailyAttendance.objects.filter(
                attendance_record__in=attendance_records,
                employee=employee,
                date__range=[start_date, end_date],
            ).select_related('work_shift', 'schedule')

            if schedules.exists():
                standard_work_days = sum(float(schedule.expected_work_days) for schedule in schedules)
            else:
                first_attendance = daily_attendances.first()
                work_days_per_day = first_attendance.work_shift.work_days if first_attendance and first_attendance.work_shift else 1
                standard_work_days = _working_days_without_sunday(start_date, end_date) * work_days_per_day

            actual_workdays = 0.0
            paid_workdays = 0.0
            unpaid_leave = 0.0
            worked_hours = 0.0
            late_early_minutes = 0

            for attendance in daily_attendances:
                if attendance.attendance_status == 'unpermitted_absence':
                    unpaid_leave += 1
                    continue
                actual_workdays += float(attendance.actual_work_days)
                paid_workdays += float(attendance.paid_work_days)
                if attendance.work_shift:
                    worked_hours += float(attendance.actual_work_days) * float(attendance.work_shift.work_hours or 0)
                late_early_minutes += _minutes_late_or_early(attendance)

            attendance_ratio = Decimal('0')
            if standard_work_days:
                attendance_ratio = Decimal(str(paid_workdays or actual_workdays)) / Decimal(str(standard_work_days))
                attendance_ratio = max(Decimal('0'), min(Decimal('1'), attendance_ratio))

            rows.append({
                'employee': employee,
                'standard_work_days': round(standard_work_days, 2),
                'standard_teaching_hours': 0,
                'normal_work_days': round(actual_workdays, 2),
                'rest_work_days': 0,
                'paid_leave': 0,
                'policy_leave': 0,
                'late_early_minutes': late_early_minutes,
                'unpaid_leave': round(unpaid_leave, 2),
                'actual_workdays': round(actual_workdays, 2),
                'paid_workdays': round(paid_workdays or actual_workdays, 2),
                'worked_hours': round(worked_hours, 2),
                'teaching_paid_hours': 0,
                'teaching_unpaid_hours': 0,
                'taught_sessions': 0,
                'attendance_ratio': attendance_ratio.quantize(Decimal('0.0001')),
            })
        return rows
    except Exception as exc:
        logger.error("Error while building legacy attendance summary data: %s", exc)
        return []


def get_employee_payroll_basis(employee, on_date=None):
    return employee.get_salary_basis(on_date)


def calculate_gross_salary(employee, employee_info, on_date=None):
    basis = get_employee_payroll_basis(employee, on_date)
    salary_type = basis.get('salary_type') or 'monthly'
    amount = Decimal(str(basis.get('amount') or 0))
    attendance_ratio = Decimal(str(employee_info.get('attendance_ratio', 0)))
    paid_workdays = Decimal(str(employee_info.get('paid_workdays', employee_info.get('actual_workdays', 0))))
    worked_hours = Decimal(str(employee_info.get('worked_hours', 0)))

    if salary_type in {'daily', 'shift'}:
        gross_salary = amount * paid_workdays
    elif salary_type == 'hourly':
        gross_salary = amount * worked_hours
    elif salary_type == 'commission':
        gross_salary = amount
    elif salary_type == 'none':
        gross_salary = Decimal('0')
    else:
        gross_salary = amount * attendance_ratio

    return {
        'salary_type': salary_type,
        'base_amount': amount,
        'gross_salary': gross_salary,
    }
