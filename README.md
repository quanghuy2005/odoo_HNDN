---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)



# 1. Các tính năng Nổi Bật của Dự án (Kế toán, CRM, Nhân sự)

### 1.1 Quản lý Tài Liệu & Kế Toán (quan_ly_tai_lieu_ke_toa)
- Quản lý vòng đời tài liệu: Hợp đồng, Báo giá, Hóa đơn,... với 7 trạng thái chuẩn.
- Gửi yêu cầu phê duyệt và theo dõi lịch sử phê duyệt.
- Quản lý file đính kèm với nhiều phiên bản (hỗ trợ hiển thị và tải xuống).
- **[NEW] Đọc và trích xuất dữ liệu từ PDF.** 
- **[NEW] Tích hợp AI (Claude/ChatGPT) tóm tắt nhanh nội dung Hợp đồng.**
- **[NEW] Tích hợp tự động Backup Hợp Đồng/Tài liệu lên Google Drive ngay khi hoàn tất.**
- Tự động sinh `Hóa Đơn Nháp` (Draft Invoice) trên phân hệ Kế Toán `account.move` khi Hợp đồng chuyển sang `Hoàn Tất`.
- Chạy nền cảnh báo tự động các Hợp đồng sắp hết hạn trong vòng 7 ngày.

### 1.2 Quản lý Khách Hàng (quan_ly_khach_hang_crm - Kế thừa Khách hàng chuẩn)
- Lưu trữ Tình trạng khách hàng, Ghi chú kinh doanh, Vai trò người đại diện.
- Form hiển thị trực quan toàn bộ `Tài Liệu Của Khách` theo danh sách thông minh (Smart Button).
- Tính tổng tiền các Hợp đồng đã chốt thành công.
- Tích hợp tính năng biến CRM Lead (Cơ hội khách hàng tiềm năng) tự động sang một Draft Hợp Đồng.

### 1.3 Quản lý Nhân Sự (quan_ly_nhan_su_mo_rong - Kế thừa Personnel)
- Mở rộng model `hr.employee`, 1 nhân viên quản lý dải danh sách Khách hàng đa dạng.
- **Tự Động Giao Việc:** Khi admin thực hiện "Lưu trữ" (Archive / Nghỉ việc) một Nhân Sự, hệ thống quét auto toàn bộ Hợp Đồng chưa Ký của họ và tự nhận diện `Manager` chuyển giao hồ sơ. Không bao giờ gãy vụn dữ liệu.
- **[NEW] Hệ thống Báo Cáo KPI (Dashboard Cá nhân):** Tính tự động "Tổng Số Hợp đồng chốt được" và "Tổng Doanh Thu mang về" ghim luôn lên form nhân viên.

# 2. Cài đặt công cụ, môi trường và các thư viện cần thiết

## 1.1. Clone project.
```
git clone https://gitlab.com/anhlta/odoo-fitdnu.git
```

```
git checkout cntt15_01
```


## 1.2. cài đặt các thư viện cần thiết

Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
## 1.3. khởi tạo môi trường ảo.

`python3.10 -m venv ./venv`
Thay đổi trình thông dịch sang môi trường ảo và chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu

```
source venv/bin/activate
pip3 install -r requirements.txt
```

# 2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.

`sudo docker-compose up -d`

# 3. Setup tham số chạy cho hệ thống

## 3.1. Khởi tạo odoo.conf

Tạo tệp **odoo.conf** có nội dung như sau:

```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
```
Có thể kế thừa từ **odoo.conf.template**


# 4. Chạy hệ thống và cài đặt các ứng dụng cần thiết
Lệnh chạy
```
python3 odoo-bin.py -c odoo.conf -u all
```

Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

Hoàn tất
    
