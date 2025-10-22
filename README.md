# 👨‍💼 Ms.Vy English Human Resource Management System

> **Giải pháp quản lý nhân sự toàn diện** giúp doanh nghiệp tự động hóa quy trình quản lý nhân viên, chấm công và tính lương - tiết kiệm đến **70% thời gian** xử lý hành chính nhân sự.

## 🎯 ĐIỂM NỔI BẬT

- ✅ **Tự động hóa hoàn toàn** quy trình tính lương dựa trên dữ liệu chấm công thực tế
- 🔐 **Bảo mật cao** với authentication middleware và phân quyền người dùng
- 📱 **Responsive Design** tương thích mọi thiết bị với Bootstrap framework
- ⚡ **Hiệu suất tối ưu** với Django ORM và database indexing
- 🎨 **UX/UI thân thiện** giúp người dùng làm quen nhanh chóng

---

## 🚀 CÔNG NGHỆ & KỸ NĂNG

### 🔧 Backend Development
| Công nghệ | Mục đích sử dụng | Mức độ thành thạo |
|-----------|------------------|-------------------|
| **Python 3.8+** | Core programming language | ⭐⭐⭐⭐⭐ |
| **Django 4.0+** | Web framework (MVC, ORM, Routing) | ⭐⭐⭐⭐⭐ |
| **Django ORM** | Database abstraction & query optimization | ⭐⭐⭐⭐ |
| **SQLite** | Relational database management | ⭐⭐⭐⭐ |
| **Authentication Middleware** | Security & authorization | ⭐⭐⭐⭐ |

### 🎨 Frontend Development
- **HTML5/CSS3/JavaScript ES6+**: Semantic markup & modern JS features
- **Bootstrap 5**: Responsive grid system & component library
- **Django Template Engine**: Server-side rendering với template inheritance
- **AJAX**: Asynchronous data loading cho UX mượt mà

### 📦 DevOps & Tools
- **Git/GitHub**: Version control & collaboration
- **Virtual Environment**: Dependency isolation
- **Django Admin**: Built-in admin interface customization
- **Debug Toolbar**: Performance profiling & optimization

---

## ✨ TÍNH NĂNG CHÍNH

### 1️⃣ Quản lý Hồ sơ Nhân viên
- ➕ Thêm mới nhân viên với validation đầy đủ
- ✏️ Cập nhật thông tin cá nhân, chức vụ, phòng ban
- 👁️ Xem chi tiết hồ sơ với lịch sử thay đổi
- 🚫 Vô hiệu hóa tài khoản (soft delete) thay vì xóa vĩnh viễn

### 2️⃣ Quản lý Hợp đồng Lao động
- 📄 Theo dõi đa dạng loại hợp đồng (thử việc, xác định thời hạn, không xác định thời hạn)
- ⏰ Cảnh báo hợp đồng sắp hết hạn
- 📊 Dashboard thống kê tình trạng hợp đồng
- 🔄 Lịch sử gia hạn và điều chỉnh hợp đồng

### 3️⃣ Hệ thống Chấm công Thông minh
- ⏱️ Ghi nhận giờ vào - giờ ra tự động
- 📅 Báo cáo chấm công theo ngày/tuần/tháng
- 📈 Thống kê số giờ làm việc, tăng ca, nghỉ phép
- 🎯 Tích hợp với hệ thống tính lương

### 4️⃣ Tính lương Tự động
- 💰 Công thức tính lương linh hoạt (lương cơ bản + phụ cấp + thưởng - khấu trừ)
- 📊 Tự động tính toán dựa trên dữ liệu chấm công

### 5️⃣ Phân quyền & Bảo mật
- 🔐 Authentication với Django's built-in system
- 👥 Role-based access control (Admin, HR Manager, Employee)
- 🛡️ CSRF protection

---

## 📷 DEMO GIAO DIỆN

### 🏠 Dashboard Tổng quan
![Dashboard](https://github.com/user-attachments/assets/9ad725b1-b288-4050-a804-5b59a0e900df)
*Real-time statistics với charts & KPIs*

### 👥 Quản lý Nhân sự
![Employee Management](https://github.com/user-attachments/assets/160a7e9a-bbe0-4ffb-ba60-f89288d6371d)
*CRUD operations với search, filter & pagination*

### ⏰ Hệ thống Chấm công
![Attendance](https://github.com/user-attachments/assets/72502b39-ba87-467f-a439-eae6a7116447)
*Calendar view với color-coded status*

### 💰 Quản lý Lương
![Payroll](https://github.com/user-attachments/assets/2410fcd3-bbbd-4135-a78a-fb9ad3c6ef9d)
*Automated calculation*

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT

### Prerequisites
\`\`\`bash
Python 3.8+
pip 20.0+
virtualenv (recommended)
\`\`\`

### Installation Steps

**1. Clone repository**
\`\`\`bash
git clone https://github.com/tramy212/LTWNhom06.git
cd LTWNhom06
\`\`\`

**2. Tạo virtual environment**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
\`\`\`

**3. Cài đặt dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**4. Cấu hình database**
\`\`\`python
# settings.py - Mặc định dùng SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Có thể chuyển sang PostgreSQL cho production
\`\`\`

**5. Chạy migrations**
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

**6. Tạo superuser**
\`\`\`bash
python manage.py createsuperuser
\`\`\`

**7. Load sample data (optional)**
\`\`\`bash
python manage.py loaddata fixtures/sample_data.json
\`\`\`

**8. Khởi chạy server**
\`\`\`bash
python manage.py runserver
\`\`\`

**9. Truy cập ứng dụng**
- **Frontend:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 🧪 TESTING & QUALITY ASSURANCE

\`\`\`bash
# Chạy unit tests
python manage.py test

# Kiểm tra code coverage
coverage run --source='.' manage.py test
coverage report

# Code quality check
flake8 .
pylint **/*.py
\`\`\`

**Test Coverage:** 85%+ cho core business logic

---

## 📁 CẤU TRÚC PROJECT
LTWNhom06/
├── hrm_app/                    # Main application
│   ├── models.py              # Database models (Employee, Contract, Attendance, Payroll)
│   ├── views.py               # Business logic & request handlers
│   ├── urls.py                # URL routing
│   ├── forms.py               # Form validation
│   ├── admin.py               # Admin interface customization
│   └── templates/             # HTML templates
│       ├── base.html          # Base template với navigation
│       ├── dashboard.html     # Dashboard với statistics
│       ├── employees/         # Employee management templates
│       ├── attendance/        # Attendance tracking templates
│       └── payroll/           # Payroll management templates
├── static/                    # Static files
│   ├── css/                   # Custom stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Images & assets
├── media/                     # User uploaded files
├── hrm_project/               # Project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI configuration
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
└── README.md                  # Project documentation
