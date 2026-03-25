#!/usr/bin/env python3
import google.generativeai as genai

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
genai.configure(api_key=api_key)

models_to_test = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
]

print("=" * 60)
print("TESTING GEMINI MODELS WITH NEW API KEY")
print("=" * 60 + "\n")

best_model = None
for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Xin chào, tôi là AI")
        if response and response.text:
            print(f"✅ {model_name}: HOẠT ĐỘNG TỐT")
            print(f"   Response: {response.text[:50]}...\n")
            if best_model is None:
                best_model = model_name
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"❌ {model_name}: {error_msg}\n")

if best_model:
    print("=" * 60)
    print(f"🎯 BEST MODEL: {best_model}")
    print("=" * 60)
else:
    print("⚠️  NO WORKING MODELS FOUND")
