"""
Comprehensive General Product-Compliance Test Suite for LM-COMPASS
Verifies that the inspection and legal compliance engine correctly processes
DIFFERENT TYPES OF PRE-PACKAGED PRODUCTS without hardcoded brand rules.

Test Cases:
1. Clear Compliant Food Product (Tata Gold Tea) -> COMPLIANT
2. Clear Non-Compliant Food Product (Prohibited 'gms', missing taxes, missing PIN) -> NON_COMPLIANT
3. Clear Compliant Personal Care / Cosmetic (Shampoo) -> COMPLIANT
4. Suboptimal / Degraded Blurry Image -> Flagged as NEEDS_REVIEW, zero false FAILs
5. Spatial MRP & Tax Statement Separation (MRP on Line 1, tax statement on Line 2) -> Verified PASS
6. Separated Consumer Care Details Block -> Verified & Extracted
7. Bilingual Hindi & English Product Label -> Successfully Extracted & COMPLIANT
8. Rule 26(a) Micro-Package Exemption (<= 10g sachet) -> Exempted, not penalized
9. Rule 26(e) Readymade Garment Exemption (Chest/Waist in cm) -> Garment rule active
10. Rule 6(1) Proviso Electronic Product (QR Code framework) -> Electronic rule active
11. OCR Engine Disagreement on MRP Amount -> Triggers NEEDS REVIEW
12. Pan Masala Micro-Package Barred from Rule 26(a) Exemption -> Full declarations required
13. Missing Mandatory Tax Phrase '(inclusive of all taxes)' -> Fails Rule 6(1)(e)
14. Non-Standard Prohibited Unit ('kgs') -> Fails Rule 13
"""

import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import (
    StructuredProductData,
    AddressInfo,
    NetQuantityInfo,
    MrpInfo,
    DateInfo,
    ConsumerCareInfo,
    ExtractedLine,
    BoundingBox
)
from backend.services.text_processor import process_and_classify_text
from backend.services.rule_engine import evaluate_legal_metrology_rules
from backend.services.ocr_engine import verify_ocr_ensemble_and_disagreement

def run_general_compliance_suite():
    print("=" * 70)
    print("LM-COMPASS GENERAL MULTI-PRODUCT COMPLIANCE TEST SUITE")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = 22

    # -------------------------------------------------------------------------
    # TEST 1: Clear Compliant Food Product
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Clear Compliant Food Product (Tata Gold Tea 500g)")
    lines_1 = [
        ExtractedLine(line_index=1, text="TATA TEA GOLD PREMIUM BLACK TEA", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Quantity: 500 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=40, height=5)),
        ExtractedLine(line_index=3, text="MRP Rs. 260.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=60, height=5)),
        ExtractedLine(line_index=4, text="Mfd: 10/2024", confidence=0.95, bbox=BoundingBox(x=10, y=40, width=30, height=5)),
        ExtractedLine(line_index=5, text="Best Before: 10/2025", confidence=0.95, bbox=BoundingBox(x=10, y=50, width=35, height=5)),
        ExtractedLine(line_index=6, text="Batch No: B-94812", confidence=0.95, bbox=BoundingBox(x=10, y=60, width=30, height=5)),
        ExtractedLine(line_index=7, text="Manufactured by: Tata Consumer Products Ltd, Kirloskar Park, Bengaluru, Karnataka - 560024", confidence=0.96, bbox=BoundingBox(x=10, y=70, width=80, height=6)),
        ExtractedLine(line_index=8, text="Consumer Care Helpline: 1800-108-4488, Email: care@tataconsumer.com", confidence=0.97, bbox=BoundingBox(x=10, y=80, width=80, height=5)),
        ExtractedLine(line_index=9, text="Country of Origin: India", confidence=0.98, bbox=BoundingBox(x=10, y=90, width=40, height=5))
    ]
    data_1, _, _ = process_and_classify_text(lines_1, "\n".join([l.text for l in lines_1]))
    checks_1, score_1, status_1 = evaluate_legal_metrology_rules(data_1, "Front (PDP)", is_image_degraded=False)
    print(f" -> Overall Status: {status_1} | Score: {score_1}%")
    assert status_1 == "COMPLIANT", f"Expected COMPLIANT, got {status_1}"
    assert score_1 >= 90
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 2: Clear Non-Compliant Food Product (Multiple Infractions)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Clear Non-Compliant Food Product (Prohibited 'gms', missing taxes, missing PIN)")
    lines_2 = [
        ExtractedLine(line_index=1, text="HERITAGE KACHI GHANI MUSTARD OIL", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Content: 500 gms", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=40, height=5)),  # Violation: gms
        ExtractedLine(line_index=3, text="M.R.P. : Rs. 145.00", confidence=0.98, bbox=BoundingBox(x=10, y=30, width=40, height=5)),     # Violation: missing taxes phrase
        ExtractedLine(line_index=4, text="Pkd: 05/2024", confidence=0.95, bbox=BoundingBox(x=10, y=40, width=30, height=5)),
        ExtractedLine(line_index=5, text="Packed by: Heritage Agro Ltd, Industrial Area, Rewari, Haryana", confidence=0.95, bbox=BoundingBox(x=10, y=50, width=80, height=6)),  # Violation: missing PIN
        ExtractedLine(line_index=6, text="Customer Helpline: 011-23849102", confidence=0.96, bbox=BoundingBox(x=10, y=60, width=50, height=5))
    ]
    data_2, _, _ = process_and_classify_text(lines_2, "\n".join([l.text for l in lines_2]))
    checks_2, score_2, status_2 = evaluate_legal_metrology_rules(data_2, "Front (PDP)", is_image_degraded=False)
    print(f" -> Overall Status: {status_2} | Score: {score_2}%")
    fail_rules = [c.rule_no for c in checks_2 if c.status == "FAIL"]
    print(f" -> Detected Violations: {fail_rules}")
    assert status_2 == "NON_COMPLIANT", f"Expected NON_COMPLIANT, got {status_2}"
    assert "RULE 6(1)(a)" in fail_rules  # Missing PIN
    assert "RULE 6(1)(e)" in fail_rules  # Missing taxes phrase
    assert "RULE 13" in fail_rules       # Non-standard unit 'gms'
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 3: Clear Compliant Personal Care / Cosmetic (Shampoo)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Clear Compliant Cosmetic (Herbal Shampoo 200ml)")
    lines_3 = [
        ExtractedLine(line_index=1, text="BOTANICAL NOURISHING HAIR SHAMPOO", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Vol: 200 ml", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5)),
        ExtractedLine(line_index=3, text="MRP ₹ 199.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5)),
        ExtractedLine(line_index=4, text="Mfd: 03/2025", confidence=0.96, bbox=BoundingBox(x=10, y=40, width=30, height=5)),
        ExtractedLine(line_index=5, text="Batch: SH-2025-01", confidence=0.96, bbox=BoundingBox(x=10, y=50, width=35, height=5)),
        ExtractedLine(line_index=6, text="Mfd by: BioCare Organics India, Sector 4, Baddi, HP - 173205", confidence=0.95, bbox=BoundingBox(x=10, y=60, width=80, height=5)),
        ExtractedLine(line_index=7, text="Consumer Care: 1800-444-2200 • support@biocare.in", confidence=0.97, bbox=BoundingBox(x=10, y=70, width=80, height=5)),
        ExtractedLine(line_index=8, text="Country of Origin: India", confidence=0.98, bbox=BoundingBox(x=10, y=80, width=40, height=5))
    ]
    data_3, _, _ = process_and_classify_text(lines_3, "\n".join([l.text for l in lines_3]))
    checks_3, score_3, status_3 = evaluate_legal_metrology_rules(data_3, "Front (PDP)", is_image_degraded=False)
    print(f" -> Overall Status: {status_3} | Score: {score_3}%")
    assert status_3 == "COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 4: Suboptimal / Degraded Blurry Image Safeguard
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Degraded Blurry Image (Zero False Violations Guarantee)")
    degraded_data = StructuredProductData(
        product_name="Generic Commodity",
        commodity_name="Packaged Item",
        net_quantity=NetQuantityInfo(raw_text="100 g", value=100.0, unit="g")
        # Missing MRP, Mfg date, Consumer care, Manufacturer address
    )
    deg_checks, deg_score, deg_status = evaluate_legal_metrology_rules(degraded_data, surface="Front (PDP)", is_image_degraded=True)
    print(f" -> Overall Status: {deg_status} | Score: {deg_score}%")
    false_fails = [c for c in deg_checks if c.status == "FAIL"]
    review_checks = [c for c in deg_checks if c.status == "NEEDS REVIEW"]
    print(f" -> False Violation FAIL count: {len(false_fails)} | Flagged for Physical Review: {len(review_checks)}")
    assert len(false_fails) == 0, "A degraded image must NEVER convict a vendor with false violation FAILs"
    assert deg_status == "NEEDS_REVIEW"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 5: Spatial MRP & Tax Statement Separation
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Spatial Separation: MRP on Line 1, '(incl. of all taxes)' on Line 2 in Coding Area")
    lines_5 = [
        ExtractedLine(line_index=1, text="CRISP DELIGHT BISCUITS", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Wt: 200 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=30, height=5)),
        ExtractedLine(line_index=3, text="MRP Rs. 40.00", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=35, height=5)),
        ExtractedLine(line_index=4, text="(incl. of all taxes)", confidence=0.97, bbox=BoundingBox(x=10, y=35, width=40, height=4)),  # Separated line directly below
        ExtractedLine(line_index=5, text="Mfd: 09/2024", confidence=0.95, bbox=BoundingBox(x=10, y=45, width=30, height=5)),
        ExtractedLine(line_index=6, text="Packed by: Baker Foods Ltd, Sector 2, Manesar, Haryana - 122050", confidence=0.96, bbox=BoundingBox(x=10, y=55, width=80, height=5)),
        ExtractedLine(line_index=7, text="Helpline: 1800-222-111, Email: help@bakerfoods.com", confidence=0.97, bbox=BoundingBox(x=10, y=65, width=70, height=5))
    ]
    data_5, _, _ = process_and_classify_text(lines_5, "\n".join([l.text for l in lines_5]))
    print(f" -> Extracted MRP: '{data_5.mrp.raw_text}' | Complies Tax Phrase: {data_5.mrp.complies_tax_phrase}")
    assert data_5.mrp.amount == 40.0
    assert data_5.mrp.complies_tax_phrase is True
    checks_5, _, status_5 = evaluate_legal_metrology_rules(data_5, "Front (PDP)", is_image_degraded=False)
    mrp_check = next(c for c in checks_5 if c.rule_no == "RULE 6(1)(e)")
    assert mrp_check.status == "PASS"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 6: Separated Consumer Care Details Block
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Consumer Care Details in Dedicated Secondary Panel")
    lines_6 = [
        ExtractedLine(line_index=1, text="INSTANT NOODLES MASALA", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Weight: 70 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5)),
        ExtractedLine(line_index=3, text="MRP Rs. 14.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=60, height=5)),
        ExtractedLine(line_index=4, text="For queries/feedback, contact Consumer Care Executive:", confidence=0.95, bbox=BoundingBox(x=10, y=70, width=80, height=5)),
        ExtractedLine(line_index=5, text="Toll Free No: 1800-103-1947", confidence=0.98, bbox=BoundingBox(x=10, y=76, width=50, height=5)),
        ExtractedLine(line_index=6, text="Email Address: feedback@nourishfoods.in", confidence=0.98, bbox=BoundingBox(x=10, y=82, width=60, height=5)),
        ExtractedLine(line_index=7, text="Manufactured by: Nourish Foods Ltd, Industrial Estate, Pune, Maharashtra - 411018", confidence=0.96, bbox=BoundingBox(x=10, y=90, width=80, height=5))
    ]
    data_6, _, _ = process_and_classify_text(lines_6, "\n".join([l.text for l in lines_6]))
    print(f" -> Phone: {data_6.consumer_care.phone} | Email: {data_6.consumer_care.email}")
    assert data_6.consumer_care.phone == "1800-103-1947"
    assert data_6.consumer_care.email == "feedback@nourishfoods.in"
    checks_6, _, status_6 = evaluate_legal_metrology_rules(data_6, "Front (PDP)", is_image_degraded=False)
    cc_check = next(c for c in checks_6 if c.rule_no == "RULE 6(1)(f)")
    assert cc_check.status == "PASS"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 7: Bilingual Hindi & English Product Label
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Bilingual Hindi & English Packaging Label")
    lines_7 = [
        ExtractedLine(line_index=1, text="शुद्ध बेसन / PURE GRAM FLOUR (BESAN)", confidence=0.97, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="शुद्ध वजन / Net Weight: 1 kg", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=50, height=5)),
        ExtractedLine(line_index=3, text="अधिकतम खुदरा मूल्य / MRP: ₹ 95.00 (सभी करों सहित / incl. of all taxes)", confidence=0.98, bbox=BoundingBox(x=10, y=30, width=80, height=5)),
        ExtractedLine(line_index=4, text="पैकिंग तिथि / Date of Packing: 09/2024", confidence=0.95, bbox=BoundingBox(x=10, y=40, width=60, height=5)),
        ExtractedLine(line_index=5, text="निर्माता / Packed by: Kisan Mills Ltd, Grain Market, Karnal, Haryana - 132001", confidence=0.96, bbox=BoundingBox(x=10, y=50, width=80, height=6)),
        ExtractedLine(line_index=6, text="उपभोक्ता सेवा / Consumer Helpline: 1800-200-1920", confidence=0.97, bbox=BoundingBox(x=10, y=60, width=65, height=5))
    ]
    data_7, _, _ = process_and_classify_text(lines_7, "\n".join([l.text for l in lines_7]))
    checks_7, score_7, status_7 = evaluate_legal_metrology_rules(data_7, "Front (PDP)", is_image_degraded=False)
    print(f" -> Hindi/English Status: {status_7} | Score: {score_7}%")
    assert status_7 == "COMPLIANT"
    assert data_7.net_quantity.value == 1.0 and data_7.net_quantity.unit == "kg"
    assert data_7.mrp.amount == 95.0 and data_7.mrp.complies_tax_phrase is True
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 8: Rule 26(a) Micro-Package Exemption (<= 10g sachet)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Rule 26(a) Micro-Package Exemption (5g Shampoo Sachet)")
    lines_8 = [
        ExtractedLine(line_index=1, text="SILKY SHINE SHAMPOO SACHET", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Qty: 5 ml", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=30, height=5)),
        ExtractedLine(line_index=3, text="MRP Rs. 2.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5)),
        ExtractedLine(line_index=4, text="Mfd by: Care Cosmetics, Solan, HP - 173212", confidence=0.96, bbox=BoundingBox(x=10, y=50, width=80, height=5))
        # Missing Mfg date, Consumer care, Batch number on 5ml sachet
    ]
    data_8, _, _ = process_and_classify_text(lines_8, "\n".join([l.text for l in lines_8]))
    checks_8, score_8, status_8 = evaluate_legal_metrology_rules(data_8, "Front (PDP)", is_image_degraded=False)
    r26_check = next(c for c in checks_8 if c.rule_no == "RULE 26(a)")
    print(f" -> Rule 26(a) Status: {r26_check.status} | Applicable: {r26_check.is_applicable}")
    print(f" -> Overall Status: {status_8}")
    assert r26_check.status == "PASS" and r26_check.is_applicable is True
    assert status_8 == "COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 9: Rule 26(e) Readymade Garment Exemption (Chest/Waist in cm)
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Rule 26(e) Readymade Garment Sizing Exemption")
    garment_data = StructuredProductData(
        product_name="Raymond Men Cotton Formal Shirt",
        commodity_name="Readymade Garment",
        manufacturer=AddressInfo(name="Raymond Apparel Ltd", full_address="Jekegram, Thane, Maharashtra - 400606", pin_code="400606", has_valid_pin=True),
        net_quantity=NetQuantityInfo(raw_text="1 N (Chest: 106 cm, Size: 42)", value=1.0, unit="N", complies_standard_units=True),
        mrp=MrpInfo(raw_text="Rs. 1,899.00 (inclusive of all taxes)", amount=1899.0, tax_inclusive_statement_present=True, complies_tax_phrase=True),
        mfd=DateInfo(raw_text="11/2024", month="11", year="2024"),
        consumer_care=ConsumerCareInfo(phone="1800-222-777", email="support@raymond.in"),
        country_of_origin="India"
    )
    g_checks, g_score, g_status = evaluate_legal_metrology_rules(garment_data, "Front (PDP)", is_image_degraded=False)
    g_check = next(c for c in g_checks if c.rule_no == "RULE 26(e)")
    print(f" -> Garment Rule 26(e) Applicable: {g_check.is_applicable} | Source PDF: {g_check.source_pdf} p.{g_check.source_pdf_page}")
    assert g_check.is_applicable is True
    assert "Garments" in g_check.source_pdf
    assert g_status == "COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 10: Rule 6(1) Proviso Electronic Product (QR Code framework)
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Rule 6(1) Proviso Electronic Product with Digital QR Code")
    elec_data = StructuredProductData(
        product_name="Wireless Bluetooth Earphones",
        commodity_name="Earphones",
        manufacturer=AddressInfo(name="Acoustic Technologies Ltd", full_address="Electronics City, Bengaluru, Karnataka - 560100", pin_code="560100", has_valid_pin=True),
        net_quantity=NetQuantityInfo(raw_text="1 N", value=1.0, unit="N", complies_standard_units=True),
        mrp=MrpInfo(raw_text="₹ 1,499.00 (inclusive of all taxes)", amount=1499.0, tax_inclusive_statement_present=True, complies_tax_phrase=True),
        mfd=DateInfo(raw_text="02/2025", month="02", year="2025"),
        consumer_care=ConsumerCareInfo(phone="1800-888-9999", email="support@acoustics.in")
    )
    e_checks, e_score, e_status = evaluate_legal_metrology_rules(elec_data, "Front (PDP)", is_image_degraded=False)
    e_check = next(c for c in e_checks if "6(1) PROVISO" in c.rule_no)
    print(f" -> Electronic QR Rule Applicable: {e_check.is_applicable} | Source PDF: {e_check.source_pdf}")
    assert e_check.is_applicable is True
    assert "QR Code" in e_check.source_pdf
    assert e_status == "COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 11: OCR Engine Disagreement on MRP Amount
    # -------------------------------------------------------------------------
    print("\n[TEST 11] Multi-Engine OCR Disagreement on MRP (₹249 vs ₹2490)")
    best_val, conf, is_disagree, status = verify_ocr_ensemble_and_disagreement(
        field_name="mrp",
        candidates={"Tesseract": "₹ 249.00", "EasyOCR": "₹ 2490.00"}
    )
    print(f" -> Disagreement Detected: {is_disagree} | Status: {status} | Value: {best_val}")
    assert is_disagree is True
    assert status == "NEEDS REVIEW"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 12: Pan Masala Micro-Package Barred from Rule 26(a) Exemption
    # -------------------------------------------------------------------------
    print("\n[TEST 12] Pan Masala Micro-Package Barred from Rule 26(a) Exemption (2nd PCR Amendment)")
    pm_data = StructuredProductData(
        product_name="SHIKHAR PAN MASALA",
        commodity_name="Pan Masala",
        net_quantity=NetQuantityInfo(raw_text="4 g", value=4.0, unit="g", complies_standard_units=True),
        mrp=MrpInfo(raw_text="Rs. 5.00 (inclusive of all taxes)", amount=5.0, tax_inclusive_statement_present=True, complies_tax_phrase=True),
        manufacturer=AddressInfo(name="Shikhar Fragrances Ltd", full_address="Transport Nagar, Kanpur, UP - 208023", pin_code="208023", has_valid_pin=True)
    )
    pm_checks, _, _ = evaluate_legal_metrology_rules(pm_data, "Front (PDP)", is_image_degraded=False)
    pm_r26_check = next(c for c in pm_checks if c.rule_no == "RULE 26(a)")
    print(f" -> Pan Masala Rule 26(a) finding: {pm_r26_check.detected_declaration}")
    assert "barred" in pm_r26_check.detected_declaration.lower() or "pan masala" in pm_r26_check.detected_declaration.lower()
    assert pm_r26_check.source_pdf == "2nd PCR Pan Masala_1764736734---39.pdf"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 13: Missing Mandatory Tax Phrase '(inclusive of all taxes)'
    # -------------------------------------------------------------------------
    print("\n[TEST 13] Violation: Missing Mandatory Tax Phrase '(inclusive of all taxes)'")
    lines_13 = [
        ExtractedLine(line_index=1, text="PREMIUM BASMATI RICE", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Quantity: 5 kg", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5)),
        ExtractedLine(line_index=3, text="MRP: Rs. 650.00", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=35, height=5)),  # Missing taxes phrase
        ExtractedLine(line_index=4, text="Packed by: Rice Mills Ltd, GT Road, Karnal, Haryana - 132001", confidence=0.96, bbox=BoundingBox(x=10, y=50, width=80, height=5))
    ]
    data_13, _, _ = process_and_classify_text(lines_13, "\n".join([l.text for l in lines_13]))
    checks_13, _, status_13 = evaluate_legal_metrology_rules(data_13, "Front (PDP)", is_image_degraded=False)
    mrp_chk_13 = next(c for c in checks_13 if c.rule_no == "RULE 6(1)(e)")
    print(f" -> MRP Status: {mrp_chk_13.status} | Violation: {mrp_chk_13.detected_declaration}")
    assert mrp_chk_13.status == "FAIL"
    assert status_13 == "NON_COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 14: Non-Standard Prohibited Unit ('kgs')
    # -------------------------------------------------------------------------
    print("\n[TEST 14] Violation: Non-Standard Prohibited Unit ('kgs' instead of 'kg')")
    lines_14 = [
        ExtractedLine(line_index=1, text="WHEAT ATTA 100% WHOLE GRAIN", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Weight: 10 kgs", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5)),  # Prohibited unit 'kgs'
        ExtractedLine(line_index=3, text="MRP: Rs. 420.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5)),
        ExtractedLine(line_index=4, text="Packed by: Agro Mills Ltd, Jaipur, Rajasthan - 302001", confidence=0.96, bbox=BoundingBox(x=10, y=50, width=80, height=5))
    ]
    data_14, _, _ = process_and_classify_text(lines_14, "\n".join([l.text for l in lines_14]))
    checks_14, _, status_14 = evaluate_legal_metrology_rules(data_14, "Front (PDP)", is_image_degraded=False)
    r13_chk = next(c for c in checks_14 if c.rule_no == "RULE 13")
    print(f" -> Rule 13 Status: {r13_chk.status} | Violation: {r13_chk.detected_declaration}")
    assert r13_chk.status == "FAIL"
    assert status_14 == "NON_COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 15: Front-Only Image with Missing Secondary Declarations (Condition 5 & 22)
    # -------------------------------------------------------------------------
    print("\n[TEST 15] Single-Surface (Front-Only) Image (Anti-False-Positive Safeguard)")
    lines_15 = [
        ExtractedLine(line_index=1, text="ALMOND NOURISHING BODY LOTION", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Quantity: 100 ml", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5)),
        ExtractedLine(line_index=3, text="MRP: Rs. 150.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5))
        # Address, MFD, Consumer Care are on the unseen Back Panel
    ]
    data_15, _, _ = process_and_classify_text(lines_15, "\n".join([l.text for l in lines_15]))
    checks_15, score_15, status_15 = evaluate_legal_metrology_rules(
        data_15,
        surface="Front (PDP)",
        is_image_degraded=False,
        surfaces_processed=["Front (PDP)"]
    )
    print(f" -> Front-Only Overall Status: {status_15} | Score: {score_15}%")
    r6_a = next(c for c in checks_15 if c.rule_no == "RULE 6(1)(a)")
    r6_d = next(c for c in checks_15 if c.rule_no == "RULE 6(1)(d)")
    r6_f = next(c for c in checks_15 if c.rule_no == "RULE 6(1)(f)")
    print(f" -> Rule 6(1)(a) Status: {r6_a.status} (Finding: {r6_a.detected_declaration})")
    print(f" -> Rule 6(1)(d) Status: {r6_d.status}")
    print(f" -> Rule 6(1)(f) Status: {r6_f.status}")
    assert r6_a.status == "NEEDS REVIEW", "Missing address on Front PDP must be NEEDS REVIEW, not false FAIL"
    assert r6_d.status == "NEEDS REVIEW", "Missing MFD on Front PDP must be NEEDS REVIEW, not false FAIL"
    assert r6_f.status == "NEEDS REVIEW", "Missing Consumer Care on Front PDP must be NEEDS REVIEW, not false FAIL"
    assert status_15 == "NEEDS_REVIEW", f"Expected NEEDS_REVIEW on single-surface scan, got {status_15}"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 16: Multi-Surface (Front + Back) Package (Condition 6 & 20)
    # -------------------------------------------------------------------------
    print("\n[TEST 16] Multi-Surface (Front + Back) Images with Missing Mandatory Declarations")
    lines_16 = [
        ExtractedLine(line_index=1, text="ALMOND NOURISHING BODY LOTION", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5), surface="Front (PDP)"),
        ExtractedLine(line_index=2, text="Net Quantity: 100 ml", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=35, height=5), surface="Front (PDP)"),
        ExtractedLine(line_index=3, text="MRP: Rs. 150.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5), surface="Front (PDP)"),
        ExtractedLine(line_index=4, text="DIRECTIONS FOR USE: Apply gently over body", confidence=0.95, bbox=BoundingBox(x=10, y=20, width=70, height=5), surface="Back Panel")
        # Manufacturer address and MFD omitted across BOTH Front and Back panels
    ]
    data_16, _, _ = process_and_classify_text(lines_16, "\n".join([l.text for l in lines_16]))
    checks_16, score_16, status_16 = evaluate_legal_metrology_rules(
        data_16,
        surface="Front (PDP)",
        is_image_degraded=False,
        surfaces_processed=["Front (PDP)", "Back Panel"]
    )
    print(f" -> Front+Back Multi-Surface Overall Status: {status_16} | Score: {score_16}%")
    r6_a_16 = next(c for c in checks_16 if c.rule_no == "RULE 6(1)(a)")
    r6_d_16 = next(c for c in checks_16 if c.rule_no == "RULE 6(1)(d)")
    print(f" -> Rule 6(1)(a) Status: {r6_a_16.status} (Finding: {r6_a_16.detected_declaration})")
    print(f" -> Rule 6(1)(d) Status: {r6_d_16.status}")
    assert r6_a_16.status == "FAIL", "Missing address across BOTH surfaces must be verified FAIL"
    assert r6_d_16.status == "FAIL", "Missing MFD across BOTH surfaces must be verified FAIL"
    assert status_16 == "NON_COMPLIANT"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 17: Small Printed Text Extraction (Condition 10)
    # -------------------------------------------------------------------------
    print("\n[TEST 17] Small Printed Text Consumer Grievance Extraction")
    lines_17 = [
        ExtractedLine(line_index=1, text="HERBAL EYE DROPS 10ML", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net: 10 ml", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=25, height=4)),
        ExtractedLine(line_index=3, text="MRP ₹ 60.00 (inclusive of all taxes)", confidence=0.98, bbox=BoundingBox(x=10, y=30, width=60, height=4)),
        ExtractedLine(line_index=4, text="Consumer Grievance Toll-free Helpline: 1800-202-3030 Email: grievance@healthfirst.in", confidence=0.96, bbox=BoundingBox(x=10, y=85, width=80, height=3))
    ]
    data_17, _, _ = process_and_classify_text(lines_17, "\n".join([l.text for l in lines_17]))
    print(f" -> Small Text Phone Extracted: {data_17.consumer_care.phone} | Email: {data_17.consumer_care.email}")
    assert data_17.consumer_care.phone == "1800-202-3030"
    assert data_17.consumer_care.email == "grievance@healthfirst.in"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 18: Rotated / Angled Stamped Text Parsing (Condition 11)
    # -------------------------------------------------------------------------
    print("\n[TEST 18] Stamped Coded Batch & Date Line Parsing")
    lines_18 = [
        ExtractedLine(line_index=1, text="CRISP CORN FLAKES", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Wt: 250 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=30, height=5)),
        ExtractedLine(line_index=3, text="MRP: Rs. 99.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5)),
        ExtractedLine(line_index=4, text="B.NO: KL-902 MFD: 12/2024 EXP: 11/2026", confidence=0.94, bbox=BoundingBox(x=10, y=90, width=70, height=4))
    ]
    data_18, _, _ = process_and_classify_text(lines_18, "\n".join([l.text for l in lines_18]))
    print(f" -> MFD: '{data_18.mfd.raw_text}' | Batch: '{data_18.batch}' | Expiry: '{data_18.expiry.raw_text}'")
    assert "12/2024" in data_18.mfd.raw_text
    assert "KL-902" in data_18.batch or "902" in data_18.batch
    assert "11/2026" in data_18.expiry.raw_text
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 19: OCR Character Error Normalization (Condition 13)
    # -------------------------------------------------------------------------
    print("\n[TEST 19] OCR Normalization (M8P -> MRP, 1NCL. -> INCL.)")
    raw_noisy_mrp = "M8P Rs. 180.00 (1NCL. OF ALL TAXES)"
    lines_19 = [
        ExtractedLine(line_index=1, text="ORGANIC GREEN TEA", confidence=0.95, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Weight: 100 g", confidence=0.95, bbox=BoundingBox(x=10, y=20, width=40, height=5)),
        ExtractedLine(line_index=3, text=raw_noisy_mrp, confidence=0.92, bbox=BoundingBox(x=10, y=30, width=65, height=5))
    ]
    data_19, _, _ = process_and_classify_text(lines_19, "\n".join([l.text for l in lines_19]))
    print(f" -> Noisy Input: '{raw_noisy_mrp}' -> Normalized MRP: '{data_19.mrp.raw_text}' | Complies Tax Phrase: {data_19.mrp.complies_tax_phrase}")
    assert data_19.mrp.amount == 180.0
    assert data_19.mrp.complies_tax_phrase is True
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 20: Best-Before Applicable vs Not Applicable (Condition 16 & 17)
    # -------------------------------------------------------------------------
    print("\n[TEST 20] Best-Before Applicable (Perishable Food) vs Not Applicable (Garment)")
    # Case A: Perishable item (Dairy / Paneer)
    paneer_data = StructuredProductData(
        product_name="FRESH MALAI PANEER 200G",
        commodity_name="Fresh Paneer",
        net_quantity=NetQuantityInfo(raw_text="200 g", value=200.0, unit="g", complies_standard_units=True),
        mrp=MrpInfo(raw_text="Rs. 90.00 (inclusive of all taxes)", amount=90.0, tax_inclusive_statement_present=True, complies_tax_phrase=True),
        expiry=DateInfo(raw_text="Best Before 15 days from packing", complies_format=True)
    )
    chks_20a, _, _ = evaluate_legal_metrology_rules(paneer_data, "Front (PDP)", is_image_degraded=False)
    exp_chk_a = next(c for c in chks_20a if c.rule_no == "RULE 6(1)(da)")
    print(f" -> Perishable Food Expiry Status: {exp_chk_a.status} (Finding: {exp_chk_a.detected_declaration})")
    assert exp_chk_a.status == "PASS"

    # Case B: Non-perishable item (Garment) without expiry
    garment_no_exp = StructuredProductData(
        product_name="COTTON DENIM JEANS",
        commodity_name="Readymade Garment",
        net_quantity=NetQuantityInfo(raw_text="1 N", value=1.0, unit="N", complies_standard_units=True),
        mrp=MrpInfo(raw_text="Rs. 1,499.00 (inclusive of all taxes)", amount=1499.0, tax_inclusive_statement_present=True, complies_tax_phrase=True)
    )
    chks_20b, _, _ = evaluate_legal_metrology_rules(garment_no_exp, "Front (PDP)", is_image_degraded=False)
    exp_chk_b = next(c for c in chks_20b if c.rule_no == "RULE 6(1)(da)")
    print(f" -> Non-perishable Garment Expiry Status: {exp_chk_b.status} (Finding: {exp_chk_b.detected_declaration})")
    assert exp_chk_b.status == "NOT APPLICABLE"
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 21: Unit Sale Price (USP) Applicable vs Not Applicable (Condition 18 & 19)
    # -------------------------------------------------------------------------
    print("\n[TEST 21] Unit Sale Price Applicable (>100g) vs Exempt (<=100g Rule 6(11) Proviso)")
    # Case A: Package <= 100g is statutorily EXEMPT under Rule 6(11) Proviso
    lines_21a = [
        ExtractedLine(line_index=1, text="MILK CHOCOLATE BAR", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Weight: 45 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=30, height=5)),
        ExtractedLine(line_index=3, text="MRP Rs. 40.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5))
    ]
    data_21a, _, _ = process_and_classify_text(lines_21a, "\n".join([l.text for l in lines_21a]))
    print(f" -> 45g Package USP is_exempt: {data_21a.unit_sale_price.is_exempt}")
    assert data_21a.unit_sale_price.is_exempt is True
    chks_21a, _, _ = evaluate_legal_metrology_rules(data_21a, "Front (PDP)", is_image_degraded=False)
    usp_chk_a = next(c for c in chks_21a if c.rule_no == "RULE 6(11)")
    assert "Exemption" in usp_chk_a.detected_declaration

    # Case B: Package > 100g has declared USP
    lines_21b = [
        ExtractedLine(line_index=1, text="PREMIUM FILTER COFFEE", confidence=0.98, bbox=BoundingBox(x=10, y=10, width=80, height=5)),
        ExtractedLine(line_index=2, text="Net Qty: 500 g", confidence=0.98, bbox=BoundingBox(x=10, y=20, width=30, height=5)),
        ExtractedLine(line_index=3, text="MRP: Rs. 350.00 (inclusive of all taxes)", confidence=0.99, bbox=BoundingBox(x=10, y=30, width=65, height=5)),
        ExtractedLine(line_index=4, text="Unit Sale Price: ₹ 0.70 / g", confidence=0.97, bbox=BoundingBox(x=10, y=40, width=45, height=5))
    ]
    data_21b, _, _ = process_and_classify_text(lines_21b, "\n".join([l.text for l in lines_21b]))
    print(f" -> 500g Package Declared USP: {data_21b.unit_sale_price.value_per_unit}")
    assert data_21b.unit_sale_price.value_per_unit is not None
    chks_21b, _, _ = evaluate_legal_metrology_rules(data_21b, "Front (PDP)", is_image_degraded=False)
    usp_chk_b = next(c for c in chks_21b if c.rule_no == "RULE 6(11)")
    assert "0.70" in usp_chk_b.detected_declaration
    passed_tests += 1
    print(" -> PASSED")

    # -------------------------------------------------------------------------
    # TEST 22: Unreadable / Smudged Stamp / Torn Declaration (Condition 21)
    # -------------------------------------------------------------------------
    print("\n[TEST 22] Unreadable Smeared Inkjet Stamp Flagged as NEEDS REVIEW")
    unreadable_data = StructuredProductData(
        product_name="PURE ALOE VERA GEL",
        commodity_name="Cosmetic Gel",
        net_quantity=NetQuantityInfo(raw_text="150 ml", value=150.0, unit="ml", complies_standard_units=True),
        mrp=MrpInfo(raw_text="MRP Rs. 120.00 (inclusive of all taxes)", amount=120.0, tax_inclusive_statement_present=True, complies_tax_phrase=True),
        mfd=DateInfo(raw_text="MFD 0*/202*", is_uncertain=True)  # Smeared / torn stamp
    )
    chks_22, _, status_22 = evaluate_legal_metrology_rules(unreadable_data, "Front (PDP)", is_image_degraded=False)
    mfd_chk_22 = next(c for c in chks_22 if c.rule_no == "RULE 6(1)(d)")
    print(f" -> Smudged MFD Status: {mfd_chk_22.status} | Finding: {mfd_chk_22.detected_declaration}")
    assert mfd_chk_22.status == "NEEDS REVIEW"
    assert status_22 == "NEEDS_REVIEW"
    passed_tests += 1
    print(" -> PASSED")

    print("\n" + "=" * 70)
    print(f">>> ALL {passed_tests} / {total_tests} GENERAL PRODUCT-COMPLIANCE TESTS PASSED! <<<")
    print("=" * 70)

if __name__ == "__main__":
    run_general_compliance_suite()

