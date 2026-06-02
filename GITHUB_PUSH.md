# 📤 Hướng dẫn Push Project lên GitHub

Hướng dẫn từng bước để push project lên GitHub, chuẩn bị cho deployment.

## Bước 1: Khởi tạo Git (nếu chưa có)

```bash
cd D:\dev-python\LTWNhom06
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Bước 2: Thêm tất cả files

```bash
git add .
```

## Bước 3: Kiểm tra files sẽ commit

```bash
git status
```

## Bước 4: Tạo commit đầu tiên

```bash
git commit -m "Initial commit - Ms.Vy HR Management System"
```

## Bước 5: Tạo repository trên GitHub

1. Truy cập https://github.com/new
2. Repository name: `LTWNhom06`
3. Description: "Ms.Vy English HR Management System"
4. Chọn **Public** (để nhà tuyển dụng có thể xem)
5. Click **Create repository**

## Bước 6: Kết nối với remote repository

```bash
git remote add origin https://github.com/YOUR_USERNAME/LTWNhom06.git
git branch -M main
```

## Bước 7: Push lên GitHub

```bash
git push -u origin main
```

## Bước 8: Xác nhận

- Truy cập https://github.com/YOUR_USERNAME/LTWNhom06
- Kiểm tra code đã upload

---

## 🔄 Push cập nhật tiếp theo

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

---

## 📝 Commit message format

```
# Good
git commit -m "Fix: duplicate imports in attendance/views.py"
git commit -m "Feature: add employee photo upload"
git commit -m "Refactor: organize imports in payroll/models.py"

# Bad
git commit -m "fixed stuff"
git commit -m "update"
```

---

## 🆘 Troubleshooting

**Error: "fatal: 'origin' does not appear to be a 'git' repository"**
```bash
git remote add origin https://github.com/YOUR_USERNAME/LTWNhom06.git
```

**Error: "Please make sure you have the correct access rights"**
- Check GitHub credentials
- Use HTTPS instead of SSH (nếu chưa setup SSH key)

**Want to see history?**
```bash
git log --oneline
```

---

**Sau khi push lên GitHub, project sẵn sàng để deploy!**
Xem: [DEPLOYMENT.md](DEPLOYMENT.md)
