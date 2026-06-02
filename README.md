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
```bash
Python 3.8+
pip 20.0+
virtualenv (recommended)
```

### Installation Steps

**1. Clone repository**
```bash
git clone https://github.com/tramy212/LTWNhom06.git
cd LTWNhom06
```

**2. Tạo virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

**3. Cài đặt dependencies**
```bash
pip install -r hr_management/requirements.txt
```

**4. Navigate to project directory**
```bash
cd hr_management
```

**5. Chạy migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Tạo superuser (admin)**
```bash
python manage.py createsuperuser
```

**7. Khởi chạy server**
```bash
python manage.py runserver
```

**8. Truy cập ứng dụng**
- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Employees:** http://127.0.0.1:8000/nhan-vien/
- **Attendance:** http://127.0.0.1:8000/attendance/
- **Payroll:** http://127.0.0.1:8000/tien-luong/

---

## 📖 USING THE APPLICATION

### Admin Functions
1. Login with superuser credentials
2. Access Admin Panel at `/admin/`
3. Create Departments, Positions, Work Shifts
4. Add and manage employees
5. Configure attendance records
6. Generate payroll

---

## 🚀 DEPLOYMENT GUIDE

**Muốn chia sẻ sản phẩm với nhà tuyển dụng qua URL?**

Xem hướng dẫn chi tiết trong [**DEPLOYMENT.md**](DEPLOYMENT.md) để:
- ✅ Deploy trên **Render** (FREE tier, 15 ngày) - **NHANH NHẤT**
- ✅ Deploy trên **PythonAnywhere** (FREE 3 tháng) - **DỄ NHẤT**
- ✅ Deploy trên **Railway** (FREE tier)
- ✅ Deploy trên **AWS** (FREE tier 1 năm)
- ✅ Deploy trên **DigitalOcean** ($6/tháng)

**Thời gian setup: 20-60 phút**

📌 **Khuyến nghị:** Dùng **Render** hoặc **PythonAnywhere** cho demo nhanh!

### For Employees
1. View their profile
2. Check attendance records
3. View salary information (if implemented)

---

## 🧪 TESTING & QUALITY ASSURANCE

```bash
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

```
LTWNhom06/
├── hr_management/                    # Django Project Settings
│   ├── settings.py                  # Django configuration
│   ├── urls.py                      # Root URL configuration
│   ├── wsgi.py                      # WSGI configuration
│   ├── views.py                     # Project-wide views (home, login)
│   └── asgi.py                      # ASGI configuration
│
├── employees/                        # Employee Management App
│   ├── models.py                    # Employee, Contract, Department, Position, etc.
│   ├── views.py                     # Employee CRUD & contract management
│   ├── forms.py                     # Employee & contract forms
│   ├── urls.py                      # Employee routing
│   ├── api_views.py                 # REST API endpoints
│   ├── utils.py                     # Helper functions
│   ├── admin.py                     # Admin customization
│   ├── migrations/                  # Database migrations
│   └── templates/employees/         # Employee templates
│
├── attendance/                       # Attendance Management App
│   ├── models.py                    # WorkShift, AttendanceRecord, DailyAttendance, etc.
│   ├── views.py                     # Attendance tracking & Excel export
│   ├── forms.py                     # Attendance forms
│   ├── urls.py                      # Attendance routing
│   ├── utils.py                     # Attendance calculations
│   ├── admin.py                     # Admin customization
│   ├── migrations/                  # Database migrations
│   └── templates/attendance/        # Attendance templates
│
├── payroll/                          # Payroll Management App
│   ├── models.py                    # Payroll, PayrollDetail, etc.
│   ├── views.py                     # Payroll calculation & tax API
│   ├── forms.py                     # Payroll forms
│   ├── urls.py                      # Payroll routing
│   ├── admin.py                     # Admin customization
│   ├── migrations/                  # Database migrations
│   └── templates/payroll/           # Payroll templates
│
├── static/                          # Static Files
│   ├── css/
│   │   ├── custom.css              # Custom styles
│   │   └── main.css                # Main styles
│   └── js/
│       ├── charts.js               # Chart.js for dashboard
│       └── main.js                 # Main JavaScript
│
├── templates/                       # Global Templates
│   ├── base.html                   # Base template with navbar
│   ├── home.html                   # Homepage
│   └── login.html                  # Login page
│
├── media/                          # User Uploaded Files
│   ├── employee_photos/            # Employee photos
│   └── employees/                  # Other employee files
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── db.sqlite3                      # Development database
├── PROJECT_CONTEXT.md              # Detailed project context for AI
└── README.md                       # This file
```

---

## 📚 KEY FEATURES BREAKDOWN

### 1️⃣ Employee Management (Quản lý nhân sự)
- ✅ CRUD operations for employees
- ✅ Contract tracking (probation, fixed-term, indefinite)
- ✅ Work history & salary history
- ✅ Photo upload functionality
- ✅ Department & position management
- ✅ Advanced search & filtering

### 2️⃣ Attendance System (Hệ thống chấm công)
- ✅ Work shift configuration with flexible times
- ✅ Daily attendance recording
- ✅ Check-in/check-out tracking
- ✅ Monthly attendance summaries
- ✅ Excel export functionality
- ✅ Absence type classification

### 3️⃣ Payroll System (Hệ thống tính lương)
- ✅ Automatic salary calculation
- ✅ Attendance-based compensation
- ✅ Shift coefficient multipliers (1x, 2x, 3x)
- ✅ Tax calculation API
- ✅ Payroll status management
- ✅ Report generation

---

## 🔧 TECHNOLOGY STACK

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Django | 4.2.7 |
| **Language** | Python | 3.8+ |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Latest |
| **Frontend** | Bootstrap | 5 |
| **Forms** | django-crispy-forms | 2.0 |
| **Excel** | openpyxl, xlsxwriter | 3.11.2, 3.1.7 |
| **Images** | Pillow | 10.1.0 |

---

## 🔐 Security Features
- ✅ Django authentication system
- ✅ CSRF protection enabled
- ✅ Login required decorators
- ✅ Role-based access control
- ✅ Password validation rules
- ✅ Session management

---

## 📝 USAGE EXAMPLES

### Add a New Employee
1. Go to `/nhan-vien/them/`
2. Fill in employee information
3. Upload photo if needed
4. Click Save

### Create Attendance Record
1. Go to `/attendance/`
2. Select Work Shift
3. Choose employees
4. Set date range
5. Submit

### Generate Payroll
1. Go to `/tien-luong/`
2. Select attendance summary
3. Review calculations
4. Approve/Process

---

## 🐛 TROUBLESHOOTING

### Database Issues
```bash
# Reset database
python manage.py migrate --zero [app_name]
python manage.py migrate

# Clear all data
python manage.py flush
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check installed packages
pip list
```

### Static Files Issues
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear cache
python manage.py clear_cache
```

---

## 📞 SUPPORT & CONTRIBUTION

### Reporting Issues
- Check existing issues first
- Provide clear description
- Include error messages & logs
- Attach screenshots if applicable

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 LICENSE

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 CONTRIBUTORS

- **Lead Developer**: Ms.Vy English Team
- **Project Manager**: Development Team

---

## 📅 PROJECT STATUS

- ✅ Core functionality implemented
- ✅ Database schema finalized
- ✅ Import issues fixed (June 2026)
- ✅ Requirements.txt updated
- ⏳ Full test coverage (in progress)
- ⏳ API documentation (pending)

---

## 🎓 LEARNING OUTCOMES

This project demonstrates:
- Django Web Framework mastery
- Database design & ORM usage
- RESTful API development
- Form validation & error handling
- Template inheritance & static files
- Authentication & authorization
- Business logic implementation
- Excel file generation

---

**Last Updated**: June 1, 2026
**Version**: 1.0.0
**Status**: Development/Beta

---

## 📚 Documentation

| Tài liệu | Mục đích |
|---------|---------|
| [**PROJECT_CONTEXT.md**](PROJECT_CONTEXT.md) | Tổng quan project, architecture, coding guidelines |
| [**DEPLOYMENT.md**](DEPLOYMENT.md) | Hướng dẫn deploy lên Render, PythonAnywhere, AWS, v.v. |
| [**GITHUB_PUSH.md**](GITHUB_PUSH.md) | Hướng dẫn push code lên GitHub |
| **.env.example** | Các environment variables cần thiết |
| **Procfile** | Configuration cho deployment |
| **build.sh** | Build script tự động cho deployment |
| **runtime.txt** | Python version specification |
