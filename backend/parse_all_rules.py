import os
import glob
import json
import re
from pypdf import PdfReader

RULES_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"
OUTPUT_JSON = r"D:\SIH\SIH26034\backend\data\legal_metrology_knowledge_base.json"
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

files = sorted(glob.glob(os.path.join(RULES_DIR, "*.pdf")))

def clean(text):
    return " ".join(text.split())

# Regex patterns for rule citations
RULE_PATTERNS = [
    r'(?:rule|Rule)\s+([0-9]{1,2}\s*(?:\([0-9a-zA-Z]+\))*)',
    r'(?:sub-rule|sub rule|Sub-rule)\s*\(([0-9a-zA-Z]+)\)',
    r'(?:clause|Clause)\s*\(([a-zA-Z0-9]+)\)',
    r'(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh)\s+Schedule',
]

def parse_pdf(file_path):
    filename = os.path.basename(file_path)
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    
    doc_entries = []
    
    # Track overall document info
    full_doc_text = ""
    page_texts = {}
    for p_num, page in enumerate(reader.pages, 1):
        txt = page.extract_text() or ""
        page_texts[p_num] = txt
        full_doc_text += f"\n--- Page {p_num} ---\n" + txt

    # Check if scanned
    if len(full_doc_text.strip()) < 50 * max(1, total_pages):
        return {
            "status": "NEEDS_OCR",
            "filename": filename,
            "pages": total_pages,
            "entries": [],
            "reason": "Scanned image PDF with no embedded text layer. Requires high-resolution OCR."
        }
        
    # Extract notification metadata
    notif_match = re.search(r'(?:G\.S\.R\.|GSR)\s*([0-9]+(?:\s*\([A-Z]\))?)', full_doc_text, re.IGNORECASE)
    notification_no = notif_match.group(0) if notif_match else ""
    
    date_match = re.search(r'(?:dated|New Delhi, the)\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4})', full_doc_text)
    doc_date = date_match.group(1) if date_match else ""
    
    # Effective date regex
    eff_match = re.search(r'(?:shall come into force (?:on|with effect from))\s*(?:the\s*)?([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4}|1st\s+day\s+of\s+[A-Za-z]+,?\s+[0-9]{4}|date of their publication in the Official Gazette)', full_doc_text, re.IGNORECASE)
    effective_date = eff_match.group(1) if eff_match else doc_date

    # Process page by page
    for p_num in range(1, total_pages + 1):
        txt = page_texts[p_num]
        if not txt.strip():
            continue
            
        # Separate Hindi and English parts if present
        # Gazette notifications typically have Hindi in first half/page and English in second half/page
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        
        # Look for specific rule amendments
        # Let's find sections or paragraphs that modify/specify rules
        paragraphs = re.split(r'\n\s*\n|\n(?=[0-9]+\.\s+)', txt)
        for p_idx, para in enumerate(paragraphs):
            para_clean = clean(para)
            if len(para_clean) < 30:
                continue
                
            # Check if this paragraph references a Rule or Schedule
            rule_mentions = re.findall(r'(?:rule|Rule)\s+([0-9]{1,2}(?:\s*\([0-9a-zA-Z]+\))*)', para_clean)
            schedule_mentions = re.findall(r'(First|Second|Third|Fourth|Fifth|Sixth|Seventh)\s+Schedule', para_clean, re.IGNORECASE)
            subrule_mentions = re.findall(r'(?:sub-rule|sub rule)\s*\(([0-9a-zA-Z]+)\)', para_clean, re.IGNORECASE)
            clause_mentions = re.findall(r'(?:clause)\s*\(([a-zA-Z0-9]+)\)', para_clean, re.IGNORECASE)
            
            # Detect product/category
            products = []
            if re.search(r'garment|hosiery|readymade|apparel', para_clean, re.IGNORECASE):
                products.append("Readymade Garments / Hosiery")
            if re.search(r'electronic|mobile|smartphone|earphone|tablet', para_clean, re.IGNORECASE):
                products.append("Electronic Products / Devices")
            if re.search(r'pan masala', para_clean, re.IGNORECASE):
                products.append("Pan Masala")
            if re.search(r'medical device', para_clean, re.IGNORECASE):
                products.append("Medical Devices")
            if re.search(r'edible oil|vanaspati|ghee|fat', para_clean, re.IGNORECASE):
                products.append("Edible Oil & Fats")
            if re.search(r'e-commerce|filter|country of origin', para_clean, re.IGNORECASE):
                products.append("E-commerce / Country of Origin")
            if re.search(r'agricultural produce|farm produce|grain|pulse', para_clean, re.IGNORECASE):
                products.append("Agricultural / Farm Produce")
            if re.search(r'fuel capacity|vehicle tank', para_clean, re.IGNORECASE):
                products.append("Vehicle Fuel Capacity Tank")
            if re.search(r'unit sale price|USP', para_clean, re.IGNORECASE):
                products.append("Unit Sale Price (USP)")
            if re.search(r'loose|50 kg', para_clean, re.IGNORECASE):
                products.append("Packages above 25kg/50kg or Industrial Consumer")
                
            product_str = ", ".join(products) if products else "General Packaged Commodities"
            
            # Detect exceptions
            exceptions = []
            exc_match = re.findall(r'(?:except|provided that|shall not apply to|other than|exemption)\s*([^.;]+)', para_clean, re.IGNORECASE)
            if exc_match:
                exceptions = [clean(m)[:150] for m in exc_match]
            exception_str = "; ".join(exceptions) if exceptions else "None specifically mentioned"

            # Determine Hindi vs English text
            has_hindi = len(re.findall(r'[\u0900-\u097F]', para)) > 20
            has_english = len(re.findall(r'[A-Za-z]', para)) > 20
            lang = "Bilingual" if (has_hindi and has_english) else ("Hindi" if has_hindi else "English")

            # If rule mentioned, create structured entry
            if rule_mentions or schedule_mentions or len(products) > 0 or "amendment" in para_clean.lower():
                r_num = rule_mentions[0] if rule_mentions else (f"{schedule_mentions[0]} Schedule" if schedule_mentions else "Legal Metrology Rules General")
                sub_r = f"Sub-rule ({subrule_mentions[0]})" if subrule_mentions else (f"Clause ({clause_mentions[0]})" if clause_mentions else "General")
                
                # Effective date for this entry
                entry_eff_date = effective_date
                eff_local = re.search(r'(?:w\.e\.f\.|with effect from|come into force on)\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4}|1st\s+day\s+of\s+[A-Za-z]+,?\s+[0-9]{4})', para_clean, re.IGNORECASE)
                if eff_local:
                    entry_eff_date = eff_local.group(1)

                doc_entries.append({
                    "rule_number": f"Rule {r_num}" if not r_num.startswith("Rule") and not "Schedule" in r_num and not "General" in r_num else r_num,
                    "sub_rule_or_clause": sub_r,
                    "requirement": para_clean[:350],
                    "product_category": product_str,
                    "exceptions": exception_str,
                    "amendment_or_change": f"Amended via {notification_no or filename}" if notification_no else f"Notification in {filename}",
                    "effective_date": entry_eff_date or "As per notification",
                    "source_pdf_filename": filename,
                    "source_pdf_page_number": p_num,
                    "language": lang,
                    "original_text_reference": para_clean
                })
                
    return {
        "status": "SUCCESS",
        "filename": filename,
        "pages": total_pages,
        "notification_no": notification_no,
        "doc_date": doc_date,
        "effective_date": effective_date,
        "entries": doc_entries
    }

def main():
    all_results = []
    total_rules = 0
    success_count = 0
    scanned_count = 0
    failed_docs = []
    
    for f in files:
        res = parse_pdf(f)
        if res["status"] == "SUCCESS":
            success_count += 1
            entries = res["entries"]
            total_rules += len(entries)
            all_results.append(res)
        else:
            scanned_count += 1
            failed_docs.append(res)
            all_results.append(res)

    print(f"Total PDFs examined: {len(files)}")
    print(f"Successfully processed: {success_count}")
    print(f"Scanned / Need OCR: {scanned_count}")
    print(f"Total structured rule entries extracted: {total_rules}")

    # Build knowledge base structure
    kb = {
        "knowledge_base_name": "Legal Metrology (Packaged Commodities) Statutory Rules Knowledge Base",
        "version": "2026.1",
        "total_source_pdfs": len(files),
        "successfully_processed_pdfs": success_count,
        "scanned_pdfs_requiring_ocr": scanned_count,
        "total_rules_extracted": total_rules,
        "storage_path": OUTPUT_JSON,
        "rules": []
    }
    
    rule_id = 1
    for r in all_results:
        for entry in r.get("entries", []):
            entry_copy = dict(entry)
            entry_copy["entry_id"] = f"LM-KB-{rule_id:04d}"
            rule_id += 1
            kb["rules"].append(entry_copy)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(kb, out, indent=2, ensure_ascii=False)

    print(f"Saved complete Knowledge Base to: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
