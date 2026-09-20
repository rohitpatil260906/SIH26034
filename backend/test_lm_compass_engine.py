"""
LM-COMPASS: Universal Packaged Commodity Compliance Vision Engine
Automated Compliance Test Suite (Master Prompt Sections 24, 25, 27)

Covers:
1. Section 24: Sunscreen Regression Test (DIRECTIONS != INGREDIENTS != MARKETER != ADDRESS)
   - Zero false "Address Missing PIN" on ingredients or directions
   - Marketer with PIN 560001 recognized cleanly
2. Section 25: Comprehensive 10-Category Packaged Commodity Dataset
   - Category A (Food), Category C (Cosmetics), Category D (Household),
   - Category F (Electronics), Category G (Stationery), Category H (Toys),
   - Category I (Textiles & Footwear), Category J (Hardware), Category P (Imported)
3. Multi-Surface Duplicate Consistency (CONSISTENT vs CONFLICT DETECTED)
4. Evidence-First Bounding Box & Text Validation
5. Section 27: Structured Compliance Dossier Validation
"""

import sys
import os
import unittest

# Ensure workspace root directory is in path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from backend.models import (
    ProductCategory,
    SemanticRegionType,
    UniversalFieldStatus,
    UniversalComplianceStatus,
    StructuredProductData,
    LmCompassResult,
    ComplianceCheckItem,
    CommercialEntity,
    BoundingBox,
)
from backend.services.text_processor import (
    classify_product_category,
    classify_text_block,
    process_and_classify_text,
    fuse_multi_surface_extractions,
    build_lm_compass_dossier,
)
from backend.services.rule_engine import (
    evaluate_legal_metrology_rules,
    validate_violation_evidence,
)


class TestSection24SunscreenRegression(unittest.TestCase):
    """
    CRITICAL SECTION 24 REGRESSION SUITE:
    Under NO circumstances may the engine flag "Address Missing PIN" when the text
    region analyzed contains directions of use, ingredient lists, or product descriptions.
    """

    def setUp(self):
        self.sunscreen_lines = [
            "GlowSun Ultra Matte Daily Sunscreen Gel SPF 50 PA+++",
            "Broad Spectrum UVA/UVB Protection & Very Water Resistant",
            "Direction of Use: Apply liberally and evenly on face and neck 15 minutes before sun exposure.",
            "Reapply every 2 hours or after 80 minutes of swimming or sweating.",
            "Ingredients: Aqua, Ethylhexyl Methoxycinnamate, Octocrylene, Butyl Methoxydibenzoylmethane, Glycerin, Silica, Salicylic Acid, Phenoxyethanol, Fragrance.",
            "Warning: For external use only. Avoid contact with eyes. Discontinue use if irritation occurs.",
            "Net Qty: 50 ml",
            "MRP: Rs. 299.00 (inclusive of all taxes)",
            "Marketed by: Stellar Beauty Care Pvt Ltd, 12th Main, Indiranagar, Bangalore 560001, Karnataka",
            "Consumer Care: Email: care@stellarbeauty.com | Helpline: 1800-123-4567",
            "Country of Origin: India",
            "Batch No: SB-2024-09",
            "Mfg Date: 08/2024",
            "Exp Date: 07/2026",
        ]
        self.raw_text = "\n".join(self.sunscreen_lines)

    def test_semantic_classification_shields_ingredients_and_directions(self):
        """Directions and Ingredients must NEVER be classified as address or commercial entity."""
        dir_line = self.sunscreen_lines[2]
        ing_line = self.sunscreen_lines[4]
        warn_line = self.sunscreen_lines[5]
        mkt_line = self.sunscreen_lines[8]

        dir_cls, dir_conf, _ = classify_text_block(dir_line)
        self.assertEqual(dir_cls, SemanticRegionType.DIRECTIONS)
        self.assertGreaterEqual(dir_conf, 0.95)

        ing_cls, ing_conf, _ = classify_text_block(ing_line)
        self.assertEqual(ing_cls, SemanticRegionType.INGREDIENTS)
        self.assertGreaterEqual(ing_conf, 0.95)

        warn_cls, warn_conf, _ = classify_text_block(warn_line)
        self.assertEqual(warn_cls, SemanticRegionType.WARNING)
        self.assertGreaterEqual(warn_conf, 0.95)

        mkt_cls, mkt_conf, _ = classify_text_block(mkt_line)
        self.assertEqual(mkt_cls, SemanticRegionType.MARKETER)
        self.assertGreaterEqual(mkt_conf, 0.90)

    def test_category_identification_as_cosmetics(self):
        """Sunscreen gel must be classified under Category C — Cosmetics & Personal Care."""
        cat_name, cat_code, cat_conf, _ = classify_product_category(
            self.raw_text
        )
        self.assertEqual(cat_code, "C")
        self.assertIn("Cosmetics", cat_name)
        self.assertGreaterEqual(cat_conf, 0.90)

    def test_zero_false_address_missing_pin_violation(self):
        """
        Engine MUST NOT generate "Address Missing PIN" violation.
        Marketer has valid PIN 560001, and ingredients/directions must not be treated as address.
        """
        data, cfs, ev = process_and_classify_text(
            self.raw_text,
            surface="Back Panel",
        )

        # Marketer must be captured
        self.assertIsNotNone(data.marketer)
        self.assertEqual(data.marketer.pin_code, "560001")
        self.assertEqual(data.postal_pin, "560001")

        # Directions and Ingredients text preserved
        self.assertIsNotNone(data.directions_text)
        self.assertIn("Apply liberally", data.directions_text)
        self.assertIsNotNone(data.ingredients_text)
        self.assertIn("Salicylic Acid", data.ingredients_text)

        # Rule evaluation
        checks, score, status = evaluate_legal_metrology_rules(data, surface="Back Panel")

        # Validate that NO check flags missing PIN as FAIL
        pin_violations = [
            c for c in checks
            if c.status == "FAIL" and (
                "missing pin" in (c.detected_declaration or "").lower() or
                "missing pin" in (c.rule_title or "").lower()
            )
        ]
        self.assertEqual(
            len(pin_violations),
            0,
            f"Expected ZERO missing PIN violations, but got: {pin_violations}",
        )

        # Rule 6(1)(a) check should be NEEDS REVIEW or PASS for officer verification under proviso
        r6_checks = [c for c in checks if "6(1)(a)" in c.rule_no]
        self.assertTrue(len(r6_checks) > 0)
        self.assertIn(
            r6_checks[0].status,
            ["PASS", "NEEDS REVIEW"],
            f"Rule 6(1)(a) status was {r6_checks[0].status}",
        )

    def test_section_27_dossier_structure(self):
        """Build full LM-COMPASS Section 27 compliance dossier and verify schema."""
        data, cfs, ev = process_and_classify_text(
            self.raw_text,
            surface="Back Panel",
        )
        checks, score, status = evaluate_legal_metrology_rules(data, surface="Back Panel")
        dossier = build_lm_compass_dossier(data, cfs, ev, checks, surfaces_processed=["Back Panel"])

        self.assertIsInstance(dossier, LmCompassResult)
        self.assertIn("Category C", dossier.category)
        self.assertIn(dossier.overall_status, ["COMPLIANT", "NEEDS_REVIEW"])
        self.assertGreaterEqual(dossier.overall_confidence, 0.85)
        self.assertTrue(len(dossier.fields) > 5)
        self.assertTrue(len(dossier.compliance) > 5)


class TestSection25Comprehensive10Categories(unittest.TestCase):
    """
    Test dataset across 10 categories described in Master Prompt Section 25.
    Verifies that the engine correctly adapts schema and validates compliance without hallucination.
    """

    def test_01_category_a_food_basmati_rice(self):
        """1. Food: Packaged Basmati Rice (5 kg, FSSAI, Veg logo, Net Qty, MRP, USP)."""
        lines = [
            "Royal Feast Premium Traditional Basmati Rice",
            "Net Weight: 5 kg",
            "MRP: Rs. 450.00 (incl. of all taxes)",
            "USP: Rs. 90.00/kg",
            "Packed by: Royal Agri Foods Pvt Ltd, GT Road, Karnal 132001, Haryana",
            "FSSAI Lic. No. 10019064001234",
            "Date of Packing: 06/2024",
            "Best Before: 24 months from packing",
            "Batch No: RF-RICE-2024-K1",
            "Consumer Care: 1800-200-1122 | care@royalagri.in",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "A")
        data, cfs, ev = process_and_classify_text(text, surface="Front (PDP)")
        self.assertEqual(data.net_quantity.value, 5.0)
        self.assertEqual(data.net_quantity.unit, "kg")
        checks, score, status = evaluate_legal_metrology_rules(data, surface="Front (PDP)")
        self.assertIn(status, ["COMPLIANT", "NEEDS_REVIEW"])

    def test_02_category_c_cosmetic_cream(self):
        """2. Cosmetic: Hydrating Day Cream (50 g, MRP, Batch, MFD, Ingredients)."""
        lines = [
            "LumiSkin Advanced Hydrating Day Cream",
            "Net Weight: 50 g",
            "MRP: Rs. 349.00 (inclusive of all taxes)",
            "Ingredients: Aqua, Glycerin, Cetearyl Alcohol, Dimethicone, Phenoxyethanol",
            "Manufactured by: LumiSkin Cosmetics Pvt Ltd, B-12 Industrial Area, Baddi 173205, HP",
            "Mfg Date: 05/2024 | Use Before: 04/2026",
            "Batch: LSM-50-2024",
            "Consumer Helpline: 1800-889-9900 | help@lumiskin.com",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "C")
        data, cfs, ev = process_and_classify_text(text, surface="Back Panel")
        self.assertEqual(data.net_quantity.value, 50.0)
        self.assertEqual(data.net_quantity.unit, "g")
        checks, score, status = evaluate_legal_metrology_rules(data, surface="Back Panel")
        self.assertIn(status, ["COMPLIANT", "NEEDS_REVIEW"])

    def test_03_category_d_household_cleaner(self):
        """3. Household: Citrus Dishwash Gel (500 ml, Warning, MRP, Mfg)."""
        lines = [
            "SparkleMax Citrus Active Dishwash Gel",
            "Net Content: 500 ml",
            "MRP: Rs. 120.00 (inclusive of all taxes)",
            "USP: Rs. 0.24/ml",
            "Caution: Keep out of reach of children. Avoid contact with eyes.",
            "Manufactured by: Sparkle Care Ltd, Plot 45, GIDC Naroda, Ahmedabad 382330, Gujarat",
            "Batch: SM-DW-0424 | Mfd: 04/2024",
            "Customer Support: care@sparklecare.com",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "D")
        data, cfs, ev = process_and_classify_text(text, surface="Front (PDP)")
        self.assertEqual(data.net_quantity.value, 500.0)
        self.assertEqual(data.net_quantity.unit, "ml")

    def test_04_category_f_electronics_mouse(self):
        """4. Electronics: Ergonomic Wireless Mouse (1 Unit, Dimensions, Importer)."""
        lines = [
            "TechGear Pro Ergonomic Optical Wireless Mouse",
            "Net Quantity: 1 Unit",
            "Package Dimensions: 12.0 cm x 7.5 cm x 4.0 cm",
            "MRP: Rs. 999.00 (inclusive of all taxes)",
            "Imported & Marketed by: TechGear Electronics India Pvt Ltd, MG Road, Gurgaon 122002, Haryana",
            "Month & Year of Import: 07/2024",
            "Country of Origin: Vietnam",
            "Customer Care: support@techgear.in | 0124-4567890",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "F")
        data, cfs, ev = process_and_classify_text(text, surface="Side Panel")
        self.assertEqual(data.country_of_origin, "Vietnam")

    def test_05_category_g_stationery_notebook(self):
        """5. Stationery: Hardbound Ruled Notebook (160 Pages, Dimensions)."""
        lines = [
            "ScholarPrime Deluxe Ruled Journal Notebook",
            "Quantity: 1 N (160 Pages)",
            "Size: 21.0 cm x 29.7 cm (A4)",
            "Paper Density: 70 GSM",
            "MRP: Rs. 150.00 (inclusive of all taxes)",
            "Manufactured by: National Paper Mills Ltd, Paper Town, Bhadravati 577301, Karnataka",
            "Pkd: 03/2024",
            "Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "G")
        data, cfs, ev = process_and_classify_text(text, surface="Back Panel")
        self.assertEqual(data.net_quantity.value, 1.0)
        self.assertEqual(data.net_quantity.unit, "N")
        self.assertEqual(data.mrp.amount, 150.0)
        self.assertEqual(data.manufacturer.pin_code, "577301")

    def test_06_category_h_toys_blocks(self):
        """6. Toys: Creative Building Blocks (50 pcs, Age 3+, BIS ISI mark)."""
        lines = [
            "PlaySmart Mega Creative Brick Set",
            "Net Quantity: 50 Pieces",
            "Warning: Choking hazard - Small parts. Not suitable for children under 3 years.",
            "BIS Certification: ISI Mark CM/L-8765432 per IS 9873",
            "MRP: Rs. 599.00 (inclusive of all taxes)",
            "Manufactured by: FunTime Toys India LLP, Sector 80, Noida 201305, UP",
            "Month & Year of Manufacture: 06/2024",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "H")
        data, cfs, ev = process_and_classify_text(text, surface="Front (PDP)")
        self.assertIsNotNone(data.warnings_text)

    def test_07_category_i_textiles_tshirt(self):
        """7. Textiles: Men's Cotton T-Shirt (Size L, Chest 102 cm, Rule 26(e))."""
        lines = [
            "UrbanStyle Classic Pure Cotton Polo T-Shirt",
            "Net Quantity: 1 N",
            "Size: L (Large)",
            "Chest / Bust Dimension: 102 cm",
            "Fiber Composition: 100% Combed Cotton",
            "MRP: Rs. 799.00 (inclusive of all taxes)",
            "Manufactured & Packed by: TexPrime Apparels, Kangeyam Road, Tirupur 641604, Tamil Nadu",
            "Mfd: 05/2024",
            "Country of Origin: India",
            "Consumer Care: feedback@urbanstyle.in",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "I")
        data, cfs, ev = process_and_classify_text(text, surface="Back Panel")
        self.assertEqual(data.net_quantity.value, 1.0)
        self.assertEqual(data.net_quantity.unit, "N")
        self.assertEqual(data.mrp.amount, 799.0)
        self.assertEqual(data.manufacturer.pin_code, "641604")

    def test_08_category_i_footwear_running_shoes(self):
        """8. Footwear: Sport Running Shoes (UK Size 9, Pair 1 N)."""
        lines = [
            "AeroStride Pro Dynamic Running Shoes",
            "Net Quantity: 1 Pair",
            "Size: UK 9 (Euro 43 / US 10)",
            "MRP: Rs. 2499.00 (inclusive of all taxes)",
            "Manufactured by: AeroStride Footwear Ltd, Industrial Area, Jalandhar 144001, Punjab",
            "Mfg Month: 04/2024",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "I")
        data, cfs, ev = process_and_classify_text(text, surface="Outer Carton")
        self.assertEqual(data.mrp.amount, 2499.0)

    def test_09_category_j_hardware_paint(self):
        """9. Hardware: Premium Acrylic Wall Emulsion (1 L, Batch, Mfg)."""
        lines = [
            "ColorShield All-Weather Exterior Wall Emulsion",
            "Net Volume: 1 L",
            "MRP: Rs. 425.00 (inclusive of all taxes)",
            "USP: Rs. 0.43/ml",
            "Manufactured by: ColorShield Paints India Ltd, Phase IV, Peenya, Bangalore 560058, Karnataka",
            "Batch: CS-EXT-0824 | Mfd: 08/2024",
            "Consumer Grievance: 1800-425-0011 | care@colorshield.com",
            "Country of Origin: India",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "J")
        data, cfs, ev = process_and_classify_text(text, surface="Front (PDP)")
        self.assertEqual(data.net_quantity.value, 1.0)
        self.assertEqual(data.net_quantity.unit.lower(), "l")

    def test_10_category_p_imported_commodity(self):
        """10. Imported: Imported Specialty Packaged Commodity (Product of Spain, Chapter III)."""
        lines = [
            "Hacienda Real Imported Specialty Commodity",
            "Imported Packaged Commodity under Chapter III provisions",
            "Net Volume: 500 ml",
            "MRP: Rs. 850.00 (inclusive of all taxes)",
            "Country of Origin: Spain | Product of Spain",
            "Imported & Marketed by: Mediterranean Imports India Pvt Ltd, Ballard Estate, Mumbai 400001, Maharashtra",
            "Month & Year of Import: 06/2024",
            "Customer Support: care@mediterraneanimports.in",
        ]
        text = "\n".join(lines)
        cat_name, cat_code, _, _ = classify_product_category(text)
        self.assertEqual(cat_code, "P")
        data, cfs, ev = process_and_classify_text(text, surface="Front (PDP)")
        self.assertEqual(data.country_of_origin, "Spain")
        self.assertIsNotNone(data.importer)
        self.assertEqual(data.importer.pin_code, "400001")


class TestMultiSurfaceFusionDuplicateConsistency(unittest.TestCase):
    """
    Verifies multi-panel duplicate consistency logic:
    - Consistent values on PDP and Back panel -> CONSISTENT
    - Conflicting MRP or Quantity values -> CONFLICT DETECTED -> NEEDS REVIEW
    """

    def test_consistent_multi_surface_extractions(self):
        """Front and back panel have identical net quantity and MRP -> CONSISTENT."""
        front_text = "Brand SuperSoap\nNet Qty: 125 g\nMRP: Rs. 65.00 (incl. of all taxes)"
        back_text = (
            "Brand SuperSoap\n"
            "Net Weight: 125 g\n"
            "MRP: Rs. 65.00 (incl. of all taxes)\n"
            "Manufactured by: CleanCare Ltd, Mumbai 400001"
        )

        d_f, cf_f, ev_f = process_and_classify_text(front_text, surface="Front (PDP)")
        d_b, cf_b, ev_b = process_and_classify_text(back_text, surface="Back Panel")

        fused_data, fused_cfs, fused_ev = fuse_multi_surface_extractions([
            (d_f, cf_f, ev_f, "Front (PDP)"),
            (d_b, cf_b, ev_b, "Back Panel")
        ])

        # Check net quantity and MRP
        self.assertEqual(fused_data.net_quantity.value, 125.0)
        self.assertEqual(fused_data.mrp.amount, 65.0)
        self.assertFalse(fused_data.net_quantity.has_contradiction)
        self.assertFalse(fused_data.mrp.has_contradiction)

        # Compliance status
        checks, score, status = evaluate_legal_metrology_rules(fused_data, surface="Front (PDP)")
        dossier = build_lm_compass_dossier(fused_data, fused_cfs, fused_ev, checks, surfaces_processed=["Front (PDP)", "Back Panel"])
        self.assertIn(dossier.overall_status, ["COMPLIANT", "NEEDS_REVIEW"])

    def test_conflicting_multi_surface_extractions(self):
        """Front panel claims 500 g but back panel claims 450 g -> CONFLICT DETECTED."""
        front_text = "SuperMalt Nutrition Drink\nNet Qty: 500 g\nMRP: Rs. 250.00 (incl. of taxes)"
        back_text = (
            "SuperMalt Nutrition Drink\n"
            "Net Weight: 450 g\n"
            "MRP: Rs. 280.00 (incl. of taxes)\n"
            "Manufactured by: MaltFoods Ltd, Pune 411001"
        )

        d_f, cf_f, ev_f = process_and_classify_text(front_text, surface="Front (PDP)")
        d_b, cf_b, ev_b = process_and_classify_text(back_text, surface="Back Panel")

        fused_data, fused_cfs, fused_ev = fuse_multi_surface_extractions([
            (d_f, cf_f, ev_f, "Front (PDP)"),
            (d_b, cf_b, ev_b, "Back Panel")
        ])

        self.assertTrue(fused_data.net_quantity.has_contradiction)
        self.assertTrue(fused_data.mrp.has_contradiction)
        self.assertIn("CONFLICT DETECTED", fused_data.net_quantity.contradiction_note)
        self.assertIn("CONFLICT DETECTED", fused_data.mrp.contradiction_note)

        # Conflict must route checks to NEEDS REVIEW
        checks, score, status = evaluate_legal_metrology_rules(fused_data, surface="Front (PDP)")
        self.assertEqual(status, "NEEDS_REVIEW")


class TestEvidenceFirstValidation(unittest.TestCase):
    """
    Evidence-first violation engine:
    Reject any violation that lacks exact evidence text/bbox or overlaps ingredients/directions.
    """

    def test_reject_pin_violation_when_marketer_has_valid_pin(self):
        """Reject 'Address Missing PIN' if marketer address has valid 6-digit PIN."""
        chk = ComplianceCheckItem(
            rule_no="RULE 6(1)(a)",
            rule_title="Name and address of manufacturer / packer with PIN code",
            sub_rule="Rule 6(1)(a) & Rule 10",
            status="FAIL",
            detected_declaration="Violation: 6-digit postal PIN code missing from manufacturer address",
            statutory_requirement="PIN required",
            font_size_or_unit_check="PIN verification",
            surface="Back Panel"
        )
        data = StructuredProductData(
            product_name="Sample Cream",
            postal_pin="560001",
            marketer=CommercialEntity(
                name="Stellar Beauty Care Pvt Ltd",
                pin_code="560001",
                full_address="12th Main, Bangalore 560001",
                has_valid_pin=True
            )
        )
        validate_violation_evidence([chk], data)
        self.assertEqual(chk.status, "NEEDS REVIEW")
        self.assertNotIn("missing pin", (chk.detected_declaration or "").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
