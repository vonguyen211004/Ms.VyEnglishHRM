# Ms.Vy English HR Management System - Project Context

## 📋 Project Overview
This is a comprehensive Human Resource Management System built with Django 4.2.7, designed to automate employee management, attendance tracking, and payroll calculation for HR departments.

**Project Name**: Ms.Vy English HR Management System
**Framework**: Django 4.2.7
**Language**: Python 3.8+
**Database**: SQLite (development), can be configured for PostgreSQL
**Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript ES6+

---

## 📁 Project Structure

```
LTWNhom06/
├── hr_management/              # Django project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   ├── views.py               # Home, login views
│   └── asgi.py                # ASGI configuration
│
├── employees/                  # Employee management app
│   ├── models.py              # Employee, Contract, WorkHistory, SalaryHistory, Department, Position
│   ├── views.py               # CRUD operations for employees, contracts
│   ├── forms.py               # Employee & Contract forms
│   ├── urls.py                # Employee routing
│   ├── api_views.py           # REST API endpoints
│   ├── utils.py               # Helper functions
│   ├── migrations/            # Database migrations
│   └── templates/
│       └── employees/         # Employee templates
│
├── attendance/                 # Attendance management app
│   ├── models.py              # WorkShift, AttendanceRecord, DailyAttendance, AttendanceSummary, EmployeeAttendance
│   ├── views.py               # Attendance tracking, summary, Excel export
│   ├── forms.py               # Attendance forms
│   ├── urls.py                # Attendance routing
│   ├── utils.py               # Attendance calculations
│   ├── migrations/            # Database migrations
│   └── templates/
│       └── attendance/        # Attendance templates
│
├── payroll/                    # Payroll management app
│   ├── models.py              # Payroll, PayrollDetail, PayrollAllowance, PayrollDeduction
│   ├── views.py               # Payroll calculation, tax calculation API
│   ├── forms.py               # Payroll forms
│   ├── urls.py                # Payroll routing
│   ├── migrations/            # Database migrations
│   └── templates/
│       └── payroll/           # Payroll templates
│
├── static/                     # Static files
│   ├── css/
│   │   ├── custom.css        # Custom styles
│   │   └── main.css          # Main styles
│   └── js/
│       ├── charts.js         # Chart.js for dashboard
│       └── main.js           # Main JavaScript logic
│
├── templates/                  # Global templates
│   ├── base.html              # Base template with navbar
│   ├── home.html              # Homepage
│   └── login.html             # Login page
│
├── media/                      # User uploaded files
│   ├── employee_photos/       # Employee photos
│   └── employees/             # Other employee files
│
├── db.sqlite3                  # Development database
├── manage.py                   # Django management script
└── requirements.txt            # Python dependencies
```

---

## 🔑 Key Models & Relationships

### Employees Module
- **Employee**: Core employee information (code, name, gender, DOB, contact, education, salary)
- **Department**: Organization units
- **Position**: Job positions with coefficients for wage calculation
- **Contract**: Employment contracts (probation, definite, indefinite terms)
- **WorkHistory**: Previous work experience
- **SalaryHistory**: Salary change history tracking

### Attendance Module
- **WorkShift**: Shift definitions with check-in/check-out times and coefficients
- **AttendanceRecord**: Attendance period configuration
- **DailyAttendance**: Daily attendance details (check-in, check-out, status)
- **AttendanceSummary**: Monthly attendance summary per position
- **EmployeeAttendance**: Aggregated attendance metrics for payroll

### Payroll Module
- **Payroll**: Monthly payroll records
- **PayrollDetail**: Individual employee salary details
- **PayrollAllowance**: Allowances (not implemented yet)
- **PayrollDeduction**: Deductions (not implemented yet)

---

## 🔐 Security Features
- Django authentication middleware
- Role-based access control
- Login required decorators
- CSRF protection enabled
- Password validation rules
- Session management

---

## 📦 Core Dependencies
- **Django 4.2.7**: Web framework
- **django-crispy-forms 2.0**: Form rendering
- **crispy-bootstrap5 0.7**: Bootstrap integration
- **Pillow 10.1.0**: Image processing (for employee photos)
- **openpyxl 3.11.2**: Excel file reading/writing
- **xlsxwriter 3.1.7**: Advanced Excel generation
- **python-decouple 3.8**: Environment variable management

---

## ⚙️ Configuration
- **Language**: Vietnamese (vi)
- **Timezone**: Asia/Ho_Chi_Minh (UTC+7)
- **Database**: SQLite (development) - easily switch to PostgreSQL in production
- **Internationalization**: Enabled with Django i18n
- **Media Files**: Images stored in `/media/` (employee photos)
- **Static Files**: CSS/JS in `/static/`
- **Logging**: Configured for console and file output to `debug.log`

---

## 🎯 Main Features

### 1. Employee Management
- Add/Edit/Delete employees with full information
- Track education and qualifications
- Upload employee photos
- View employee contracts and work history
- Track salary changes

### 2. Attendance Tracking
- Define work shifts with flexible check-in/check-out windows
- Record daily attendance per shift or by day
- Track absences (permitted, unpermitted, regime-based)
- Generate monthly attendance summaries
- Export attendance data to Excel

### 3. Payroll Calculation
- Automatic salary calculation based on attendance
- Support for different shift coefficients (normal day: 1x, rest day: 2x, holiday: 3x)
- Tax calculation (Personal Income Tax - TNCN)
- Handle allowances and deductions
- Generate payroll reports

---

## 🔧 Common Development Tasks

### Running the Application
```bash
cd hr_management
python manage.py runserver
```

### Creating Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Accessing Admin Panel
Navigate to: `http://localhost:8000/admin/`

---

## 📝 Coding Guidelines

### Import Organization
1. Django core imports
2. Third-party imports
3. Local app imports
4. Always remove duplicate imports

### Model Guidelines
- Use `verbose_name` and `verbose_name_plural` for all fields
- Use `_()` function for translatable strings
- Add `__str__()` method for readable representation
- Use proper `related_name` for ForeignKey relationships
- Document complex properties with docstrings

### View Guidelines
- Use `@login_required` decorator for protected views
- Use `get_object_or_404()` for safe queries
- Implement proper pagination for list views
- Use `messages` framework for user feedback
- Implement proper error handling

### Form Guidelines
- Use crispy-forms for consistent styling
- Validate data thoroughly
- Add custom error messages
- Use ModelForms when possible

---

## 🐛 Known Issues & Fixed
- ✅ Removed duplicate imports in attendance/models.py, attendance/views.py, payroll/views.py
- ✅ Added missing dependencies to requirements.txt (Pillow, openpyxl, xlsxwriter)
- ✅ Verified all model relationships are correct

---

## 📚 API Endpoints (if used)
- `/api/employees/` - Employee list/filter API
- `/api/payroll/tax/` - Tax calculation API

---

## 🚀 Future Enhancements
1. Implement PayrollAllowance and PayrollDeduction models
2. Add leave management system
3. Implement employee performance tracking
4. Add dashboard with charts and analytics
5. Implement email notifications for important events
6. Add employee self-service portal
7. Support for multiple companies/departments
8. Advanced reporting and export features

---

## 📞 Support & Documentation
- Admin Interface: Built-in Django admin customization
- Email Notifications: Ready to implement
- Logging: Debug.log file for troubleshooting

---

**Last Updated**: June 1, 2026
**Status**: Development
