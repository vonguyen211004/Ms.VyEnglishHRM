from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.personnel_overview, name='personnel_overview'),
    path('profile/', views.personnel_profile, name='personnel_profile'),
]
