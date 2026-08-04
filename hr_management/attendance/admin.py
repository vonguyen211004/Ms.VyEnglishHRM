from django.contrib import admin

from .models import (
    AttendanceAdjustment,
    AttendanceRecord,
    AttendanceSummary,
    ClassSession,
    Course,
    DailyAttendance,
    EmployeeAttendance,
    EmployeeSchedule,
    MonthlyTimesheet,
    SessionAttendance,
    StaffSchedule,
    TeacherAssignment,
    TimesheetApproval,
    WorkShift,
)


@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'start_time', 'end_time', 'work_days', 'work_hours')
    search_fields = ('name', 'code')


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'work_shift', 'expected_work_days', 'status')
    list_filter = ('date', 'work_shift', 'status')
    search_fields = ('employee__full_name', 'employee__code', 'work_shift__name', 'work_shift__code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'level')
    search_fields = ('code', 'name')


class TeacherAssignmentInline(admin.TabularInline):
    model = TeacherAssignment
    extra = 1


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'start_time', 'end_time', 'room', 'status')
    list_filter = ('date', 'status', 'course')
    search_fields = ('course__code', 'course__name', 'room')
    inlines = [TeacherAssignmentInline]


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('class_session', 'employee', 'role', 'expected_hours', 'pay_multiplier')
    list_filter = ('role', 'class_session__date')
    search_fields = ('employee__full_name', 'employee__code', 'class_session__course__name')


@admin.register(SessionAttendance)
class SessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'status', 'paid_hours', 'approved')
    list_filter = ('status', 'approved', 'assignment__class_session__date')
    search_fields = ('assignment__employee__full_name', 'assignment__class_session__course__name')


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'work_shift', 'attendance_status', 'paid_work_days', 'actual_work_days')
    list_filter = ('date', 'attendance_status', 'work_shift')
    search_fields = ('employee__full_name', 'employee__code')


@admin.register(MonthlyTimesheet)
class MonthlyTimesheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'month', 'year', 'status', 'transferred')
    list_filter = ('year', 'month', 'position', 'status', 'transferred')
    search_fields = ('name', 'position__name')


@admin.register(TimesheetApproval)
class TimesheetApprovalAdmin(admin.ModelAdmin):
    list_display = ('monthly_timesheet', 'action', 'created_by', 'created_at')
    list_filter = ('action', 'created_at')


@admin.register(AttendanceAdjustment)
class AttendanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('monthly_timesheet', 'employee', 'adjustment_type', 'value', 'created_at')
    list_filter = ('adjustment_type', 'created_at')
    search_fields = ('employee__full_name', 'employee__code', 'reason')


# Legacy data models kept registered for maintenance only.
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'attendance_type')
    list_filter = ('start_date', 'end_date', 'attendance_type')
    search_fields = ('name',)


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'work_shift', 'expected_work_days')
    list_filter = ('date', 'work_shift')
    search_fields = ('employee__full_name', 'employee__code', 'work_shift__name', 'work_shift__code')


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'month', 'year', 'transferred')
    list_filter = ('year', 'month', 'position', 'transferred')
    search_fields = ('name',)


@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance_summary', 'workdays', 'paid_leave', 'unpaid_leave', 'policy_leave')
    search_fields = ('employee__full_name', 'employee__code', 'attendance_summary__name')
