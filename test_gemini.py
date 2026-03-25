import google.generativeai as genai

api_key = "AIzaSyDoAsH1Yi6pDzg-3WHS9JY-8zkkj46i__w"
genai.configure(api_key=api_key)

# Test các model khả dụng
models_to_test = [
    'gemini-2.0-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro'
]

print("Testing Gemini models...\n")
for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Xin chào")
        print(f"✅ {model_name}: HOẠT ĐỘNG")
    except Exception as e:
        print(f"❌ {model_name}: {str(e)[:60]}")
