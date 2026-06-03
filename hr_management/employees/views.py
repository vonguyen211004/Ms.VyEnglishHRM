from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse
import os
from django.conf import settings

from .models import Employee, Position, Contract, WorkHistory, SalaryHistory, Department
from .forms import (EmployeeForm, ContractForm, WorkHistoryForm, SalaryHistoryForm,
                    ContractFilterForm)


# Employee views
def employee_list(request):
    # Lấy tham số tìm kiếm từ request
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')
    status_filter = request.GET.get('status', 'all')  # Mặc định hiển thị tất cả nhân viên

    # Truy vấn cơ sở dữ liệu - Lấy tất cả nhân viên
    employees = Employee.objects.all()

    # Lọc theo trạng thái nếu có
    if status_filter == 'active':
        employees = employees.filter(is_active=True)
    elif status_filter == 'inactive':
        employees = employees.filter(is_active=False)
    # Nếu status_filter là 'all', hiển thị tất cả nhân viên

    # Áp dụng bộ lọc tìm kiếm nếu có
    if search_query:
        employees = employees.filter(
            Q(code__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Lọc theo vị trí nếu có
    if position_filter:
        employees = employees.filter(position_id=position_filter)

    # Lấy danh sách vị trí cho dropdown
    positions = Position.objects.filter(is_active=True)

    # Đảm bảo thông tin vị trí được load đầy đủ
    employees = employees.select_related('position')

    # Phân trang
    paginator = Paginator(employees, 10)  # 10 nhân viên mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'positions': positions,
        'search_query': search_query,
        'position_filter': position_filter,
        'status_filter': status_filter,
    }

    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    contracts = Contract.objects.filter(employee=employee).order_by('-start_date')
    work_history = WorkHistory.objects.filter(employee=employee).order_by('-start_date')
    salary_history = SalaryHistory.objects.filter(employee=employee).order_by('-effective_date')

    context = {
        'employee': employee,
        'contracts': contracts,
        'work_history': work_history,
        'salary_history': salary_history,
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            # Gộp họ tên
            employee.full_name = f"{employee.last_name} {employee.first_name}"
            employee.save()
            messages.success(request, f'Nhân viên {employee.full_name} đã được tạo thành công')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'title': 'Thêm nhân viên mới',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            # Cập nhật full_name trước khi lưu
            employee.full_name = f"{employee.last_name} {employee.first_name}"
            employee.save()
            messages.success(request, f'Thông tin nhân viên {employee.full_name} đã được cập nhật')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'Cập nhật thông tin nhân viên',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_deactivate(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = False
    employee.save()

    # Cập nhật end_date cho tất cả hợp đồng của nhân viên
    active_contracts = Contract.objects.filter(employee=employee, end_date__isnull=True)
    for contract in active_contracts:
        contract.end_date = timezone.now().date()
        contract.save()

    messages.success(request, f'Nhân viên {employee.full_name} đã được vô hiệu hóa.')
    return redirect('employee_list')


@login_required
def employee_activate(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = True
    employee.save()
    messages.success(request, f'Nhân viên {employee.full_name} đã được kích hoạt lại.')
    return redirect('employee_list')


@login_required
def employee_contracts(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    contracts = Contract.objects.filter(employee=employee).order_by('-start_date')

    context = {
        'employee': employee,
        'contracts': contracts,
    }
    return render(request, 'employees/employee_contracts.html', context)


# Contract views
@login_required
def contract_list(request):
    form = ContractFilterForm(request.GET)
    contracts = Contract.objects.all().select_related('employee', 'position')
    today = timezone.now().date()
    expiry_date = today + timezone.timedelta(days=30)  # Ngày hết hạn trong vòng 30 ngày

    # Cập nhật trạng thái hợp đồng trước khi hiển thị
    for contract in contracts:
        # Kiểm tra hợp đồng sắp hết hạn
        contract.is_expiring = (
                contract.is_active and
                contract.end_date and
                contract.end_date <= expiry_date and
                contract.end_date > today
        )

        # Nếu hợp đồng có ngày kết thúc và đã qua ngày kết thúc, đánh dấu là không còn hiệu lực
        if contract.end_date and contract.end_date <= today and contract.is_active:
            contract.is_active = False
            contract.save(update_fields=['is_active'])
        # Nếu hợp đồng đã bị đánh dấu là không còn hiệu lực nhưng không có ngày kết thúc hoặc ngày kết thúc trong tương lai
        elif not contract.is_active and (not contract.end_date or contract.end_date > today):
            # Đây có thể là trường hợp hợp đồng bị chấm dứt thủ công
            if not contract.end_date:
                contract.end_date = today
                contract.save(update_fields=['end_date'])

    if form.is_valid():
        search = form.cleaned_data.get('search')
        contract_type = form.cleaned_data.get('contract_type')
        department = form.cleaned_data.get('department')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        status = form.cleaned_data.get('status')

        if search:
            contracts = contracts.filter(
                Q(contract_number__icontains=search) |
                Q(employee__full_name__icontains=search) |
                Q(employee__code__icontains=search)
            )

        if contract_type:
            contracts = contracts.filter(contract_type=contract_type)

        if department:
            contracts = contracts.filter(
                Q(department=department) |
                Q(position__department=department)
            )

        if date_from:
            contracts = contracts.filter(start_date__gte=date_from)

        if date_to:
            contracts = contracts.filter(start_date__lte=date_to)

        if status == 'active':
            contracts = contracts.filter(is_active=True)
        elif status == 'inactive':
            contracts = contracts.filter(is_active=False)
        elif status == 'expiring':
            # Lọc hợp đồng sắp hết hạn (còn hiệu lực và sẽ hết hạn trong vòng 30 ngày)
            contracts = contracts.filter(
                is_active=True,
                end_date__isnull=False,
                end_date__lte=expiry_date,
                end_date__gt=today
            )

    # Sắp xếp theo ngày ký giảm dần
    contracts = contracts.order_by('-sign_date')

    # Phân trang
    paginator = Paginator(contracts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Thêm thuộc tính is_expiring cho các hợp đồng trong trang hiện tại
    for contract in page_obj:
        contract.is_expiring = (
                contract.is_active and
                contract.end_date and
                contract.end_date <= expiry_date and
                contract.end_date > today
        )

    # Thống kê
    total_contracts = contracts.count()
    active_contracts = contracts.filter(is_active=True).count()
    expiring_contracts = contracts.filter(
        is_active=True,
        end_date__isnull=False,
        end_date__lte=expiry_date,
        end_date__gt=today
    ).count()

    context = {
        'page_obj': page_obj,
        'filter_form': form,
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'expiring_contracts': expiring_contracts,
        'contract_statuses': Contract.CONTRACT_TYPES,
        'contract_types': Contract.CONTRACT_TYPES,
        'today': today,  # Thêm biến today vào context
    }
    return render(request, 'employees/contract_list.html', context)

@login_required
def contract_create(request, employee_id=None):
    """
    Hàm tạo hợp đồng mới.
    Nếu employee_id được cung cấp, tạo hợp đồng cho nhân viên đó.
    Nếu không, hiển thị form để chọn nhân viên và tạo hợp đồng.
    """
    employee = None
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)

    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            if employee:
                contract.employee = employee
            else:
                employee_id = request.POST.get('employee_id')
                if not employee_id:
                    messages.error(request, 'Vui lòng chọn nhân viên')
                    return redirect('contract_create_general')
                employee = get_object_or_404(Employee, pk=employee_id)
                contract.employee = employee

            # Nếu không có ngày ký, sử dụng ngày hiện tại
            if not contract.sign_date:
                contract.sign_date = timezone.now().date()

            # Nếu không có tên hợp đồng, tạo tên mặc định
            if not contract.contract_name:
                contract.contract_name = f"Hợp đồng {contract.get_contract_type_display()} - {employee.full_name}"

            # Nếu không có đơn vị, sử dụng đơn vị của vị trí
            if not contract.department and contract.position and hasattr(contract.position, 'department'):
                contract.department = contract.position.department

            # Nếu là hợp đồng không xác định thời hạn, xóa ngày kết thúc
            if contract.contract_type == 'indefinite':
                contract.end_date = None

            contract.save()
            messages.success(request, f'Hợp đồng mới cho nhân viên {employee.full_name} đã được tạo thành công')

            if 'save_and_new' in request.POST:
                return redirect('contract_create_general')
            return redirect('contract_detail', pk=contract.pk)
    else:
        # Tạo số hợp đồng tự động
        last_contract = Contract.objects.order_by('-contract_number').first()
        next_number = 'HD0000001'
        if last_contract and last_contract.contract_number.startswith('HD'):
            try:
                num = int(last_contract.contract_number[2:])
                next_number = f'HD{(num + 1):07d}'
            except ValueError:
                pass

        initial_data = {
            'contract_number': next_number,
            'sign_date': timezone.now().date(),
            'start_date': timezone.now().date(),
        }

        if employee:
            initial_data['position'] = employee.position
            if employee.position and hasattr(employee.position, 'department'):
                initial_data['department'] = employee.position.department

        form = ContractForm(initial=initial_data)

    context = {
        'form': form,
        'employee': employee,
    }
    return render(request, 'employees/contract_form.html', context)


@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    today = timezone.now().date()

    # Cập nhật trạng thái is_active dựa trên ngày kết thúc
    if contract.end_date and contract.end_date <= today:
        if contract.is_active:
            contract.is_active = False
            contract.save(update_fields=['is_active'])

    context = {
        'contract': contract,
        'today': today,
    }
    return render(request, 'employees/contract_detail.html', context)


@login_required
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            contract = form.save(commit=False)

            # Nếu không có tên hợp đồng, tạo tên mặc định
            if not contract.contract_name:
                contract.contract_name = f"Hợp đồng {contract.get_contract_type_display()} - {contract.employee.full_name}"

            # Nếu là hợp đồng không xác định thời hạn, xóa ngày kết thúc
            if contract.contract_type == 'indefinite':
                contract.end_date = None

            # Cập nhật trạng thái is_active dựa trên ngày kết thúc
            today = timezone.now().date()
            if contract.end_date and contract.end_date <= today:
                contract.is_active = False

            contract.save()
            messages.success(request, 'Hợp đồng đã được cập nhật thành công')
            return redirect('contract_detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)

    context = {
        'form': form,
        'contract': contract,
        'title': 'Cập nhật hợp đồng',
    }
    return render(request, 'employees/contract_form.html', context)


@login_required
def contract_terminate(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    today = timezone.now().date()

    if request.method == 'POST':
        termination_date = request.POST.get('termination_date')
        termination_reason = request.POST.get('termination_reason')

        if termination_date:
            # Chuyển đổi chuỗi ngày thành đối tượng date
            from datetime import datetime
            try:
                # Thử chuyển đổi theo định dạng YYYY-MM-DD
                contract.end_date = datetime.strptime(termination_date, '%Y-%m-%d').date()
            except ValueError:
                # Nếu lỗi, sử dụng ngày hiện tại
                messages.error(request, 'Định dạng ngày không hợp lệ. Sử dụng ngày hiện tại.')
                contract.end_date = today
        else:
            contract.end_date = today

        # Đặt trạng thái hợp đồng thành không còn hiệu lực
        contract.is_active = False
        contract.save()

        messages.success(request, 'Hợp đồng đã được chấm dứt')
        return redirect('contract_detail', pk=contract.pk)

    context = {
        'contract': contract,
        'today': today,
    }
    return render(request, 'employees/contract_terminate.html', context)


@login_required
def contract_download(request, pk):
    """
    Hàm tải xuống file hợp đồng
    """
    contract = get_object_or_404(Contract, pk=pk)

    if not contract.file:
        messages.error(request, 'Không tìm thấy file hợp đồng.')
        return redirect('contract_detail', pk=contract.pk)

    file_path = os.path.join(settings.MEDIA_ROOT, contract.file.name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response

    messages.error(request, 'Không tìm thấy file hợp đồng.')
    return redirect('contract_detail', pk=contract.pk)

@login_required
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.method == 'POST':
        # Lưu thông tin để hiển thị trong thông báo
        contract_number = contract.contract_number
        employee_name = contract.employee.full_name

        # Xóa hợp đồng
        contract.delete()

        messages.success(request, f'Hợp đồng {contract_number} của nhân viên {employee_name} đã được xóa thành công')
        return redirect('contract_list')

    context = {
        'contract': contract,
    }
    return render(request, 'employees/contract_delete.html', context)

# Personnel views
@login_required
def personnel_overview(request):
    total_employees = Employee.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()
    total_positions = Position.objects.count()

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_positions': total_positions,
    }
    return render(request, 'personnel/overview.html', context)


@login_required
def personnel_profile(request):
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')

    employees = Employee.objects.all()

    if search_query:
        employees = employees.filter(
            Q(code__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if position_filter:
        employees = employees.filter(position_id=position_filter)

    positions = Position.objects.all()

    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'positions': positions,
        'search_query': search_query,
        'position_filter': position_filter,
    }
    return render(request, 'personnel/profile_list.html', context)


@login_required
def contract_create_general(request):
    """
    Hàm tạo hợp đồng mới không gắn với nhân viên cụ thể.
    Chuyển hướng đến hàm contract_create.
    """
    return contract_create(request)
