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
