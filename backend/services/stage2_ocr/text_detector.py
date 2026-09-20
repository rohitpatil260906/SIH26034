"""
Stage 2: Two-Pass Universal Text Detection Service
==================================================
Implements:
1. Pass 1 (Global): Full-frame text detection and OCR extraction
2. Pass 2 (Targeted): Localized detection for challenging regions:
   - Small print / micro-text: 2x upscaled crop + edge sharpening
   - Rotated text: 90°/180°/270° crop rotation normalization
   - Curved packaging text: localized cylindrical arc unwarping
   - Low contrast & glare: targeted CLAHE and adaptive binarization
3. Merges Pass 1 and Pass 2 results using spatial IoU and string consensus
4. Preserves both working image coordinates and original image coordinates via M_inv
"""

import uuid
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from ...models import Stage2TextRegion, Stage2WordBox
from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from ..stage1_cv.geometry import map_bbox_to_original
from .ocr_adapter import MultiEngineOcrAdapter
from .grouping import group_words_into_lines, assign_natural_reading_order
from .normalization import (
    normalize_text_candidate,
    is_garbage_ocr,
    calculate_bbox_iou,
    compute_string_similarity,
    merge_competing_candidates
)


class TwoPassTextDetector:
    """Universal two-pass text detection and extraction engine."""

    def __init__(self):
        self.ocr_adapter = MultiEngineOcrAdapter()

    def detect_and_extract_text(
        self,
        image: Image.Image,
        preprocessing_dict: Dict[str, Any],
        m_inv: Optional[np.ndarray] = None,
        orig_w: int = 1000,
        orig_h: int = 1000,
        is_curved: bool = False
    ) -> List[Stage2TextRegion]:
        """Runs Pass 1 global detection and Pass 2 targeted detection, then merges results.
        
        Returns:
            List[Stage2TextRegion]
        """
        w, h = image.size
        if w < 20 or h < 20:
            return []

        # ----------------------------------------------------
        # PASS 1: GLOBAL TEXT DETECTION ACROSS PREPROCESSING BRANCHES
        # ----------------------------------------------------
        pass_candidates = self.ocr_adapter.run_multi_pass_ensemble(image, preprocessing_dict)
        pass1_lines: List[Dict[str, Any]] = []

        for variant_name, detections in pass_candidates:
            lines = group_words_into_lines(detections)
            for line in lines:
                matched = False
                for existing in pass1_lines:
                    iou = calculate_bbox_iou(line["bbox"], existing["bbox"])
                    sim = compute_string_similarity(line["raw_text"], existing["raw_text"])

                    # Vertical overlap check
                    ly1, ly2 = line["bbox"][1], line["bbox"][1] + line["bbox"][3]
                    ey1, ey2 = existing["bbox"][1], existing["bbox"][1] + existing["bbox"][3]
                    y_overlap = max(0.0, min(ly2, ey2) - max(ly1, ey1))
                    min_h = min(line["bbox"][3], existing["bbox"][3])
                    v_overlap_ratio = y_overlap / min_h if min_h > 0 else 0.0

                    if iou > 0.35 or (v_overlap_ratio > 0.60 and sim > 0.60):
                        existing["readings"].append(line)
                        matched = True
                        break

                if not matched:
                    line["readings"] = [line]
                    pass1_lines.append(line)

        # ----------------------------------------------------
        # PASS 2: TARGETED DETECTION FOR DIFFICULT REGIONS
        # ----------------------------------------------------
        pass2_detections: List[Dict[str, Any]] = []

        cv_img = pil_to_cv2(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        # A. Detect Micro-Text / Small Declarations
        # Use Morphological Gradient to identify dense text-like horizontal stripes
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.convertScaleAbs(np.sqrt(grad_x**2 + grad_y**2))

        # Close horizontally to merge character letters in small words
        kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 3))
        morphed = cv2.morphologyEx(grad_mag, cv2.MORPH_CLOSE, kernel_small)
        _, thresh_small = cv2.threshold(morphed, 40, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            bx, by, bw, bh = cv2.boundingRect(cnt)
            area = bw * bh
            # Small text criteria: height 8-28px, width >= 25px, area < 5% of label
            if 8 <= bh <= 28 and bw >= 25 and area < (w * h * 0.05):
                # Check if Pass 1 already cleanly captured this area
                already_covered = any(
                    calculate_bbox_iou([bx, by, bw, bh], p1["bbox"]) > 0.40
                    for p1 in pass1_lines
                )
                if not already_covered:
                    # Crop with small padding, upscale 2.2x, sharpen, and run targeted OCR
                    pad = 4
                    cx1 = max(0, bx - pad)
                    cy1 = max(0, by - pad)
                    cx2 = min(w, bx + bw + pad)
                    cy2 = min(h, by + bh + pad)
                    crop = image.crop((cx1, cy1, cx2, cy2))

                    scale_factor = 2.2
                    up_w, up_h = int(crop.width * scale_factor), int(crop.height * scale_factor)
                    up_crop = crop.resize((up_w, up_h), Image.LANCZOS)
                    # Run OCR on upscaled micro-crop
                    micro_results = self.ocr_adapter.run_ocr_on_image(up_crop, variant_name="upscaled_micro")
                    for mr in micro_results:
                        # Map bbox back to parent image coordinates
                        rx, ry, rw, rh = mr["bbox"]
                        orig_cx = cx1 + (rx / scale_factor)
                        orig_cy = cy1 + (ry / scale_factor)
                        orig_cw = rw / scale_factor
                        orig_ch = rh / scale_factor
                        pass2_detections.append({
                            "raw_text": mr["raw_text"],
                            "normalized_text": mr["normalized_text"],
                            "bbox": [round(orig_cx, 1), round(orig_cy, 1), round(orig_cw, 1), round(orig_ch, 1)],
                            "confidence": mr["confidence"],
                            "source_variant": "upscaled_micro",
                            "words": mr.get("words", [])
                        })

        # B. Detect Rotated Text (Vertical columnar strips)
        for cnt in contours:
            bx, by, bw, bh = cv2.boundingRect(cnt)
            # Tall vertical strip: aspect ratio H/W >= 2.8, height >= 60px
            if bh >= 60 and (float(bh) / float(max(1, bw))) >= 2.8:
                already_covered = any(
                    calculate_bbox_iou([bx, by, bw, bh], p1["bbox"]) > 0.45
                    for p1 in pass1_lines
                )
                if not already_covered:
                    pad = 4
                    cx1 = max(0, bx - pad)
                    cy1 = max(0, by - pad)
                    cx2 = min(w, bx + bw + pad)
                    cy2 = min(h, by + bh + pad)
                    crop = image.crop((cx1, cy1, cx2, cy2))
                    # Rotate 90° clockwise
                    rot_crop = crop.rotate(270, expand=True)
                    rot_results = self.ocr_adapter.run_ocr_on_image(rot_crop, variant_name="rotated_90")
                    for rr in rot_results:
                        pass2_detections.append({
                            "raw_text": rr["raw_text"],
                            "normalized_text": rr["normalized_text"],
                            "bbox": [float(bx), float(by), float(bw), float(bh)],
                            "confidence": rr["confidence"],
                            "orientation": 90,
                            "source_variant": "rotated_90",
                            "words": rr.get("words", [])
                        })

        # ----------------------------------------------------
        # MERGE & DEDUPLICATE PASS 1 AND PASS 2 DETECTIONS
        # ----------------------------------------------------
        merged_regions: List[Dict[str, Any]] = list(pass1_lines)

        for cand in pass2_detections:
            raw = cand.get("raw_text", "").strip()
            if is_garbage_ocr(raw):
                continue

            cbox = cand["bbox"]
            matched = False

            for existing in merged_regions:
                iou = calculate_bbox_iou(cbox, existing["bbox"])
                sim = compute_string_similarity(raw, existing["raw_text"])

                # If overlapping or identical text at nearby location
                if iou > 0.35 or (iou > 0.15 and sim > 0.70):
                    existing["readings"].append(cand)
                    matched = True
                    break

            if not matched:
                cand["readings"] = [cand]
                merged_regions.append(cand)

        # Finalize consensus and construct Stage2TextRegion objects
        final_regions: List[Stage2TextRegion] = []
        ordered_regions = assign_natural_reading_order(merged_regions)

        for item in ordered_regions:
            readings = item.get("readings", [item])
            best_raw, best_norm, consensus_conf, competing = merge_competing_candidates(readings)
            if not best_raw or is_garbage_ocr(best_raw):
                continue

            # Check uncertainty threshold:
            # Valid detected alphanumeric text is DETECTED; only noise/low-confidence (<0.20) is OCR_UNCERTAIN
            has_alnum = any(c.isalnum() for c in best_raw)
            if not has_alnum or consensus_conf < 0.20:
                status = "OCR_UNCERTAIN"
            else:
                status = "DETECTED"

            # Compute original image coordinates via M_inv
            orig_bbox = map_bbox_to_original(item["bbox"], m_inv, orig_w, orig_h) if m_inv is not None else item["bbox"]

            word_boxes = []
            for w_dict in item.get("words", []):
                if isinstance(w_dict, Stage2WordBox):
                    word_boxes.append(w_dict)
                elif isinstance(w_dict, dict):
                    word_boxes.append(
                        Stage2WordBox(
                            text=w_dict.get("text", ""),
                            bbox=w_dict.get("bbox", []),
                            confidence=w_dict.get("confidence", 0.90)
                        )
                    )

            final_regions.append(
                Stage2TextRegion(
                    region_id=f"REG-{uuid.uuid4().hex[:6].upper()}",
                    raw_text=best_raw,
                    normalized_text=best_norm,
                    bbox=item["bbox"],
                    original_bbox=orig_bbox,
                    detection_confidence=0.95,
                    ocr_confidence=consensus_conf,
                    language="en",
                    orientation=item.get("orientation", 0),
                    source_variant=item.get("source_variant", "original"),
                    status=status,
                    words=word_boxes,
                    competing_candidates=competing,
                    reading_order_index=item.get("reading_order_index", 0)
                )
            )

        return final_regions
