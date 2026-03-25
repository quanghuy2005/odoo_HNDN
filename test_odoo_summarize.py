#!/usr/bin/env python3
import google.generativeai as genai

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
genai.configure(api_key=api_key)

print("\n" + "=" * 70)
print("🧪 TEST GEMINI 2.5 FLASH LITE - ODOO TÓM TẮT DOCUMENT")
print("=" * 70 + "\n")

try:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    test_text = """
    Hệ thống quản lý tài liệu điện tử Odoo 15 là một giải pháp toàn diện 
    cho các doanh nghiệp Việt Nam. Nó cung cấp khả năng lưu trữ, quản lý 
    phiên bản, ký số, tóm tắt tự động với AI, và theo dõi lịch sử thay đổi 
    cho tất cả tài liệu. Hệ thống hỗ trợ các định dạng tệp phổ biến như PDF, 
    Word, Excel và tích hợp hoàn toàn với Odoo ERP.
    """
    
    prompt = f"""Vui lòng tóm tắt nội dung sau thành 2-3 câu tiếng Việt:

{test_text}

Tóm tắt:"""
    
    response = model.generate_content(prompt)
    
    print("✅ THÀNH CÔNG!\n")
    print(f"📝 Văn bản gốc ({len(test_text)} ký tự):")
    print(f"   {test_text.strip()[:100]}...\n")
    print(f"🤖 Tóm tắt AI ({len(response.text)} ký tự):")
    print(f"   {response.text}\n")
    print("✨ API key hoạt động tốt! Sẵn sàng dùng trong Odoo.")
    
except Exception as e:
    print(f"❌ LỖI: {e}\n")
    import traceback
    traceback.print_exc()

print("=" * 70 + "\n")
