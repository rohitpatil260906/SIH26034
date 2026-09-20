"""
Stage 5: Rotation & Skew Normalization Service
=============================================
Detects orientation (0°, 90°, 180°, 270°) and arbitrary fine skew angles (-45° to +45°).
Generates deskewed and rotated variants while maintaining complete coordinate traceability.
"""

import math
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from .coordinate_mapper import CoordinateTransformChain, CoordinateTransformStep


class RotationCorrector:
    """Handles cardinal rotation (90/180/270) and fine skew normalization."""

    def __init__(self):
        pass

    def detect_skew_angle(self, cv_img: np.ndarray) -> float:
        """Detects dominant skew angle between -45 and +45 degrees using Hough transform on text lines."""
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
        h, w = gray.shape[:2]

        # Sobel horizontal gradients to highlight text baselines
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.convertScaleAbs(np.sqrt(grad_x**2 + grad_y**2))

        # Morphological connect along horizontal text strokes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        connected = cv2.morphologyEx(mag, cv2.MORPH_CLOSE, kernel)
        _, thresh = cv2.threshold(connected, 40, 255, cv2.THRESH_BINARY)

        lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold=70, minLineLength=w * 0.15, maxLineGap=12)
        if lines is None or len(lines) == 0:
            return 0.0

        angles = []
        for line in lines:
            l = line.reshape(-1)
            if len(l) >= 4:
                x1, y1, x2, y2 = float(l[0]), float(l[1]), float(l[2]), float(l[3])
                ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
                while ang > 45.0:
                    ang -= 90.0
                while ang < -45.0:
                    ang += 90.0
                angles.append(ang)

        if not angles:
            return 0.0

        median_angle = float(np.median(angles))
        return median_angle

    def correct_orientation_and_skew(
        self,
        image: Image.Image,
        force_cardinal_angle: Optional[int] = None,
        chain: Optional[CoordinateTransformChain] = None
    ) -> Tuple[Image.Image, CoordinateTransformChain, bool, float]:
        """Normalizes cardinal rotation and fine skew.
        
        Returns:
            (corrected_image, updated_chain, corrected_bool, angle_applied)
        """
        active_chain = chain.clone() if chain is not None else CoordinateTransformChain()
        w, h = image.size

        # 1. Cardinal rotation if requested or needed
        cardinal = force_cardinal_angle or 0
        if cardinal == 0:
            cv_raw = pil_to_cv2(image)
            gray_raw = cv2.cvtColor(cv_raw, cv2.COLOR_BGR2GRAY) if len(cv_raw.shape) == 3 else cv_raw
            gy_mag = float(np.mean(np.abs(cv2.Sobel(gray_raw, cv2.CV_32F, 0, 1, ksize=3))))
            gx_mag = float(np.mean(np.abs(cv2.Sobel(gray_raw, cv2.CV_32F, 1, 0, ksize=3))))
            if gy_mag > 1.3 * gx_mag and (h / max(1, w)) > 1.15:
                cardinal = 90

        current_img = image

        if cardinal in [90, 180, 270]:
            # PIL rotate is counter-clockwise; angle degrees is clockwise
            pil_angle = {90: 270, 180: 180, 270: 90}[cardinal]
            current_img = current_img.rotate(pil_angle, expand=True)
            active_chain.add_rotation(cardinal, float(w), float(h))
            w, h = current_img.size

        # 2. Fine skew detection & rectification
        cv_img = pil_to_cv2(current_img)
        skew_angle = self.detect_skew_angle(cv_img)

        if abs(skew_angle) > 1.8:
            # Rotate fine angle
            center = (w / 2.0, h / 2.0)
            rot_mat = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
            deskewed_cv = cv2.warpAffine(
                cv_img,
                rot_mat,
                (w, h),
                flags=cv2.INTER_LANCZOS4,
                borderMode=cv2.BORDER_REPLICATE
            )
            deskewed_pil = cv2_to_pil(deskewed_cv)

            # Homogeneous 3x3 for affine
            aff_3x3 = np.vstack([rot_mat, [0.0, 0.0, 1.0]])
            inv_aff_3x3 = np.linalg.inv(aff_3x3)

            active_chain.add_step(
                CoordinateTransformStep(
                    operation="rotate",
                    parameters={"angle": skew_angle, "src_w": float(w), "src_h": float(h)},
                    matrix=aff_3x3,
                    inv_matrix=inv_aff_3x3
                )
            )
            return deskewed_pil, active_chain, True, (cardinal + skew_angle)

        is_corrected = (cardinal != 0)
        return current_img, active_chain, is_corrected, float(cardinal)
