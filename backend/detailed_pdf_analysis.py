import os
import glob
import json
import re
from pypdf import PdfReader

RULES_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"

files = sorted(glob.glob(os.path.join(RULES_DIR, "*.pdf")))

analysis = []

for idx, f in enumerate(files):
    name = os.path.basename(f)
    size_kb = round(os.path.getsize(f) / 1024, 1)
    
    try:
        reader = PdfReader(f)
        pages = len(reader.pages)
        meta = reader.metadata or {}
        
        # Metadata title/subject
        pdf_title = str(meta.title or "") if hasattr(meta, 'title') else ""
        pdf_subject = str(meta.subject or "") if hasattr(meta, 'subject') else ""
        
        full_text = ""
        for p in reader.pages:
            t = p.extract_text() or ""
            full_text += "\n" + t
            
        char_count = len(full_text.strip())
        is_scanned = (char_count / max(1, pages)) < 60
        
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', full_text))
        english_chars = len(re.findall(r'[A-Za-z]', full_text))
        
        if not is_scanned:
            if hindi_chars > 50 and english_chars > 50:
                lang = "Bilingual (Hindi & English)"
            elif hindi_chars > english_chars:
                lang = "Hindi"
            else:
                lang = "English"
        else:
            lang = "Needs OCR (Scanned Image)"
            
        # Clean lines
        lines = [l.strip() for l in full_text.splitlines() if l.strip()]
        preview = " | ".join(lines[:10])[:500]
        
        analysis.append({
            "index": idx + 1,
            "filename": name,
            "size_kb": size_kb,
            "pages": pages,
            "char_count": char_count,
            "is_scanned": is_scanned,
            "language": lang,
            "hindi_chars": hindi_chars,
            "english_chars": english_chars,
            "meta_title": pdf_title,
            "meta_subject": pdf_subject,
            "preview": preview,
            "first_lines": lines[:15]
        })
    except Exception as e:
        analysis.append({
            "index": idx + 1,
            "filename": name,
            "size_kb": size_kb,
            "pages": 0,
            "char_count": 0,
            "is_scanned": True,
            "language": "Error",
            "hindi_chars": 0,
            "english_chars": 0,
            "meta_title": "",
            "meta_subject": "",
            "preview": str(e),
            "first_lines": []
        })

with open("detailed_pdf_analysis.json", "w", encoding="utf-8") as out:
    json.dump(analysis, out, indent=2, ensure_ascii=False)

print("Saved detailed analysis for", len(analysis), "PDFs")
