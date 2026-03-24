# 📋 HƯỚNG DẪN SỬ DỤNG - QUẢN LÝ VĂN BẢN

## 📚 MỤC LỤC
1. [Tổng Quan](#tổng-quan)
2. [Các Thành Phần Chính](#các-thành-phần-chính)
3. [Hướng Dẫn Chi Tiết](#hướng-dẫn-chi-tiết)
4. [Ví Dụ Thực Tế](#ví-dụ-thực-tế)
5. [Mẹo & Thủ Thuật](#mẹo--thủ-thuật)

---

## 🎯 TỔNG QUAN

Module **Quản Lý Văn Bản** giúp bạn:
- ✅ Quản lý **Văn Bản Đến** (nhận từ bên ngoài)
- ✅ Quản lý **Văn Bản Đi** (gửi đi)
- ✅ Tổ chức **Hồ Sơ Văn Bản** (nhóm các văn bản liên quan)
- ✅ Tracking lịch sử & trạng thái
- ✅ Đính kèm file & tài liệu

---

## 📊 CÁC THÀNH PHẦN CHÍNH

### **1️⃣ VĂN BẢN ĐẾN (Van Ban Đến)**
**Định nghĩa:** Các văn bản nhận được từ cơ quan khác, đối tác, khách hàng

| **Thông Tin** | **Ý Nghĩa** |
|---|---|
| **Số Văn Bản** | Mã định danh văn bản (bắt buộc) |
| **Trích Yếu** | Nội dung tóm tắt (bắt buộc) |
| **Ngày Văn Bản** | Ngày ký của cơ quan ban hành |
| **Ngày Đến** | Ngày nhận được tại công ty |
| **Cơ Quan Ban Hành** | Nơi phát hành (VD: Sở TT&TT, Sở KX) |
| **Loại Văn Bản** | Quyết định, Công văn, Thông báo, v.v |
| **Độ Khẩn** | Thường / Khẩn / Hỏa Tốc |
| **Độ Mật** | Bình thường / Mật / Tuyệt Mật |
| **Trạng Thái** | Mới → Đang xử lý → Đã xử lý |

---

### **2️⃣ VĂN BẢN ĐI (Van Ban Di)**
**Định nghĩa:** Các văn bản phát hành từ công ty gửi ra ngoài

| **Thông Tin** | **Ý Nghĩa** |
|---|---|
| **Số Văn Bản** | Mã định danh (bắt buộc) |
| **Trích Yếu** | Nội dung tóm tắt (bắt buộc) |
| **Ngày Văn Bản** | Ngày ký tại công ty |
| **Ngày Gửi** | Ngày gửi đi |
| **Nơi Nhận** | Địa chỉ nơi gửi tới |
| **Loại Văn Bản** | Quyết định, Công văn, Thông báo, v.v |
| **Độ Khẩn** | Thường / Khẩn / Hỏa Tốc |
| **Độ Mật** | Bình thường / Mật / Tuyệt Mật |
| **Trạng Thái** | Dự thảo → Chờ duyệt → Đã duyệt → Đã gửi |

---

### **3️⃣ HỒ SƠ VĂN BẢN (Ho So Van Ban)**
**Định nghĩa:** Nhóm các văn bản liên quan đến 1 sự kiện/dự án/khách hàng

| **Thông Tin** | **Ý Nghĩa** |
|---|---|
| **Số Hồ Sơ** | Mã hồ sơ (bắt buộc) |
| **Tên Hồ Sơ** | Tên mô tả (bắt buộc) |
| **Mã Hồ Sơ** | Kí hiệu hồ sơ |
| **Loại Hồ Sơ** | Hành chính / Nhân sự / Tài chính / Dự án |
| **Khách Hàng Liên Quan** | Công ty/khách hàng cấp bổ hồ sơ này |
| **Mức Độ Bảo Mật** | Bình thường / Mật / Tuyệt Mật |
| **Trạng Thái** | Đang xử lý / Đã hoàn thành / Tạm dừng / Hủy bỏ |
| **Văn Bản Đến** | Các văn bản đến liên quan |
| **Văn Bản Đi** | Các văn bản đi liên quan |

---

## 📖 HƯỚNG DẪN CHI TIẾT

### **QUY TRÌNH 1: TẠO VĂN BẢN ĐẾN**

#### **Bước 1: Vào Menu**
```
Quản Lý Văn Bản → Văn Bản Đến
(hoặc Văn Bản → Văn Bản Đến)
```

#### **Bước 2: Nhấn "Tạo Mới" (New)**
```
Điền các thông tin:
□ Số Văn Bản: 123/2024/XYZ      ← Bắt buộc
□ Trích Yếu: Gửi quy định...     ← Bắt buộc
□ Ngày Văn Bản: 01/01/2024
□ Ngày Đến: 01/01/2024
□ Cơ Quan Ban Hành: Sở TT&TT
□ Người Ký: Ông Nguyễn Văn A
□ Loại Văn Bản: [Chọn]
□ Độ Khẩn: [Thường/Khẩn/Hỏa Tốc]
□ Độ Mật: [Bình thường/Mật/Tuyệt Mật]
□ File Đính Kèm: [Upload file PDF/Word]
```

#### **Bước 3: Lưu**
```
Nhấn "Save" (Ctrl+S)
→ Văn bản được tạo với trạng thái "Mới"
```

#### **Bước 4: Cập Nhật Trạng Thái**
```
Thay đổi Trạng Thái:
□ Mới (ban đầu)
  ⬇
□ Đang xử lý (gán cho người xử lý)
  ⬇
□ Đã xử lý (hoàn thành xử lý)
```

---

### **QUY TRÌNH 2: TẠO VĂN BẢN ĐI**

#### **Bước 1: Vào Menu**
```
Quản Lý Văn Bản → Văn Bản Đi
```

#### **Bước 2: Tạo Mới**
```
□ Số Văn Bản: 456/2024/XYZ      ← Bắt buộc
□ Trích Yếu: Thông báo...       ← Bắt buộc
□ Ngày Văn Bản: 02/01/2024
□ Ngày Gửi: 02/01/2024
□ Nơi Nhận: Công ty ABC, tp.HCM
□ Người Ký: Bà Trần Thị B
□ Loại Văn Bản: Công văn
□ Độ Khẩn: Khẩn
□ Độ Mật: Bình thường
□ File Đính Kèm: [Upload]
```

#### **Bước 3: Phê Duyệt**
```
Trạng Thái chuyển:
□ Dự thảo (draft)
  ⬇
□ Chờ duyệt (assign cho người duyệt)
  ⬇
□ Đã duyệt (manager confirm)
  ⬇
□ Đã gửi (gửi đi thành công)
```

---

### **QUY TRÌNH 3: TẠO HỒ SƠ VĂN BẢN**

#### **Bước 1: Vào Menu**
```
Quản Lý Văn Bản → Hồ Sơ Văn Bản
```

#### **Bước 2: Tạo Mới**
```
□ Số Hồ Sơ: HS001/2024         ← Bắt buộc
□ Tên Hồ Sơ: Hồ sơ Dự Án X    ← Bắt buộc
□ Mã Hồ Sơ: PRJ-X-2024
□ Thời Gian Bắt Đầu: 01/01/2024
□ Thời Gian Kết Thúc: 31/12/2024
□ Loại Hồ Sơ: Dự Án
□ Khách Hàng Liên Quan: Công ty DEF
□ Mức Độ Bảo Mật: Bình thường
□ Mô Tả: Hồ sơ liên quan dự án xây dựng...
```

#### **Bước 3: Thêm Văn Bản Vào Hồ Sơ**
```
Phần "Văn Bản Đến" & "Văn Bản Đi":
→ Nhấn "Add line" hoặc "Add"
→ Chọn văn bản từ danh sách
→ Save

Lợi ích:
✓ Nhóm các văn bản liên quan
✓ Dễ tìm kiếm
✓ Quản lý theo Project/Khách hàng
```

---

## 💡 VÍ DỤ THỰC TẾ

### **Ví Dụ 1: Xử Lý Hợp Đồng Với Khách Hàng**

```
📌 TÌNH HUỐNG:
Công ty nhận được hợp đồng từ khách hàng ABC
→ Cần track -> Cung cấp văn bản → Gửi ký

📋 CÁC BƯỚC:

1️⃣ TẠO VĂN BẢN ĐẾN
   Quản Lý Văn Bản → Văn Bản Đến
   • Số Văn Bản: HD-ABC-001/2024
   • Trích Yếu: Hợp đồng cung cấp hàng
   • Ngày Đến: 15/03/2024
   • File Đính Kèm: HopDong.pdf
   • Trạng Thái: Mới → Đang xử lý

2️⃣ TẠO VĂN BẢN ĐI (Phản hồi)
   Quản Lý Văn Bản → Văn Bản Đi
   • Số Văn Bản: CV-002/2024
   • Trích Yếu: Gửi lại hợp đồng đã ký
   • Nơi Nhận: Công ty ABC
   • File Đính Kèm: HopDong_Signed.pdf
   • Trạng Thái: Dự thảo → Chờ duyệt → Đã duyệt → Đã gửi

3️⃣ TẠO HỒ SƠ VĂN BẢN
   • Tên Hồ Sơ: Hồ sơ Khách hàng ABC
   • Loại: Hành chính
   • Khách Hàng: ABC Company
   • Thêm 2 văn bản trên vào hồ sơ
   → Tất cả tài liệu liên quan ABC được nhóm lại

✅ LỢI ÍCH:
- Dễ tìm tài liệu ABC
- Tracking toàn bộ giao dịch
- Lịch sử rõ ràng
```

---

## 🎯 MẸO & THỦ THUẬT

### **1. Lọc & Tìm Kiếm Nhanh**
```
Ở tất cả danh sách, sử dụng bộ lọc:
□ Theo Loại Văn Bản (Công văn, Quyết định, v.v)
□ Theo Độ Khẩn (Thường, Khẩn, Hỏa Tốc)
□ Theo Độ Mật (Bình thường, Mật, Tuyệt Mật)
□ Theo Trạng Thái (Mới, Đang xử lý, Đã xử lý)
□ Theo Ngày (Tuần này, Tháng này, v.v)

VD: Tìm tất cả Công Văn Khẩn chưa xử lý
→ Filter by: Loại = Công văn + Độ Khẩn = Khẩn + Trạng Thái = Mới
```

### **2. Xuất & In Báo Cáo**
```
Vào danh sách → Chọn các bản ghi
→ Menu "Print" hoặc "Export Excel"
→ Chọn định dạng
→ Download
```

### **3. Nhóm Theo Hồ Sơ**
```
Thay vì tìm lẻ, hãy tạo hồ sơ for:
- Từng khách hàng
- Từng dự án
- Từng sự kiện
→ Sau này dễ tìm + quản lý
```

### **4. Với File Lớn**
```
Nếu file > 5MB:
□ Nén file trước (WinRAR, 7zip)
□ Hoặc upload link Google Drive

Trường File Đính Kèm nhận:
✓ PDF, Word, Excel, PPT
✓ JPG, PNG, ZIP
```

---

## 📞 LIÊN HỆ & HỖ TRỢ

**Có vấn đề?**
- Kiểm tra trạng thái văn bản
- Xem lịch sử thay đổi (History)
- Liên hệ admin để cấp quyền

---

**Tác Giả:** Quang Developer  
**Phiên Bản:** 1.0  
**Cập Nhật:** 24/03/2024
