# Ms.Vy English HR Management System

Ứng dụng quản lý nhân sự nội bộ cho Ms.Vy English, xây dựng bằng Django 4.2.7. Hệ thống tập trung vào ba nhóm nghiệp vụ chính: quản lý hồ sơ nhân sự, chấm công/bảng công tháng và tính lương.

## Mục Lục

- [Tính năng chính](#tính-năng-chính)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Các module chính](#các-module-chính)
- [Luồng nghiệp vụ](#luồng-nghiệp-vụ)
- [Cài đặt local](#cài-đặt-local)
- [Biến môi trường](#biến-môi-trường)
- [URL chính](#url-chính)
- [Lệnh phát triển](#lệnh-phát-triển)
- [Triển khai](#triển-khai)
- [Ghi chú cho lập trình viên](#ghi-chú-cho-lập-trình-viên)

## Tính Năng Chính

- Đăng nhập, đăng xuất, đổi mật khẩu và xem hồ sơ người dùng.
- Quản lý nhân viên, phòng ban, vị trí công việc, thông tin liên hệ, bằng cấp và trạng thái làm việc.
- Quản lý hợp đồng lao động, file hợp đồng, loại hợp đồng, hình thức làm việc, loại lương và lương đóng bảo hiểm.
- Quản lý ca làm việc, lịch làm việc cho nhân viên vận hành và chấm công hằng ngày.
- Quản lý lớp/khóa học, buổi học, phân công giáo viên/trợ giảng và chấm công buổi dạy.
- Tổng hợp bảng công tháng theo loại nhân sự, vị trí, tháng/năm; hỗ trợ duyệt, khóa, điều chỉnh công và chuyển sang tính lương.
- Tính lương từ bảng công tháng đã khóa, quản lý trạng thái bảng lương, phụ cấp, khấu trừ, thuế TNCN và xuất Excel.
- Giao diện server-rendered bằng Django Template, Bootstrap 5, Bootstrap Icons và crispy forms.
- API nội bộ để tìm kiếm nhân viên và trích xuất dữ liệu CV/CCCD bằng AI khi cấu hình khóa API phù hợp.

## Công Nghệ Sử Dụng

- Python 3.11.9 theo `runtime.txt` trên môi trường triển khai.
- Django 4.2.7.
- SQLite cho phát triển local; PostgreSQL khi có `DATABASE_URL`.
- Bootstrap 5, Bootstrap Icons, Django templates.
- `django-crispy-forms` và `crispy-bootstrap5`.
- `openpyxl`, `xlsxwriter` cho xử lý/xuất Excel.
- `Pillow`, `pypdf` cho xử lý file upload/CV.
- `gunicorn`, `whitenoise`, `dj-database-url`, `python-decouple` cho cấu hình production.
- `google-generativeai`, `groq` cho chức năng parse CV/CCCD.

## Các Màn hình chính
-Trang chủ
<img width="1920" height="1080" alt="Screenshot (49)" src="https://github.com/user-attachments/assets/f1a7853e-abc1-4546-af26-5835a7f5a089" />
-Quản lý Thông tin nhân viên
<img width="1920" height="1080" alt="Screenshot (50)" src="https://github.com/user-attachments/assets/96f47d8b-d15a-4df8-8342-706d0386bfed" />
-Quản lý Chấm công
<img width="1920" height="1080" alt="Screenshot (51)" src="https://github.com/user-attachments/assets/2b97aeb8-f70f-4abf-988c-2a7f94da4045" />
-Quản lý Tiền lương
<img width="1920" height="1080" alt="Screenshot (52)" src="https://github.com/user-attachments/assets/d0ca08a5-59f7-4be1-8b79-b69e6b8dfc34" />





## Cấu Trúc Dự Án

```text
LTWNhom06/
├── README.md
├── PROJECT_CONTEXT.md
├── Procfile
├── build.sh
├── runtime.txt
└── hr_management/
    ├── manage.py
    ├── requirements.txt
    ├── hr_management/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── employees/
    ├── attendance/
    ├── payroll/
    ├── templates/
    └── static/
```

## Các Module Chính

### `hr_management`

Module cấu hình lõi của Django project.

- `settings.py`: cấu hình app, database, static/media, đăng nhập, crispy forms, logging và biến môi trường.
- `urls.py`: khai báo route tổng, gồm trang chủ, xác thực, admin và include các app `employees`, `attendance`, `payroll`.
- `views.py`: xử lý trang chủ, đăng nhập/đăng xuất, hồ sơ người dùng và đổi mật khẩu.
- `templates/`: layout chung như `base.html`, `home.html`, `login.html`, `profile.html`, `change_password.html`.
- `static/`: CSS/JS dùng chung cho giao diện.

### `employees`

Module quản lý dữ liệu nhân sự.

Các model chính:

- `Department`: phòng ban/đơn vị.
- `Position`: vị trí công việc, có liên kết phòng ban và tự sinh mã khi cần.
- `Employee`: hồ sơ nhân viên, thông tin cá nhân, liên hệ, công việc và học vấn.
- `Contract`: hợp đồng lao động, loại hợp đồng, hình thức làm việc, loại lương, lương cơ bản, lương bảo hiểm và file đính kèm.
- `WorkHistory`: lịch sử làm việc.
- `SalaryHistory`: lịch sử thay đổi lương.

Chức năng chính:

- Danh sách, thêm, sửa, xem chi tiết, kích hoạt/ngưng kích hoạt nhân viên.
- Quản lý hợp đồng theo nhân viên hoặc tạo hợp đồng độc lập.
- Chấm dứt, xóa, tải file hợp đồng.
- Tự đồng bộ vị trí/trạng thái nhân viên theo hợp đồng đang hiệu lực.
- API tìm nhân viên đang hoạt động nhưng chưa có hợp đồng hiệu lực.
- API parse CV/CCCD để gợi ý dữ liệu nhập hồ sơ.

### `attendance`

Module quản lý lịch làm việc, chấm công và bảng công.

Các model chính:

- `WorkShift`: mẫu ca làm việc, giờ vào/ra, thời gian nghỉ, giờ công và ngày công.
- `StaffSchedule`: lịch ca cho nhân viên vận hành.
- `Course`: lớp/khóa học.
- `ClassSession`: buổi học theo lớp, ngày, giờ và phòng học.
- `TeacherAssignment`: phân công giáo viên/trợ giảng/dạy thay cho buổi học.
- `SessionAttendance`: chấm công buổi dạy.
- `DailyAttendance`: chấm công hằng ngày cho nhân viên vận hành.
- `MonthlyTimesheet`: bảng công tháng theo loại bảng công, vị trí và tháng/năm.
- `TimesheetApproval`: lịch sử rà soát, duyệt, khóa, mở khóa bảng công.
- `AttendanceAdjustment`: điều chỉnh công, giờ, nghỉ phép hoặc ghi chú.
- `AttendanceRecord`, `AttendanceSummary`, `EmployeeAttendance`, `EmployeeSchedule`: model cũ được giữ để tương thích dữ liệu và endpoint legacy.

Chức năng chính:

- Dashboard chấm công.
- Quản lý ca làm việc.
- Xếp lịch nhân viên vận hành theo khoảng ngày và thứ trong tuần.
- Quản lý lớp/khóa học và tạo lịch buổi học hàng loạt.
- Nhập chấm công hằng ngày.
- Lập bảng công tháng cho nhân viên vận hành hoặc giáo viên/trợ giảng.
- Xem chi tiết, điều chỉnh, khóa và chuyển bảng công sang payroll.
- Một số endpoint import/export Excel và cập nhật chấm công cũ vẫn được giữ để tương thích.

### `payroll`

Module tính lương và quản lý bảng lương.

Các model chính:

- `Payroll`: bảng lương theo tháng/năm, vị trí, người tạo, trạng thái và nguồn bảng công tháng.
- `PayrollDetail`: dòng lương từng nhân viên, gồm lương cơ bản, công chuẩn, công thực tế, tỷ lệ hưởng lương, thưởng/phạt, khấu trừ, thuế TNCN, tổng thu nhập và thực lĩnh.
- `PayrollAllowance`: phụ cấp theo dòng lương.
- `PayrollDeduction`: khấu trừ theo dòng lương.

Chức năng chính:

- Tạo/sửa/xem danh sách/xem chi tiết bảng lương.
- Tính lương từ `MonthlyTimesheet` đã khóa hoặc dữ liệu chấm công cũ.
- Tự tính thực lĩnh khi lưu chi tiết lương.
- Chuyển bảng công sang bảng lương.
- Kích hoạt/vô hiệu hóa bảng lương.
- Xuất bảng lương ra file Excel.

## Luồng Nghiệp Vụ

1. Tạo phòng ban và vị trí trong Django Admin hoặc qua dữ liệu có sẵn.
2. Tạo hồ sơ nhân viên trong module `employees`.
3. Tạo hợp đồng cho nhân viên, chọn loại lương và mức lương/đơn giá tính lương.
4. Với nhân viên vận hành: tạo ca làm việc, xếp lịch ca, nhập chấm công hằng ngày.
5. Với giáo viên/trợ giảng: tạo lớp/khóa học, tạo buổi học, phân công giảng dạy và ghi nhận chấm công buổi dạy.
6. Tạo bảng công tháng trong module `attendance`, rà soát, điều chỉnh nếu cần và khóa bảng công.
7. Chuyển bảng công đã khóa sang module `payroll`.
8. Kiểm tra chi tiết lương, cập nhật phụ cấp/khấu trừ/trạng thái và xuất Excel.

## Cài Đặt Local

Yêu cầu:

- Python 3.11 được khuyến nghị.
- Git.
- SQLite dùng được mặc định, không cần cài database riêng cho local.

Các bước chạy trên Windows PowerShell:

```powershell
cd D:\dev-python\LTWNhom06
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r .\hr_management\requirements.txt
```

Tạo file `.env` ở thư mục `LTWNhom06/hr_management/`:

```env
SECRET_KEY=dev-secret-key-change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=
GEMINI_API_KEY=
```

Khởi tạo database và tài khoản quản trị:

```powershell
cd .\hr_management
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sau đó mở:

```text
http://127.0.0.1:8000/
```

## Biến Môi Trường

| Biến | Bắt buộc | Mô tả |
| --- | --- | --- |
| `SECRET_KEY` | Có | Khóa bí mật của Django. Bắt buộc vì `settings.py` đọc bằng `python-decouple`. |
| `DEBUG` | Không | `true` khi chạy local, `false` trên production. Mặc định là `false`. |
| `ALLOWED_HOSTS` | Không | Danh sách host phân tách bằng dấu phẩy. Mặc định `localhost,127.0.0.1`. |
| `DATABASE_URL` | Không | Nếu có, ứng dụng dùng PostgreSQL qua `dj-database-url`; nếu không có, dùng SQLite local. |
| `GROQ_API_KEY` | Không | Dùng cho API parse CV/CCCD. |
| `GEMINI_API_KEY` | Không | Đã được cấu hình trong API module; hiện chức năng parse chính đang gọi Groq. |

## URL Chính

| URL | Chức năng |
| --- | --- |
| `/` | Trang chủ sau đăng nhập |
| `/login/` | Đăng nhập |
| `/logout/` | Đăng xuất |
| `/profile/` | Hồ sơ người dùng |
| `/change-password/` | Đổi mật khẩu |
| `/admin/` | Django Admin |
| `/employees/` | Danh sách nhân viên |
| `/employees/contracts/` | Danh sách hợp đồng |
| `/attendance/` | Dashboard chấm công |
| `/attendance/work-shifts/` | Quản lý ca làm việc |
| `/attendance/schedules/` | Lịch ca nhân viên vận hành |
| `/attendance/courses/` | Quản lý lớp/khóa học |
| `/attendance/sessions/` | Quản lý buổi học |
| `/attendance/daily-attendance/` | Nhập chấm công hằng ngày |
| `/attendance/summary/` | Bảng công tháng |
| `/payroll/` | Danh sách bảng lương |
| `/payroll/create/` | Tạo bảng lương |
| `/payroll/calculate/` | Tính lương |
| `/api/employees/search/` | API tìm kiếm nhân viên |
| `/api/employees/parse-cv/` | API parse CV/CCCD |

## Lệnh Phát Triển

Chạy từ thư mục `LTWNhom06/hr_management`:

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py runserver
```

Thu thập static file cho production:

```powershell
python manage.py collectstatic --noinput
```

## Triển Khai

Repo có sẵn các file hỗ trợ triển khai:

- `runtime.txt`: khai báo Python `3.11.9`.
- `requirements.txt`: dependency của Django app.
- `build.sh`: cài dependency, migrate database và collect static.
- `Procfile`: chạy migrate, collectstatic và start Gunicorn.

Gợi ý cấu hình production:

- `DEBUG=false`.
- Thiết lập `SECRET_KEY` mạnh và không commit vào Git.
- Thiết lập `ALLOWED_HOSTS` theo domain triển khai.
- Thiết lập `DATABASE_URL` nếu dùng PostgreSQL.
- Thiết lập `GROQ_API_KEY` nếu bật chức năng parse CV/CCCD.
- Kiểm tra lại route `create-admin-temp/` trong `hr_management/urls.py`; route này chỉ nên dùng tạm trong môi trường dev và cần gỡ hoặc bảo vệ trước khi public.

## Ghi Chú Cho Lập Trình Viên

- Không commit file runtime/local như `db.sqlite3`, `debug.log`, `venv/`, `__pycache__/`, `.env`, `media/`, `staticfiles/`.
- Layout chung nằm ở `hr_management/templates/base.html`.
- Trang nhân viên dùng sidebar `employees/sidebar.html`.
- Trang chấm công dùng sidebar `attendance/sidebar.html` qua block `module_sidebar`.
- Trang payroll nên kế thừa `payroll/base_payroll.html` để giữ sidebar lương.
- Public URL đang dùng tiếng Anh để nhất quán: `/employees/`, `/attendance/`, `/payroll/`, `/api/employees/search/`.
- Một số model/route legacy trong module `attendance` vẫn được giữ để tránh vỡ dữ liệu cũ; khi chỉnh sửa nên kiểm tra tác động tới cả bảng công tháng mới và dữ liệu legacy.
- Nếu render trang có truy vấn SQLite bị `sqlite3.OperationalError: disk I/O error`, hãy kiểm tra quyền file database, dung lượng ổ đĩa, file lock hoặc process khác đang giữ `db.sqlite3`.

---

**Phiên bản tài liệu**: cập nhật theo cấu trúc module hiện tại  
**Trạng thái dự án**: Development/Beta
