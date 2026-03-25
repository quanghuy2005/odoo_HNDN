#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Google Generative AI API"""

import google.generativeai as genai

# API Key
API_KEY = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"

def test_api():
    """Test Google Generative AI API"""
    print("=" * 60)
    print("🧪 Testing Google Generative AI API")
    print("=" * 60)
    
    try:
        # Configure API
        genai.configure(api_key=API_KEY)
        print("✅ API configured successfully")
        
        # List available models
        print("\n📋 Available Models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}: {model.display_name}")
        
        # Test with Gemini Flash (cheaper, faster)
        print("\n🚀 Testing with Gemini 2.5 Flash...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content("What is Odoo ERP? Answer in 50 words.")
        print(f"\n📝 Response:\n{response.text}")
        
        print("\n✅ API Test Successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"📌 Details: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)
