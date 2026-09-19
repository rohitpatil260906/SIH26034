"""
Stage 2: Barcode & QR Code Localization and Decoding Service
============================================================
Provides:
1. 1D Barcode detection & decoding (EAN-13, UPC, Code 128, ITF)
2. 2D QR Code detection & payload decoding
3. Completely isolates barcode/QR regions so they are not confused with text OCR
4. Maps coordinates back to the original image space using M_inv
"""

import uuid
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
import numpy as np
import cv2

from ...models import Stage2BarcodeRegion, Stage2QRRegion
from ..cv_pipeline import pil_to_cv2
from ..stage1_cv.geometry import map_bbox_to_original


class BarcodeQRService:
    """Detects, segments, and decodes 1D Barcodes and 2D QR codes."""

    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()
        try:
            self.barcode_detector = cv2.barcode.BarcodeDetector()
        except Exception:
            self.barcode_detector = None

    def detect_barcodes_and_qr(
        self,
        image: Image.Image,
        m_inv: Optional[np.ndarray] = None,
        orig_w: int = 1000,
        orig_h: int = 1000
    ) -> Tuple[List[Stage2BarcodeRegion], List[Stage2QRRegion]]:
        """Finds barcode and QR regions, decodes data, and maps coordinates.
        
        Returns:
            (barcode_regions, qr_regions)
        """
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        barcodes: List[Stage2BarcodeRegion] = []
        qr_codes: List[Stage2QRRegion] = []

        # ----------------------------------------------------
        # 1. 2D QR CODE DETECTION & DECODING
        # ----------------------------------------------------
        try:
            decoded_info, points, _ = self.qr_detector.detectAndDecode(gray)
            if points is not None and len(points) > 0:
                pts = points[0]
                qx = float(np.min(pts[:, 0]))
                qy = float(np.min(pts[:, 1]))
                qw = float(np.max(pts[:, 0]) - qx)
                qh = float(np.max(pts[:, 1]) - qy)

                qr_bbox = [round(qx, 1), round(qy, 1), round(max(qw, 10.0), 1), round(max(qh, 10.0), 1)]
                orig_bbox = map_bbox_to_original(qr_bbox, m_inv, orig_w, orig_h) if m_inv is not None else qr_bbox

                qr_codes.append(
                    Stage2QRRegion(
                        qr_id=f"QR-{uuid.uuid4().hex[:6].upper()}",
                        bbox=qr_bbox,
                        original_bbox=orig_bbox,
                        decoded_payload=decoded_info if decoded_info else None,
                        confidence=0.98 if decoded_info else 0.85
                    )
                )
        except Exception:
            pass

        # ----------------------------------------------------
        # 2. 1D BARCODE DETECTION & DECODING
        # ----------------------------------------------------
        found_barcode = False
        if self.barcode_detector is not None:
            try:
                res = self.barcode_detector.detectAndDecode(gray)
                # res is (decoded_info, decoded_type, points) in OpenCV 5.0
                if len(res) >= 3 and res[2] is not None:
                    decoded_info, barcode_type, points = res[0], res[1], res[2]
                    pts = points[0] if len(points.shape) > 2 else points
                    bx = float(np.min(pts[:, 0]))
                    by = float(np.min(pts[:, 1]))
                    bw = float(np.max(pts[:, 0]) - bx)
                    bh = float(np.max(pts[:, 1]) - by)

                    bar_bbox = [round(bx, 1), round(by, 1), round(max(bw, 10.0), 1), round(max(bh, 10.0), 1)]
                    orig_bbox = map_bbox_to_original(bar_bbox, m_inv, orig_w, orig_h) if m_inv is not None else bar_bbox

                    barcodes.append(
                        Stage2BarcodeRegion(
                            barcode_id=f"BAR-{uuid.uuid4().hex[:6].upper()}",
                            format=str(barcode_type) if barcode_type else "1D_BARCODE",
                            bbox=bar_bbox,
                            original_bbox=orig_bbox,
                            decoded_data=decoded_info if decoded_info else None,
                            confidence=0.98 if decoded_info else 0.85
                        )
                    )
                    found_barcode = True
            except Exception:
                pass

        # Morphological fallback for 1D barcodes (Scharr vertical gradient stripes)
        if not found_barcode:
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=-1)
            grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=-1)
            gradient = cv2.subtract(grad_x, grad_y)
            gradient = cv2.convertScaleAbs(gradient)

            blurred = cv2.blur(gradient, (9, 9))
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Close vertical gaps
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            closed = cv2.erode(closed, None, iterations=3)
            closed = cv2.dilate(closed, None, iterations=3)

            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > (w * h * 0.008):
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    aspect = float(bw) / float(bh) if bh > 0 else 1.0
                    # Typical 1D barcode aspect ratio between 0.8 and 5.0
                    if 0.8 <= aspect <= 5.5 and bw < w * 0.9:
                        bar_bbox = [float(bx), float(by), float(bw), float(bh)]
                        orig_bbox = map_bbox_to_original(bar_bbox, m_inv, orig_w, orig_h) if m_inv is not None else bar_bbox
                        barcodes.append(
                            Stage2BarcodeRegion(
                                barcode_id=f"BAR-{uuid.uuid4().hex[:6].upper()}",
                                format="1D_BARCODE",
                                bbox=bar_bbox,
                                original_bbox=orig_bbox,
                                decoded_data=None,
                                confidence=0.85
                            )
                        )
                        break

        return barcodes, qr_codes
