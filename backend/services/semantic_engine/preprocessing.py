"""
Service 2: Image Preprocessing Service
======================================
Produces multi-pass optical enhancements for downstream OCR and Layout analysis:
- CLAHE (Contrast-Limited Adaptive Histogram Equalization)
- Bilateral Filtering / Denoising
- Adaptive Gaussian & Otsu Thresholding
- Deskewing & Perspective Correction
- Morphological text enhancement & unsharp masking
"""

from typing import Dict, Tuple, List, Optional
from PIL import Image
import numpy as np
import cv2

from ...models import PreprocessingVariantInfo
from ..cv_pipeline import generate_13_preprocessing_variants, pil_to_cv2, cv2_to_pil


class ImagePreprocessingService:
    """Multi-pass computer vision image preprocessing service."""

    def __init__(self):
        pass

    def generate_variants(
        self,
        image: Image.Image,
        include_base64: bool = False
    ) -> Dict[str, Tuple[Image.Image, PreprocessingVariantInfo]]:
        """Generates the 13 statutory optical preprocessing variants."""
        return generate_13_preprocessing_variants(image, include_base64=include_base64)

    def enhance_for_ocr(self, image: Image.Image) -> Image.Image:
        """Produces an optimal single high-contrast enhanced image for primary OCR."""
        cv_img = pil_to_cv2(image)
        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_img

        # Denoise
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)

        return cv2_to_pil(contrast)
