"""
Stage 10: Sequential Pipeline Execution Runner
==============================================
Executes Stages 1 through 9 sequentially with resilience & error isolation:
- STAGE 1: Image Ingestion, Quality Analysis & Panel Localization
- STAGE 5: Advanced Curved / Distorted Image Recovery
- STAGE 2: Multi-Pass Ensemble OCR & Text Region Detection
- STAGE 3: Semantic Field Understanding & Value Normalization
- STAGE 4: Product & Entity Identification
- STAGE 6: Universal Adaptive Product Schema Engine
- STAGE 7: Cross-Panel Information Merging Engine
- STAGE 8: Verified Legal Metrology Rule Engine
- STAGE 9: Violation & Evidence Engine
"""

import time
import logging
from typing import List, Dict, Any, Optional

from ..services.stage1_cv import Stage1Pipeline
from ..services.stage2_ocr import Stage2Pipeline
from ..services.stage3_semantic import Stage3Pipeline
from ..services.stage4_identity import Stage4Pipeline
from ..services.stage5_recovery import Stage5Pipeline
from ..services.stage6_adaptive_schema import Stage6Pipeline
from ..services.stage7_cross_panel import Stage7Pipeline
from ..rules import Stage8RuleEngine
from ..violations import Stage9ViolationEngine
from .pipeline_models import Stage10StageProgress
from .pipeline_events import AuditTrailLogger
from .pipeline_state import PipelineState

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Executes sequential pipeline stages with error isolation & retries."""

    def __init__(self, scan_id: str, logger_audit: AuditTrailLogger):
        self.scan_id = scan_id
        self.audit = logger_audit

        # Stage Service Instances
        self.stage1 = Stage1Pipeline()
        self.stage5 = Stage5Pipeline()
        self.stage2 = Stage2Pipeline()
        self.stage3 = Stage3Pipeline()
        self.stage4 = Stage4Pipeline()
        self.stage6 = Stage6Pipeline()
        self.stage7 = Stage7Pipeline()
        self.stage8 = Stage8RuleEngine()
        self.stage9 = Stage9ViolationEngine()

    def run_full_pipeline(
        self,
        images_input: List[Dict[str, Any]],
        session_id: str = "session_001",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs end-to-end Stages 1-9 pipeline for multi-image packaging inputs."""
        options = options or {}
        progress_history: List[Stage10StageProgress] = []

        # ----------------------------------------------------
        # STAGE 1: INGESTION & QUALITY ANALYSIS
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_1", "STAGE_START", "RUNNING")
        stage1_responses = []

        for idx, img_info in enumerate(images_input):
            try:
                base64_data = img_info.get("data", "")
                fname = img_info.get("filename", f"panel_{idx+1}.jpg")
                src = img_info.get("source", "upload")

                if base64_data:
                    res1 = self.stage1.process_base64_image(base64_data, filename=fname, source=src)
                    stage1_responses.append(res1)
            except Exception as e:
                logger.error(f"Stage 1 error on image {idx}: {e}")
                self.audit.log_event("STAGE_1", "IMAGE_ERROR", "PARTIAL", details={"image_index": idx, "error": str(e)})

        dt1 = (time.time() - t0) * 1000
        p1 = Stage10StageProgress(
            stage_name="STAGE_1_QUALITY",
            status="COMPLETED" if stage1_responses else "FAILED",
            processing_time_ms=dt1
        )
        progress_history.append(p1)
        self.audit.log_event("STAGE_1", "STAGE_COMPLETE", p1.status)

        if not stage1_responses:
            return {"status": "FAILED", "error": "All images failed Stage 1 ingestion", "progress": progress_history}

        # ----------------------------------------------------
        # STAGE 5: CURVED / DIFFICULT LABEL RECOVERY
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_5", "STAGE_START", "RUNNING")
        stage5_responses = []

        for idx, res1 in enumerate(stage1_responses):
            try:
                base64_data = images_input[idx].get("data", "") if idx < len(images_input) else ""
                if base64_data:
                    import base64
                    import io
                    from PIL import Image
                    image_bytes = base64.b64decode(base64_data)
                    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    res5, best_img, _ = self.stage5.process_from_stage1(res1, pil_img, original_image=pil_img)
                    stage5_responses.append(res5)
                else:
                    stage5_responses.append(res1)
            except Exception as e:
                logger.warning(f"Stage 5 recovery fallback for image {getattr(res1, 'filename', idx)}: {e}")
                stage5_responses.append(res1)

        dt5 = (time.time() - t0) * 1000
        p5 = Stage10StageProgress(stage_name="STAGE_5_RECOVERY", status="COMPLETED", processing_time_ms=dt5)
        progress_history.append(p5)
        self.audit.log_event("STAGE_5", "STAGE_COMPLETE", p5.status)

        # ----------------------------------------------------
        # STAGE 2: UNIVERSAL TEXT DETECTION & OCR
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_2", "STAGE_START", "RUNNING")
        stage2_responses = []

        for idx, img_info in enumerate(images_input):
            try:
                base64_data = img_info.get("data", "")
                fname = img_info.get("filename", f"panel_{idx+1}.jpg")
                src = img_info.get("source", "upload")
                if base64_data:
                    res2 = self.stage2.process_base64_image(base64_data, filename=fname, source=src)
                    stage2_responses.append(res2)
            except Exception as e:
                logger.error(f"Stage 2 OCR error on image {idx}: {e}")

        dt2 = (time.time() - t0) * 1000
        p2 = Stage10StageProgress(stage_name="STAGE_2_OCR", status="COMPLETED" if stage2_responses else "FAILED", processing_time_ms=dt2)
        progress_history.append(p2)
        if not stage2_responses:
            return {"status": "FAILED", "error": "All images failed Stage 2 OCR text extraction", "progress": progress_history}

        # ----------------------------------------------------
        # STAGE 3: SEMANTIC UNDERSTANDING
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_3", "STAGE_START", "RUNNING")
        stage3_responses = []

        for res2 in stage2_responses:
            try:
                res3 = self.stage3.process_stage2_output(res2)
                stage3_responses.append(res3)
            except Exception as e:
                logger.error(f"Stage 3 semantic error on image {res2.image_id}: {e}")

        dt3 = (time.time() - t0) * 1000
        p3 = Stage10StageProgress(stage_name="STAGE_3_SEMANTIC", status="COMPLETED" if stage3_responses else "FAILED", processing_time_ms=dt3)
        progress_history.append(p3)
        self.audit.log_event("STAGE_3", "STAGE_COMPLETE", p3.status)

        # ----------------------------------------------------
        # STAGE 4: PRODUCT & ENTITY IDENTIFICATION
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_4", "STAGE_START", "RUNNING")
        stage4_responses = []

        for res3 in stage3_responses:
            try:
                res4 = self.stage4.process_stage3_output(res3)
                stage4_responses.append(res4)
            except Exception as e:
                logger.error(f"Stage 4 identity error on image {res3.image_id}: {e}")

        dt4 = (time.time() - t0) * 1000
        p4 = Stage10StageProgress(stage_name="STAGE_4_IDENTITY", status="COMPLETED" if stage4_responses else "FAILED", processing_time_ms=dt4)
        progress_history.append(p4)
        self.audit.log_event("STAGE_4", "STAGE_COMPLETE", p4.status)

        # ----------------------------------------------------
        # STAGE 6: UNIVERSAL ADAPTIVE PRODUCT SCHEMA
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_6", "STAGE_START", "RUNNING")
        stage6_responses = []

        for res4 in stage4_responses:
            try:
                res6 = self.stage6.process_from_stages(stage4_output=res4)
                stage6_responses.append(res6)
            except Exception as e:
                logger.error(f"Stage 6 adaptive schema error: {e}")

        dt6 = (time.time() - t0) * 1000
        p6 = Stage10StageProgress(stage_name="STAGE_6_SCHEMA", status="COMPLETED" if stage6_responses else "FAILED", processing_time_ms=dt6)
        progress_history.append(p6)
        self.audit.log_event("STAGE_6", "STAGE_COMPLETE", p6.status)

        # ----------------------------------------------------
        # STAGE 7: CROSS-PANEL INFORMATION MERGING
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_7", "STAGE_START", "RUNNING")
        try:
            image_inputs = []
            for idx, img_info in enumerate(images_input):
                image_inputs.append({
                    "image_id": img_info.get("filename", f"panel_{idx+1}.jpg"),
                    "panel": img_info.get("panel", "UNKNOWN"),
                    "stage1_output": stage1_responses[idx] if idx < len(stage1_responses) else None,
                    "stage2_output": stage2_responses[idx] if idx < len(stage2_responses) else None,
                    "stage3_output": stage3_responses[idx] if idx < len(stage3_responses) else None,
                    "stage4_output": stage4_responses[idx] if idx < len(stage4_responses) else None,
                    "stage6_output": stage6_responses[idx] if idx < len(stage6_responses) else None,
                })
            stage7_res = self.stage7.process_session(session_id=session_id, image_inputs=image_inputs)
            dt7 = (time.time() - t0) * 1000
            p7 = Stage10StageProgress(stage_name="STAGE_7_CROSS_PANEL_MERGE", status="COMPLETED", processing_time_ms=dt7)
        except Exception as e:
            logger.error(f"Stage 7 cross-panel merge error: {e}")
            dt7 = (time.time() - t0) * 1000
            p7 = Stage10StageProgress(stage_name="STAGE_7_CROSS_PANEL_MERGE", status="FAILED", errors=[str(e)], processing_time_ms=dt7)
            stage7_res = None

        progress_history.append(p7)
        self.audit.log_event("STAGE_7", "STAGE_COMPLETE", p7.status)

        if not stage7_res or not stage7_res.products:
            return {"status": "FAILED", "error": "Stage 7 product consolidation failed", "progress": progress_history}

        # ----------------------------------------------------
        # STAGE 8: VERIFIED LEGAL METROLOGY RULE ENGINE
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_8", "STAGE_START", "RUNNING")
        try:
            stage8_res = self.stage8.evaluate_session(
                session_id=session_id,
                stage7_response=stage7_res,
                rule_context=options.get("rule_context")
            )
            dt8 = (time.time() - t0) * 1000
            p8 = Stage10StageProgress(stage_name="STAGE_8_RULE_ENGINE", status="COMPLETED", processing_time_ms=dt8)
        except Exception as e:
            logger.error(f"Stage 8 rule engine error: {e}")
            dt8 = (time.time() - t0) * 1000
            p8 = Stage10StageProgress(stage_name="STAGE_8_RULE_ENGINE", status="FAILED", errors=[str(e)], processing_time_ms=dt8)
            stage8_res = None

        progress_history.append(p8)
        self.audit.log_event("STAGE_8", "STAGE_COMPLETE", p8.status)

        if not stage8_res or not stage8_res.product_evaluations:
            return {"status": "FAILED", "error": "Stage 8 rule engine failed", "progress": progress_history}

        # ----------------------------------------------------
        # STAGE 9: VIOLATION & EVIDENCE ENGINE
        # ----------------------------------------------------
        t0 = time.time()
        self.audit.log_event("STAGE_9", "STAGE_START", "RUNNING")
        try:
            stage9_res = self.stage9.evaluate_session_violations(
                session_id=session_id,
                product_evaluations=stage8_res.product_evaluations,
                scan_id=self.scan_id
            )
            dt9 = (time.time() - t0) * 1000
            p9 = Stage10StageProgress(stage_name="STAGE_9_VIOLATIONS", status="COMPLETED", processing_time_ms=dt9)
        except Exception as e:
            logger.error(f"Stage 9 violation engine error: {e}")
            dt9 = (time.time() - t0) * 1000
            p9 = Stage10StageProgress(stage_name="STAGE_9_VIOLATIONS", status="FAILED", errors=[str(e)], processing_time_ms=dt9)
            stage9_res = None

        progress_history.append(p9)
        self.audit.log_event("STAGE_9", "STAGE_COMPLETE", p9.status)

        return {
            "status": "COMPLETED",
            "stage7_response": stage7_res,
            "stage8_response": stage8_res,
            "stage9_response": stage9_res,
            "progress": progress_history,
            "images_input": images_input
        }
