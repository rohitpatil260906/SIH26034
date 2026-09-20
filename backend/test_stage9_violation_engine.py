"""
Stage 9 Automated Unit Test Suite
=================================
Tests Stage 9: Violation & Evidence Engine.

25 Comprehensive Test Scenarios:
1. Stage 8 NON_COMPLIANT + valid evidence -> CONFIRMED violation.
2. Stage 8 COMPLIANT -> no violation.
3. NOT_VISIBLE -> no confirmed violation.
4. UNKNOWN -> no confirmed violation.
5. NEEDS_REVIEW -> review queue item.
6. CONFLICT -> review/conflict handling.
7. Unverified rule -> no confirmed violation.
8. Missing evidence -> NEEDS_REVIEW.
9. Multiple evidence regions -> one violation with multiple evidence records.
10. Same violation on two panels -> one deduplicated violation.
11. Different violations -> separate violation records.
12. Multiple products -> no cross-product contamination.
13. Ingredients block -> never address violation.
14. Serving size -> never automatically becomes net quantity violation.
15. Technical dimension -> never automatically becomes net quantity violation.
16. Brand -> never automatically becomes manufacturer.
17. Marketer -> never automatically becomes manufacturer.
18. OCR garbage -> never becomes legal evidence.
19. Original bounding box preserved.
20. Rule source/version preserved.
21. Violation fingerprint is deterministic.
22. Evidence confidence is preserved.
23. Unknown severity -> UNCLASSIFIED.
24. Review reason is preserved.
25. Rule trace remains linked.
"""

import unittest
from typing import List, Dict, Any

from backend.models import (
    Stage4ProductIdentity,
    Stage4ValueWithStatus,
    Stage4CategoryInfo,
    Stage4Entity,
    Stage6ProductProfile,
    Stage7UnifiedProduct,
    Stage7UnifiedField,
    Stage7FieldSource,
    Stage7FieldConflict,
    Stage7ConflictCandidate,
    Stage7SourceImage,
    Stage8RuleDefinition,
    Stage8EvidenceItem,
    Stage8RuleTrace,
    Stage8RuleEvaluation,
    Stage8ProductEvaluation,
    Stage9Violation,
    Stage9EvidenceItem,
    Stage9ReviewItem
)
from backend.rules import Stage8RuleEngine
from backend.violations import (
    Stage9ViolationEngine,
    FingerprintEngine,
    EvidenceHighlighter,
    DeduplicationEngine,
    ReviewQueueEngine
)


class TestStage9ViolationEngine(unittest.TestCase):
    def setUp(self):
        self.rule_engine = Stage8RuleEngine()
        self.violation_engine = Stage9ViolationEngine()

    def _create_mock_unified_product(
        self,
        product_id: str = "product_001",
        category: str = "FOOD",
        brand: str = "ROYAL TEA",
        name: str = "ROYAL CHAI TEA",
        fields_dict: Dict[str, str] = None,
        conflicts: List[Stage7FieldConflict] = None,
        entities: List[Stage4Entity] = None
    ) -> Stage7UnifiedProduct:
        fields = []
        if fields_dict:
            for fname, fval in fields_dict.items():
                fields.append(Stage7UnifiedField(
                    field_name=fname,
                    value=fval,
                    status="CONFIRMED",
                    confidence=0.95,
                    sources=[Stage7FieldSource(image_id="img_001", panel="FRONT", region_id="reg_1", bbox=[10, 10, 50, 50], confidence=0.95, raw_text=fval)]
                ))

        return Stage7UnifiedProduct(
            product_id=product_id,
            source_images=[Stage7SourceImage(image_id="img_001", panel="FRONT")],
            identity=Stage4ProductIdentity(
                product_id=product_id,
                product_name=Stage4ValueWithStatus(value=name, status="CONFIRMED", confidence=0.95),
                brand=Stage4ValueWithStatus(value=brand, status="CONFIRMED", confidence=0.95),
                category=Stage4CategoryInfo(value=category, confidence=0.90),
                entities=entities or []
            ),
            category_profile=Stage6ProductProfile(category=category, subcategory="TEA", category_confidence=0.95, category_status="CONFIRMED"),
            fields=fields,
            conflicts=conflicts or [],
            status="MERGED"
        )

    # 1. NON_COMPLIANT + valid evidence -> CONFIRMED violation
    def test_01_non_compliant_with_evidence_creates_confirmed_violation(self):
        """1. Stage 8 NON_COMPLIANT + valid evidence -> CONFIRMED violation."""
        prod = self._create_mock_unified_product(fields_dict={
            "PRODUCT_NAME": "ROYAL CHAI TEA",
            "MANUFACTURER_NAME": "Royal Tea Packers Ltd",
            "MANUFACTURER_ADDRESS": "Assam, India"
            # Missing NET_QUANTITY, MRP, etc.
        })
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertEqual(s9_res.overall_status, "NON_COMPLIANT")
        self.assertTrue(len(s9_res.violations) > 0)
        v0 = s9_res.violations[0]
        self.assertEqual(v0.violation_status, "CONFIRMED")
        self.assertEqual(v0.product_id, "product_001")

    # 2. Stage 8 COMPLIANT -> no violation
    def test_02_compliant_product_has_no_violations(self):
        """2. Stage 8 COMPLIANT -> no violation."""
        prod = self._create_mock_unified_product(fields_dict={
            "PRODUCT_NAME": "ROYAL CHAI TEA",
            "MANUFACTURER_NAME": "Royal Tea Packers Ltd",
            "MANUFACTURER_ADDRESS": "Assam, India",
            "NET_QUANTITY": "500 g",
            "MRP": "₹250",
            "MANUFACTURING_DATE": "01/2024",
            "CONSUMER_CARE": "1800-123-4567",
            "BATCH_NUMBER": "BATCH-001"
        })
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertEqual(s9_res.overall_status, "COMPLIANT")
        self.assertEqual(len(s9_res.violations), 0)
        self.assertEqual(s9_res.summary.confirmed_violations, 0)

    # 3. NOT_VISIBLE -> no confirmed violation
    def test_03_not_visible_creates_no_confirmed_violation(self):
        """3. NOT_VISIBLE -> no confirmed violation."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="MRP", value=None, status="NOT_VISIBLE"))
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mrp_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_MRP"]
        self.assertEqual(len(mrp_viols), 0)
        mrp_reviews = [r for r in s9_res.review_items if r.related_rule_id == "RULE_06_MRP"]
        self.assertTrue(len(mrp_reviews) > 0)

    # 4. UNKNOWN -> no confirmed violation
    def test_04_unknown_creates_no_confirmed_violation(self):
        """4. UNKNOWN -> no confirmed violation."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="MRP", value="Blurry Text", status="UNKNOWN"))
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mrp_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_MRP"]
        self.assertEqual(len(mrp_viols), 0)

    # 5. NEEDS_REVIEW -> review item
    def test_05_needs_review_creates_review_item(self):
        """5. NEEDS_REVIEW -> review queue item."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="NET_QUANTITY", value="500 g", status="NEEDS_REVIEW"))
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertTrue(len(s9_res.review_items) > 0)
        self.assertTrue(any(r.related_rule_id == "RULE_06_NET_QUANTITY" for r in s9_res.review_items))

    # 6. CONFLICT -> review/conflict handling
    def test_06_conflict_creates_review_item(self):
        """6. CONFLICT -> review/conflict handling."""
        conflict = Stage7FieldConflict(
            field_name="MRP",
            status="CONFLICT",
            candidates=[
                Stage7ConflictCandidate(value="₹299", image_id="img_1", panel="FRONT"),
                Stage7ConflictCandidate(value="₹349", image_id="img_2", panel="BACK")
            ]
        )
        prod = self._create_mock_unified_product(conflicts=[conflict])
        prod.fields.append(Stage7UnifiedField(field_name="MRP", status="CONFLICT", candidates=conflict.candidates))

        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mrp_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_MRP"]
        self.assertEqual(len(mrp_viols), 0)
        mrp_reviews = [r for r in s9_res.review_items if r.related_rule_id == "RULE_06_MRP"]
        self.assertTrue(len(mrp_reviews) > 0)
        self.assertEqual(mrp_reviews[0].reason, "CONFLICTING_DECLARATIONS")

    # 7. Unverified rule -> no confirmed violation
    def test_07_unverified_rule_cannot_create_violation(self):
        """7. Unverified rule -> no confirmed violation."""
        unverified_rule = Stage8RuleDefinition(
            rule_id="RULE_UNVERIFIED_99",
            rule_number="RULE 99",
            title="Draft Unverified Requirement",
            requirement_text="Draft text",
            verification_status="UNVERIFIED"
        )
        self.rule_engine.registry.register_rule(unverified_rule)
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEST PRODUCT"})

        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        unv_viols = [v for v in s9_res.violations if v.rule_id == "RULE_UNVERIFIED_99"]
        self.assertEqual(len(unv_viols), 0)

    # 8. Missing evidence -> NEEDS_REVIEW
    def test_08_missing_evidence_results_in_needs_review(self):
        """8. Missing evidence -> NEEDS_REVIEW."""
        s8_eval = Stage8ProductEvaluation(
            product_id="prod_001",
            overall_status="NEEDS_REVIEW",
            evaluations=[
                Stage8RuleEvaluation(
                    rule_id="RULE_06_NET_QUANTITY",
                    rule_number="Rule 6(1)(c)",
                    requirement_title="Net Quantity",
                    applicability_status="APPLICABLE",
                    evaluation_status="NEEDS_REVIEW",
                    confidence=0.50,
                    evidence=[]
                )
            ]
        )
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)
        self.assertEqual(len(s9_res.violations), 0)
        self.assertEqual(len(s9_res.review_items), 1)

    # 9. Multiple evidence regions -> one violation with multiple evidence records
    def test_09_multiple_evidence_regions_consolidated(self):
        """9. Multiple evidence regions -> one violation with multiple evidence records."""
        ev1 = Stage8EvidenceItem(image_id="img_1", panel="FRONT", bbox=[10, 10, 50, 50], observed_text="MRP 100", normalized_value="₹100")
        ev2 = Stage8EvidenceItem(image_id="img_2", panel="BACK", bbox=[20, 20, 60, 60], observed_text="MRP 100", normalized_value="₹100")

        r_eval1 = Stage8RuleEvaluation(
            rule_id="RULE_06_MRP",
            rule_number="Rule 6(1)(e)",
            requirement_title="MRP",
            applicability_status="APPLICABLE",
            evaluation_status="NON_COMPLIANT",
            evidence=[ev1]
        )
        r_eval2 = Stage8RuleEvaluation(
            rule_id="RULE_06_MRP",
            rule_number="Rule 6(1)(e)",
            requirement_title="MRP",
            applicability_status="APPLICABLE",
            evaluation_status="NON_COMPLIANT",
            evidence=[ev2]
        )

        s8_eval = Stage8ProductEvaluation(product_id="prod_001", overall_status="NON_COMPLIANT", evaluations=[r_eval1, r_eval2])
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertEqual(len(s9_res.violations), 1)
        self.assertEqual(len(s9_res.violations[0].evidence), 2)

    # 10. Same violation on two panels -> one deduplicated violation
    def test_10_same_violation_on_two_panels_deduplicated(self):
        """10. Same violation on two panels -> one deduplicated violation."""
        v1 = Stage9Violation(
            violation_id="v1", product_id="p1", rule_id="RULE_06_MRP", rule_number="Rule 6(1)(e)",
            requirement="MRP", violation_type="PRICE_DECLARATION_ISSUE", description="MRP issue",
            expected_condition="MRP", fingerprint="fp_mrp_100", evidence=[Stage9EvidenceItem(image_id="img_1", panel="FRONT")]
        )
        v2 = Stage9Violation(
            violation_id="v2", product_id="p1", rule_id="RULE_06_MRP", rule_number="Rule 6(1)(e)",
            requirement="MRP", violation_type="PRICE_DECLARATION_ISSUE", description="MRP issue",
            expected_condition="MRP", fingerprint="fp_mrp_100", evidence=[Stage9EvidenceItem(image_id="img_2", panel="BACK")]
        )

        deduped = DeduplicationEngine.deduplicate_violations([v1, v2])
        self.assertEqual(len(deduped), 1)
        self.assertEqual(len(deduped[0].evidence), 2)

    # 11. Different violations -> separate violation records
    def test_11_different_violations_remain_separate(self):
        """11. Different violations -> separate violation records."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "ROYAL CHAI TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        rule_ids = [v.rule_id for v in s9_res.violations]
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue(len(s9_res.violations) > 1)

    # 12. Multiple products -> no cross-product contamination
    def test_12_multiple_products_remain_strictly_isolated(self):
        """12. Multiple products -> no cross-product contamination."""
        p1 = self._create_mock_unified_product(product_id="prod_A", name="TEA A", fields_dict={"PRODUCT_NAME": "TEA A"})
        p2 = self._create_mock_unified_product(product_id="prod_B", name="TEA B", fields_dict={"PRODUCT_NAME": "TEA B"})

        pe1 = self.rule_engine.evaluate_product(p1)
        pe2 = self.rule_engine.evaluate_product(p2)

        s9_res = self.violation_engine.evaluate_session_violations("sess_multi", [pe1, pe2])
        self.assertEqual(len(s9_res.product_results), 2)
        self.assertEqual(s9_res.product_results[0].product_id, "prod_A")
        self.assertEqual(s9_res.product_results[1].product_id, "prod_B")

        for v in s9_res.product_results[0].violations:
            self.assertEqual(v.product_id, "prod_A")
        for v in s9_res.product_results[1].violations:
            self.assertEqual(v.product_id, "prod_B")

    # 13. Ingredients block -> never address violation
    def test_13_ingredient_block_never_triggers_address_violation(self):
        """13. Ingredients block -> never address violation."""
        prod = self._create_mock_unified_product(fields_dict={
            "MANUFACTURER_NAME": "Royal Nutrients Ltd",
            "INGREDIENTS": "Aqua, Salt, Protein 10g, Assam 781001"
        })
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mfg_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NAME_ADDRESS"]
        self.assertTrue(len(mfg_viols) > 0)
        self.assertEqual(mfg_viols[0].violation_type, "ENTITY_INFORMATION_ISSUE")

    # 14. Serving size -> never automatically becomes net quantity violation
    def test_14_serving_size_never_treated_as_net_quantity(self):
        """14. Serving size -> never automatically becomes net quantity violation."""
        prod = self._create_mock_unified_product(fields_dict={"SERVING_SIZE": "50 g"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        nq_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NET_QUANTITY"]
        self.assertTrue(len(nq_viols) > 0)
        self.assertEqual(nq_viols[0].observed_value, None)

    # 15. Technical dimension -> never automatically becomes net quantity violation
    def test_15_technical_dimension_never_treated_as_net_quantity(self):
        """15. Technical dimension -> never automatically becomes net quantity violation."""
        prod = self._create_mock_unified_product(category="HARDWARE", fields_dict={"DIMENSION": "10 mm"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        nq_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NET_QUANTITY"]
        self.assertTrue(len(nq_viols) > 0)
        self.assertEqual(nq_viols[0].observed_value, None)

    # 16. Brand -> never automatically becomes manufacturer
    def test_16_brand_never_becomes_manufacturer(self):
        """16. Brand -> never automatically becomes manufacturer."""
        prod = self._create_mock_unified_product(brand="ROYAL BRAND", fields_dict={"BRAND": "ROYAL BRAND"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mfg_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NAME_ADDRESS"]
        self.assertTrue(len(mfg_viols) > 0)

    # 17. Marketer -> never automatically becomes manufacturer
    def test_17_marketer_never_becomes_manufacturer(self):
        """17. Marketer -> never automatically becomes manufacturer."""
        prod = self._create_mock_unified_product(entities=[Stage4Entity(role="MARKETER", name="Marketer Corp Ltd")])
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mfg_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NAME_ADDRESS"]
        self.assertTrue(len(mfg_viols) > 0)

    # 18. OCR garbage -> never becomes legal evidence
    def test_18_ocr_garbage_never_becomes_legal_evidence(self):
        """18. OCR garbage -> never becomes legal evidence."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="NET_QUANTITY", value="$$--GARBAGE--$$", status="NEEDS_REVIEW"))
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        nq_viols = [v for v in s9_res.violations if v.rule_id == "RULE_06_NET_QUANTITY"]
        self.assertEqual(len(nq_viols), 0)

    # 19. Original bounding box preserved
    def test_19_original_bounding_box_preserved(self):
        """19. Original bounding box preserved."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        for v in s9_res.violations:
            for ev in v.evidence:
                self.assertIsInstance(ev.original_bbox, list)
                if ev.original_bbox:
                    self.assertEqual(len(ev.original_bbox), 4)

    # 20. Rule source/version preserved
    def test_20_rule_source_and_version_preserved(self):
        """20. Rule source/version preserved."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertTrue(len(s9_res.violations) > 0)
        v0 = s9_res.violations[0]
        self.assertIsNotNone(v0.rule_source)
        self.assertEqual(v0.rule_version, "2024.1")

    # 21. Violation fingerprint is deterministic
    def test_21_violation_fingerprint_is_deterministic(self):
        """21. Violation fingerprint is deterministic."""
        fp1 = FingerprintEngine.generate_fingerprint("p1", "RULE_06_MRP", "PRICE_DECLARATION_ISSUE", "100")
        fp2 = FingerprintEngine.generate_fingerprint("p1", "RULE_06_MRP", "PRICE_DECLARATION_ISSUE", "100")
        fp3 = FingerprintEngine.generate_fingerprint("p1", "RULE_06_MRP", "PRICE_DECLARATION_ISSUE", "200")

        self.assertEqual(fp1, fp2)
        self.assertNotEqual(fp1, fp3)

    # 22. Evidence confidence is preserved
    def test_22_evidence_confidence_preserved(self):
        """22. Evidence confidence is preserved."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertTrue(len(s9_res.violations) > 0)
        v0 = s9_res.violations[0]
        self.assertTrue(v0.confidence > 0.0)

    # 23. Unknown severity -> UNCLASSIFIED
    def test_23_unknown_severity_becomes_unclassified(self):
        """23. Unknown severity -> UNCLASSIFIED."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        for v in s9_res.violations:
            self.assertEqual(v.severity, "UNCLASSIFIED")

    # 24. Review reason is preserved
    def test_24_review_reason_preserved(self):
        """24. Review reason is preserved."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="MRP", status="CONFLICT"))
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        mrp_reviews = [r for r in s9_res.review_items if r.related_rule_id == "RULE_06_MRP"]
        self.assertTrue(len(mrp_reviews) > 0)
        self.assertEqual(mrp_reviews[0].reason, "CONFLICTING_DECLARATIONS")

    # 25. Rule trace remains linked
    def test_25_rule_trace_remains_linked(self):
        """25. Rule trace remains linked."""
        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEA"})
        s8_eval = self.rule_engine.evaluate_product(prod)
        s9_res = self.violation_engine.evaluate_product_violations(s8_eval)

        self.assertTrue(len(s9_res.violations) > 0)
        v0 = s9_res.violations[0]
        self.assertTrue(v0.rule_id in [t.rule_id for t in s8_eval.rule_traces])


if __name__ == "__main__":
    unittest.main()
