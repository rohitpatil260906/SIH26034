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
        try:
            EASYOCR_READER = easyocr.Reader(['hi'], download_enabled=False, gpu=False, verbose=False)
        except Exception:
            EASYOCR_READER = None
        EASYOCR_INITIALIZED = True
    except Exception:
        EASYOCR_READER = None
        EASYOCR_INITIALIZED = True
    return EASYOCR_READER

# -------------------------------------------------------------------
# OCR POST-PROCESSING & TYPO NORMALIZATION
# -------------------------------------------------------------------

def normalize_ocr_token(text: str, expected_type: Optional[str] = None) -> str:
    """Fuzzy fixes common OCR character confusions in statutory packaging contexts
    without modifying legal meaning or inventing proper nouns.
    Preserves company names, brand names, and addresses verbatim.
    """
    if not text:
        return ""
    t = text.strip()

    if expected_type == "number":
        # Numbers context: O/o -> 0, I/l -> 1, S/s -> 5, B -> 8
        res = []
        for ch in t:
            if ch in ('O', 'o'):
                res.append('0')
            elif ch in ('I', 'l', '|'):
                res.append('1')
            elif ch in ('S', 's'):
                res.append('5')
            elif ch == 'B':
                res.append('8')
            else:
                res.append(ch)
        return "".join(res)

    if expected_type == "unit":
        # Unit context: 1OO9 -> 100g, 5OOm1 -> 500ml
        t = re.sub(r'([0-9])OO([0-9a-zA-Z])', r'\g<1>00\2', t)
        t = re.sub(r'([0-9])O([0-9a-zA-Z])', r'\g<1>0\2', t)
        t = re.sub(r'(\d+)\s*9\b', r'\g<1>g', t)
        t = re.sub(r'(\d+)\s*m1\b', r'\g<1>ml', t)
        return t

    if expected_type == "date":
        # Date context: O3/2O24 -> 03/2024
        return t.replace('O', '0').replace('o', '0')
    
    # 1. Common OCR confusions in MRP labels
    t = re.sub(r'\bM8P\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bNRP\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bM\.?R\.?P\.?\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bMR\.P\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\b(?:Rs|RS)\s*[.:\-]?\s*', 'Rs. ', t)
    t = re.sub(r'₹\s*', '₹ ', t)
    
    # 2. Common OCR confusions in taxes clause
    t = re.sub(r'[1iI]nc[l1I](?:\.|\b)\s*(?:of)?\s*(?:al[l1I]\s*)?taxes', 'inclusive of all taxes', t, flags=re.I)
    t = re.sub(r'incl(?:\.|\b)\s*(?:of)?\s*al[l1]\s*taxes', 'inclusive of all taxes', t, flags=re.I)
    t = re.sub(r'inc[l1]\.?\s*taxes', 'incl. of all taxes', t, flags=re.I)
    t = re.sub(r'सभी\s*करों\s*सहित', 'inclusive of all taxes', t)
    
    # 3. Common OCR confusions in metric units (e.g. 50g where g looks like 9 or q)
    t = re.sub(r'(?<=\d)\s*(?:gms|gm)\b', ' g', t, flags=re.I)
    t = re.sub(r'(?<=\d)\s*(?:kgs)\b', ' kg', t, flags=re.I)
    t = re.sub(r'(?<=\d)\s*m[1liI|]\b', ' ml', t)
    t = re.sub(r'(?<=\d)\s*(?:ltrs|ltr)\b', ' l', t, flags=re.I)
    t = re.sub(r'\bnel\s*qty\b', 'Net Qty', t, flags=re.I)
    t = re.sub(r'\bnct\s*wt\b', 'Net Wt', t, flags=re.I)
    t = re.sub(r'\bnet\s*w[tl][.:;]?\s*', 'Net Wt: ', t, flags=re.I)
    
    # 4. Common OCR confusions in date headers
    t = re.sub(r'\bmfg\s*[.:\-]?\s*(?:date|on)?\b', 'Mfg Date: ', t, flags=re.I)
    t = re.sub(r'\bmfd\s*[.:\-]?\s*(?:date|on)?\b', 'Mfd Date: ', t, flags=re.I)
    t = re.sub(r'\bpkd\s*[.:\-]?\s*(?:date|on)?\b', 'Packed Date: ', t, flags=re.I)
    t = re.sub(r'\bexp\s*[.:\-]?\s*(?:date|on)?\b', 'Expiry Date: ', t, flags=re.I)
    t = re.sub(r'\bb\.?\s*no\b', 'Batch No', t, flags=re.I)
    
    # 5. Clean up redundant spaces around punctuation
    t = re.sub(r'\s+([,.:;])', r'\1', t)
    t = re.sub(r'\s{2,}', ' ', t)
    
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
    
    If OCR engines disagree significantly on a statutory field (e.g. MRP ₹240 vs ₹2400):
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
            # Significant disagreement on price (e.g. 240 vs 2400)
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
        return best_candidate, 0.94, False, "VERIFIED"
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
    surface: str = "Front (PDP)",
    targeted_crops: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[ExtractedLine], str]:
    """Scans the image using an intelligent, high-performance multi-pass OCR architecture:
    
    Pass 1: Primary full-image scan on original image (or contrast-enhanced if low contrast).
    Pass 2: Targeted high-density crop pass (e.g. coding panel, declaration panel) with
            coordinate re-mapping to capture tiny dot-matrix dates & batch codes.
    Pass 3: Selective variant enhancement pass (adaptive threshold / sharpened) if
            primary pass yielded low confidence or missed critical statutory areas.
    Pass 4: 90° & 270° orientation fallback if vertical or rotated text is detected.
    
    Stores for EVERY detected item:
    - raw_text: unmodified OCR string
    - text: normalized text token
    - confidence: numerical confidence (boosted if verified across multiple passes)
    - bbox: normalized percentage coordinates (0-100)
    - preprocessing_version: variant used
    - engine: Tesseract or EasyOCR
    - surface: packaging surface
    """
    all_lines: List[ExtractedLine] = []
    seen_texts: List[str] = []
    raw_transcripts: List[str] = []
    engine_results: List[Dict[str, Any]] = []
    
    w, h = pil_image.size

    # --- PASS 1: PRIMARY SCAN ON BASE IMAGE ---
    primary_variant = "original"
    if "original" in variants:
        prim_img = variants["original"][0]
    else:
        prim_img = pil_image

    t_res = run_tesseract_ocr(prim_img)
    for r in t_res:
        r["variant"] = primary_variant
    engine_results.extend(t_res)

    e_res = run_easyocr_lines(prim_img)
    for r in e_res:
        r["variant"] = primary_variant
    engine_results.extend(e_res)

    # --- PASS 2: TARGETED HIGH-DENSITY REGION / CROP PASS ---
    # If variants contains "multiscale" (the targeted bottom 40% crop where MRP & Dates reside),
    # or if specific crops were passed in targeted_crops
    if "multiscale" in variants:
        ms_img = variants["multiscale"][0]
        # Run targeted recognition on the crop
        crop_t_res = run_tesseract_ocr(ms_img)
        crop_e_res = run_easyocr_lines(ms_img)
        
        # Coordinate shift: crop corresponds to bottom y in [55%, 100%]
        for r in crop_t_res + crop_e_res:
            orig_bbox = r.get("bbox", [10.0, 10.0, 80.0, 10.0])
            shifted_y = round(55.0 + (orig_bbox[1] * 0.45), 2)
            shifted_h = round(orig_bbox[3] * 0.45, 2)
            r["bbox"] = [orig_bbox[0], shifted_y, orig_bbox[2], shifted_h]
            r["variant"] = "multiscale_crop"
            engine_results.append(r)

    # If specific high-resolution crops were provided (from region detector)
    if targeted_crops:
        for crop_info in targeted_crops[:3]:
            crop_img = crop_info.get("image")
            crop_bbox = crop_info.get("bbox")  # [x%, y%, w%, h%]
            if crop_img and crop_bbox:
                c_lines = run_easyocr_lines(crop_img)
                for r in c_lines:
                    # Shift into full image percentage space
                    cb = r.get("bbox", [0, 0, 100, 100])
                    mapped_x = round(crop_bbox[0] + (cb[0] * crop_bbox[2] / 100.0), 2)
                    mapped_y = round(crop_bbox[1] + (cb[1] * crop_bbox[3] / 100.0), 2)
                    mapped_w = round(cb[2] * crop_bbox[2] / 100.0, 2)
                    mapped_h = round(cb[3] * crop_bbox[3] / 100.0, 2)
                    r["bbox"] = [mapped_x, mapped_y, mapped_w, mapped_h]
                    r["variant"] = "targeted_region_crop"
                    engine_results.append(r)

    # --- PASS 3: SELECTIVE VARIANT FALLBACK ---
    # If fewer than 5 lines found, or if critical fields (MRP / Date / Net Qty) are missing,
    # run on contrast_enhanced or adaptive_threshold
    has_statutory = any(re.search(r'\b(?:mrp|₹|rs|net\s*qty|mfd|exp|pvt|ltd)\b', r.get("text", ""), re.I) for r in engine_results)
    if len(engine_results) < 5 or not has_statutory:
        fallback_keys = ["contrast_enhanced", "adaptive_threshold", "clahe_enhanced"]
        for fk in fallback_keys:
            if fk in variants and len(engine_results) < 15:
                var_img = variants[fk][0]
                t_fb = run_tesseract_ocr(var_img)
                for r in t_fb:
                    r["variant"] = fk
                engine_results.extend(t_fb)
                
                e_fb = run_easyocr_lines(var_img)
                for r in e_fb:
                    r["variant"] = fk
                engine_results.extend(e_fb)
                if len(engine_results) >= 8:
                    break

    # --- PASS 4: ORIENTATION FALLBACK ---
    # If fewer than 2 lines found, test 90° and 270° rotations
    if len(engine_results) < 2:
        for angle in [90, 270]:
            try:
                rot_img = pil_image.rotate(angle, expand=True)
                t_rot = run_tesseract_ocr(rot_img)
                e_rot = run_easyocr_lines(rot_img)
                for r in t_rot + e_rot:
                    r["variant"] = f"rotated_{angle}"
                engine_results.extend(t_rot)
                engine_results.extend(e_rot)
            except Exception:
                pass

    # --- DEDUPLICATION, CONSENSUS BOOSTING & NORMALIZATION ---
    line_idx = 0
    candidate_occurrences: Dict[str, int] = {}
    
    # First tally occurrences across passes to calculate consensus
    for item in engine_results:
        raw_t = item.get("text", "").strip()
        if not raw_t:
            continue
        cleaned_key = re.sub(r'[^a-zA-Z0-9]', '', raw_t).lower()
        if cleaned_key:
            candidate_occurrences[cleaned_key] = candidate_occurrences.get(cleaned_key, 0) + 1

    for item in engine_results:
        raw_txt = item.get("text", "").strip()
        if not raw_txt:
            continue
            
        norm_txt = normalize_ocr_token(raw_txt)
        lower_norm = norm_txt.lower()
        
        # Check duplicate
        is_dup = False
        for seen in seen_texts:
            if difflib.SequenceMatcher(None, lower_norm, seen).ratio() > 0.85:
                is_dup = True
                break
                
        if is_dup:
            continue
            
        seen_texts.append(lower_norm)
        line_idx += 1
        
        # Confidence computation with consensus boost:
        # If detected in multiple passes, boost confidence
        base_conf = float(item.get("confidence", 0.90))
        cleaned_key = re.sub(r'[^a-zA-Z0-9]', '', raw_txt).lower()
        passes_count = candidate_occurrences.get(cleaned_key, 1)
        if passes_count >= 2:
            base_conf = min(0.99, base_conf + 0.05)
            
        is_unc = base_conf < 0.65 or "?" in norm_txt or "[unclear]" in norm_txt.lower()
        
        bbox_coords = item.get("bbox", [10.0, min(90.0, line_idx * 7.0), 80.0, 5.0])
        engine_name = item.get("engine", "EasyOCR")
        variant_name = item.get("variant", "original")
        
        all_lines.append(ExtractedLine(
            line_index=line_idx,
            text=norm_txt,
            raw_text=raw_txt,
            confidence=round(base_conf, 2),
            bbox=BoundingBox(
                x=float(bbox_coords[0]),
                y=float(bbox_coords[1]),
                width=float(bbox_coords[2]),
                height=float(bbox_coords[3]),
                label=f"Line {line_idx}"
            ),
            is_uncertain=is_unc,
            surface=surface,
            preprocessing_version=variant_name,
            engine=engine_name
        ))
        raw_transcripts.append(norm_txt)

    full_transcript = "\n".join(raw_transcripts)
    return all_lines, full_transcript
