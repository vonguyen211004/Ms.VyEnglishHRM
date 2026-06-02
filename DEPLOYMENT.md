# 🚀 Hướng dẫn Deploy HR Management System

> Hướng dẫn chi tiết để deploy project trên các platform khác nhau sao cho nhà tuyển dụng có thể xem sản phẩm qua URL

---

## 📌 Tóm tắt các phương án Deploy

| Platform | Chi phí | Độ khó | Miễn phí | Ưu điểm |
|----------|--------|--------|---------|---------|
| **PythonAnywhere** | $5/tháng | ⭐⭐ | 3 tháng | Dễ, hỗ trợ Django tốt |
| **Render** | $7/tháng | ⭐⭐ | ✅ | Free tier, auto deploy |
| **Railway** | $5/tháng | ⭐⭐⭐ | ✅ | Fast, modern |
| **Heroku** | $7+/tháng | ⭐⭐ | ❌ | Free tier bị xóa |
| **DigitalOcean** | $6/tháng | ⭐⭐⭐ | ❌ | Mạnh, linh hoạt |
| **AWS** | Free tier | ⭐⭐⭐⭐ | ✅ | Powerful nhưng phức tạp |

---

## 🎯 GIẢI PHÁP NHANH NHẤT (Khuyến nghị cho nhà tuyển dụng)

### **Phương án 1: Render (⭐ DỄ NHẤT - 30 PHÚT)**

#### Bước 1: Chuẩn bị Project
```bash
cd d:\dev-python\LTWNhom06
```

#### Bước 2: Tạo file `Procfile`
```bash
echo web: gunicorn hr_management.wsgi > Procfile
```

**Nội dung Procfile:**
```
web: python hr_management/manage.py migrate && python hr_management/manage.py collectstatic --noinput && gunicorn hr_management.wsgi:application --log-file -
```

#### Bước 3: Tạo file `build.sh`
```bash
# Tạo file build.sh tại root folder
```

**Nội dung build.sh:**
```bash
#!/bin/bash
set -o errexit

pip install -r hr_management/requirements.txt
cd hr_management
python manage.py collectstatic --noinput
python manage.py migrate
```

#### Bước 4: Update requirements.txt
Thêm vào `hr_management/requirements.txt`:
```txt
Django==4.2.7
django-crispy-forms==2.0
crispy-bootstrap5==0.7
Pillow==11.0.0
openpyxl==3.1.5
xlsxwriter==3.1.7
python-decouple==3.8
gunicorn==21.2.0
whitenoise==6.6.0
```

#### Bước 5: Cập nhật settings.py
Thêm vào `hr_management/settings.py`:

```python
# Nhập os module tại đầu file nếu chưa có
import os

# Tìm ALLOWED_HOSTS và thay đổi
ALLOWED_HOSTS = ['*']  # Hoặc ['yourdomain.render.com']

# Thêm CSRF_TRUSTED_ORIGINS nếu có domain riêng
CSRF_TRUSTED_ORIGINS = [
    'https://*.render.com',
    'https://yourdomain.com'
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database - SQLite cho dev, PostgreSQL cho production
if os.getenv('DATABASE_URL'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(default=os.getenv('DATABASE_URL'))
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}
```

#### Bước 6: Tạo `.gitignore` (nếu chưa có)
```
venv/
*.pyc
__pycache__/
db.sqlite3
.env
.DS_Store
*.log
staticfiles/
media/
```

#### Bước 7: Push lên GitHub
```bash
git init
git add .
git commit -m "Initial commit - HR Management System"
git remote add origin https://github.com/YOUR_USERNAME/LTWNhom06.git
git push -u origin main
```

#### Bước 8: Deploy trên Render

1. **Truy cập:** https://render.com
2. **Đăng nhập/Đăng ký** bằng GitHub
3. **Chọn:** "New Web Service"
4. **Kết nối:** Chọn repository `LTWNhom06`
5. **Cấu hình:**
   - **Name:** `hr-management-system` (hoặc tên khác)
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn hr_management.wsgi:application --log-file -`
   - **Free/Paid:** Chọn Free tier

6. **Environment Variables** (click "Advanced"):
   ```
   PYTHON_VERSION = 3.11
   SECRET_KEY = your-secret-key-here
   DEBUG = False
   ALLOWED_HOSTS = yourdomain.render.com
   ```

7. **Click Deploy** → Chờ 5-10 phút

8. **Kết quả:**
   - URL: `https://hr-management-system.onrender.com`
   - Chia cho nhà tuyển dụng

---

## 🎯 PHƯƠNG ÁN 2: PythonAnywhere (⭐ PHỔ BIẾN - 20 PHÚT)

### Bước 1: Đăng ký PythonAnywhere
- Truy cập: https://www.pythonanywhere.com
- Đăng ký tài khoản miễn phí

### Bước 2: Upload Project
1. Mở **Web** → **Add a new web app**
2. Chọn **Python 3.11**
3. Chọn **Django**

### Bước 3: Cấu hình
```bash
# SSH vào PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.11 mysite

# Clone/upload code
git clone https://github.com/YOUR_USERNAME/LTWNhom06.git
cd LTWNhom06

# Cài dependencies
pip install -r hr_management/requirements.txt

# Tạo superuser
python hr_management/manage.py migrate
python hr_management/manage.py createsuperuser
```

### Bước 4: Update WSGI
Edit `WSGI configuration file` trên Web tab:
```python
import os
import sys
path = os.path.expanduser('~/LTWNhom06')
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_management.settings'
from django.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())
```

### Bước 5: URL
- Mặc định: `https://yourusername.pythonanywhere.com`

---

## 🎯 PHƯƠNG ÁN 3: Railway (⭐ HIỆN ĐẠI - 25 PHÚT)

### Bước 1: Tạo project trên Railway
- https://railway.app
- Connect GitHub

### Bước 2: Tạo `railway.json`
```json
{
  "builder": "nixpacks",
  "buildCommand": "pip install -r hr_management/requirements.txt && cd hr_management && python manage.py migrate && python manage.py collectstatic --noinput"
}
```

### Bước 3: Environment variables
```
DJANGO_SETTINGS_MODULE=hr_management.settings
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
```

### Bước 4: Deploy
- Railway auto deploy từ GitHub
- URL: `https://yourproject-production.up.railway.app`

---

## 🎯 PHƯƠNG ÁN 4: AWS Free Tier (⭐ CÓ TIỂM NĂNG - 1 TIẾNG)

### Bước 1: Tạo EC2 Instance
1. Truy cập AWS Console
2. EC2 → Launch Instance
3. Chọn Ubuntu 22.04 (free tier eligible)
4. Instance type: t2.micro (free)
5. Configure security groups (allow HTTP/HTTPS)

### Bước 2: Connect SSH
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Bước 3: Setup Server
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-venv git nginx

# Clone project
git clone https://github.com/YOUR_USERNAME/LTWNhom06.git
cd LTWNhom06

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r hr_management/requirements.txt
pip install gunicorn

# Create superuser
cd hr_management
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Bước 4: Cấu hình Gunicorn
```bash
# Tạo service file
sudo nano /etc/systemd/system/hrm.service
```

**Nội dung:**
```ini
[Unit]
Description=HRM Gunicorn Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/LTWNhom06/hr_management
ExecStart=/home/ubuntu/LTWNhom06/venv/bin/gunicorn --workers 3 --bind unix:hrm.sock hr_management.wsgi

[Install]
WantedBy=multi-user.target
```

### Bước 5: Cấu hình Nginx
```bash
sudo nano /etc/nginx/sites-available/hrm
```

**Nội dung:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://unix:/home/ubuntu/LTWNhom06/hr_management/hrm.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ubuntu/LTWNhom06/hr_management/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/LTWNhom06/media/;
    }
}
```

### Bước 6: Enable và Start
```bash
sudo systemctl enable hrm
sudo systemctl start hrm
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## ⚙️ CẤU HÌNH CHO PRODUCTION

### 1. Update settings.py
```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database - Dùng PostgreSQL cho production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hrm_db',
        'USER': 'hrm_user',
        'PASSWORD': 'strong_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/hrm.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 2. Tạo `.env` file (KHÔNG COMMIT)
```bash
SECRET_KEY=your-secret-key-from-django
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
```

### 3. Sử dụng .env file
```python
# Thêm vào settings.py
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

---

## 🔍 TESTING TRƯỚC DEPLOY

```bash
# 1. Local testing
cd hr_management
python manage.py runserver

# 2. Kiểm tra static files
python manage.py collectstatic --dry-run

# 3. Chạy tests
python manage.py test

# 4. Check security
python manage.py check --deploy
```

---

## 📊 MONITORING & MAINTENANCE

### Logs
```bash
# Render
# Dashboard → Logs tab

# PythonAnywhere
# Web → Error log & Server log

# AWS EC2
tail -f /var/log/django/hrm.log
```

### Database Backup
```bash
# Render/Railway: Automatic
# AWS: Manual backup or RDS automated snapshots
```

### Update Code
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart hrm  # For AWS
```

---

## 🎁 DOMAIN RIÊNG (Optional)

### Mua domain
- Godaddy, Namecheap, Hosting24

### Cấu hình DNS
**Ví dụ cho Render:**
- Type: CNAME
- Name: @
- Value: your-render-url.onrender.com

---

## 📱 DEMO ĐỂ NHÌU TUYỂN DỤNG

### URL chuẩn bị
```
https://your-hrm-system.onrender.com

Hoặc

https://hr-management.yourdomain.com
```

### Test accounts cho demo
```
Admin:
- Username: admin
- Password: demo123456

Tạo thêm test employee account nếu cần
```

### Checklist trước demo
- [ ] Static files load đúng (CSS, JS)
- [ ] Photos upload được
- [ ] Excel export hoạt động
- [ ] Database có data sample
- [ ] Login/logout hoạt động
- [ ] Admin panel accessible
- [ ] Responsive design (mobile)

---

## 🆘 TROUBLESHOOTING

### Static files không load
```bash
python manage.py collectstatic --clear --noinput
```

### Database connection error
```bash
# Check database URL
python manage.py dbshell

# Migrate
python manage.py migrate --fake-initial
```

### 500 Error
```bash
# Check logs
tail -f debug.log

# Set DEBUG=True tạm thời để xem error chi tiết
```

### Memory/CPU issues
```bash
# Render: Upgrade paid plan
# AWS: Upgrade instance type
# Railway: Check metrics
```

---

## 💡 RECOMMENDATIONS

1. **Chọn Render** nếu muốn nhanh + dễ (Free tier 15 ngày)
2. **Chọn PythonAnywhere** nếu thích simplicity + support tốt (Free 3 tháng)
3. **Chọn AWS** nếu muốn free tier dài hạn (1 năm)
4. **Chọn Railway** nếu thích modern interface + fast deployment

---

## 📞 NEXT STEPS

1. Chọn platform deployment
2. Chuẩn bị project theo hướng dẫn
3. Deploy và test
4. Share URL với nhà tuyển dụng
5. Monitor performance

**Thời gian setup: 20-60 phút tùy platform**
