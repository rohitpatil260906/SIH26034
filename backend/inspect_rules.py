import os
import re
import json
import glob
from pypdf import PdfReader

RULES_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"

def analyze_pdf(file_path):
    filename = os.path.basename(file_path)
    file_size_kb = round(os.path.getsize(file_path) / 1024, 1)
    
    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        
        extracted_text = ""
        page_texts = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            page_texts.append(txt)
            extracted_text += "\n" + txt
            
        char_count = len(extracted_text.strip())
        word_count = len(extracted_text.split())
        
        # Scanned check: if text is negligible across pages
        avg_chars_per_page = char_count / max(1, num_pages)
        is_scanned = avg_chars_per_page < 60
        
        # Language detection: check Devanagari unicode range \u0900-\u097F
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', extracted_text))
        english_chars = len(re.findall(r'[A-Za-z]', extracted_text))
        
        if is_scanned and char_count < 30:
            language = "Undetermined (Scanned Image - Requires OCR)"
        elif hindi_chars > 50 and english_chars > 50:
            language = "Both (Hindi & English Bilingual)"
        elif hindi_chars > english_chars * 1.5:
            language = "Hindi"
        elif english_chars > 0:
            language = "English"
        else:
            language = "Undetermined (Scanned Image - Requires OCR)"
            
        readable = char_count > 50
        
        # First 500 characters of clean text for inspection
        clean_preview = " ".join(extracted_text.split())[:600]
        
        return {
            "filename": filename,
            "size_kb": file_size_kb,
            "pages": num_pages,
            "readable": readable,
            "char_count": char_count,
            "is_scanned": is_scanned,
            "language": language,
            "hindi_chars": hindi_chars,
            "english_chars": english_chars,
            "preview": clean_preview,
            "full_text": extracted_text
        }
    except Exception as e:
        return {
            "filename": filename,
            "size_kb": file_size_kb,
            "pages": 0,
            "readable": False,
            "char_count": 0,
            "is_scanned": True,
            "language": "Error reading PDF",
            "hindi_chars": 0,
            "english_chars": 0,
            "preview": f"Error: {str(e)}",
            "full_text": ""
        }

def run():
    files = sorted(glob.glob(os.path.join(RULES_DIR, "*.pdf")))
    print(f"Total PDF files found: {len(files)}")
    
    results = []
    for idx, f in enumerate(files):
        res = analyze_pdf(f)
        results.append(res)
        
    with open("pdf_analysis_results.json", "w", encoding="utf-8") as out:
        # Don't save entire full_text in json to keep it manageable
        cleaned_results = [{k: v for k, v in r.items() if k != "full_text"} for r in results]
        json.dump(cleaned_results, out, indent=2, ensure_ascii=False)
        
    print(f"Saved analysis to pdf_analysis_results.json")

if __name__ == "__main__":
    run()
