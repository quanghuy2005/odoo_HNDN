#!/usr/bin/env python3
"""Test full PDF -> Gemini summarization workflow"""
import io
import base64
import google.genai as genai
from PyPDF2 import PdfReader

api_key = "AIzaSyB7n1U3GAOAMAUpkRVzb89iuBwmjZh-dlM"
client = genai.Client(api_key=api_key)

# Sample PDF with Vietnamese content
pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 180 >>
stream
BT
/F1 10 Tf
50 750 Td
(QUYET DINH) Tj
0 -15 Td
(Cong ty TNHH Phat trien Cong Nghe Viet Nam phe duyet) Tj
0 -15 Td
(ke hoach phat trien nhan su voi tong kinh phi 250 trieu dong.) Tj
0 -15 Td
(Quyet dinh nay co hieu luc tu ngay 1/7/2024.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000273 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
452
%%EOF
"""

print("\n" + "=" * 70)
print("🎯 FULL WORKFLOW TEST: PDF → EXTRACT → SUMMARIZE")
print("=" * 70 + "\n")

try:
    # STEP 1: Extract PDF text
    print("📖 Step 1: Reading PDF...")
    pdf_file = io.BytesIO(pdf_content)
    reader = PdfReader(pdf_file)
    
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() + "\n"
    
    print(f"✅ PDF extracted ({len(extracted_text)} chars)")
    print(f"   Content: {extracted_text.strip()[:80]}...\n")
    
    # STEP 2: Summarize with Gemini
    print("🤖 Step 2: Summarizing with Gemini 2.5 Flash Lite...")
    response = client.models.generate_content(
        model='models/gemini-2.5-flash-lite',
        contents=f"Hãy tóm tắt 1 câu: {extracted_text}"
    )
    
    summary = response.text
    print(f"✅ Summary generated:\n   {summary}\n")
    
    # STEP 3: Classify
    print("🏷️  Step 3: Classifying document...")
    classify_resp = client.models.generate_content(
        model='models/gemini-2.5-flash-lite',
        contents=f"Phân loại (1 từ): {extracted_text}"
    )
    
    classification = classify_resp.text.strip().lower()
    print(f"✅ Classification: {classification}\n")
    
    print("=" * 70)
    print("✨ FULL WORKFLOW PASSED - READY FOR ODOO!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}\n")
    import traceback
    traceback.print_exc()
