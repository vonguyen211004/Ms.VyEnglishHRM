from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from employees.models import Employee

@login_required
def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_profile(request):
    """View user profile"""
    try:
        employee = Employee.objects.filter(email=request.user.email).first() if request.user.email else None
    except Exception:
        employee = None
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'profile.html', context)

from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view with Vietnamese template"""
    template_name = 'change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('user_profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Mật khẩu đã được thay đổi thành công!')
        return super().form_valid(form)