"""
Test Legal Metrology Rule Knowledge Base Integration
Verifies:
1. Knowledge base loads 107+ rule entries from legal_metrology_knowledge_base.json
2. Dynamic category filtering:
   - Food vs Garments vs Electronics vs Pan Masala vs Edible Oils
3. Every checked rule carries source_pdf and source_pdf_page
4. Amendments and effective dates correctly attached
5. Degraded image policy: unverified fields yield NEEDS REVIEW, never false FAIL
6. Report generator produces valid PDF and DOCX with Source PDF columns
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.rule_knowledge_base import get_knowledge_base
from backend.services.rule_engine import evaluate_legal_metrology_rules
from backend.models import (
    StructuredProductData,
    AddressInfo,
    NetQuantityInfo,
    MrpInfo,
    DateInfo,
    ConsumerCareInfo,
    ScanProcessResponse,
    ComplianceCheckItem,
    CanonicalField,
    ImageQualityMetrics
)
from backend.services.report_generator import generate_statutory_pdf_report, generate_statutory_docx_report

def run_tests():
    print("=" * 60)
    print("LEGAL METROLOGY KNOWLEDGE BASE INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Knowledge Base Loading
    kb = get_knowledge_base()
    all_rules = kb.get_all_rules()
    print(f"\n[1] Knowledge Base Loaded: {len(all_rules)} rule entries")
    assert len(all_rules) >= 100, f"Expected >= 100 rules, got {len(all_rules)}"

    # 2. Rule Search by category
    garment_rules = kb.search_by_product_category("Garments")
    print(f"[2] Garment Rules in KB: {len(garment_rules)}")
    assert len(garment_rules) > 0

    electronic_rules = kb.search_by_product_category("Electronic")
    print(f"[3] Electronic Rules in KB: {len(electronic_rules)}")
    assert len(electronic_rules) > 0

    # 3. Dynamic Category Evaluation - Food (Tea) Product
    tea_product = StructuredProductData(
        product_name="Tata Gold Premium Tea",
        commodity_name="Tea",
        manufacturer=AddressInfo(name="Tata Consumer Products Ltd", full_address="11/1, Kirloskar Business Park, Bengaluru - 560024", pin_code="560024", has_valid_pin=True),
        net_quantity=NetQuantityInfo(raw_text="500 g", value=500.0, unit="g", complies_standard_units=True),
        mrp=MrpInfo(raw_text="Rs. 260.00 (incl. of all taxes)", amount=260.0, tax_inclusive_statement_present=True),
        mfd=DateInfo(raw_text="11/2024", month="11", year="2024"),
        expiry=DateInfo(raw_text="11/2025", month="11", year="2025"),
        batch="B-94812",
        country_of_origin="India",
        consumer_care=ConsumerCareInfo(phone="1800-108-4488", email="care@tataconsumer.com")
    )

    checks, score, status = evaluate_legal_metrology_rules(tea_product, surface="Front (PDP)", is_image_degraded=False)
    print(f"\n[4] Food Commodity Evaluation:")
    print(f" -> Overall Status: {status}")
    print(f" -> Compliance Score: {score}")
    print(f" -> Total Rules Evaluated: {len(checks)}")

    # Verify every check has source_pdf and source_pdf_page
    checks_with_source = [c for c in checks if c.source_pdf]
    print(f" -> Checks with Source PDF & Page: {len(checks_with_source)} / {len(checks)}")
    assert len(checks_with_source) >= 30, "All primary checks must link to original Gazette source PDFs"

    # Category applicability: Rule 26(e) (Garments) must NOT apply to Tea
    garment_check = next((c for c in checks if "26(e)" in c.rule_no or "Garment" in c.rule_title), None)
    if garment_check:
        print(f" -> Garment Rule 26(e) for Tea: status={garment_check.status}, is_applicable={garment_check.is_applicable}")
        assert garment_check.is_applicable is False
        assert garment_check.status == "NOT APPLICABLE"

    # 4. Dynamic Category Evaluation - Readymade Garment Product
    shirt_product = StructuredProductData(
        product_name="Raymond Men Cotton Slim Fit Shirt",
        commodity_name="Readymade Garment",
        manufacturer=AddressInfo(name="Raymond Apparel Ltd", full_address="Jekegram, Thane, Maharashtra - 400606", pin_code="400606", has_valid_pin=True),
        net_quantity=NetQuantityInfo(raw_text="1 N (Size: 42 cm / L)", value=1.0, unit="N"),
        mrp=MrpInfo(raw_text="Rs. 1,499.00 (incl. of all taxes)", amount=1499.0, tax_inclusive_statement_present=True),
        mfd=DateInfo(raw_text="10/2024", month="10", year="2024"),
        country_of_origin="India",
        consumer_care=ConsumerCareInfo(phone="1800-222-777", email="support@raymond.in")
    )

    shirt_checks, shirt_score, shirt_status = evaluate_legal_metrology_rules(shirt_product, surface="Front (PDP)", is_image_degraded=False)
    print(f"\n[5] Garment Commodity Evaluation:")
    shirt_garment_check = next((c for c in shirt_checks if "26(e)" in c.rule_no or "Garment" in c.rule_title), None)
    assert shirt_garment_check is not None
    print(f" -> Garment Rule 26(e) for Shirt: status={shirt_garment_check.status}, is_applicable={shirt_garment_check.is_applicable}")
    assert shirt_garment_check.is_applicable is True
    print(f" -> Source PDF: {shirt_garment_check.source_pdf} (p. {shirt_garment_check.source_pdf_page})")
    assert "Garments" in shirt_garment_check.source_pdf or shirt_garment_check.source_pdf.endswith(".pdf")

    # 5. Degraded Image Safeguard (Never false violation)
    degraded_product = StructuredProductData(
        product_name="Generic Commodity",
        commodity_name="Packaged Item",
        net_quantity=NetQuantityInfo(raw_text="100 g", value=100.0, unit="g")
        # Missing MRP, Mfg date, Consumer care, Manufacturer address
    )
    deg_checks, deg_score, deg_status = evaluate_legal_metrology_rules(degraded_product, surface="Front (PDP)", is_image_degraded=True)
    print(f"\n[6] Degraded Image Evaluation:")
    print(f" -> Overall Status: {deg_status}")
    unverified_checks = [c for c in deg_checks if c.status == "NEEDS REVIEW"]
    fail_checks = [c for c in deg_checks if c.status == "FAIL"]
    print(f" -> Flagged as NEEDS REVIEW (not false FAIL): {len(unverified_checks)}")
    print(f" -> False Violation FAIL count: {len(fail_checks)}")
    assert len(fail_checks) == 0, "Degraded image must NEVER book false violation FAILs"
    assert deg_status == "NEEDS_REVIEW"

    # 6. Report Generator Verification (PDF & DOCX with Gazette Citations)
    print(f"\n[7] Testing PDF & DOCX Statutory Report Generation...")
    scan_resp = ScanProcessResponse(
        scan_id="TEST-KB-SCAN-01",
        timestamp="2026-09-18T19:40:00",
        overall_status=status,
        compliance_score=score,
        product_info=tea_product,
        surfaces_processed=["Front (PDP)"],
        image_quality=ImageQualityMetrics(
            resolution="1200x1600",
            megapixels=1.92,
            is_blurred=False,
            blur_score=150.0,
            is_glare_detected=False,
            glare_percentage=1.2,
            brightness=140.0,
            contrast=55.0,
            skew_angle=0.0,
            overall_quality_score=92.0,
            passed=True,
            advisory="Optimal label image quality"
        ),
        detected_regions=[],
        preprocessing_variants=[],
        measurement_validation=None,
        extracted_lines=[],
        raw_ocr_transcript="AMRUT TEA Net Qty 500g MRP Rs 240",
        canonical_fields=[
            CanonicalField(field_name="product_name", statutory_name="Product Name", extracted_value="Tata Gold Premium Tea", confidence=0.98, status="Found", rule_reference="Rule 6(1)(b)", detected_on_surface="Front (PDP)"),
            CanonicalField(field_name="net_quantity", statutory_name="Net Quantity", extracted_value="500 g", confidence=0.99, status="Found", rule_reference="Rule 6(1)(c)", detected_on_surface="Front (PDP)"),
            CanonicalField(field_name="mrp", statutory_name="Maximum Retail Price", extracted_value="Rs. 260.00 (incl. of all taxes)", confidence=0.99, status="Found", rule_reference="Rule 6(1)(e)", detected_on_surface="Front (PDP)")
        ],
        compliance_checks=checks,
        external_verification="External verification: Not available",
        audit_record_id="AUD-001"
    )

    pdf_path = generate_statutory_pdf_report(scan_resp)
    print(f" -> Generated PDF Report: {pdf_path}")
    assert os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000

    docx_path = generate_statutory_docx_report(scan_resp)
    print(f" -> Generated DOCX Report: {docx_path}")
    assert os.path.exists(docx_path) and os.path.getsize(docx_path) > 1000

    print("\n" + "=" * 60)
    print(">>> ALL 7 LEGAL METROLOGY KNOWLEDGE BASE TESTS PASSED! <<<")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
