# Ms.Vy English HR Management System

Ứng dụng quản lý nhân sự nội bộ xây bằng Django 4.2.7. Hệ thống tập trung vào ba nghiệp vụ chính: hồ sơ nhân viên, chấm công và tính lương.

## Tính năng chính

- Quản lý nhân viên, vị trí, phòng ban và hợp đồng lao động.
- Quản lý ca làm việc, bảng chấm công chi tiết và bảng chấm công tổng hợp.
- Tính lương theo dữ liệu chấm công, xuất Excel và quản lý trạng thái bảng lương.
- Giao diện server-rendered bằng Django Template + Bootstrap 5.
- Đăng nhập, đổi mật khẩu và trang hồ sơ người dùng.

## Công nghệ

- Python 3.8+
- Django 4.2.7
- SQLite cho môi trường development
- Bootstrap 5, Bootstrap Icons
- django-crispy-forms, crispy-bootstrap5
- openpyxl, xlsxwriter, Pillow

## Cài đặt local

```bash
cd LTWNhom06
python -m venv venv
venv\Scripts\activate
pip install -r hr_management/requirements.txt
cd hr_management
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Truy cập:

- Trang chủ: `http://127.0.0.1:8000/`
- Nhân viên: `http://127.0.0.1:8000/employees/`
- Chấm công: `http://127.0.0.1:8000/attendance/`
- Tiền lương: `http://127.0.0.1:8000/payroll/`
- Admin: `http://127.0.0.1:8000/admin/`

## API và URL

Các route public dùng tiếng Anh để nhất quán hơn:

- `/employees/`
- `/attendance/`
- `/payroll/`
- `/api/employees/search/`

Trong template nên luôn dùng `{% url %}` với route name thay vì hard-code path.

## Cấu trúc project

```text
LTWNhom06/
├── README.md
├── PROJECT_CONTEXT.md
├── hr_management/
│   ├── manage.py
│   ├── hr_management/      # settings, root urls, project views
│   ├── employees/          # employee, contract, position, department
│   ├── attendance/         # work shifts, attendance records, summaries
│   ├── payroll/            # payroll records and salary details
│   ├── templates/          # global templates
│   ├── static/             # css/js
│   └── media/              # uploaded files
```

## Kiểm tra nhanh

```bash
cd hr_management
python manage.py check
python manage.py test
```

Nếu gặp `sqlite3.OperationalError: disk I/O error`, kiểm tra quyền ghi file `hr_management/db.sqlite3`, dung lượng ổ đĩa và việc DB có đang bị process khác lock hay không.

## Ghi chú cho contributor

- Không commit `venv/`, `__pycache__/`, `*.pyc`, `debug.log` hoặc database local nếu không có lý do rõ ràng.
- Giữ route name ổn định để template reverse không bị lỗi.
- Khi sửa UI form, các field `required` cần có dấu `*` đỏ để người dùng dễ nhận biết.
- Xem thêm [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) trước khi giao việc cho AI code agent.
