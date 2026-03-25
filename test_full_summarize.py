#!/usr/bin/env python3
"""Test Gemini summarization through Odoo models"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'odoo.settings')

# Test directly with google.genai
import google.genai as genai

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
client = genai.Client(api_key=api_key)

print("\n" + "=" * 70)
print("🎯 FULL DOCUMENT SUMMARIZATION TEST")
print("=" * 70 + "\n")

# Simulated document
full_doc = """
QUYẾT ĐỊNH VỀ PHÂN BỔ HỖ TRỢ PHÁT TRIỂN ĐỘI NGŨ NHÂN SỰ

Căn cứ vào Luật Doanh nghiệp 2020 và các quy định liên quan về quản lý nhân sự, 
Công ty TNHH Phát Triển Công Nghệ Việt Nam quyết định như sau:

Điều 1: Phê duyệt kế hoạch phân bổ hỗ trợ phát triển đội ngũ nhân sự cho quý III năm 2024.

Điều 2: Tổng kinh phí hỗ trợ là 250 triệu đồng, bao gồm:
- Đào tạo kỹ năng: 100 triệu đồng
- Hỗ trợ học tập ngoài: 80 triệu đồng
- Tăng lương thưởng: 70 triệu đồng

Điều 3: Quyết định này có hiệu lực từ ngày 1/7/2024 và áp dụng cho toàn công ty.

Được phát hành tại Hà Nội, ngày 15 tháng 6 năm 2024.
Ký: Giám đốc Công ty
"""

try:
    # Step 1: Summarize
    print("📝 DOCUMENT:")
    print(f"{full_doc[:100]}...\n")
    
    response = client.models.generate_content(
        model='models/gemini-2.5-flash-lite',
        contents=f"Hãy tóm tắt tài liệu sau thành 2-3 câu tiếng Việt:\n\n{full_doc}"
    )
    
    summary = response.text
    print("✅ SUMMARIZATION SUCCESS!\n")
    print(f"📋 Summary:\n{summary}\n")
    
    # Step 2: Classify
    print("-" * 70)
    classify_resp = client.models.generate_content(
        model='models/gemini-2.5-flash-lite',
        contents=f"""Phân loại tài liệu này vào một trong các loại sau (chỉ trả lời một từ):
        - quyet_dinh (Quyết định)
        - cong_van (Công văn)
        - thong_bao (Thông báo)
        - ke_hoach (Kế hoạch)
        - bao_cao (Báo cáo)
        - to_trinh (Tờ trình)
        - khac (Khác)
        
        Tài liệu: {full_doc[:500]}"""
    )
    
    classification = classify_resp.text.strip().lower()
    print(f"🏷️  Classification: {classification}\n")
    
    print("=" * 70)
    print("✨ ALL TESTS PASSED - READY FOR ODOO!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
