from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_list, name='payroll_list'),
    path('create/', views.payroll_create, name='payroll_create'),
    path('<int:pk>/', views.payroll_detail, name='payroll_detail'),
    path('<int:pk>/update/', views.payroll_update, name='payroll_update'),
    path('<int:pk>/activate/', views.activate_payroll, name='activate_payroll'),
    path('<int:pk>/disable/', views.disable_payroll, name='disable_payroll'),
    path('<int:pk>/export/', views.export_payroll_excel, name='export_payroll_excel'),

    path('<int:payroll_id>/detail/<int:detail_id>/', views.payroll_employee_detail, name='payroll_employee_detail'),
    path('calculate/', views.calculate_payroll, name='calculate_payroll'),

    # Chuyển tính lương từ bảng chấm công
    path('transfer/<int:attendance_summary_id>/', views.transfer_to_payroll, name='transfer_to_payroll'),
]