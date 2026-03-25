#!/usr/bin/env python3
import io

# Test PyPDF2 v1
try:
    from PyPDF2 import PdfFileReader
    print("✅ PdfFileReader imported (v1)")
except Exception as e:
    print(f"❌ PdfFileReader: {e}")

# Minimal PDF
pdf_bytes = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer << /Size 4 /Root 1 0 R >>
startxref
195
%%EOF"""

try:
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfFileReader(pdf_file)
    print(f"✅ PdfFileReader works with BytesIO! Pages: {reader.getNumPages()}")
except Exception as e:
    print(f"❌ PdfFileReader error: {type(e).__name__}: {e}")
