"""
Stage 5: Local Curved-Region & Curved-Text Line Rectification Service
====================================================================
Straightens curved text baselines (arched, parabolic, or cylindrical) locally
without distorting unaffected planar sections of the packaging.
"""

import math
from typing import Tuple, List, Dict, Any, Optional
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from .coordinate_mapper import CoordinateTransformChain, CoordinateTransformStep


class CurvatureCorrector:
    """Straightens local curved text patches and curved packaging boundaries."""

    def __init__(self):
        pass

    def straighten_curved_patch(
        self,
        patch: Image.Image,
        parent_chain: Optional[CoordinateTransformChain] = None,
        patch_crop_box: Optional[List[float]] = None
    ) -> Tuple[Image.Image, CoordinateTransformChain, bool]:
        """Straightens parabolic or arched text curvature within a local image crop.
        
        Returns:
            (straightened_patch, local_chain, is_straightened)
        """
        chain = parent_chain.clone() if parent_chain is not None else CoordinateTransformChain()
        if patch_crop_box and len(patch_crop_box) == 4:
            chain.add_crop(patch_crop_box[0], patch_crop_box[1], patch_crop_box[2], patch_crop_box[3])

        cv_patch = pil_to_cv2(patch)
        h, w = cv_patch.shape[:2]
        if h < 20 or w < 40:
            return patch, chain, False

        gray = cv2.cvtColor(cv_patch, cv2.COLOR_BGR2GRAY) if len(cv_patch.shape) == 3 else cv_patch

        # Detect horizontal curved text baselines via morphological filter
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 2))
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag_y = cv2.convertScaleAbs(np.abs(grad_y))
        morphed = cv2.morphologyEx(mag_y, cv2.MORPH_CLOSE, kernel_h)
        _, thresh = cv2.threshold(morphed, 40, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        best_poly = None
        best_span = 0

        for cnt in contours:
            pts = cnt.reshape(-1, 2)
            if len(pts) < 25:
                continue
            span = float(np.max(pts[:, 0]) - np.min(pts[:, 0]))
            if span > best_span and span > (w * 0.40):
                try:
                    poly = np.polyfit(pts[:, 0], pts[:, 1], 2)
                    # Check if curved
                    if abs(poly[0]) > 0.0001:
                        best_poly = poly
                        best_span = span
                except Exception:
                    pass

        if best_poly is None:
            # No pronounced polynomial curvature detected
            return patch, chain, False

        # Build vertical displacement grid to straighten: y_new = y - dy(x)
        # dy(x) = poly[0]*x^2 + poly[1]*x + poly[2] - baseline_mean
        xs = np.arange(w, dtype=np.float32)
        curve_ys = best_poly[0] * (xs**2) + best_poly[1] * xs + best_poly[2]
        center_y = float(np.mean(curve_ys))
        dy = curve_ys - center_y

        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)

        for y in range(h):
            map_x[y, :] = xs
            map_y[y, :] = np.clip(y + dy, 0, h - 1)

        straightened_cv = cv2.remap(
            cv_patch,
            map_x,
            map_y,
            interpolation=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_REPLICATE
        )
        straightened_pil = cv2_to_pil(straightened_cv)

        return straightened_pil, chain, True
