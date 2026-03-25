#!/usr/bin/env python3
"""Test PyPDF2 3.0 with actual PDF"""
import io
import base64
from PyPDF2 import PdfReader

# Minimal but valid PDF
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
<< /Length 65 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World - Odoo PDF Test) Tj
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
337
%%EOF
"""

print("\n" + "=" * 70)
print("🧪 TEST PYPDF2 3.0 - PDF READING")
print("=" * 70 + "\n")

try:
    # Test 1: PdfReader import
    print("✅ PdfReader imported successfully")
    
    # Test 2: Create PdfReader from BytesIO
    pdf_file = io.BytesIO(pdf_content)
    reader = PdfReader(pdf_file)
    print(f"✅ PdfReader created from BytesIO")
    
    # Test 3: Get pages
    pages = reader.pages
    print(f"✅ .pages attribute accessed: {len(pages)} page(s)")
    
    # Test 4: Extract text
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += page_text + "\n"
        print(f"✅ Page {page_num} text extracted ({len(page_text)} chars)")
    
    print(f"\n📝 Extracted text:\n{text}\n")
    
    print("=" * 70)
    print("✨ ALL TESTS PASSED - PyPDF2 3.0 WORKS!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}\n")
    import traceback
    traceback.print_exc()
