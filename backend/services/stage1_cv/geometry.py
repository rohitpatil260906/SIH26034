"""
Stage 1: Geometric Rectification & Coordinate Mapping Service
=============================================================
Provides:
1. Quadrilateral package/label detection and corner sorting (TL, TR, BR, BL)
2. 4-point perspective rectification via homography matrix (cv2.getPerspectiveTransform)
3. Bidirectional coordinate mapping between rectified image and original image space:
   - map_point_to_original(x, y, M_inv)
   - map_bbox_to_original(bbox, M_inv)
4. Cylindrical curvature detection and unwarping for curved packaging (bottles, cans, tubes)
5. Fallback mechanisms ensuring zero crashes on irregular geometries
"""

import math
from typing import Tuple, List, Optional, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ...models import Stage1GeometryResult
from ..cv_pipeline import pil_to_cv2, cv2_to_pil


def order_corner_points(pts: np.ndarray) -> np.ndarray:
    """Orders 4 points into [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left has smallest sum (x+y)
    rect[2] = pts[np.argmax(s)]  # Bottom-right has largest sum (x+y)

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right has smallest difference (y-x)
    rect[3] = pts[np.argmax(diff)]  # Bottom-left has largest difference (y-x)
    return rect


def map_point_to_original(x: float, y: float, m_inv: np.ndarray) -> Tuple[float, float]:
    """Maps a 2D point from rectified coordinate frame back to original image space using M_inv."""
    if m_inv is None:
        return x, y
    vec = np.array([x, y, 1.0], dtype=np.float64)
    res = m_inv.dot(vec)
    z = res[2] if abs(res[2]) > 1e-8 else 1.0
    return float(res[0] / z), float(res[1] / z)


def map_bbox_to_original(
    bbox: List[float],
    m_inv: np.ndarray,
    orig_w: int,
    orig_h: int
) -> List[float]:
    """Maps a bounding box [x, y, w, h] from rectified space back to original image space.
    
    Returns:
        [x, y, w, h] clamped to original image dimensions.
    """
    if m_inv is None or len(bbox) < 4:
        return bbox

    bx, by, bw, bh = bbox
    corners = [
        (bx, by),
        (bx + bw, by),
        (bx + bw, by + bh),
        (bx, by + bh)
    ]

    orig_pts = [map_point_to_original(px, py, m_inv) for px, py in corners]
    xs = [p[0] for p in orig_pts]
    ys = [p[1] for p in orig_pts]

    min_x = max(0.0, min(xs))
    min_y = max(0.0, min(ys))
    max_x = min(float(orig_w), max(xs))
    max_y = min(float(orig_h), max(ys))

    return [round(min_x, 1), round(min_y, 1), round(max_x - min_x, 1), round(max_y - min_y, 1)]


class GeometryCorrectionService:
    """Detects and corrects perspective distortion and cylindrical package curvature."""

    def __init__(self):
        pass

    def detect_and_rectify(
        self,
        image: Image.Image
    ) -> Tuple[Image.Image, Stage1GeometryResult, Optional[np.ndarray], Optional[np.ndarray]]:
        """Finds prominent package quadrilateral, computes homography, and rectifies perspective.
        
        Returns:
            (rectified_image, Stage1GeometryResult, M, M_inv)
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        # Detect strong edges
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)

        # Morphological close to bridge edge gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        found_quad = None
        min_quad_area = (w * h) * 0.12  # Must occupy at least 12% of image frame

        for cnt in contours[:6]:
            area = cv2.contourArea(cnt)
            if area < min_quad_area:
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                found_quad = approx.reshape(4, 2)
                break

        # Check for cylindrical curvature
        curvature_detected = self._detect_cylindrical_curvature(gray, w, h)

        if found_quad is not None:
            ordered_pts = order_corner_points(found_quad.astype(np.float32))
            tl, tr, br, bl = ordered_pts

            # Determine rectified destination dimensions
            width_top = np.linalg.norm(tr - tl)
            width_bottom = np.linalg.norm(br - bl)
            dst_w = int(max(width_top, width_bottom))

            height_left = np.linalg.norm(bl - tl)
            height_right = np.linalg.norm(br - tr)
            dst_h = int(max(height_left, height_right))

            # Ensure minimum viable dimensions
            dst_w = max(dst_w, 100)
            dst_h = max(dst_h, 100)

            dst_pts = np.array([
                [0, 0],
                [dst_w - 1, 0],
                [dst_w - 1, dst_h - 1],
                [0, dst_h - 1]
            ], dtype=np.float32)

            m_matrix = cv2.getPerspectiveTransform(ordered_pts, dst_pts)
            ret_val, m_inv = cv2.invert(m_matrix)

            warped = cv2.warpPerspective(cv_img, m_matrix, (dst_w, dst_h), flags=cv2.INTER_LANCZOS4)
            rectified_pil = cv2_to_pil(warped)

            # Measure perspective angle deviation
            top_angle = math.degrees(math.atan2(abs(tr[1] - tl[1]), abs(tr[0] - tl[0]) + 1e-5))
            left_angle = math.degrees(math.atan2(abs(bl[0] - tl[0]), abs(bl[1] - tl[1]) + 1e-5))
            perspective_detected = (top_angle > 4.0 or left_angle > 4.0)

            geom_result = Stage1GeometryResult(
                perspective_detected=perspective_detected,
                curvature_detected=curvature_detected,
                rectification_available=True,
                transformation_matrix=[[float(v) for v in row] for row in m_matrix],
                corner_points=[[float(pt[0]), float(pt[1])] for pt in ordered_pts]
            )

            # If cylindrical curvature is also detected, unwarp curved surface
            if curvature_detected:
                unwarped = self.unwarp_cylindrical_surface(warped)
                rectified_pil = cv2_to_pil(unwarped)

            return rectified_pil, geom_result, m_matrix, m_inv

        # Fallback: No prominent quadrilateral detected -> return original image with identity transform
        identity_m = np.eye(3, dtype=np.float64)
        corners = [
            [0.0, 0.0],
            [float(w), 0.0],
            [float(w), float(h)],
            [0.0, float(h)]
        ]

        # Check if curved bottle unwarping is still needed on whole image
        if curvature_detected:
            unwarped = self.unwarp_cylindrical_surface(cv_img)
            result_pil = cv2_to_pil(unwarped)
        else:
            result_pil = image.copy()

        geom_result = Stage1GeometryResult(
            perspective_detected=False,
            curvature_detected=curvature_detected,
            rectification_available=False,
            transformation_matrix=[[float(v) for v in row] for row in identity_m],
            corner_points=corners
        )

        return result_pil, geom_result, identity_m, identity_m

    def _detect_cylindrical_curvature(self, gray: np.ndarray, w: int, h: int) -> bool:
        """Detects whether horizontal label boundaries or text lines exhibit cylindrical parabolic curvature."""
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        curved_line_count = 0
        min_span = w * 0.35  # Must span at least 35% of image width

        for cnt in contours:
            pts = cnt.reshape(-1, 2)
            if len(pts) < 40:
                continue
            x_span = np.max(pts[:, 0]) - np.min(pts[:, 0])
            if x_span < min_span:
                continue

            # Fit 2nd-degree polynomial y = a*x^2 + b*x + c
            try:
                poly = np.polyfit(pts[:, 0], pts[:, 1], 2)
                curvature_a = abs(poly[0])
                # Significant parabolic curvature threshold
                if 0.00015 <= curvature_a <= 0.005:
                    curved_line_count += 1
            except Exception:
                continue

        return curved_line_count >= 2

    def unwarp_cylindrical_surface(self, cv_img: np.ndarray) -> np.ndarray:
        """Unwarps a curved cylindrical packaging surface (bottle/can/tube) into a planar rectangular projection."""
        h, w = cv_img.shape[:2]
        # Cylinder radius estimated from package width (assumed R ~ w / 1.6)
        radius = float(w) / 1.5
        center_x = float(w) / 2.0
        center_y = float(h) / 2.0

        # Construct coordinate mapping matrices
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)

        # Inverse cylindrical projection: x_cyl = R * sin((x_rect - center_x) / R) + center_x
        x_indices = np.arange(w, dtype=np.float32)
        theta = (x_indices - center_x) / radius
        # Clamp theta to prevent invalid domain
        theta = np.clip(theta, -np.pi / 2.4, np.pi / 2.4)
        x_source = radius * np.sin(theta) + center_x

        for y in range(h):
            map_x[y, :] = x_source
            map_y[y, :] = y

        unwarped = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        return unwarped
