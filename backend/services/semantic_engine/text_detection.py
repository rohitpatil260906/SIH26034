"""
Service 4: Text Detection Service
=================================
Identifies text-bearing visual bounding boxes and regions across the packaging:
- Generates line-level and region-level bounding boxes
- Normalizes coordinates to both relative percentages (0-100%) and pixel coordinates [x1, y1, x2, y2]
- Filters non-text artifacts and noise
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import numpy as np
import cv2

from ...models import BoundingBox, DetectedRegion
from ..region_detector import detect_regions_of_interest, get_yolo_model


class TextDetectionService:
    """Detects text regions, blocks, and statutory areas of interest."""

    def __init__(self):
        self.yolo_model = get_yolo_model()

    def detect_text_regions(
        self,
        image: Image.Image
    ) -> Tuple[List[DetectedRegion], List[BoundingBox]]:
        """Finds statutory text regions and raw bounding boxes."""
        regions, labelme_ann = detect_regions_of_interest(image)
        boxes: List[BoundingBox] = [reg.bbox for reg in regions if reg.bbox is not None]
        return regions, boxes

    def crop_region(
        self,
        image: Image.Image,
        bbox: BoundingBox
    ) -> Image.Image:
        """Crops the specified bounding box from the PIL image."""
        w, h = image.size
        x1 = max(0, int((bbox.x / 100.0) * w))
        y1 = max(0, int((bbox.y / 100.0) * h))
        x2 = min(w, int(((bbox.x + bbox.width) / 100.0) * w))
        y2 = min(h, int(((bbox.y + bbox.height) / 100.0) * h))

        if x2 <= x1 or y2 <= y1:
            return image
        return image.crop((x1, y1, x2, y2))
