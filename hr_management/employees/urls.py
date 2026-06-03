from django.urls import path
from . import views

urlpatterns = [
    # Employee URLs
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/update/', views.employee_update, name='employee_update'),
    path('<int:pk>/deactivate/', views.employee_deactivate, name='employee_deactivate'),
    path('<int:pk>/activate/', views.employee_activate, name='employee_activate'),
    path('<int:pk>/contracts/', views.employee_contracts, name='employee_contracts'),

    # Contract URLs
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/create/', views.contract_create, name='contract_create'),
    path('contracts/new/', views.contract_create_general, name='contract_create_general'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract_detail'),
    path('contracts/<int:pk>/update/', views.contract_update, name='contract_update'),
    path('contracts/<int:pk>/terminate/', views.contract_terminate, name='contract_terminate'),
    path('contracts/<int:pk>/download/', views.contract_download, name='contract_download'),
    path('<int:employee_id>/contracts/create/', views.contract_create, name='employee_contract_create'),
    path('contracts/<int:pk>/delete/', views.contract_delete, name='contract_delete'),

    # Personnel URLs
    path('overview/', views.personnel_overview, name='personnel_overview'),
    path('profile/', views.personnel_profile, name='personnel_profile'),
]
