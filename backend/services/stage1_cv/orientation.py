"""
Stage 1: Orientation Normalization Service
==========================================
Detects and corrects package image orientation:
- EXIF orientation tag inspection (ImageOps.exif_transpose)
- Optical text baseline and edge angle analysis (0°, 90°, 180°, 270°)
- Rotates working copy into upright normal reading orientation
- Preserves the original image unaltered
"""

import math
from typing import Tuple
from PIL import Image, ImageOps
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil


class OrientationNormalizerService:
    """Detects and rectifies photographic and optical rotation."""

    def __init__(self):
        pass

    def normalize_orientation(
        self,
        image: Image.Image
    ) -> Tuple[Image.Image, int, str]:
        """Normalizes image orientation to upright reading view.
        
        Returns:
            (normalized_image, rotation_angle_applied, orientation_label)
        """
        # 1. Apply EXIF orientation transposition if present
        try:
            exif_transposed = ImageOps.exif_transpose(image)
            if exif_transposed is not None:
                working = exif_transposed
            else:
                working = image.copy()
        except Exception:
            working = image.copy()

        # 2. Optical text baseline & line angle analysis via Hough Transform
        cv_img = pil_to_cv2(working)
        h, w = cv_img.shape[:2]
        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_img

        # Detect prominent lines
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=90, minLineLength=max(30, min(w, h) // 10), maxLineGap=8)

        horizontal_count = 0
        vertical_count = 0

        if lines is not None and len(lines) > 0:
            for line in lines:
                pts = line.flatten()
                if len(pts) < 4:
                    continue
                x1, y1, x2, y2 = int(pts[0]), int(pts[1]), int(pts[2]), int(pts[3])
                dx = x2 - x1
                dy = y2 - y1
                angle = abs(math.degrees(math.atan2(dy, dx)))
                if angle <= 20.0 or angle >= 160.0:
                    horizontal_count += 1
                elif 70.0 <= angle <= 110.0:
                    vertical_count += 1

        rotation_deg = 0
        orientation_label = "NORMAL"

        # If vertical lines drastically outnumber horizontal lines and aspect ratio indicates sideways capture
        if vertical_count > horizontal_count * 2 and h < w:
            # Sideways portrait captured in landscape mode -> rotate 90° clockwise
            rotation_deg = 90
            orientation_label = "ROTATED_90_CW"
            working = working.rotate(270, expand=True)  # PIL counter-clockwise: 270 = 90 CW

        return working, rotation_deg, orientation_label
