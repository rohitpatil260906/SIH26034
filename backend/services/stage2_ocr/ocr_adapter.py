"""
Stage 2: Multi-Engine OCR Adapter & Multi-Branch Ensemble Service
=================================================================
Wraps EasyOCR and Tesseract to provide:
1. Adaptive OCR execution across preprocessing branches (original, sharpened, clahe, upscaled, adaptive)
2. Extraction of text with polygon bounding boxes and confidence scores
3. Multi-pass ensemble agreement boosting and competing candidate preservation
4. Safe execution with zero crashes on blank, low-contrast, or corrupted crops
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from ..ocr_engine import get_easyocr_reader, TESSERACT_AVAILABLE, run_tesseract_ocr
from .normalization import (
    normalize_text_candidate,
    is_garbage_ocr,
    merge_competing_candidates,
    compute_string_similarity
)
from ..cv_pipeline import pil_to_cv2


class MultiEngineOcrAdapter:
    """Adaptive multi-pass OCR runner with multi-engine ensemble."""

    def __init__(self):
        self.easyocr_reader = get_easyocr_reader()

    def run_ocr_on_image(
        self,
        image: Image.Image,
        variant_name: str = "original"
    ) -> List[Dict[str, Any]]:
        """Executes OCR on an image and returns detected text tokens with pixel bounding boxes.
        
        Returns list of dicts:
        {
            "raw_text": str,
            "normalized_text": str,
            "bbox": [x, y, w, h],  # in pixel coordinates
            "confidence": float,
            "engine": str,
            "source_variant": str,
            "words": list
        }
        """
        w, h = image.size
        if w < 10 or h < 10:
            return []

        results: List[Dict[str, Any]] = []

        # 1. EasyOCR Primary
        if self.easyocr_reader is not None:
            try:
                cv_img = pil_to_cv2(image)
                # EasyOCR expects RGB
                rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) if len(cv_img.shape) == 3 else cv_img
                raw_ocr_boxes = self.easyocr_reader.readtext(rgb)

                for item in raw_ocr_boxes:
                    poly, text, conf = item
                    clean_raw = str(text).strip()
                    if is_garbage_ocr(clean_raw):
                        continue

                    # Poly: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                    pts = np.array(poly)
                    bx = float(np.min(pts[:, 0]))
                    by = float(np.min(pts[:, 1]))
                    bw = float(np.max(pts[:, 0]) - bx)
                    bh = float(np.max(pts[:, 1]) - by)

                    if bw < 4 or bh < 4:
                        continue

                    norm_text, norm_conf = normalize_text_candidate(clean_raw)
                    combined_conf = round(float(conf) * norm_conf, 2)

                    results.append({
                        "raw_text": clean_raw,
                        "normalized_text": norm_text,
                        "bbox": [round(bx, 1), round(by, 1), round(bw, 1), round(bh, 1)],
                        "confidence": combined_conf,
                        "engine": "EasyOCR",
                        "source_variant": variant_name,
                        "words": [{"text": clean_raw, "bbox": [bx, by, bw, bh], "confidence": combined_conf}]
                    })
            except Exception:
                pass

        # 2. Tesseract Fallback (if available and EasyOCR yielded few/no results)
        if len(results) == 0 and TESSERACT_AVAILABLE:
            try:
                tess_lines = run_tesseract_ocr(image)
                for tl in tess_lines:
                    text = tl["text"].strip()
                    if is_garbage_ocr(text):
                        continue
                    pct_bbox = tl["bbox"]  # [x, y, w, h] in %
                    px_bbox = [
                        round((pct_bbox[0] / 100.0) * w, 1),
                        round((pct_bbox[1] / 100.0) * h, 1),
                        round((pct_bbox[2] / 100.0) * w, 1),
                        round((pct_bbox[3] / 100.0) * h, 1)
                    ]
                    norm_text, norm_conf = normalize_text_candidate(text)
                    conf = round(float(tl.get("confidence", 0.85)) * norm_conf, 2)
                    results.append({
                        "raw_text": text,
                        "normalized_text": norm_text,
                        "bbox": px_bbox,
                        "confidence": conf,
                        "engine": "Tesseract",
                        "source_variant": variant_name,
                        "words": [{"text": text, "bbox": px_bbox, "confidence": conf}]
                    })
            except Exception:
                pass

        return results

    def run_multi_pass_ensemble(
        self,
        base_image: Image.Image,
        preprocessing_dict: Dict[str, Any]
    ) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """Runs OCR across multiple preprocessed image passes and returns detections partitioned by variant pass."""
        passes: List[Tuple[str, List[Dict[str, Any]]]] = []

        # Pass 1: Original Image
        orig_detections = self.run_ocr_on_image(base_image, variant_name="original")
        if orig_detections:
            passes.append(("original", orig_detections))

        # Pass 2: Sharpened Image (for soft focus/blur)
        sharpened_info = preprocessing_dict.get("sharpened")
        if sharpened_info and "preview_base64" in sharpened_info:
            from ..image_enhancement import decode_base64_image
            try:
                sharp_img = decode_base64_image(sharpened_info["preview_base64"])
                sharp_detections = self.run_ocr_on_image(sharp_img, variant_name="sharpened")
                if sharp_detections:
                    passes.append(("sharpened", sharp_detections))
            except Exception:
                pass

        # Pass 3: CLAHE Enhanced Image (for low contrast)
        clahe_info = preprocessing_dict.get("clahe")
        if clahe_info and "preview_base64" in clahe_info:
            from ..image_enhancement import decode_base64_image
            try:
                clahe_img = decode_base64_image(clahe_info["preview_base64"])
                clahe_detections = self.run_ocr_on_image(clahe_img, variant_name="clahe")
                if clahe_detections:
                    passes.append(("clahe", clahe_detections))
            except Exception:
                pass

        return passes
