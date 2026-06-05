from django.urls import path
from . import api_views

urlpatterns = [
    path('employees/search/', api_views.employee_search, name='api_employee_search'),
    path('employees/parse-cv/', api_views.parse_cv_api, name='api_parse_cv'),
]
