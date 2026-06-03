from django.contrib import admin
from .models import Department, Position, Employee, Contract, WorkHistory, SalaryHistory

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('department', 'is_active')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('code', 'full_name', 'position', 'phone', 'is_active')
    search_fields = ('code', 'full_name', 'phone', 'email')
    list_filter = ('position', 'is_active', 'gender', 'education_level')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'first_name', 'last_name', 'gender', 'date_of_birth')
        }),
        ('Thông tin liên hệ', {
            'fields': ('phone', 'email', 'id_number', 'address')
        }),
        ('Thông tin công việc', {
            'fields': ('position', 'join_date', 'is_active')
        }),
        ('Thông tin bằng cấp', {
            'fields': ('education_level', 'degree', 'major')
        }),
        ('Thông tin lương', {
            'fields': ('basic_salary',)
        }),
    )

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('employee', 'contract_number', 'contract_type', 'start_date', 'end_date', 'basic_salary', 'is_active')
    search_fields = ('employee__full_name', 'employee__code', 'contract_number')
    list_filter = ('contract_type', 'is_active')
    date_hierarchy = 'start_date'

@admin.register(WorkHistory)
class WorkHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'position', 'start_date', 'end_date')
    search_fields = ('employee__full_name', 'company', 'position')
    list_filter = ('start_date',)

@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'effective_date', 'old_salary', 'new_salary')
    search_fields = ('employee__full_name',)
    list_filter = ('effective_date',)
