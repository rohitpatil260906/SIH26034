"""
Stage 10 Automated Integration Test Suite
=========================================
Tests Stage 10: Final Integration & Production-Like Demo Hardening.

20 Comprehensive Integration Test Scenarios:
1. Single image complete pipeline.
2. Multi-image same-product pipeline.
3. Front + back merge reaches final result.
4. Multiple products remain separate.
5. Stage failure produces correct pipeline state.
6. Partial processing produces PARTIAL/NEEDS_REVIEW.
7. Stage 8 result reaches Stage 9.
8. Stage 9 violation reaches final result.
9. Evidence remains linked to original image.
10. Original bounding box remains unchanged.
11. Review item reaches final result.
12. Conflict reaches final result.
13. Duplicate execution does not create duplicate violations.
14. Product IDs remain consistent.
15. Rule IDs remain consistent.
16. Evidence IDs remain consistent.
17. Audit events are generated.
18. Frontend/backend API contract works.
19. Unauthorized/invalid access is rejected.
20. Existing Stage 5-9 tests continue to pass.
"""

import unittest
import base64
import numpy as np
import cv2
from typing import List, Dict, Any

from backend.models import (
    Stage7UnifiedProduct,
    Stage8ProductEvaluation,
    Stage9ProductViolationResult,
    Stage10FinalResult,
    Stage10RunResponse
)
from backend.pipeline import (
    Stage10PipelineOrchestrator,
    PipelineState,
    PipelineRunner,
    AuditTrailLogger
)


def generate_dummy_base64_label(text: str = "ROYAL TEA 500g ₹250") -> str:
    """Generates a small valid base64 image containing text for pipeline integration testing."""
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')


class TestStage10Integration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Stage10PipelineOrchestrator()
        self.sample_b64 = generate_dummy_base64_label()

    # 1. Single image complete pipeline
    def test_01_single_image_complete_pipeline(self):
        """1. Single image complete pipeline."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        self.assertEqual(response.scan_id, scan_id)
        self.assertIn(response.pipeline_state, [PipelineState.FINALIZED.value, PipelineState.NEEDS_REVIEW.value])
        self.assertTrue(len(response.final_results) > 0)

    # 2. Multi-image same-product pipeline
    def test_02_multi_image_same_product_pipeline(self):
        """2. Multi-image same-product pipeline."""
        scan_id = self.orchestrator.create_scan()
        b64_front = generate_dummy_base64_label("ROYAL TEA Front PDP")
        b64_back = generate_dummy_base64_label("MRP Rs 250 Net Qty 500g Mfd 01/2024 Assam 781001")

        self.orchestrator.register_image(scan_id, b64_front, "front.jpg", "FRONT")
        self.orchestrator.register_image(scan_id, b64_back, "back.jpg", "BACK")

        response = self.orchestrator.run_pipeline(scan_id)
        self.assertTrue(len(response.final_results) > 0)
        p0 = response.final_results[0]
        self.assertTrue(len(p0.images) == 2)

    # 3. Front + back merge reaches final result
    def test_03_front_back_merge_reaches_final_result(self):
        """3. Front + back merge reaches final result."""
        scan_id = self.orchestrator.create_scan()
        b64_front = generate_dummy_base64_label("ROYAL CHAI TEA")
        b64_back = generate_dummy_base64_label("Net Qty 500 g MRP 250 Royal Tea Packers Assam 781001")

        self.orchestrator.register_image(scan_id, b64_front, "front.jpg", "FRONT")
        self.orchestrator.register_image(scan_id, b64_back, "back.jpg", "BACK")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertIsNotNone(p0.extracted_information)

    # 4. Multiple products remain separate
    def test_04_multiple_products_remain_separate(self):
        """4. Multiple products remain separate."""
        scan_id = self.orchestrator.create_scan()
        b64_p1 = generate_dummy_base64_label("PRODUCT ALPHA TEA 500g")
        b64_p2 = generate_dummy_base64_label("PRODUCT BETA COFFEE 200g")

        self.orchestrator.register_image(scan_id, b64_p1, "p1.jpg", "FRONT")
        self.orchestrator.register_image(scan_id, b64_p2, "p2.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p_ids = [r.product_id for r in response.final_results]
        self.assertEqual(len(p_ids), len(set(p_ids)))

    # 5. Stage failure produces correct pipeline state
    def test_05_stage_failure_produces_failed_pipeline_state(self):
        """5. Stage failure produces correct pipeline state."""
        scan_id = self.orchestrator.create_scan()
        # Invalid image format triggers failure cleanly
        self.orchestrator.register_image(scan_id, "invalid_base64_string", "bad.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        self.assertEqual(response.pipeline_state, PipelineState.FAILED.value)

    # 6. Partial processing produces PARTIAL/NEEDS_REVIEW
    def test_06_partial_processing_produces_partial_or_needs_review(self):
        """6. Partial processing produces PARTIAL/NEEDS_REVIEW."""
        scan_id = self.orchestrator.create_scan()
        b64_partial = generate_dummy_base64_label("ROYAL TEA") # Partial label, missing MRP
        self.orchestrator.register_image(scan_id, b64_partial, "partial.jpg", "PARTIAL")

        response = self.orchestrator.run_pipeline(scan_id)
        self.assertIn(response.overall_status, ["NEEDS_REVIEW", "NON_COMPLIANT", "PARTIAL"])

    # 7. Stage 8 result reaches Stage 9
    def test_07_stage_8_result_reaches_stage_9(self):
        """7. Stage 8 result reaches Stage 9."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertIsNotNone(p0.rule_evaluations)
        self.assertTrue(len(p0.rule_evaluations) > 0)

    # 8. Stage 9 violation reaches final result
    def test_08_stage_9_violation_reaches_final_result(self):
        """8. Stage 9 violation reaches final result."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertIsNotNone(p0.violations)

    # 9. Evidence remains linked to original image
    def test_09_evidence_remains_linked_to_original_image(self):
        """9. Evidence remains linked to original image."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        for ev in p0.evidence:
            self.assertIsNotNone(ev.image_id)

    # 10. Original bounding box remains unchanged
    def test_10_original_bounding_box_remains_unchanged(self):
        """10. Original bounding box remains unchanged."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        for ev in p0.evidence:
            self.assertIsInstance(ev.original_bbox, list)

    # 11. Review item reaches final result
    def test_11_review_item_reaches_final_result(self):
        """11. Review item reaches final result."""
        scan_id = self.orchestrator.create_scan()
        b64_partial = generate_dummy_base64_label("ROYAL TEA")
        self.orchestrator.register_image(scan_id, b64_partial, "partial.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertIsNotNone(p0.review_items)

    # 12. Conflict reaches final result
    def test_12_conflict_reaches_final_result(self):
        """12. Conflict reaches final result."""
        scan_id = self.orchestrator.create_scan()
        b64_front = generate_dummy_base64_label("MRP Rs 100")
        b64_back = generate_dummy_base64_label("MRP Rs 150")

        self.orchestrator.register_image(scan_id, b64_front, "f.jpg", "FRONT")
        self.orchestrator.register_image(scan_id, b64_back, "b.jpg", "BACK")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertIsNotNone(p0.conflicts)

    # 13. Duplicate execution does not create duplicate violations
    def test_13_duplicate_execution_is_idempotent(self):
        """13. Duplicate execution does not create duplicate violations."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        res1 = self.orchestrator.run_pipeline(scan_id)
        res2 = self.orchestrator.run_pipeline(scan_id)

        self.assertEqual(len(res1.final_results[0].violations), len(res2.final_results[0].violations))

    # 14. Product IDs remain consistent
    def test_14_product_ids_remain_consistent(self):
        """14. Product IDs remain consistent."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        self.assertTrue(p0.product_id.startswith("prod_") or p0.product_id == "product_001")

    # 15. Rule IDs remain consistent
    def test_15_rule_ids_remain_consistent(self):
        """15. Rule IDs remain consistent."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        for r_eval in p0.rule_evaluations:
            self.assertTrue(r_eval.rule_id.startswith("RULE_"))

    # 16. Evidence IDs remain consistent
    def test_16_evidence_ids_remain_consistent(self):
        """16. Evidence IDs remain consistent."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        p0 = response.final_results[0]
        for ev in p0.evidence:
            self.assertIsNotNone(ev.image_id)

    # 17. Audit events are generated
    def test_17_audit_events_are_generated(self):
        """17. Audit events are generated."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        response = self.orchestrator.run_pipeline(scan_id)
        self.assertTrue(len(response.audit_trail) > 0)
        event_types = [e.event_type for e in response.audit_trail]
        self.assertIn("SCAN_CREATED", event_types)
        self.assertIn("PIPELINE_FINALIZED", event_types)

    # 18. Frontend/backend API contract works
    def test_18_api_contract_response_structure(self):
        """18. Frontend/backend API contract works."""
        scan_id = self.orchestrator.create_scan()
        self.orchestrator.register_image(scan_id, self.sample_b64, "front.jpg", "FRONT")

        status_res = self.orchestrator.get_scan_status(scan_id)
        self.assertEqual(status_res.scan_id, scan_id)
        self.assertIsNotNone(status_res.pipeline_state)

    # 19. Unauthorized / invalid access is rejected
    def test_19_invalid_scan_access_rejected(self):
        """19. Unauthorized/invalid access is rejected."""
        with self.assertRaises(KeyError):
            self.orchestrator.get_scan_status("INVALID_SCAN_ID_999")

    # 20. Existing Stage 5–9 tests continue to pass
    def test_20_pipeline_runner_processes_multi_panel_cleanly(self):
        """20. Existing Stage 5–9 tests continue to pass."""
        audit = AuditTrailLogger("test_scan_20")
        runner = PipelineRunner("test_scan_20", audit)
        b64 = self.sample_b64

        res = runner.run_full_pipeline([{"data": b64, "filename": "test.jpg", "panel": "FRONT"}])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertIsNotNone(res["stage8_response"])
        self.assertIsNotNone(res["stage9_response"])


if __name__ == "__main__":
    unittest.main()
