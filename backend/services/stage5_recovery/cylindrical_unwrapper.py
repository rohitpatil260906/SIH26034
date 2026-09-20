"""
Stage 5: Cylindrical Unwrapping Service for Curved Containers
============================================================
Handles cylindrical projection unwarping for bottles, cans, jars, and tubes.
Maps curved circular arcs into planar rectangular projections so text lines
become straight and horizontal for high-accuracy OCR.
Preserves exact coordinate mapping back to the original curved surface.
"""

import math
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from .coordinate_mapper import CoordinateTransformChain, CoordinateTransformStep


class CylindricalUnwrapper:
    """Performs geometric unwrapping of 3D cylindrical packaging labels."""

    def __init__(self):
        pass

    def estimate_cylinder_parameters(
        self,
        cv_img: np.ndarray
    ) -> Tuple[float, float, float, float]:
        """Estimates (centerline_x, radius, left_bound, right_bound) of cylinder."""
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        # Look for vertical edge boundaries of the cylinder
        edges = cv2.Canny(gray, 40, 130)
        col_sums = np.sum(edges > 0, axis=0)

        # Smooth column density
        kernel = np.ones(15) / 15.0
        smooth_sums = np.convolve(col_sums, kernel, mode='same')

        # Left and right boundary peaks
        left_bound = 0.0
        right_bound = float(w - 1)

        # Find significant edge columns in first and last thirds
        left_third = smooth_sums[:w // 3]
        right_third = smooth_sums[2 * w // 3:]

        if np.max(left_third) > np.mean(smooth_sums) * 1.3:
            left_bound = float(np.argmax(left_third))
        if np.max(right_third) > np.mean(smooth_sums) * 1.3:
            right_bound = float((2 * w // 3) + np.argmax(right_third))

        cyl_width = max(float(w) * 0.4, right_bound - left_bound)
        center_x = (left_bound + right_bound) / 2.0
        # Typical cylinder curvature radius is approximately w / 1.5 - 1.8
        radius = cyl_width / 1.55

        return center_x, radius, left_bound, right_bound

    def unwrap(
        self,
        image: Image.Image,
        center_x: Optional[float] = None,
        radius: Optional[float] = None,
        chain: Optional[CoordinateTransformChain] = None
    ) -> Tuple[Image.Image, CoordinateTransformChain, bool]:
        """Unwraps a curved cylindrical container into a planar label.
        
        Returns:
            (unwrapped_image, updated_chain, unwrapped_bool)
        """
        active_chain = chain.clone() if chain is not None else CoordinateTransformChain()
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]

        if center_x is None or radius is None:
            est_cx, est_r, _, _ = self.estimate_cylinder_parameters(cv_img)
            center_x = center_x or est_cx
            radius = radius or est_r

        radius = max(radius, float(w) / 2.5)

        # Build coordinate remap grid
        # In planar image x_rect: source coordinate x_cyl = cx + R * sin((x_rect - cx) / R)
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)

        x_indices = np.arange(w, dtype=np.float32)
        theta = (x_indices - center_x) / radius
        # Clamp theta to visible cylinder front [-pi/2.3, +pi/2.3]
        theta_clamped = np.clip(theta, -math.pi / 2.3, math.pi / 2.3)
        x_source = center_x + radius * np.sin(theta_clamped)

        for y in range(h):
            map_x[y, :] = x_source
            map_y[y, :] = y

        unwrapped_cv = cv2.remap(
            cv_img,
            map_x,
            map_y,
            interpolation=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_REPLICATE
        )
        unwrapped_pil = cv2_to_pil(unwrapped_cv)

        # Register unwrap in transformation chain
        active_chain.add_cylindrical_unwrap(center_x=center_x, radius=radius)

        return unwrapped_pil, active_chain, True
