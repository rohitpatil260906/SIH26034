"""
Stage 5: Perspective Homography Rectification Service
====================================================
Detects packaging quadrilateral boundaries, computes homography matrix H,
applies inverse perspective warp, and registers the transformation with
the CoordinateTransformChain for exact coordinate back-mapping.
"""

import math
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from .coordinate_mapper import CoordinateTransformChain, CoordinateTransformStep


def order_quad_corners(pts: np.ndarray) -> np.ndarray:
    """Orders 4 points into [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


class PerspectiveCorrector:
    """Detects and rectifies perspective distortion on packages and labels."""

    def __init__(self):
        pass

    def rectify(
        self,
        image: Image.Image,
        known_corners: Optional[List[List[float]]] = None,
        chain: Optional[CoordinateTransformChain] = None
    ) -> Tuple[Image.Image, CoordinateTransformChain, bool, Optional[np.ndarray]]:
        """Rectifies perspective distortion.
        
        Returns:
            (rectified_pil_image, updated_chain, perspective_corrected_bool, homography_matrix)
        """
        active_chain = chain.clone() if chain is not None else CoordinateTransformChain()
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        quad_pts = None

        if known_corners is not None and len(known_corners) == 4:
            quad_pts = order_quad_corners(np.array(known_corners, dtype=np.float32))
        else:
            # Detect prominent quadrilateral
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 35, 130)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            min_area = (w * h) * 0.10
            for cnt in contours[:6]:
                area = cv2.contourArea(cnt)
                if area < min_area:
                    continue
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    quad_pts = order_quad_corners(approx.reshape(4, 2).astype(np.float32))
                    break

        if quad_pts is None:
            # No prominent quad detected -> return copy with identity
            return image.copy(), active_chain, False, None

        tl, tr, br, bl = quad_pts

        # Destination dimensions
        w_top = float(np.linalg.norm(tr - tl))
        w_bot = float(np.linalg.norm(br - bl))
        dst_w = int(round(max(w_top, w_bot)))

        h_left = float(np.linalg.norm(bl - tl))
        h_right = float(np.linalg.norm(br - tr))
        dst_h = int(round(max(h_left, h_right)))

        dst_w = max(dst_w, 80)
        dst_h = max(dst_h, 80)

        # Measure deviation angle
        top_ang = math.degrees(math.atan2(abs(tr[1] - tl[1]), abs(tr[0] - tl[0]) + 1e-5))
        left_ang = math.degrees(math.atan2(abs(bl[0] - tl[0]), abs(bl[1] - tl[1]) + 1e-5))
        if top_ang < 3.0 and left_ang < 3.0 and abs(w_top - w_bot) < 15 and abs(h_left - h_right) < 15:
            # Minimal distortion, no need to warp
            return image.copy(), active_chain, False, None

        dst_pts = np.array([
            [0.0, 0.0],
            [float(dst_w - 1), 0.0],
            [float(dst_w - 1), float(dst_h - 1)],
            [0.0, float(dst_h - 1)]
        ], dtype=np.float32)

        m_matrix = cv2.getPerspectiveTransform(quad_pts, dst_pts)
        ret, m_inv = cv2.invert(m_matrix) if hasattr(cv2, 'invert') else (True, np.linalg.inv(m_matrix))

        warped_cv = cv2.warpPerspective(cv_img, m_matrix, (dst_w, dst_h), flags=cv2.INTER_LANCZOS4)
        rectified_pil = cv2_to_pil(warped_cv)

        # Register in coordinate chain
        active_chain.add_step(
            CoordinateTransformStep(
                operation="perspective",
                parameters={"dst_w": dst_w, "dst_h": dst_h},
                matrix=m_matrix,
                inv_matrix=m_inv
            )
        )

        return rectified_pil, active_chain, True, m_matrix
