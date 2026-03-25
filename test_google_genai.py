#!/usr/bin/env python3
import google.genai as genai

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
client = genai.Client(api_key=api_key)

print("\n" + "=" * 70)
print("🧪 TEST GOOGLE.GENAI (NEW API) - GEMINI 2.5 FLASH LITE")
print("=" * 70 + "\n")

try:
    test_text = "Hệ thống Odoo 15 là ERP mạnh mẽ cho doanh nghiệp Việt Nam"
    
    response = client.models.generate_content(
        model='models/gemini-2.5-flash-lite',
        contents=f"Tóm tắt 1 câu: {test_text}"
    )
    
    print("✅ THÀNH CÔNG!\n")
    print(f"📝 Input: {test_text}\n")
    print(f"🤖 Response:\n{response.text}\n")
    print("✨ google.genai hoạt động tốt!")
    
except Exception as e:
    print(f"❌ LỖI: {e}\n")
    import traceback
    traceback.print_exc()

print("=" * 70 + "\n")
