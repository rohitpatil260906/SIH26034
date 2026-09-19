"""
Stage 1: Packaging Panel Identification & Label Coverage Service
================================================================
Classifies packaging panels and determines label completeness:
1. Panel Category:
   - FRONT (Principal Display Panel / PDP)
   - BACK (Information panel, statutory declarations, ingredients)
   - SIDE (Left/Right side panel, tall/columnar)
   - TOP / BOTTOM (Lids, caps, batch coding areas)
   - UNKNOWN_PANEL
2. Coverage Category:
   - FULL (Full label visible within boundaries)
   - PARTIAL (Close-up, cropped label, single table/section)

Statutory Rule:
- Non-front validity guarantee: The system NEVER rejects an image because it is not a front PDP.
  Back panels, side panels, and partial labels are 100% valid inputs.
"""

from typing import Tuple, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ...models import Stage1PanelInfo
from ..cv_pipeline import pil_to_cv2


class PanelDetectionService:
    """Classifies packaging panel orientation and checks label visibility completeness."""

    def __init__(self):
        pass

    def detect_panel(
        self,
        image: Image.Image,
        package_bbox_pct: Tuple[float, float, float, float] = (0.0, 0.0, 100.0, 100.0)
    ) -> Stage1PanelInfo:
        """Analyzes spatial layout, text density, and aspect ratio to classify the panel.
        
        Returns:
            Stage1PanelInfo
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        aspect_ratio = float(w) / float(h) if h > 0 else 1.0

        # 1. Connected components analysis to measure text layout & density
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thresh)

        # Count text-like glyphs (small-to-medium aspect ratio components)
        glyph_count = 0
        total_glyph_area = 0
        for i in range(1, num_labels):
            gw = stats[i, cv2.CC_STAT_WIDTH]
            gh = stats[i, cv2.CC_STAT_HEIGHT]
            ga = stats[i, cv2.CC_STAT_AREA]
            if 6 <= gh <= 70 and 3 <= gw <= 150 and ga > 10:
                glyph_count += 1
                total_glyph_area += ga

        frame_area = w * h
        glyph_density = float(total_glyph_area) / float(frame_area + 1e-5)

        # 2. Horizontal edge line density (dense rows indicate tabular or statutory text)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        horizontal_line_energy = float(np.mean(np.abs(sobel_y)))

        # 3. Panel Classification Heuristics
        # SIDE: Very tall and narrow
        if aspect_ratio < 0.48 or aspect_ratio > 2.8:
            panel_type = "SIDE"
            confidence = 0.88
            is_front = False
        # BACK: High glyph count, dense rows of text (tables, statutory declarations, paragraphs)
        elif glyph_count > 120 or (glyph_count > 60 and glyph_density > 0.04):
            panel_type = "BACK"
            confidence = 0.90
            is_front = False
        # FRONT: Low-to-moderate glyph count (large logo, product name, hero image)
        elif glyph_count < 45 and glyph_density < 0.025:
            panel_type = "FRONT"
            confidence = 0.85
            is_front = True
        elif aspect_ratio >= 0.8 and aspect_ratio <= 1.25 and glyph_count < 25:
            # Often top lid or bottom coding area
            panel_type = "TOP"
            confidence = 0.75
            is_front = False
        else:
            # Moderate text density
            panel_type = "BACK" if glyph_count >= 45 else "FRONT"
            confidence = 0.70
            is_front = (panel_type == "FRONT")

        # 4. Coverage Analysis (FULL vs PARTIAL)
        # If the image is a tight crop of a section, or package bbox fills > 85% of frame
        is_macro_crop = (glyph_count >= 4 and (w <= 600 and h <= 500))
        covers_almost_entire_frame = (
            package_bbox_pct[2] >= 85.0 and package_bbox_pct[3] >= 85.0
        )

        if is_macro_crop or covers_almost_entire_frame:
            coverage = "PARTIAL"
        else:
            coverage = "FULL"

        return Stage1PanelInfo(
            type=panel_type,
            confidence=round(confidence, 2),
            coverage=coverage,
            is_front=is_front
        )
