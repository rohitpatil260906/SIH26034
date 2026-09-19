"""
Stage 2: Universal Text Detection & Advanced OCR Master Pipeline
================================================================
Integrates:
1. Stage 1 verified inputs (rectified panel, quality gate, M_inv matrix, preprocessing variants)
2. Two-Pass Universal Text Detection (Global pass + Targeted micro-text/rotated/curved pass)
3. Multi-Engine OCR Ensemble with agreement confidence boosting
4. Word-to-line grouping, paragraph clustering, and natural reading order
5. Table grid structure detection & cell text extraction
6. 1D Barcode & 2D QR code detection/decoding (isolated from text OCR)
7. Coordinate back-mapping preserving original image coordinates via M_inv
8. Strict principle: Answers ONLY "What text is visible and where is it?"
   Does NOT guess semantic meaning or generate Legal Metrology violations.
"""

import uuid
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image
import numpy as np

from ...models import (
    Stage1Response,
    Stage2Response,
    Stage2TextRegion,
    Stage2TableInfo,
    Stage2BarcodeRegion,
    Stage2QRRegion
)
from ..stage1_cv import Stage1Pipeline
from ..stage1_cv.geometry import map_bbox_to_original
from ..image_enhancement import decode_base64_image
from .text_detector import TwoPassTextDetector
from .tables import TableDetectionService
from .barcodes import BarcodeQRService
from .grouping import cluster_lines_into_blocks


class Stage2Pipeline:
    """Master production pipeline for Stage 2 of LM-COMPASS."""

    def __init__(self):
        self.stage1_pipeline = Stage1Pipeline()
        self.text_detector = TwoPassTextDetector()
        self.table_service = TableDetectionService()
        self.barcode_service = BarcodeQRService()

    def process_from_stage1(
        self,
        stage1_output: Stage1Response,
        working_image: Image.Image,
        original_image: Optional[Image.Image] = None
    ) -> Stage2Response:
        """Executes Stage 2 using existing Stage 1 outputs."""
        scan_id = stage1_output.scan_id.replace("STAGE1", "STAGE2")

        # 1. Check Quality Gate
        if stage1_output.quality.status == "INSUFFICIENT" or stage1_output.status == "INSUFFICIENT_QUALITY":
            return Stage2Response(
                scan_id=scan_id,
                text_detection_status="INSUFFICIENT_QUALITY",
                message=stage1_output.message or "Image quality insufficient for text detection.",
                total_text_regions=0,
                estimated_coverage_pct=0.0
            )

        # 2. Extract Coordinate Transformation Matrix M_inv
        m_inv = None
        if stage1_output.geometry.transformation_matrix:
            m_mat = np.array(stage1_output.geometry.transformation_matrix, dtype=np.float64)
            ret, inv = cv2.invert(m_mat) if hasattr(cv2, 'invert') else (True, np.linalg.inv(m_mat))
            m_inv = inv

        orig_w = stage1_output.input.width or working_image.width
        orig_h = stage1_output.input.height or working_image.height
        is_curved = stage1_output.geometry.curvature_detected

        # 3. Two-Pass Text Detection & OCR Extraction
        all_regions = self.text_detector.detect_and_extract_text(
            image=working_image,
            preprocessing_dict=stage1_output.preprocessing,
            m_inv=m_inv,
            orig_w=orig_w,
            orig_h=orig_h,
            is_curved=is_curved
        )

        # Separate verified vs uncertain text regions
        verified_regions: List[Stage2TextRegion] = []
        uncertain_regions: List[Stage2TextRegion] = []

        for r in all_regions:
            if r.status == "OCR_UNCERTAIN":
                uncertain_regions.append(r)
            else:
                verified_regions.append(r)

        # 4. Table Structure & Cell Detection
        text_dicts = [
            {"bbox": r.bbox, "raw_text": r.raw_text, "normalized_text": r.normalized_text}
            for r in verified_regions
        ]
        tables = self.table_service.detect_tables(
            image=working_image,
            text_regions=text_dicts,
            m_inv=m_inv,
            orig_w=orig_w,
            orig_h=orig_h
        )

        # 5. Barcode & QR Code Detection and Decoding
        barcodes, qr_codes = self.barcode_service.detect_barcodes_and_qr(
            image=working_image,
            m_inv=m_inv,
            orig_w=orig_w,
            orig_h=orig_h
        )

        # 6. Calculate Text Coverage
        total_text_area = sum(r.bbox[2] * r.bbox[3] for r in verified_regions)
        image_area = float(working_image.width * working_image.height + 1e-5)
        coverage_pct = round(min(100.0, (total_text_area / image_area) * 100.0), 1)

        status_msg = (
            f"Stage 2 complete. Detected {len(verified_regions)} text region(s), "
            f"{len(tables)} table(s), {len(barcodes)} barcode(s), and {len(qr_codes)} QR code(s). "
            f"Text coverage: {coverage_pct}%."
        )

        return Stage2Response(
            scan_id=scan_id,
            text_detection_status="COMPLETED",
            regions=verified_regions,
            uncertain_regions=uncertain_regions,
            barcode_regions=barcodes,
            qr_regions=qr_codes,
            tables=tables,
            total_text_regions=len(verified_regions),
            estimated_coverage_pct=coverage_pct,
            message=status_msg
        )

    def process_image_bytes(
        self,
        image_bytes: bytes,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage2Response:
        """Executes full Stage 1 ingestion & geometry first, then executes Stage 2."""
        # Run Stage 1
        stage1_res = self.stage1_pipeline.process_image_bytes(
            image_bytes, filename=filename, source=source, generate_previews=True
        )

        if stage1_res.status == "INSUFFICIENT_QUALITY" or stage1_res.quality.status == "INSUFFICIENT":
            scan_id = stage1_res.scan_id.replace("STAGE1", "STAGE2")
            return Stage2Response(
                scan_id=scan_id,
                text_detection_status="INSUFFICIENT_QUALITY",
                message=stage1_res.message or "Image quality insufficient for text detection.",
                total_text_regions=0,
                estimated_coverage_pct=0.0
            )

        # Decode working copy from original bytes
        import io
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.process_from_stage1(stage1_res, working_image=pil_img, original_image=pil_img)

    def process_base64_image(
        self,
        base64_str: str,
        filename: str = "package.jpg",
        source: str = "upload"
    ) -> Stage2Response:
        """Decodes base64, runs Stage 1, then executes Stage 2."""
        import base64
        clean_b64 = base64_str.split(",", 1)[1] if "," in base64_str else base64_str
        raw_bytes = base64.b64decode(clean_b64)
        return self.process_image_bytes(raw_bytes, filename=filename, source=source)


import cv2
