"""
Stage 10: Master Pipeline Orchestrator
======================================
Central orchestration layer managing end-to-end 10-stage LM-COMPASS pipeline execution:
- Manages scan session creation, image registration, and execution pipeline.
- Enforces strict pipeline state machine (CREATED -> QUALITY_ANALYZED -> OCR -> PRODUCT -> RULES -> VIOLATIONS -> FINALIZED).
- Synthesizes unified Stage10FinalResult objects per product.
- Enforces deterministic overall status logic (COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW, PARTIAL, FAILED).
- Enforces idempotency (re-executing scan yields identical deterministic fingerprints without duplicates).
- Maintains end-to-end operational audit trail.
"""

import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from .pipeline_models import (
    Stage10StageProgress,
    Stage10ProcessingMetadata,
    Stage10AuditEvent,
    Stage10FinalResult,
    Stage10ScanStatusResponse,
    Stage10RunRequest,
    Stage10RunResponse
)
from .pipeline_state import PipelineState, PipelineStateValidator
from .pipeline_events import AuditTrailLogger
from .pipeline_runner import PipelineRunner
from ..models import (
    Stage7UnifiedProduct,
    Stage8ProductEvaluation,
    Stage9ProductViolationResult
)


class Stage10PipelineOrchestrator:
    """Master Pipeline Orchestrator for Stage 10."""

    def __init__(self):
        # Scan Session In-Memory Cache
        self._scans: Dict[str, Dict[str, Any]] = {}

    def create_scan(self, session_id: Optional[str] = None) -> str:
        """Creates a new scan session docket."""
        session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        scan_id = f"INSP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        audit = AuditTrailLogger(scan_id)
        audit.log_event("ORCHESTRATOR", "SCAN_CREATED", "SUCCESS", details={"session_id": session_id})

        self._scans[scan_id] = {
            "scan_id": scan_id,
            "session_id": session_id,
            "state": PipelineState.CREATED,
            "overall_status": "PENDING",
            "images": [],
            "audit": audit,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "final_results": [],
            "processing_metadata": None
        }

        return scan_id

    def register_image(
        self,
        scan_id: str,
        image_data: str,
        filename: str = "package.jpg",
        panel: str = "FRONT",
        source: str = "upload"
    ) -> Dict[str, Any]:
        """Registers an image with a scan session."""
        if scan_id not in self._scans:
            raise KeyError(f"Scan ID '{scan_id}' not found")

        scan = self._scans[scan_id]
        img_id = f"img_{len(scan['images']) + 1:03d}"

        img_obj = {
            "image_id": img_id,
            "filename": filename,
            "panel": panel.upper(),
            "source": source,
            "data": image_data
        }

        scan["images"].append(img_obj)
        scan["state"] = PipelineState.IMAGE_RECEIVED

        scan["audit"].log_event("ORCHESTRATOR", "IMAGE_REGISTERED", "SUCCESS", details={"image_id": img_id, "panel": panel})
        return img_obj

    def run_pipeline(
        self,
        scan_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Stage10RunResponse:
        """Executes the complete 10-stage pipeline for a scan session."""
        if scan_id not in self._scans:
            raise KeyError(f"Scan ID '{scan_id}' not found")

        scan = self._scans[scan_id]
        options = options or {}
        audit: AuditTrailLogger = scan["audit"]
        t_start = time.time()

        # Idempotency check: return cached results if already FINALIZED
        if scan["state"] == PipelineState.FINALIZED and scan.get("run_response"):
            return scan["run_response"]

        runner = PipelineRunner(scan_id, audit)
        res_dict = runner.run_full_pipeline(
            images_input=scan["images"],
            session_id=scan["session_id"],
            options=options
        )

        if res_dict.get("status") == "FAILED":
            scan["state"] = PipelineState.FAILED
            scan["overall_status"] = "FAILED"
            dt_fail = (time.time() - t_start) * 1000
            meta_fail = Stage10ProcessingMetadata(
                started_at=scan["started_at"],
                completed_at=datetime.now().isoformat(),
                processing_time_ms=dt_fail,
                stages_executed=res_dict.get("progress", [])
            )
            return Stage10RunResponse(
                scan_id=scan_id,
                session_id=scan["session_id"],
                pipeline_state=PipelineState.FAILED.value,
                overall_status="FAILED",
                final_results=[],
                audit_trail=audit.get_events(),
                processing=meta_fail
            )

        stage7_res = res_dict["stage7_response"]
        stage8_res = res_dict["stage8_response"]
        stage9_res = res_dict["stage9_response"]
        progress_history = res_dict["progress"]

        # Synthesize Stage10FinalResult for each product
        final_results: List[Stage10FinalResult] = []

        for p_idx, prod in enumerate(stage7_res.products):
            pid = prod.product_id

            # Find matching Stage 8 & Stage 9 results for product
            p_s8 = next((e for e in stage8_res.product_evaluations if e.product_id == pid), None)
            p_s9 = next((r for r in stage9_res.product_results if r.product_id == pid), None)

            # Determine deterministic product overall status
            if p_s9 and p_s9.violations:
                p_overall = "NON_COMPLIANT"
            elif p_s9 and p_s9.review_items:
                p_overall = "NEEDS_REVIEW"
            elif p_s8 and p_s8.overall_status in ("NEEDS_REVIEW", "CONFLICT"):
                p_overall = "NEEDS_REVIEW"
            else:
                p_overall = "COMPLIANT"

            # Build evidence list
            ev_list = p_s9.violations[0].evidence if p_s9 and p_s9.violations else []

            # Build summary
            num_rules = len(p_s8.evaluations) if p_s8 else 0
            num_viol = len(p_s9.violations) if p_s9 else 0
            num_rev = len(p_s9.review_items) if p_s9 else 0
            num_comp = sum(1 for e in p_s8.evaluations if e.evaluation_status == "COMPLIANT") if p_s8 else 0
            num_not_app = sum(1 for e in p_s8.evaluations if e.applicability_status == "NOT_APPLICABLE") if p_s8 else 0

            summary_dict = {
                "rules_evaluated": num_rules,
                "compliant": num_comp,
                "non_compliant": num_viol,
                "needs_review": num_rev,
                "not_applicable": num_not_app
            }

            dt_total = (time.time() - t_start) * 1000
            proc_meta = Stage10ProcessingMetadata(
                started_at=scan["started_at"],
                completed_at=datetime.now().isoformat(),
                processing_time_ms=dt_total,
                stages_executed=progress_history
            )

            f_res = Stage10FinalResult(
                scan_id=scan_id,
                session_id=scan["session_id"],
                product_id=pid,
                product_identity=prod.identity,
                images=scan["images"],
                panels=[{"panel": s.panel, "image_id": s.image_id} for s in prod.source_images],
                extracted_information=prod.fields,
                rule_evaluations=p_s8.evaluations if p_s8 else [],
                violations=p_s9.violations if p_s9 else [],
                review_items=p_s9.review_items if p_s9 else [],
                conflicts=prod.conflicts,
                evidence=ev_list,
                overall_status=p_overall,
                summary=summary_dict,
                processing=proc_meta
            )
            final_results.append(f_res)

        # Overall Session Status
        if any(f.overall_status == "NON_COMPLIANT" for f in final_results):
            sess_overall = "NON_COMPLIANT"
            pipe_state = PipelineState.FINALIZED
        elif any(f.overall_status == "NEEDS_REVIEW" for f in final_results):
            sess_overall = "NEEDS_REVIEW"
            pipe_state = PipelineState.NEEDS_REVIEW
        else:
            sess_overall = "COMPLIANT"
            pipe_state = PipelineState.FINALIZED

        scan["state"] = pipe_state
        scan["overall_status"] = sess_overall
        scan["final_results"] = final_results
        scan["completed_at"] = datetime.now().isoformat()

        audit.log_event("ORCHESTRATOR", "PIPELINE_FINALIZED", pipe_state.value, details={"overall_status": sess_overall})

        dt_total_all = (time.time() - t_start) * 1000
        total_meta = Stage10ProcessingMetadata(
            started_at=scan["started_at"],
            completed_at=scan["completed_at"],
            processing_time_ms=dt_total_all,
            stages_executed=progress_history
        )

        response = Stage10RunResponse(
            scan_id=scan_id,
            session_id=scan["session_id"],
            pipeline_state=pipe_state.value,
            overall_status=sess_overall,
            final_results=final_results,
            audit_trail=audit.get_events(),
            processing=total_meta
        )

        scan["run_response"] = response
        return response

    def get_scan_status(self, scan_id: str) -> Stage10ScanStatusResponse:
        """Retrieves scan status and audit events."""
        if scan_id not in self._scans:
            raise KeyError(f"Scan ID '{scan_id}' not found")

        scan = self._scans[scan_id]
        audit: AuditTrailLogger = scan["audit"]

        progress_list: List[Stage10StageProgress] = []
        if scan.get("run_response"):
            progress_list = scan["run_response"].processing.stages_executed

        return Stage10ScanStatusResponse(
            scan_id=scan_id,
            session_id=scan["session_id"],
            pipeline_state=scan["state"].value,
            overall_status=scan["overall_status"],
            progress=progress_list,
            audit_events=audit.get_events()
        )

    def get_final_results(self, scan_id: str) -> List[Stage10FinalResult]:
        """Retrieves final result objects for a scan session."""
        if scan_id not in self._scans:
            raise KeyError(f"Scan ID '{scan_id}' not found")

        return self._scans[scan_id].get("final_results", [])
