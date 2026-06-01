from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='attendance_dashboard'),

    # Chấm công hàng ngày
    path('daily-attendance/', views.daily_attendance_form, name='daily_attendance_form'),

    # Ca làm việc
    path('work-shifts/', views.work_shift_list, name='work_shift_list'),
    path('work-shifts/add/', views.work_shift_form, name='work_shift_add'),
    path('work-shifts/edit/<int:id>/', views.work_shift_form, name='work_shift_edit'),
    path('work-shifts/detail/<int:id>/', views.work_shift_detail, name='work_shift_detail'),
    path('work-shifts/delete/<int:id>/', views.work_shift_delete, name='work_shift_delete'),

    # Bảng chấm công chi tiết
    path('attendance-details/', views.attendance_detail_list, name='attendance_detail_list'),
    path('attendance-details/add/', views.attendance_detail_form, name='attendance_detail_add'),
    path('attendance-details/edit/<int:id>/', views.attendance_detail_form, name='attendance_detail_edit'),
    path('attendance-details/delete/<int:id>/', views.attendance_detail_delete, name='attendance_detail_delete'),
    path('attendance-details/view/<int:id>/', views.attendance_detail_view, name='attendance_detail_view'),
    path('attendance-details/save/', views.attendance_detail_save, name='attendance_detail_save'),
    path('attendance-details/export/<int:record_id>/', views.export_attendance_to_excel, name='export_attendance_to_excel'),
    path('attendance-details/import/<int:record_id>/', views.import_attendance_from_excel, name='import_attendance_from_excel'),

    # API chấm công chi tiết
    path('attendance-details/get/<int:record_id>/<int:employee_id>/<str:date>/', views.get_attendance_detail, name='get_attendance_detail'),
    path('attendance-details/update/<int:record_id>/<int:employee_id>/<str:date>/', views.update_attendance_detail, name='update_attendance_detail'),
    path('attendance-details/daily-get/<int:record_id>/<int:employee_id>/<str:date_str>/', views.get_daily_attendance, name='get_daily_attendance'),
    path('attendance-details/daily-update/<int:record_id>/<int:employee_id>/<str:date_str>/', views.update_daily_attendance, name='update_daily_attendance'),

    # Bảng chấm công tổng hợp
    path('summary/', views.attendance_summary, name='attendance_summary'),
    path('summary/add/', views.attendance_summary_form, name='attendance_summary_add'),
    path('summary/edit/<int:id>/', views.attendance_summary_form, name='attendance_summary_edit_form'),
    path('summary/<int:id>/', views.attendance_summary_view, name='attendance_summary_view'),
    path('summary/<int:id>/edit/', views.attendance_summary_edit, name='attendance_summary_edit'),
    path('summary/<int:id>/delete/', views.attendance_summary_delete, name='attendance_summary_delete'),

    # Chuyển tính lương
    path('summary/<int:summary_id>/transfer/', views.transfer_to_payroll, name='transfer_to_payroll'),
]