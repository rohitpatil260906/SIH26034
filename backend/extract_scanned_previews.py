import os
import glob
import json
from pypdf import PdfReader

RULES_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"
PREVIEWS_DIR = r"D:\SIH\SIH26034\backend\scanned_previews"
os.makedirs(PREVIEWS_DIR, exist_ok=True)

with open("detailed_pdf_analysis.json", encoding="utf-8") as f:
    data = json.load(f)

scanned = [d for d in data if d["is_scanned"]]

extracted = []
for s in scanned:
    path = os.path.join(RULES_DIR, s["filename"])
    reader = PdfReader(path)
    page = reader.pages[0]
    out_img = os.path.join(PREVIEWS_DIR, f"{s['index']}_{s['filename'][:30]}.png")
    
    if page.images:
        img_obj = page.images[0]
        with open(out_img, "wb") as img_file:
            img_file.write(img_obj.data)
        extracted.append((s["index"], s["filename"], out_img, len(img_obj.data)))
    else:
        extracted.append((s["index"], s["filename"], "NO_IMAGE", 0))

print(f"Extracted first page images for {len(extracted)} scanned documents")
for e in extracted:
    print(e[0], e[1], "-> Image:", e[2] != "NO_IMAGE")
