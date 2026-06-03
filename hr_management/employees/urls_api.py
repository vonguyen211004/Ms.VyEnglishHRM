from django.urls import path
from . import api_views

urlpatterns = [
    path('employees/search/', api_views.employee_search, name='api_employee_search'),
]
