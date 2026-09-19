"""
Stage 2: Text Normalization, Garbage Rejection, & Candidate Consensus
====================================================================
Provides:
1. Character confusion normalization (context-aware, preserving raw_text)
2. Currency symbol and metric unit preservation (₹, Rs., INR, g, ml, L, kg)
3. Garbage OCR filtering and uncertainty detection
4. Multi-pass candidate consensus and disagreement tracking
5. Duplicate region merging based on spatial IoU and string similarity
"""

import re
import difflib
from typing import Tuple, List, Dict, Any, Optional


def is_garbage_ocr(text: str) -> bool:
    """Detects obvious OCR noise, low-entropy punctuation, or non-lexical fragments."""
    if not text:
        return True
    t = text.strip()
    if len(t) == 0:
        return True

    # If length is 1 and not an alphanumeric digit or legal character
    if len(t) == 1 and not (t.isalnum() or t in "₹$€"):
        return True

    # High ratio of non-alphanumeric punctuation spam (e.g. "- a — pe—— - | AKMI 0| HA")
    alnums = sum(1 for c in t if c.isalnum() or c in "₹")
    non_alnums = len(t) - alnums
    if len(t) > 6 and (non_alnums / len(t)) > 0.65:
        return True

    # Repeated punctuation strings (e.g. "----", "....", "____", "| | |")
    if re.match(r'^[\-_=.~|/\\:;,\'"`!@#$%^&*()+\[\]{} ]+$', t):
        return True

    return False


def normalize_text_candidate(raw_text: str) -> Tuple[str, float]:
    """Generates a contextually normalized candidate from raw OCR while preserving original text.
    
    Returns:
        (normalized_candidate, normalization_confidence)
    """
    if not raw_text:
        return "", 1.0

    t = raw_text.strip()
    norm_conf = 0.95

    # 0. Multilingual digit mapping (Devanagari ०-९ to 0-9)
    devanagari_digits = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
    for dev_ch, ar_ch in devanagari_digits.items():
        t = t.replace(dev_ch, ar_ch)

    # 1. Currency normalization (keep attached and properly spaced)
    t = re.sub(r'\bM8P\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bNRP\b', 'MRP', t, flags=re.I)
    t = re.sub(r'\bM\.?R\.?P\.?\b', 'MRP', t, flags=re.I)
    t = re.sub(r'₹\s*', '₹', t)
    t = re.sub(r'\b(?:Rs|RS)\s*[.:\-]?\s*', 'Rs. ', t)

    # 2. Obvious digit confusions after currency: MRP Rs. 2O9 -> MRP Rs. 209
    def fix_price_digits(match):
        prefix = match.group(1)
        num_part = match.group(2)
        fixed_num = num_part.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1').replace('S', '5')
        return f"{prefix}{fixed_num}"

    t = re.sub(r'(₹\s*|Rs\.\s*)([0-9OoIlS\s\.]+)', fix_price_digits, t, flags=re.I)

    # 3. Metric units confusions: 1OOg -> 100 g, 5OOm1 -> 500 ml
    def fix_unit_digits(match):
        num_part = match.group(1)
        unit = match.group(2).lower()
        fixed_num = num_part.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')
        if unit in ('m1', 'ml', 'mil', 'mi'):
            return f"{fixed_num} ml"
        elif unit in ('g', 'gm', 'gms'):
            return f"{fixed_num} g"
        elif unit in ('kg', 'kgs'):
            return f"{fixed_num} kg"
        elif unit in ('l', 'ltr', 'ltrs'):
            return f"{fixed_num} L"
        return f"{fixed_num} {unit}"

    t = re.sub(r'([0-9OoIl]+)\s*(m1|ml|gms|gm|g|kgs|kg|ltrs|ltr|l)\b', fix_unit_digits, t, flags=re.I)

    # 4. Date confusions: O8/2O26 -> 08/2026
    def fix_date_digits(match):
        d_str = match.group(0)
        return d_str.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')

    t = re.sub(r'\b[0-9OoIl]{1,2}[/\-\.][0-9OoIl]{2,4}\b', fix_date_digits, t)

    # 5. PIN code confusions: 6 digits
    def fix_pin_digits(match):
        pin_str = match.group(0)
        return pin_str.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')

    t = re.sub(r'\b[1-9][0-9OoIl]{5}\b', fix_pin_digits, t)

    # 6. Standard statutory keyword headers
    t = re.sub(r'\bnel\s*qty\b', 'Net Qty', t, flags=re.I)
    t = re.sub(r'\bnct\s*wt\b', 'Net Wt', t, flags=re.I)
    t = re.sub(r'\bnet\s*w[tl][.:;]?\s*', 'Net Wt: ', t, flags=re.I)
    t = re.sub(r'\bnet\s*quantity[.:;]?\s*', 'Net Quantity: ', t, flags=re.I)
    t = re.sub(r'\bmfg\s*[.:\-]?\s*(?:date|on)?\b', 'Mfg Date: ', t, flags=re.I)
    t = re.sub(r'\bmfd\s*[.:\-]?\s*(?:date|on)?\b', 'Mfd Date: ', t, flags=re.I)
    t = re.sub(r'\bpkd\s*[.:\-]?\s*(?:date|on)?\b', 'Packed Date: ', t, flags=re.I)
    t = re.sub(r'\bexp\s*[.:\-]?\s*(?:date|on)?\b', 'Expiry Date: ', t, flags=re.I)
    t = re.sub(r'\bb\.?\s*no[.:\-]?\s*', 'Batch No: ', t, flags=re.I)

    # 7. Clean up whitespace
    t = re.sub(r'\s+([,.:;])', r'\1', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()

    return t, norm_conf


def compute_string_similarity(s1: str, s2: str) -> float:
    """Computes normalized Levenshtein-like string similarity (0.0 to 1.0)."""
    return difflib.SequenceMatcher(None, s1.strip().lower(), s2.strip().lower()).ratio()


def calculate_bbox_iou(box1: List[float], box2: List[float]) -> float:
    """Calculates Intersection-over-Union (IoU) between two bounding boxes [x, y, w, h]."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    ix1 = max(x1, x2)
    iy1 = max(y1, y2)
    ix2 = min(x1 + w1, x2 + w2)
    iy2 = min(y1 + h1, y2 + h2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter_area = iw * ih

    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area
    if union_area <= 0.0:
        return 0.0

    return inter_area / union_area


def merge_competing_candidates(
    readings: List[Dict[str, Any]]
) -> Tuple[str, str, float, List[str]]:
    """Ensembles multiple OCR readings for the same spatial region.
    
    Returns:
        (best_raw_text, best_normalized_text, consensus_confidence, competing_candidates)
    """
    if not readings:
        return "", "", 0.0, []

    # Sort by confidence descending
    sorted_readings = sorted(readings, key=lambda r: r.get("confidence", 0.0), reverse=True)
    best = sorted_readings[0]
    best_raw = best.get("raw_text", "").strip()
    best_norm = best.get("normalized_text", "").strip()
    if not best_norm and best_raw:
        best_norm, _ = normalize_text_candidate(best_raw)
    base_conf = float(best.get("confidence", 0.85))

    competing: List[str] = []
    matches = 0
    for r in sorted_readings:
        cand = r.get("raw_text", "").strip()
        if not cand:
            continue
        sim = compute_string_similarity(best_raw, cand)
        if sim >= 0.85:
            matches += 1
        elif cand not in competing:
            competing.append(cand)

    # Boost confidence if multiple independent passes produced matching text
    if matches >= 3:
        final_conf = min(0.99, base_conf + 0.10)
    elif matches == 2:
        final_conf = min(0.98, base_conf + 0.05)
    else:
        final_conf = base_conf

    return best_raw, best_norm, round(final_conf, 2), competing
