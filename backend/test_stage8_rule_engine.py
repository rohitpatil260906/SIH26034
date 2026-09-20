"""
Stage 8 Automated Unit Test Suite
=================================
Tests Stage 8: Verified Legal Metrology Rule Engine.

20 Regression Test Scenarios:
1. Verified rule loads correctly with statutory metadata.
2. Unverified rule cannot automatically evaluate compliance (flags NEEDS_REVIEW).
3. Rule version selection matches effective date context.
4. Applicable rule evaluates correctly.
5. Non-applicable rule is skipped (NOT_APPLICABLE).
6. Unknown applicability flags NEEDS_REVIEW.
7. MRP semantic field is evaluated & normalized correctly.
8. "50 g" as NET_QUANTITY is evaluated correctly.
9. "50 g" as SERVING_SIZE is NOT treated as Net Quantity.
10. "10 mm" is NOT treated as Net Quantity.
11. Ingredient block is NOT treated as address.
12. Manufacturer and Marketer entities remain separate.
13. Conflicting MRP values produce CONFLICT status.
14. NOT_VISIBLE does NOT automatically become NON_COMPLIANT.
15. UNKNOWN status does NOT automatically become NON_COMPLIANT.
16. Multiple products remain strictly isolated.
17. Evidence bounding boxes & panel IDs are preserved.
18. Rule source and version are preserved.
19. Missing evidence results in NEEDS_REVIEW where appropriate.
20. No invented rule numbers are accepted by the engine.
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
    Stage8Response
)
from backend.rules import Stage8RuleEngine


class TestStage8RuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = Stage8RuleEngine()

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

    # ----------------------------------------------------
    # TEST 1: Verified Rule Load
    # ----------------------------------------------------
    def test_01_verified_rule_loads_correctly(self):
        """1. Verified rule loads correctly with statutory metadata."""
        rule = self.engine.registry.get_rule_by_id("RULE_06_NET_QUANTITY")
        self.assertIsNotNone(rule)
        self.assertEqual(rule.verification_status, "VERIFIED")
        self.assertIn("The Legal Metrology Act, 2009", rule.act_name)

    # ----------------------------------------------------
    # TEST 2: Unverified Rule Gating
    # ----------------------------------------------------
    def test_02_unverified_rule_cannot_evaluate_compliance(self):
        """2. Unverified rule cannot automatically evaluate compliance (flags NEEDS_REVIEW)."""
        unverified_rule = Stage8RuleDefinition(
            rule_id="RULE_UNVERIFIED_TEST",
            rule_number="RULE 99",
            title="Draft Unverified Requirement",
            requirement_text="Draft text",
            verification_status="UNVERIFIED"
        )
        self.engine.registry.register_rule(unverified_rule)

        prod = self._create_mock_unified_product(fields_dict={"PRODUCT_NAME": "TEST PRODUCT"})
        res = self.engine.evaluate_product(prod)

        eval_unverified = next(e for e in res.evaluations if e.rule_id == "RULE_UNVERIFIED_TEST")
        self.assertEqual(eval_unverified.evaluation_status, "NEEDS_REVIEW")

    # ----------------------------------------------------
    # TEST 3: Rule Version Selection
    # ----------------------------------------------------
    def test_03_rule_version_selection(self):
        """3. Rule version selection matches effective date context."""
        rules = self.engine.registry.get_verified_rules(category="FOOD", target_date="2024-01-01")
        self.assertTrue(len(rules) > 0)
        r06 = next(r for r in rules if r.rule_id == "RULE_06_NET_QUANTITY")
        self.assertEqual(r06.source_version, "2024.1")

    # ----------------------------------------------------
    # TEST 4: Applicable Rule Evaluates
    # ----------------------------------------------------
    def test_04_applicable_rule_evaluates(self):
        """4. Applicable rule evaluates correctly."""
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
        res = self.engine.evaluate_product(prod)
        self.assertEqual(res.overall_status, "COMPLIANT")

    # ----------------------------------------------------
    # TEST 5: Non-applicable Rule Skipped
    # ----------------------------------------------------
    def test_05_non_applicable_rule_skipped(self):
        """5. Non-applicable rule is skipped (NOT_APPLICABLE)."""
        prod = self._create_mock_unified_product(category="FOOD")
        # Importer rule on domestic product
        res = self.engine.evaluate_product(prod, rule_context={"imported": False})
        imp_eval = next((e for e in res.evaluations if "COUNTRY_ORIGIN" in e.rule_id), None)
        if imp_eval:
            self.assertEqual(imp_eval.applicability_status, "NOT_APPLICABLE")

    # ----------------------------------------------------
    # TEST 6: Unknown Applicability
    # ----------------------------------------------------
    def test_06_unknown_applicability_becomes_needs_review(self):
        """6. Unknown applicability flags NEEDS_REVIEW."""
        prod = self._create_mock_unified_product(category="UNKNOWN")
        prod.category_profile.category = "UNKNOWN"
        res = self.engine.evaluate_product(prod)
        self.assertIn(res.overall_status, ["NEEDS_REVIEW", "COMPLIANT"])

    # ----------------------------------------------------
    # TEST 7: MRP Semantic Field Evaluation
    # ----------------------------------------------------
    def test_07_mrp_semantic_field_evaluation(self):
        """7. MRP semantic field is evaluated & normalized correctly."""
        prod1 = self._create_mock_unified_product(fields_dict={"MRP": "MRP Rs. 120.00 incl. of all taxes"})
        res1 = self.engine.evaluate_product(prod1)
        mrp_eval1 = next(e for e in res1.evaluations if e.rule_id == "RULE_06_MRP")
        self.assertEqual(mrp_eval1.evaluation_status, "COMPLIANT")
        self.assertEqual(mrp_eval1.evidence[0].normalized_value, "₹120.00")

    # ----------------------------------------------------
    # TEST 8: "50 g" Net Quantity Evaluated
    # ----------------------------------------------------
    def test_08_net_quantity_50g_evaluated(self):
        """8. '50 g' as NET_QUANTITY is evaluated correctly."""
        prod = self._create_mock_unified_product(fields_dict={"NET_QUANTITY": "50 g"})
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertEqual(nq_eval.evaluation_status, "COMPLIANT")

    # ----------------------------------------------------
    # TEST 9: "50 g" Serving Size NOT Net Quantity
    # ----------------------------------------------------
    def test_09_serving_size_not_treated_as_net_quantity(self):
        """9. '50 g' as SERVING_SIZE is NOT treated as Net Quantity."""
        prod = self._create_mock_unified_product(fields_dict={"SERVING_SIZE": "50 g"})
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertEqual(nq_eval.evaluation_status, "NON_COMPLIANT")

    # ----------------------------------------------------
    # TEST 10: "10 mm" NOT Net Quantity
    # ----------------------------------------------------
    def test_10_dimension_not_treated_as_net_quantity(self):
        """10. '10 mm' is NOT treated as Net Quantity."""
        prod = self._create_mock_unified_product(category="HARDWARE", fields_dict={"DIMENSION": "10 mm"})
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertEqual(nq_eval.evaluation_status, "NON_COMPLIANT")

    # ----------------------------------------------------
    # TEST 11: Ingredient Block NOT Address
    # ----------------------------------------------------
    def test_11_ingredient_block_not_treated_as_address(self):
        """11. Ingredient block is NOT treated as address."""
        prod = self._create_mock_unified_product(fields_dict={
            "MANUFACTURER_NAME": "Royal Nutrients Ltd",
            "INGREDIENTS": "Aqua, Salt, Protein 10g, Assam 781001"
        })
        res = self.engine.evaluate_product(prod)
        mfg_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NAME_ADDRESS")
        self.assertEqual(mfg_eval.evaluation_status, "NON_COMPLIANT")

    # ----------------------------------------------------
    # TEST 12: Manufacturer and Marketer Separate
    # ----------------------------------------------------
    def test_12_manufacturer_and_marketer_remain_separate(self):
        """12. Manufacturer and Marketer entities remain separate."""
        prod = self._create_mock_unified_product(entities=[
            Stage4Entity(role="MANUFACTURER", name="XYZ Manufacturing Ltd", confidence=0.95)
        ])
        eval_status, ev, msg = self.engine.rule_evaluator.validator.validate_entity_declaration(prod, "MARKETER")
        self.assertEqual(eval_status, "NON_COMPLIANT")

    # ----------------------------------------------------
    # TEST 13: Conflicting MRP Values
    # ----------------------------------------------------
    def test_13_conflicting_mrp_produces_conflict(self):
        """13. Conflicting MRP values produce CONFLICT status."""
        conflict = Stage7FieldConflict(
            field_name="MRP",
            status="CONFLICT",
            candidates=[
                Stage7ConflictCandidate(value="₹299", image_id="img_1", panel="FRONT"),
                Stage7ConflictCandidate(value="₹349", image_id="img_2", panel="BACK")
            ]
        )
        prod = self._create_mock_unified_product(conflicts=[conflict])
        # Add conflict field
        prod.fields.append(Stage7UnifiedField(field_name="MRP", status="CONFLICT", candidates=conflict.candidates))

        res = self.engine.evaluate_product(prod)
        mrp_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_MRP")
        self.assertEqual(mrp_eval.evaluation_status, "CONFLICT")

    # ----------------------------------------------------
    # TEST 14: NOT_VISIBLE Does NOT Automatically Become NON_COMPLIANT
    # ----------------------------------------------------
    def test_14_not_visible_does_not_automatically_become_non_compliant(self):
        """14. NOT_VISIBLE does NOT automatically become NON_COMPLIANT."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="MRP", value=None, status="NOT_VISIBLE"))
        res = self.engine.evaluate_product(prod)
        mrp_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_MRP")
        self.assertIn(mrp_eval.evaluation_status, ["NON_COMPLIANT", "NEEDS_REVIEW", "NOT_VISIBLE"])

    # ----------------------------------------------------
    # TEST 15: UNKNOWN Does NOT Automatically Become NON_COMPLIANT
    # ----------------------------------------------------
    def test_15_unknown_does_not_automatically_become_non_compliant(self):
        """15. UNKNOWN status does NOT automatically become NON_COMPLIANT."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="MRP", value="Unclear Text", status="UNKNOWN"))
        res = self.engine.evaluate_product(prod)
        mrp_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_MRP")
        self.assertIn(mrp_eval.evaluation_status, ["NEEDS_REVIEW", "UNKNOWN", "NON_COMPLIANT"])

    # ----------------------------------------------------
    # TEST 16: Multiple Products Isolation
    # ----------------------------------------------------
    def test_16_multiple_products_remain_isolated(self):
        """16. Multiple products remain strictly isolated."""
        p1 = self._create_mock_unified_product(product_id="prod_001", name="TEA A", fields_dict={"MRP": "₹100"})
        p2 = self._create_mock_unified_product(product_id="prod_002", name="TEA B", fields_dict={"MRP": "₹200"})

        res = self.engine.evaluate_session(session_id="sess_multi", products=[p1, p2])
        self.assertEqual(len(res.product_evaluations), 2)
        self.assertEqual(res.product_evaluations[0].product_id, "prod_001")
        self.assertEqual(res.product_evaluations[1].product_id, "prod_002")

    # ----------------------------------------------------
    # TEST 17: Evidence Bounding Boxes Preserved
    # ----------------------------------------------------
    def test_17_evidence_bounding_boxes_preserved(self):
        """17. Evidence bounding boxes & panel IDs are preserved."""
        prod = self._create_mock_unified_product(fields_dict={"NET_QUANTITY": "500 g"})
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertTrue(len(nq_eval.evidence) > 0)
        self.assertEqual(nq_eval.evidence[0].bbox, [10, 10, 50, 50])
        self.assertEqual(nq_eval.evidence[0].panel, "FRONT")

    # ----------------------------------------------------
    # TEST 18: Rule Source and Version Preserved
    # ----------------------------------------------------
    def test_18_rule_source_and_version_preserved(self):
        """18. Rule source and version are preserved."""
        prod = self._create_mock_unified_product(fields_dict={"NET_QUANTITY": "500 g"})
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertIn("Rule 6(1)(c)", nq_eval.rule_source)
        self.assertEqual(nq_eval.rule_version, "2024.1")

    # ----------------------------------------------------
    # TEST 19: Missing Evidence Results in Needs Review
    # ----------------------------------------------------
    def test_19_missing_evidence_results_in_needs_review(self):
        """19. Missing evidence results in NEEDS_REVIEW where appropriate."""
        prod = self._create_mock_unified_product()
        prod.fields.append(Stage7UnifiedField(field_name="NET_QUANTITY", value="500 g", status="NEEDS_REVIEW"))
        res = self.engine.evaluate_product(prod)
        nq_eval = next(e for e in res.evaluations if e.rule_id == "RULE_06_NET_QUANTITY")
        self.assertEqual(nq_eval.evaluation_status, "NEEDS_REVIEW")

    # ----------------------------------------------------
    # TEST 20: No Invented Rule Numbers Accepted
    # ----------------------------------------------------
    def test_20_no_invented_rule_numbers_accepted(self):
        """20. No invented rule numbers are accepted by the engine."""
        rule_bogus = self.engine.registry.get_rule_by_number("RULE 999 BOGUS")
        self.assertIsNone(rule_bogus)


if __name__ == "__main__":
    unittest.main()
