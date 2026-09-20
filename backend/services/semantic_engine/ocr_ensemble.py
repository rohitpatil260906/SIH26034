"""
Service 5: OCR Ensemble Service
===============================
Executes multi-pass, multi-engine OCR voting and token normalization:
- Tesseract (eng+hin) and EasyOCR engines
- Multi-engine voting and agreement scoring
- Optical token disambiguation (O/0, I/1, S/5, B/8, 9/g)
- Garbled / unreadable text detection
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image

from ...models import ExtractedLine, BoundingBox
from ..ocr_engine import (
    extract_all_visible_lines,
    normalize_ocr_token,
    verify_ocr_ensemble_and_disagreement,
    TESSERACT_AVAILABLE,
    get_easyocr_reader
)


class OcrEnsembleService:
    """Ensemble OCR pipeline with token disambiguation."""

    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE
        self.easyocr_reader = get_easyocr_reader()

    def run_ensemble(
        self,
        image: Image.Image,
        variants_dict: Optional[Dict[str, Any]] = None,
        surface: str = "Front (PDP)"
    ) -> Tuple[List[ExtractedLine], str]:
        """Runs multi-engine OCR across the image and variants."""
        return extract_all_visible_lines(image, variants_dict or {}, surface)

    def disambiguate_token(
        self,
        token: str,
        expected_type: Optional[str] = None
    ) -> str:
        """Disambiguates characters based on expected context (number, unit, date, etc.)."""
        return normalize_ocr_token(token, expected_type=expected_type)

    def evaluate_agreement(
        self,
        candidates: Dict[str, str]
    ) -> Tuple[str, float, bool]:
        """Calculates multi-engine consensus and flags disagreement."""
        return verify_ocr_ensemble_and_disagreement(candidates)
