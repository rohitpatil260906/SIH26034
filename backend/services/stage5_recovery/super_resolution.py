"""
Stage 5: Micro-Text Super-Resolution & Targeted Enhancement Service
===================================================================
Upscales and sharpens fine statutory text (MRP, Net Qty, Batch No, Address).
Preserves original_crop, upscaled_crop, and enhanced_crop separately without
mutating original ground-truth evidence.
"""

from typing import Tuple, Dict, Any, Optional, List
from PIL import Image, ImageFilter
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from .coordinate_mapper import CoordinateTransformChain, CoordinateTransformStep


class SuperResolutionCropResult:
    """Encapsulates multi-stage recovery evidence for a small text crop."""

    def __init__(
        self,
        crop_id: str,
        original_crop: Image.Image,
        upscaled_crop: Image.Image,
        enhanced_crop: Image.Image,
        crop_bbox: List[float],
        scale_factor: float,
        chain: CoordinateTransformChain
    ):
        self.crop_id = crop_id
        self.original_crop = original_crop
        self.upscaled_crop = upscaled_crop
        self.enhanced_crop = enhanced_crop
        self.crop_bbox = crop_bbox
        self.scale_factor = scale_factor
        self.chain = chain


class SuperResolutionService:
    """Performs localized high-DPI upscaling and edge preservation on micro-text blocks."""

    def __init__(self):
        pass

    def upscale_crop(
        self,
        image: Image.Image,
        crop_bbox: List[float],
        scale_factor: float = 2.4,
        parent_chain: Optional[CoordinateTransformChain] = None,
        crop_id: str = "crop_001"
    ) -> SuperResolutionCropResult:
        """Extracts a local text region and generates upscaled + enhanced variants.
        
        Args:
            image: Source parent image
            crop_bbox: [x, y, w, h]
            scale_factor: Upscaling multiplier (default 2.4x)
        """
        w, h = image.size
        bx, by, bw, bh = crop_bbox
        pad = 4
        cx1 = max(0, int(bx - pad))
        cy1 = max(0, int(by - pad))
        cx2 = min(w, int(bx + bw + pad))
        cy2 = min(h, int(by + bh + pad))

        actual_w = max(1, cx2 - cx1)
        actual_h = max(1, cy2 - cy1)

        # 1. Original crop
        orig_crop = image.crop((cx1, cy1, cx2, cy2))

        # 2. High-quality Lanczos4 interpolation upscaling
        up_w = int(round(actual_w * scale_factor))
        up_h = int(round(actual_h * scale_factor))
        cv_crop = pil_to_cv2(orig_crop)
        upscaled_cv = cv2.resize(cv_crop, (up_w, up_h), interpolation=cv2.INTER_LANCZOS4)
        upscaled_pil = cv2_to_pil(upscaled_cv)

        # 3. Edge-directed local contrast enhancement
        # CLAHE on luminance channel + subtle unsharp masking
        if len(upscaled_cv.shape) == 3:
            lab = cv2.cvtColor(upscaled_cv, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(6, 6))
            l_clahe = clahe.apply(l)
            merged_lab = cv2.merge([l_clahe, a, b])
            enhanced_cv = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
            enhanced_pil = cv2_to_pil(enhanced_cv)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(6, 6))
            enhanced_gray = clahe.apply(upscaled_cv)
            enhanced_pil = Image.fromarray(enhanced_gray)

        enhanced_pil = enhanced_pil.filter(ImageFilter.UnsharpMask(radius=1.5, percent=140, threshold=2))

        # 4. Register transformation chain
        chain = parent_chain.clone() if parent_chain is not None else CoordinateTransformChain()
        chain.add_crop(float(cx1), float(cy1), float(actual_w), float(actual_h))
        chain.add_scale(scale_factor, scale_factor)

        return SuperResolutionCropResult(
            crop_id=crop_id,
            original_crop=orig_crop,
            upscaled_crop=upscaled_pil,
            enhanced_crop=enhanced_pil,
            crop_bbox=[float(cx1), float(cy1), float(actual_w), float(actual_h)],
            scale_factor=scale_factor,
            chain=chain
        )
