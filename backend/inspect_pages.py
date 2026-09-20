import os
import glob
import json
import re
from pypdf import PdfReader

RULES_DIR = r"D:\SIH\SIH26034\legal_metrology_rules"

files = sorted(glob.glob(os.path.join(RULES_DIR, "*.pdf")))

def inspect_pages():
    for f in files:
        name = os.path.basename(f)
        try:
            reader = PdfReader(f)
            text_by_page = []
            for p_num, p in enumerate(reader.pages, 1):
                txt = p.extract_text() or ""
                if len(txt.strip()) > 30:
                    text_by_page.append({
                        "page": p_num,
                        "char_count": len(txt),
                        "snippet": " ".join(txt.split())[:300]
                    })
            if text_by_page:
                print(f"=== {name} ({len(reader.pages)} pages, {len(text_by_page)} with text) ===")
                for pinfo in text_by_page:
                    print(f"  Page {pinfo['page']}: {pinfo['snippet'][:120]}...")
        except Exception as e:
            print(f"ERR: {name}: {e}")

if __name__ == "__main__":
    inspect_pages()
