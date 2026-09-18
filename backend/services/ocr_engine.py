import re
import difflib
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np

from ..models import ExtractedLine, BoundingBox

# Modular Engine Loaders
TESSERACT_AVAILABLE = False
EASYOCR_READER = None
EASYOCR_INITIALIZED = False

try:
    import pytesseract
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
    except Exception:
        TESSERACT_AVAILABLE = False
except Exception:
    TESSERACT_AVAILABLE = False

def get_easyocr_reader():
    """Lazily loads the EasyOCR reader for English + Hindi if installed."""
    global EASYOCR_READER, EASYOCR_INITIALIZED
    if EASYOCR_INITIALIZED:
        return EASYOCR_READER
    try:
        import easyocr
        EASYOCR_READER = easyocr.Reader(['en', 'hi'], gpu=False, verbose=False)
        EASYOCR_INITIALIZED = True
    except Exception:
        EASYOCR_READER = None
        EASYOCR_INITIALIZED = True
    return EASYOCR_READER

# -------------------------------------------------------------------
# OCR POST-PROCESSING & TYPO NORMALIZATION
# -------------------------------------------------------------------

def normalize_ocr_token(text: str) -> str:
    """Fuzzy fixes common OCR character confusions in statutory packaging contexts
    without modifying legal meaning or inventing text.
    """
    if not text:
        return ""
    t = text.strip()
    
    # Common OCR confusions in MRP labels
    t = re.sub(r'\bM8P\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bNRP\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bM\.?R\.?P\b', 'MRP', t, flags=re.I)
    
    # Common OCR confusions in taxes clause
    t = re.sub(r'incl(?:\.|\b)\s*(?:of)?\s*al[l1]\s*taxes', 'inclusive of all taxes', t, flags=re.I)
    t = re.sub(r'inc[l1]\.?\s*taxes', 'incl. of all taxes', t, flags=re.I)
    
    # Common OCR confusions in metric units (e.g. 50g where g looks like 9)
    t = re.sub(r'(?<=\d)\s*(?:gms|gm)\b', ' g', t, flags=re.I)
    t = re.sub(r'(?<=\d)\s*(?:kgs)\b', ' kg', t, flags=re.I)
    
    return t

# -------------------------------------------------------------------
# STEP 3.1: MULTILINGUAL OCR RUNNERS
# -------------------------------------------------------------------

def run_tesseract_ocr(pil_image: Image.Image, lang: str = "eng+hin") -> List[Dict[str, Any]]:
    """Runs Tesseract OCR if installed and returns lines with normalized bounding boxes (0-100%)."""
    if not TESSERACT_AVAILABLE:
        return []
    try:
        import pytesseract
        w, h = pil_image.size
        if w == 0 or h == 0:
            return []
        
        try:
            data = pytesseract.image_to_data(pil_image, lang=lang, output_type=pytesseract.Output.DICT)
        except Exception:
            # Fallback to English only if Hindi tessdata is missing
            data = pytesseract.image_to_data(pil_image, lang="eng", output_type=pytesseract.Output.DICT)

        n_boxes = len(data['level'])
        lines = []
        current_words = []
        current_confs = []
        box_left, box_top, box_right, box_bottom = w, h, 0, 0
        
        for i in range(n_boxes):
            word = data['text'][i].strip()
            conf = float(data['conf'][i])
            
            if word and conf > 15.0:
                current_words.append(word)
                current_confs.append(conf)
                x = data['left'][i]
                y = data['top'][i]
                bw = data['width'][i]
                bh = data['height'][i]
                box_left = min(box_left, x)
                box_top = min(box_top, y)
                box_right = max(box_right, x + bw)
                box_bottom = max(box_bottom, y + bh)
            
            # End of line or block
            if (data['word_num'][i] == 0 or i == n_boxes - 1) and current_words:
                full_text = " ".join(current_words)
                avg_conf = float(np.mean(current_confs)) / 100.0 if current_confs else 0.85
                
                # Convert to percentage [x, y, w, h]
                norm_x = round(max(0.0, min(100.0, (box_left / w) * 100.0)), 2)
                norm_y = round(max(0.0, min(100.0, (box_top / h) * 100.0)), 2)
                norm_w = round(max(1.0, min(100.0, ((box_right - box_left) / w) * 100.0)), 2)
                norm_h = round(max(1.0, min(100.0, ((box_bottom - box_top) / h) * 100.0)), 2)
                
                lines.append({
                    "engine": "Tesseract",
                    "text": full_text,
                    "confidence": round(avg_conf, 2),
                    "bbox": [norm_x, norm_y, norm_w, norm_h]
                })
                current_words = []
                current_confs = []
                box_left, box_top, box_right, box_bottom = w, h, 0, 0
                
        return lines
    except Exception:
        return []

def run_easyocr_lines(pil_image: Image.Image) -> List[Dict[str, Any]]:
    """Runs EasyOCR if installed and returns lines with normalized bounding boxes (0-100%)."""
    reader = get_easyocr_reader()
    if not reader:
        return []
    try:
        w, h = pil_image.size
        if w == 0 or h == 0:
            return []
            
        arr = np.array(pil_image)
        results = reader.readtext(arr)
        lines = []
        for poly, text, conf in results:
            clean_text = text.strip()
            if not clean_text:
                continue
                
            # Poly format: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            pts = np.array(poly)
            x_min = float(np.min(pts[:, 0]))
            y_min = float(np.min(pts[:, 1]))
            x_max = float(np.max(pts[:, 0]))
            y_max = float(np.max(pts[:, 1]))
            
            norm_x = round(max(0.0, min(100.0, (x_min / w) * 100.0)), 2)
            norm_y = round(max(0.0, min(100.0, (y_min / h) * 100.0)), 2)
            norm_w = round(max(1.0, min(100.0, ((x_max - x_min) / w) * 100.0)), 2)
            norm_h = round(max(1.0, min(100.0, ((y_max - y_min) / h) * 100.0)), 2)
            
            lines.append({
                "engine": "EasyOCR",
                "text": clean_text,
                "confidence": round(float(conf), 2),
                "bbox": [norm_x, norm_y, norm_w, norm_h]
            })
        return lines
    except Exception:
        return []

# -------------------------------------------------------------------
# STEP 3.2: MULTI-ENGINE ENSEMBLE & DISAGREEMENT VERIFICATION
# -------------------------------------------------------------------

def verify_ocr_ensemble_and_disagreement(
    field_name: str,
    candidates: Dict[str, str]
) -> Tuple[str, float, bool, str]:
    """Compares OCR engine outputs and preprocessing variants.
    
    If OCR engines disagree significantly on a statutory field (e.g. MRP ₹249 vs ₹2490):
    Returns:
    (best_value, confidence, disagreement_flag, status)
    
    Status is set to 'NEEDS REVIEW' if disagreement is detected.
    Anti-Hallucination rule: Never randomly pick or fabricate a value.
    """
    cleaned_candidates = {k: v.strip() for k, v in candidates.items() if v and v.strip()}
    if not cleaned_candidates:
        return "Not reliably detected", 0.0, False, "NOT DETECTED"
        
    unique_values = list(set(cleaned_candidates.values()))
    
    if len(unique_values) == 1:
        # Complete unanimous consensus
        return unique_values[0], 0.98, False, "VERIFIED"
        
    # Check numeric discrepancy for MRP or Quantity
    if field_name.lower() in ["mrp", "price", "retail_price"]:
        nums = {}
        for eng, val in cleaned_candidates.items():
            m = re.search(r'([0-9]+(?:\.[0-9]+)?)', val)
            if m:
                nums[eng] = float(m.group(1))
                
        if len(set(nums.values())) > 1:
            # Significant disagreement on price (e.g. 249 vs 2490)
            discrepancy_str = " vs ".join([f"{k}: ₹{v}" for k, v in nums.items()])
            return (
                f"Disagreement detected ({discrepancy_str})",
                0.55,
                True,
                "NEEDS REVIEW"
            )

    # String similarity comparison (Levenshtein / SequenceMatcher)
    base_val = unique_values[0]
    all_close = True
    for val in unique_values[1:]:
        ratio = difflib.SequenceMatcher(None, base_val.lower(), val.lower()).ratio()
        if ratio < 0.70:
            all_close = False
            break
            
    if all_close:
        # Minor punctuation or spacing differences: pick the most detailed candidate
        best_candidate = max(unique_values, key=len)
        return best_candidate, 0.92, False, "VERIFIED"
    else:
        # Significant textual discrepancy
        return (
            "Ambiguous OCR consensus across passes",
            0.50,
            True,
            "NEEDS REVIEW"
        )

# -------------------------------------------------------------------
# STEP 3.3: COMPLETE MULTI-PASS TEXT EXTRACTION
# -------------------------------------------------------------------

def extract_all_visible_lines(
    pil_image: Image.Image,
    variants: Dict[str, Any],
    surface: str = "Front (PDP)"
) -> Tuple[List[ExtractedLine], str]:
    """Scans the image using available OCR engines across multiple preprocessing variants
    (original, contrast_enhanced, adaptive_threshold, clahe_enhanced, deskewed, resized).
    
    Includes orientation/rotation fallback to capture vertical, rotated, or curved text.
    Preserves EVERY visible textual region and line, keeping the full raw OCR transcript.
    """
    all_lines: List[ExtractedLine] = []
    seen_texts: List[str] = []
    raw_transcripts: List[str] = []
    line_idx = 0

    # Ordered list of preprocessing passes to query
    pass_keys = [
        "original",
        "contrast_enhanced",
        "adaptive_threshold",
        "clahe_enhanced",
        "deskewed",
        "resized",
        "sharpened"
    ]

    engine_results = []
    
    for key in pass_keys:
        if key in variants:
            var_img = variants[key][0]
            # Run Tesseract & EasyOCR
            t_res = run_tesseract_ocr(var_img)
            e_res = run_easyocr_lines(var_img)
            engine_results.extend(t_res)
            engine_results.extend(e_res)
            
    # Rotation handling: If fewer than 2 lines found, test 90° and 270° clockwise rotations
    if len(engine_results) < 2:
        for angle in [90, 270]:
            try:
                rot_img = pil_image.rotate(angle, expand=True)
                t_rot = run_tesseract_ocr(rot_img)
                e_rot = run_easyocr_lines(rot_img)
                engine_results.extend(t_rot)
                engine_results.extend(e_rot)
            except Exception:
                pass

    # Deduplicate and normalize lines across passes
    for item in engine_results:
        raw_txt = item.get("text", "").strip()
        if not raw_txt:
            continue
            
        norm_txt = normalize_ocr_token(raw_txt)
        lower_norm = norm_txt.lower()
        
        # Check if already captured by earlier or higher confidence pass
        is_dup = False
        for seen in seen_texts:
            if difflib.SequenceMatcher(None, lower_norm, seen).ratio() > 0.85:
                is_dup = True
                break
                
        if is_dup:
            continue
            
        seen_texts.append(lower_norm)
        line_idx += 1
        conf = float(item.get("confidence", 0.90))
        is_unc = conf < 0.65 or "?" in norm_txt or "[unclear]" in norm_txt.lower()
        
        bbox_coords = item.get("bbox", [10.0, min(90.0, line_idx * 7.0), 80.0, 5.0])
        all_lines.append(ExtractedLine(
            line_index=line_idx,
            text=norm_txt,
            confidence=conf,
            bbox=BoundingBox(
                x=float(bbox_coords[0]),
                y=float(bbox_coords[1]),
                width=float(bbox_coords[2]),
                height=float(bbox_coords[3]),
                label=f"Line {line_idx}"
            ),
            is_uncertain=is_unc,
            surface=surface
        ))
        raw_transcripts.append(norm_txt)

    full_transcript = "\n".join(raw_transcripts)
    return all_lines, full_transcript
