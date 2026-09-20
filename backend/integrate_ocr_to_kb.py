import os
import json
import re

KB_FILE = r"D:\SIH\SIH26034\backend\data\legal_metrology_knowledge_base.json"
OCR_FILE = "scanned_ocr_results.json"

with open(KB_FILE, "r", encoding="utf-8") as f:
    kb = json.load(f)

with open(OCR_FILE, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

print(f"Loaded existing KB with {len(kb['rules'])} rules.")
print(f"Loaded OCR data for {len(ocr_data)} scanned documents.")

# Map preview image filename back to original PDF filename
# Preview filenames look like: '10_2023.7.10 Medical Devices revi.png', '17_8(i)_0_1732860957--2.pdf.png'
# Let's match by prefix index or substring
import glob
all_pdfs = sorted(glob.glob(r"D:\SIH\SIH26034\legal_metrology_rules\*.pdf"))
pdf_map = {}
for idx, p in enumerate(all_pdfs, 1):
    pdf_map[idx] = os.path.basename(p)

additional_entries = []

for img_name, ocr_item in ocr_data.items():
    # extract index prefix
    m = re.match(r'^([0-9]+)_', img_name)
    if not m:
        continue
    idx = int(m.group(1))
    orig_pdf = pdf_map.get(idx, img_name)
    
    lines = ocr_item.get("raw_lines", [])
    full_text = ocr_item.get("text", "")
    
    # Check language
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', full_text))
    eng_chars = len(re.findall(r'[A-Za-z]', full_text))
    if hindi_chars > 30 and eng_chars > 30:
        lang = "Bilingual (Hindi & English)"
    elif hindi_chars > eng_chars:
        lang = "Hindi"
    else:
        lang = "English"
        
    # Extract notification or circular subject
    subject_lines = [l for l in lines if any(k in l.lower() for k in ["subject", "sub:", "regard", "advisory", "order", "direction", "rule", "pcr"])]
    subject = " | ".join(subject_lines[:3]) if subject_lines else " ".join(lines[:4])
    
    # Identify product/category
    products = []
    if re.search(r'garment|hosiery|apparel', full_text, re.IGNORECASE):
        products.append("Readymade Garments / Hosiery")
    if re.search(r'medical device', full_text, re.IGNORECASE):
        products.append("Medical Devices")
    if re.search(r'edible oil|fats|vanaspati|ghee', full_text, re.IGNORECASE):
        products.append("Edible Oil & Fats")
    if re.search(r'fuel capacity|vehicle tank|tank', full_text, re.IGNORECASE):
        products.append("Vehicle Fuel Capacity Tank")
    if re.search(r'farm produce|agricultural|50 kg', full_text, re.IGNORECASE):
        products.append("Agricultural / Farm Produce up to 50kg")
    if re.search(r'compounding|section 48|penalty', full_text, re.IGNORECASE):
        products.append("Compounding of Offenses")
    if re.search(r'font|numeral|table 1|height', full_text, re.IGNORECASE):
        products.append("Table 1 Numeral Height & Font Size")
    prod_str = ", ".join(products) if products else "General Packaged Commodities"
    
    # Identify Rule mention
    rule_m = re.search(r'(?:rule|Rule)\s*([0-9]{1,2}(?:\s*\([0-9a-zA-Z]+\))*)', full_text)
    r_num = f"Rule {rule_m.group(1)}" if rule_m else ("Section 48 / Rule 32A" if "compounding" in prod_str else "Legal Metrology Advisory / Guidelines")
    
    # Exceptions
    exc_m = re.search(r'(?:except|provided that|exemption|shall not apply)\s*([^.;|]+)', full_text, re.IGNORECASE)
    exc_str = exc_m.group(1).strip() if exc_m else "None specifically mentioned"

    # Effective date
    date_m = re.search(r'(?:dated|date of issue|the)\s*([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}|[0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+[0-9]{4})', full_text)
    eff_date = date_m.group(1) if date_m else "As per advisory"

    entry = {
        "rule_number": r_num,
        "sub_rule_or_clause": "Advisory / Direction / SOP",
        "requirement": subject[:300] if len(subject) > 20 else full_text[:300],
        "product_category": prod_str,
        "exceptions": exc_str[:200],
        "amendment_or_change": f"Department Advisory / SOP in {orig_pdf}",
        "effective_date": eff_date,
        "source_pdf_filename": orig_pdf,
        "source_pdf_page_number": 1,
        "language": lang,
        "original_text_reference": full_text[:500]
    }
    additional_entries.append(entry)

print(f"Extracted {len(additional_entries)} additional rule entries from OCR of scanned PDFs.")

# Add to KB
current_count = len(kb["rules"])
for idx, entry in enumerate(additional_entries, 1):
    entry["entry_id"] = f"LM-KB-{current_count + idx:04d}"
    kb["rules"].append(entry)

kb["total_rules_extracted"] = len(kb["rules"])
kb["successfully_processed_pdfs"] = 24
kb["scanned_pdfs_processed_via_ocr"] = len(additional_entries)
kb["scanned_pdfs_requiring_manual_high_res_audit"] = ["8_1732871406--1.pdf (83-page manual)", "8(v)_0_1732861119--8.pdf (9-page compilation)", "8(x)_0_1732870750--13.pdf (6-page guidelines)"]

with open(KB_FILE, "w", encoding="utf-8") as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print(f"Updated KB now contains {len(kb['rules'])} rules total!")
