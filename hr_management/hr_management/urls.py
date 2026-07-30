from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, login_view, logout_view, user_profile, CustomPasswordChangeView

#TEST
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if User.objects.filter(username='admin').exists():
        return HttpResponse('Admin already exists')

    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='test123456'
    )
    return HttpResponse('Admin created')

urlpatterns = [
    #TEST
    path('create-admin-temp/', create_admin),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', user_profile, name='user_profile'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('admin/', admin.site.urls),

    # App URLs
    path('employees/', include('employees.urls')),
    path('api/', include('employees.urls_api')),
    path('payroll/', include('payroll.urls')),
    path('attendance/', include('attendance.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
