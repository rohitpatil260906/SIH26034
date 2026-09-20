import os
import sys
import glob
import json

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import easyocr

PREVIEWS_DIR = r"D:\SIH\SIH26034\backend\scanned_previews"

reader = easyocr.Reader(['en', 'hi'], gpu=False, verbose=False)

images = sorted(glob.glob(os.path.join(PREVIEWS_DIR, "*.png")))
print(f"Running OCR on {len(images)} scanned previews...")

ocr_results = {}
for img_path in images:
    base = os.path.basename(img_path)
    print(f"Processing {base}...")
    try:
        # Read text
        results = reader.readtext(img_path, detail=0)
        clean_text = " | ".join(results[:25])
        ocr_results[base] = {
            "text": clean_text,
            "raw_lines": results[:20]
        }
    except Exception as e:
        ocr_results[base] = {
            "text": f"Error: {e}",
            "raw_lines": []
        }

with open("scanned_ocr_results.json", "w", encoding="utf-8") as f:
    json.dump(ocr_results, f, indent=2, ensure_ascii=False)

print("Saved scanned OCR results to scanned_ocr_results.json")
