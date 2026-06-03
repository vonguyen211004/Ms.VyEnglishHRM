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
