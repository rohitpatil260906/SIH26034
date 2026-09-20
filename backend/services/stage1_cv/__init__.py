"""
Stage 1: Image Ingestion, Quality Analysis, and Package Localization Master Pipeline
=====================================================================================
Integrates:
1. Safe Ingestion & Metadata Extraction (ImageIngestionService)
2. Orientation Normalization (OrientationNormalizerService)
3. 18-Dimension Quality Evaluation & Gating (QualityAnalyzerService)
4. Package Localization & Multi-Product Segmentation (PackageLocalizationService)
5. Perspective Homography & Cylindrical Unwarping (GeometryCorrectionService)
6. Panel Classification & Non-Front Label Support (PanelDetectionService)
7. Multi-Branch Preprocessing for Subsequent Text Detection Passes
"""

import uuid
import time
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import cv2

from ...models import (
    Stage1Response,
    Stage1InputMetadata,
    Stage1QualityResult,
    Stage1PackageDetection,
    Stage1PanelInfo,
    Stage1GeometryResult,
)
from ..cv_pipeline import pil_to_cv2, cv2_to_pil, encode_image_to_base64
from .ingestion import ImageIngestionService
from .orientation import OrientationNormalizerService
from .quality import QualityAnalyzerService
from .geometry import GeometryCorrectionService, map_point_to_original, map_bbox_to_original
from .localization import PackageLocalizationService
from .panel import PanelDetectionService


class Stage1Pipeline:
    """Master production pipeline for Stage 1 of LM-COMPASS."""

    def __init__(self):
        self.ingestion_service = ImageIngestionService()
        self.orientation_service = OrientationNormalizerService()
        self.quality_service = QualityAnalyzerService()
        self.localization_service = PackageLocalizationService()
        self.geometry_service = GeometryCorrectionService()
        self.panel_service = PanelDetectionService()

    def process_image_bytes(
        self,
        image_bytes: bytes,
        filename: str = "package.jpg",
        source: str = "upload",
        generate_previews: bool = True
    ) -> Stage1Response:
        """Processes raw image bytes through the entire Stage 1 pipeline."""
        scan_id = f"STAGE1-{uuid.uuid4().hex[:10].upper()}"

        # 1. Ingestion & Validation
        orig_img, working_img, metadata, err = self.ingestion_service.ingest_from_bytes(
            image_bytes, original_filename=filename, source=source
        )
        if err or orig_img is None or working_img is None:
            return Stage1Response(
                scan_id=scan_id,
                input=metadata,
                quality=Stage1QualityResult(
                    status="INSUFFICIENT",
                    overall_score=0.0,
                    blur_score=0.0,
                    resolution_score=0.0,
                    contrast_score=0.0,
                    glare_score=0.0,
                    perspective_score=0.0,
                    curvature_score=0.0,
                    occlusion_score=0.0,
                    issues=[err or "Ingestion failed"],
                    explanation="The uploaded image could not be processed. Please provide a valid JPEG, PNG, or WEBP image."
                ),
                package_detection=Stage1PackageDetection(detected=False),
                panel=Stage1PanelInfo(),
                geometry=Stage1GeometryResult(),
                status="INSUFFICIENT_QUALITY",
                message=err or "Image ingestion rejected."
            )

        # 2. Orientation Normalization
        oriented_img, rot_deg, orient_label = self.orientation_service.normalize_orientation(working_img)
        metadata.orientation = orient_label

        # 3. 18-Dimension Quality Assessment
        quality_res, full_metrics = self.quality_service.evaluate_image(oriented_img)

        # If image quality is INSUFFICIENT, halt with detailed retake advisory (prevents false statutory violations)
        if quality_res.status == "INSUFFICIENT":
            return Stage1Response(
                scan_id=scan_id,
                input=metadata,
                quality=quality_res,
                package_detection=Stage1PackageDetection(detected=False),
                panel=Stage1PanelInfo(),
                geometry=Stage1GeometryResult(),
                status="INSUFFICIENT_QUALITY",
                message=quality_res.explanation or "Image quality insufficient for legal compliance scanning."
            )

        # 4. Package Localization & Multi-Product Segmentation
        pkg_detection, isolated_pkg_img, fg_mask = self.localization_service.localize_packages(oriented_img)

        # 5. Geometric Rectification & Cylindrical Unwarping
        rectified_img, geom_result, m_mat, m_inv = self.geometry_service.detect_and_rectify(isolated_pkg_img)

        # 6. Panel Detection & Label Coverage Assessment
        panel_info = self.panel_service.detect_panel(
            rectified_img,
            package_bbox_pct=tuple(pkg_detection.bbox) if len(pkg_detection.bbox) == 4 else (0.0, 0.0, 100.0, 100.0)
        )

        # 7. Multi-Branch Image Preprocessing Variants for Subsequent Stages
        preprocessing_dict: Dict[str, Any] = {}
        if generate_previews:
            preprocessing_dict = self._generate_preprocessing_variants(rectified_img)

        pipeline_status = "READY_FOR_TEXT_DETECTION"
        status_msg = (
            f"Stage 1 complete. Package localized with {pkg_detection.products_count} product instance(s). "
            f"Panel: {panel_info.type} ({panel_info.coverage} coverage). Ready for Stage 2 text detection."
        )

        return Stage1Response(
            scan_id=scan_id,
            input=metadata,
            quality=quality_res,
            package_detection=pkg_detection,
            panel=panel_info,
            geometry=geom_result,
            preprocessing=preprocessing_dict,
            status=pipeline_status,
            message=status_msg
        )

    def process_base64_image(
        self,
        base64_str: str,
        filename: str = "package.jpg",
        source: str = "upload",
        generate_previews: bool = True
    ) -> Stage1Response:
        """Processes base64 encoded image through Stage 1."""
        orig_img, working_img, metadata, err = self.ingestion_service.ingest_from_base64(
            base64_str, original_filename=filename, source=source
        )
        if err or working_img is None:
            scan_id = f"STAGE1-{uuid.uuid4().hex[:10].upper()}"
            return Stage1Response(
                scan_id=scan_id,
                input=metadata,
                quality=Stage1QualityResult(
                    status="INSUFFICIENT",
                    overall_score=0.0,
                    blur_score=0.0,
                    resolution_score=0.0,
                    contrast_score=0.0,
                    glare_score=0.0,
                    perspective_score=0.0,
                    curvature_score=0.0,
                    occlusion_score=0.0,
                    issues=[err or "Base64 decode failed"],
                    explanation="Invalid image data provided."
                ),
                package_detection=Stage1PackageDetection(detected=False),
                panel=Stage1PanelInfo(),
                geometry=Stage1GeometryResult(),
                status="INSUFFICIENT_QUALITY",
                message=err or "Invalid image data."
            )

        # Save to buffer and reuse process_image_bytes
        import io
        buf = io.BytesIO()
        working_img.save(buf, format=working_img.format or "JPEG")
        return self.process_image_bytes(
            buf.getvalue(), filename=filename, source=source, generate_previews=generate_previews
        )

    def _generate_preprocessing_variants(self, image: Image.Image) -> Dict[str, Any]:
        """Generates key preprocessed branches optimized for downstream OCR passes."""
        cv_img = pil_to_cv2(image)
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img

        branches: Dict[str, Any] = {}

        # 1. Upscaled (Bicubic / Lanczos)
        scale = 1.5 if max(w, h) < 1400 else 1.0
        up_w, up_h = int(w * scale), int(h * scale)
        upscaled_cv = cv2.resize(cv_img, (up_w, up_h), interpolation=cv2.INTER_LANCZOS4)
        branches["upscaled"] = {
            "width": up_w,
            "height": up_h,
            "scale_factor": scale,
            "preview_base64": encode_image_to_base64(cv2_to_pil(upscaled_cv), quality=75)
        }

        # 2. Grayscale
        branches["grayscale"] = {
            "width": w,
            "height": h,
            "preview_base64": encode_image_to_base64(Image.fromarray(gray), quality=75)
        }

        # 3. CLAHE Enhanced
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        clahe_gray = clahe.apply(gray)
        branches["clahe"] = {
            "width": w,
            "height": h,
            "clip_limit": 2.2,
            "preview_base64": encode_image_to_base64(Image.fromarray(clahe_gray), quality=75)
        }

        # 4. Sharpened (Unsharp mask)
        sharpened_pil = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        branches["sharpened"] = {
            "width": w,
            "height": h,
            "preview_base64": encode_image_to_base64(sharpened_pil, quality=75)
        }

        # 5. Denoised
        denoised_cv = cv2.fastNlMeansDenoisingColored(cv_img, None, 6, 6, 7, 21) if max(w, h) <= 1200 else cv2.bilateralFilter(cv_img, 5, 40, 40)
        branches["denoised"] = {
            "width": w,
            "height": h,
            "preview_base64": encode_image_to_base64(cv2_to_pil(denoised_cv), quality=75)
        }

        # 6. Adaptive Threshold (Sauvola-style local window binarization)
        adaptive_cv = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 23, 7)
        branches["adaptive_thresh"] = {
            "width": w,
            "height": h,
            "preview_base64": encode_image_to_base64(Image.fromarray(adaptive_cv), quality=75)
        }

        # 7. Glare & Shadow Reduced (Gamma illumination leveling)
        gamma = 1.3
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        glare_shadow_cv = cv2.LUT(cv_img, table)
        branches["glare_shadow_reduced"] = {
            "width": w,
            "height": h,
            "gamma": gamma,
            "preview_base64": encode_image_to_base64(cv2_to_pil(glare_shadow_cv), quality=75)
        }

        return branches
