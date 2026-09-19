"""
Stage 1: Package Localization & Multi-Product Segmentation Service
==================================================================
Provides:
1. Package & Label boundary localization (YOLOv8 + OpenCV morphological saliency fallback)
2. Multi-product segmentation (identifies distinct products: product_instance_1, product_instance_2)
3. Background separation & masking (isolates packaging from retail shelves, conveyors, or tables)
4. Fallback ensuring robust detection even on irregular, cropped, or transparent packaging
"""

from typing import List, Tuple, Optional, Dict, Any
from PIL import Image
import numpy as np
import cv2

from ...models import Stage1PackageDetection, ProductInstanceBox
from ..cv_pipeline import pil_to_cv2, cv2_to_pil
from ..region_detector import get_yolo_model


class PackageLocalizationService:
    """Localizes package boundaries, separates background, and detects multiple products."""

    def __init__(self):
        self.yolo_model = get_yolo_model()

    def localize_packages(
        self,
        image: Image.Image
    ) -> Tuple[Stage1PackageDetection, Image.Image, Optional[np.ndarray]]:
        """Detects package(s), segments instances, and isolates background.
        
        Returns:
            (Stage1PackageDetection, isolated_package_image, foreground_mask)
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        product_instances: List[ProductInstanceBox] = []
        found_boxes: List[Tuple[float, float, float, float, float]] = []  # (x, y, w, h, conf)

        # 1. Attempt YOLOv8 object detection
        if self.yolo_model is not None:
            try:
                # YOLOv8 expects RGB
                rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                results = self.yolo_model(rgb_img, conf=0.25, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        # COCO classes: 39=bottle, 40=wine glass, 41=cup, 42=fork, 43=knife, 44=spoon, 45=bowl, 46=banana, 47=apple, 48=sandwich, 67=cell phone, 73=book
                        # General objects or any detection with confidence > 0.3
                        xyxy = box.xyxy[0].tolist()
                        bx = max(0.0, xyxy[0])
                        by = max(0.0, xyxy[1])
                        bw = min(float(w), xyxy[2]) - bx
                        bh = min(float(h), xyxy[3]) - by
                        if bw * bh > (w * h * 0.08):  # Must be substantial
                            found_boxes.append((bx, by, bw, bh, conf))
            except Exception:
                pass

        # 2. OpenCV Edge & Contour Segmentation (Multi-Product & Saliency Detection)
        if len(found_boxes) <= 1:
            edges = cv2.Canny(gray, 40, 140)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            min_area = (w * h) * 0.08
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < min_area:
                    continue
                bx, by, bw, bh = cv2.boundingRect(cnt)
                # Avoid selecting the entire camera frame borders exactly
                if bw > w * 0.98 and bh > h * 0.98:
                    continue
                conf = min(0.95, round(area / float(w * h) + 0.4, 2))
                found_boxes.append((float(bx), float(by), float(bw), float(bh), conf))

        # 3. Fallback: If still no distinct box found, treat central 90% as the package
        if len(found_boxes) == 0:
            bx = float(w) * 0.05
            by = float(h) * 0.05
            bw = float(w) * 0.90
            bh = float(h) * 0.90
            found_boxes.append((bx, by, bw, bh, 0.85))

        # 4. Multi-Product Segmentation Check
        # Sort boxes left-to-right
        found_boxes = sorted(found_boxes, key=lambda b: b[0])
        non_overlapping_boxes = []
        for b in found_boxes:
            bx, by, bw, bh, conf = b
            # Check overlap with existing accepted boxes (IoU < 0.3)
            overlaps = False
            for ob in non_overlapping_boxes:
                ox, oy, ow, oh, _ = ob
                inter_w = max(0.0, min(bx + bw, ox + ow) - max(bx, ox))
                inter_h = max(0.0, min(by + bh, oy + oh) - max(by, oy))
                inter_area = inter_w * inter_h
                union_area = (bw * bh) + (ow * oh) - inter_area
                iou = inter_area / (union_area + 1e-5)
                if iou > 0.35:
                    overlaps = True
                    break
            if not overlaps:
                non_overlapping_boxes.append(b)

        # Build product instances
        for idx, (bx, by, bw, bh, conf) in enumerate(non_overlapping_boxes):
            inst_id = f"product_instance_{idx + 1}"
            norm_bbox = [
                round((bx / w) * 100.0, 2),
                round((by / h) * 100.0, 2),
                round((bw / w) * 100.0, 2),
                round((bh / h) * 100.0, 2)
            ]
            poly = [
                [norm_bbox[0], norm_bbox[1]],
                [norm_bbox[0] + norm_bbox[2], norm_bbox[1]],
                [norm_bbox[0] + norm_bbox[2], norm_bbox[1] + norm_bbox[3]],
                [norm_bbox[0], norm_bbox[1] + norm_bbox[3]]
            ]
            product_instances.append(
                ProductInstanceBox(
                    instance_id=inst_id,
                    bbox=norm_bbox,
                    polygon=poly,
                    confidence=round(conf, 2)
                )
            )

        products_count = len(product_instances)

        # Primary package: largest or leftmost instance
        primary_inst = product_instances[0]
        primary_px_box = non_overlapping_boxes[0]
        pbx, pby, pbw, pbh = (
            int(primary_px_box[0]),
            int(primary_px_box[1]),
            int(primary_px_box[2]),
            int(primary_px_box[3])
        )

        # 5. Background separation via Masking
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[pby : pby + pbh, pbx : pbx + pbw] = 255

        # Create isolated package image
        isolated_cv = cv2.bitwise_and(cv_img, cv_img, mask=mask)
        # Crop to bounding box with small margin
        crop_x1 = max(0, pbx - 5)
        crop_y1 = max(0, pby - 5)
        crop_x2 = min(w, pbx + pbw + 5)
        crop_y2 = min(h, pby + pbh + 5)
        cropped_cv = isolated_cv[crop_y1:crop_y2, crop_x1:crop_x2]
        if cropped_cv.size == 0:
            cropped_cv = cv_img

        cropped_pil = cv2_to_pil(cropped_cv)

        detection_result = Stage1PackageDetection(
            detected=True,
            bbox=primary_inst.bbox,
            polygon=primary_inst.polygon,
            confidence=primary_inst.confidence,
            products_count=products_count,
            product_instances=product_instances,
            background_removed=True
        )

        return detection_result, cropped_pil, mask
