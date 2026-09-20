"""
Full-Page OCR Processing for the 3 Incomplete Legal Metrology Documents:
1. 8(x)_0_1732870750--13.pdf (6 pages)
2. 8(v)_0_1732861119--8.pdf (9 pages)
3. 8_1732871406--1.pdf (83 pages)

Features:
- Incremental caching per page to backend/data/ocr_target_three_cache.json
- Preserves Hindi (Devanagari) & English bilingual text
- Tracks exact source PDF filename and page number
- Marks unreadable pages as UNREADABLE_MANUAL_REVIEW
- Extracts structured rules into backend/data/legal_metrology_knowledge_base.json
"""

import os
import sys
import io
import time
import json
import re
from PIL import Image
from pypdf import PdfReader
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import easyocr

PDF_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"
CACHE_FILE = r"D:\SIH\SIH26034\backend\data\ocr_target_three_cache.json"
KB_FILE = r"D:\SIH\SIH26034\backend\data\legal_metrology_knowledge_base.json"

TARGET_DOCS = [
    ("8(x)_0_1732870750--13.pdf", 6),
    ("8(v)_0_1732861119--8.pdf", 9),
    ("8_1732871406--1.pdf", 83)
]

def clean(text):
    return " ".join(text.split())

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def run_ocr():
    print("=" * 60)
    print("STARTING FULL-PAGE OCR ON 3 INCOMPLETE LEGAL METROLOGY DOCUMENTS")
    print("=" * 60)
    
    reader = easyocr.Reader(['en', 'hi'], gpu=False, verbose=False)
    cache = load_cache()
    
    total_pages_all = sum(pages for _, pages in TARGET_DOCS)
    processed_count = len(cache)
    print(f"Total target pages: {total_pages_all} | Already in cache: {processed_count}")

    for doc_name, expected_pages in TARGET_DOCS:
        pdf_path = os.path.join(PDF_DIR, doc_name)
        if not os.path.exists(pdf_path):
            print(f"ERROR: File not found: {pdf_path}")
            continue
            
        reader_pdf = PdfReader(pdf_path)
        actual_pages = len(reader_pdf.pages)
        print(f"\n>>> Processing {doc_name} ({actual_pages} pages) <<<")

        for p_idx in range(actual_pages):
            p_num = p_idx + 1
            key = f"{doc_name}#P{p_num}"
            
            if key in cache and cache[key].get("status") in ["SUCCESS", "UNREADABLE_MANUAL_REVIEW"]:
                print(f"[{doc_name} P.{p_num}/{actual_pages}] Skipped (Cached: {cache[key]['status']})")
                continue

            page = reader_pdf.pages[p_idx]
            t0 = time.time()

            # Check if page has image
            if not page.images:
                cache[key] = {
                    "source_pdf_filename": doc_name,
                    "source_pdf_page_number": p_num,
                    "status": "UNREADABLE_MANUAL_REVIEW",
                    "reason": "No image found on page",
                    "language": "None",
                    "char_count": 0,
                    "text": ""
                }
                save_cache(cache)
                print(f"[{doc_name} P.{p_num}/{actual_pages}] UNREADABLE: No image on page")
                continue

            try:
                img_data = page.images[0].data
                img = Image.open(io.BytesIO(img_data)).convert("RGB")
                # Scale appropriately for fast yet accurate CPU recognition
                w, h = img.size
                if max(w, h) > 1100:
                    scale = 1100 / max(w, h)
                    img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

                # Execute OCR with NumPy array
                img_np = np.array(img)
                lines = reader.readtext(img_np, detail=0)
                full_text = "\n".join(lines).strip()
                dt = time.time() - t0

                # Analyze language
                hindi_chars = len(re.findall(r'[\u0900-\u097F]', full_text))
                eng_chars = len(re.findall(r'[A-Za-z]', full_text))

                if len(full_text) < 25:
                    status = "UNREADABLE_MANUAL_REVIEW"
                    reason = f"Insufficient text recognized ({len(full_text)} chars); page may be blank or heavily degraded"
                    lang = "Indeterminate"
                else:
                    status = "SUCCESS"
                    reason = "OCR completed successfully"
                    if hindi_chars > 30 and eng_chars > 30:
                        lang = "Bilingual (Hindi & English)"
                    elif hindi_chars > eng_chars:
                        lang = "Hindi"
                    else:
                        lang = "English"

                cache[key] = {
                    "source_pdf_filename": doc_name,
                    "source_pdf_page_number": p_num,
                    "status": status,
                    "reason": reason,
                    "language": lang,
                    "hindi_chars": hindi_chars,
                    "english_chars": eng_chars,
                    "char_count": len(full_text),
                    "duration_sec": round(dt, 2),
                    "text": full_text
                }
                save_cache(cache)
                print(f"[{doc_name} P.{p_num}/{actual_pages}] {status} in {dt:.1f}s | {len(full_text)} chars | {lang}")

            except Exception as e:
                dt = time.time() - t0
                cache[key] = {
                    "source_pdf_filename": doc_name,
                    "source_pdf_page_number": p_num,
                    "status": "UNREADABLE_MANUAL_REVIEW",
                    "reason": f"OCR processing exception: {str(e)}",
                    "language": "Error",
                    "char_count": 0,
                    "duration_sec": round(dt, 2),
                    "text": ""
                }
                save_cache(cache)
                print(f"[{doc_name} P.{p_num}/{actual_pages}] ERROR: {e}")

    # Now update knowledge base
    update_knowledge_base(cache)

def update_knowledge_base(cache):
    print("\n" + "=" * 60)
    print("UPDATING KNOWLEDGE BASE WITH OCR RESULTS")
    print("=" * 60)

    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # Remove previous preliminary OCR entries for the 3 files so we don't have duplicate or obsolete first-page entries
    target_names = [d[0] for d in TARGET_DOCS]
    kb["rules"] = [r for r in kb["rules"] if r.get("source_pdf_filename") not in target_names]
    print(f"Base KB rules (excluding 3 target files): {len(kb['rules'])}")

    new_entries = []
    
    for key, pdata in sorted(cache.items()):
        if pdata.get("status") != "SUCCESS":
            continue
            
        doc_name = pdata["source_pdf_filename"]
        p_num = pdata["source_pdf_page_number"]
        txt = pdata["text"]
        lang = pdata["language"]

        # Parse rules, schedules, and sections in text
        # Look for Rule citations
        paragraphs = [p.strip() for p in txt.split("\n\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [p.strip() for p in txt.split("\n") if len(p.strip()) > 40]
            
        for p in paragraphs:
            rule_match = re.search(r'(?:rule|Rule)\s*([0-9]{1,2}(?:\s*\([0-9a-zA-Z]+\))*)', p)
            sched_match = re.search(r'(First|Second|Third|Fourth|Fifth|Sixth|Seventh)\s+Schedule', p, re.IGNORECASE)
            sub_match = re.search(r'(?:sub-rule|sub rule)\s*\(([0-9a-zA-Z]+)\)', p, re.IGNORECASE)
            cl_match = re.search(r'(?:clause)\s*\(([a-zA-Z0-9]+)\)', p, re.IGNORECASE)
            sec_match = re.search(r'(?:section|Section)\s*([0-9]{1,2})', p)

            if rule_match or sched_match or sec_match or "compound" in p.lower() or "prescribe" in p.lower():
                r_num = f"Rule {rule_match.group(1)}" if rule_match else (
                    f"{sched_match.group(0).title()}" if sched_match else (
                        f"Section {sec_match.group(1)}" if sec_match else "Legal Metrology Provisions"
                    )
                )
                sub_r = f"Sub-rule ({sub_match.group(1)})" if sub_match else (
                    f"Clause ({cl_match.group(1)})" if cl_match else "General"
                )

                # Product categories
                products = []
                if re.search(r'garment|hosiery|apparel', p, re.IGNORECASE): products.append("Readymade Garments / Hosiery")
                if re.search(r'electronic|device|phone', p, re.IGNORECASE): products.append("Electronic Products / Devices")
                if re.search(r'edible oil|vanaspati|ghee', p, re.IGNORECASE): products.append("Edible Oil & Fats")
                if re.search(r'medical device', p, re.IGNORECASE): products.append("Medical Devices")
                if re.search(r'farm produce|agricultural', p, re.IGNORECASE): products.append("Agricultural / Farm Produce")
                if re.search(r'fuel|tank', p, re.IGNORECASE): products.append("Vehicle Fuel Capacity Tank")
                prod_str = ", ".join(products) if products else "General Packaged Commodities"

                # Exceptions
                exc_m = re.search(r'(?:except|provided that|shall not apply|exemption)\s*([^.;]+)', p, re.IGNORECASE)
                exc_str = exc_m.group(1).strip() if exc_m else "None specifically mentioned"

                new_entries.append({
                    "rule_number": r_num,
                    "sub_rule_or_clause": sub_r,
                    "requirement": p[:350],
                    "product_category": prod_str,
                    "exceptions": exc_str[:200],
                    "amendment_or_change": f"Full-Page OCR Digitized from {doc_name}",
                    "effective_date": "As per statutory Gazette / Advisory",
                    "source_pdf_filename": doc_name,
                    "source_pdf_page_number": p_num,
                    "language": lang,
                    "original_text_reference": p
                })

    # Add new entries
    current_count = len(kb["rules"])
    for idx, entry in enumerate(new_entries, 1):
        entry["entry_id"] = f"LM-KB-{current_count + idx:04d}"
        kb["rules"].append(entry)

    kb["total_rules_extracted"] = len(kb["rules"])
    kb["fully_processed_target_docs"] = [d[0] for d in TARGET_DOCS]
    kb["last_updated_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    print(f"Total new rule entries extracted from 3 target PDFs: {len(new_entries)}")
    print(f"Updated Total Rules in Knowledge Base: {len(kb['rules'])}")
    print(f"Saved to: {KB_FILE}")

if __name__ == "__main__":
    run_ocr()
