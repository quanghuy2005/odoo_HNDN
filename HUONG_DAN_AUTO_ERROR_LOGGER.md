# 🔍 AUTO ERROR LOGGER - Hướng dẫn sử dụng

## ❓ Cái này là gì?

Script **`auto_error_logger.py`** tự động ghi lỗi từ Odoo vào file **`BAO_CAO_LOI.txt`** 
- Khi Odoo có thông báo ERROR/CRITICAL → tự động lưu vào file
- không cần manual copy-paste
- Đi kèm timestamp tự động

---

## 🚀 Cách sử dụng

### **Bước 1: Khỏi động Odoo**

```bash
cd /home/quang/TTDN-15-01-N1
sudo docker compose up -d
```

### **Bước 2: Chạy script monitor lỗi**

Mở terminal khác (giữ nguyên terminal Docker ở bước 1) rồi chạy:

```bash
cd /home/quang/TTDN-15-01-N1
python3 auto_error_logger.py
```

**Output:**
```
🔍 Bắt đầu monitor lỗi từ Odoo...
📝 Lỗi sẽ tự động được lưu vào BAO_CAO_LOI.txt
⏹️  Nhấn Ctrl+C để dừng
```

### **Bước 3: Sử dụng Odoo bình thường**

- Mở browser: **http://localhost:8069**
- Làm các công việc bình thường
- Nếu có lỗi → script sẽ tự động ghi vào file

### **Bước 4: Dừng monitoring**

```
Nhấn: Ctrl + C
```

---

## 📂 Output

Lỗi sẽ được lưu vào **`BAO_CAO_LOI.txt`** với format:

```
[Lỗi #1]
Thời gian: 2026-03-24 14:35:22
Loại: ERROR

Thông báo lỗi:
---
ERROR: Module 'van_ban' not found
...
---
```

---

## 🎯 Các tùy chọn

### Monitor từ Docker logs (mặc định):
```bash
python3 auto_error_logger.py
```

### Monitor từ file log của Odoo:
```bash
python3 auto_error_logger.py file
```

---

## ✅ Lợi ích

✅ **Tự động ghi lỗi** - không cần copy-paste  
✅ **Có timestamp** - biết lỗi xảy ra khi nào  
✅ **Phân loại lỗi** - ERROR / CRITICAL / WARNING  
✅ **Format rõ ràng** - dễ đọc để debug  

---

## ⚠️ Lưu ý

1. Phải chạy **sau khi Odoo đã khởi động** xong
2. Nếu thấy:
   ```
   ❌ Lỗi: docker-compose không tìm được
   ```
   → Chạy: `sudo apt install docker-compose -y`

3. Script detect lỗi bằng keywords:
   - ERROR, CRITICAL, Traceback, Exception, ...
   - Nếu thấy missed lỗi → ghi manual vào file hoặc báo tôi

---

## 🔧 Troubleshoot

**Q: Script chạy nhưng monitor không thấy gì?**  
A: Chắc Odoo chưa startup xong. Chờ 10-15 giây rồi làm gì đó để trigger lỗi (ví dụ: reload page)

**Q: Permission denied?**  
A: Chạy: `chmod +x auto_error_logger.py` rồi thử lại

**Q: Vẫn không được?**  
A: Ghi vào **BAO_CAO_LOI.txt** rồi gửi cho tôi debug

---

## 💡 Cách tạo lỗi để test

Mở Odoo → xem menu có tính năng nào mới → nhấn vào → nếu lỗi → auto_logger sẽ ghi

Hoặc test trực tiếp ở Python:

```python
# Terminal
python3
>>> from addons.van_ban.models.vanban_pdf_analyzer import VanBanPdfAnalyzer
>>> # Nếu lỗi import → auto_logger sẽ capture
```

---

**Happy debugging! 🎉**
