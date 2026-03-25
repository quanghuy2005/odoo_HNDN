#!/usr/bin/env python3
import google.generativeai as genai

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
genai.configure(api_key=api_key)

print("=" * 60)
print("LISTING AVAILABLE MODELS")
print("=" * 60 + "\n")

try:
    models = genai.list_models()
    print("Available models:\n")
    for model in models:
        print(f"  • {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            if methods:
                print(f"    Methods: {', '.join(methods)}")
except Exception as e:
    print(f"Error: {e}")
