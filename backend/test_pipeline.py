import os
import io
import json
import base64
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.cv_pipeline import analyze_complete_image_quality, generate_13_preprocessing_variants
from backend.services.llm_extractor import get_ai_provider, NLPFallbackProvider
from backend.services.ml_service import ml_service, DeclarationClassifier, ProductCategoryClassifier
from backend.services.rule_engine import evaluate_legal_metrology_rules
from backend.models import StructuredProductData, AddressInfo, NetQuantityInfo, MrpInfo, DateInfo, ConsumerCareInfo
from backend.services.data_layer import (
    save_case_docket,
    get_case_docket_by_id,
    list_case_dockets,
    delete_case_docket,
    get_dashboard_metrics
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "data", "sample_test_products")

client = TestClient(app)

# ----------------------------------------------------
# 1. IMAGE PROCESSING & CV TESTS
# ----------------------------------------------------

def test_image_quality_sharp_vs_blurry():
    compliant_path = os.path.join(SAMPLE_DIR, "sample_1_fully_compliant.png")
    blurry_path = os.path.join(SAMPLE_DIR, "sample_5_blurry_degraded.png")

    assert os.path.exists(compliant_path)
    assert os.path.exists(blurry_path)

    img_good = Image.open(compliant_path)
    metrics_good = analyze_complete_image_quality(img_good)
    assert metrics_good.is_blurred is False
    assert metrics_good.overall_quality_score >= 45

    img_blur = Image.open(blurry_path)
    metrics_blur = analyze_complete_image_quality(img_blur)
    assert metrics_blur.blur_laplacian_variance < metrics_good.blur_laplacian_variance

def test_preprocessing_variants_generation():
    compliant_path = os.path.join(SAMPLE_DIR, "sample_1_fully_compliant.png")
    img = Image.open(compliant_path)
    variants = generate_13_preprocessing_variants(img, include_base64=False)
    assert len(variants) >= 10
    assert "grayscale" in variants
    assert "contrast_enhanced" in variants
    assert "adaptive_threshold" in variants

# ----------------------------------------------------
# 2. AI / LLM EXTRACTION LAYER TESTS
# ----------------------------------------------------

def test_nlp_fallback_provider_extraction():
    provider = NLPFallbackProvider()
    raw_text = (
        "LAKME SUN EXPERT ULTRA MATTE GEL SPF 50\n"
        "Net Qty: 50 g\n"
        "MRP: Rs. 499.00 (inclusive of all taxes)\n"
        "USP: Rs. 9.98 / g\n"
        "Mfd: 08/2024\n"
        "Batch: B-LK8942\n"
        "Mfd by: Aero Care Personal Products, Survey 284/2, Naroli 396235, D&NH\n"
        "Consumer Care: 1800-10-22-221 • care@unilever.com"
    )
    res = provider.extract_structured_label_data(raw_text, [])
    assert res["net_quantity"]["value"] == 50.0
    assert res["net_quantity"]["unit"] == "g"
    assert res["net_quantity"]["complies_standard_units"] is True
    assert res["mrp"]["amount"] == 499.0
    assert res["mrp"]["tax_inclusive_statement_present"] is True
    assert res["manufacturer"]["pin_code"] == "396235"
    assert res["consumer_care"]["phone"] == "1800-10-22-221"

def test_ai_provider_factory():
    provider = get_ai_provider()
    assert provider is not None
    res = provider.explain_extraction("net_quantity", "50 g", "sample context")
    assert isinstance(res, str) and len(res) > 0

# ----------------------------------------------------
# 3. ML SERVICE TESTS
# ----------------------------------------------------

def test_ml_declaration_classifier():
    classifier = DeclarationClassifier()
    cat1, conf1 = classifier.predict_line_category("MRP Rs. 499.00 incl of all taxes")
    assert cat1 == "MRP"
    assert conf1 >= 0.70

    cat2, conf2 = classifier.predict_line_category("Net Quantity: 100 ml")
    assert cat2 == "NET_QUANTITY"

    cat3, conf3 = classifier.predict_line_category("Manufactured by: CleanHome India Ltd")
    assert cat3 == "MANUFACTURER"

def test_ml_product_category_classifier():
    cat_classifier = ProductCategoryClassifier()
    cat1, _ = cat_classifier.predict_category("Aqua Sun Gel SPF 50 moisturizer cream", "Sunscreen")
    assert "Cosmetics" in cat1

    cat2, _ = cat_classifier.predict_category("Kachi Ghani edible Mustard Oil 1 L", "Cooking Oil")
    assert "Food" in cat2

def test_ml_risk_confidence_module():
    risk_output = ml_service.risk_module.evaluate_risk(
        ocr_confidence=0.95,
        extracted_fields={"net_quantity": {"complies_standard_units": False}},
        has_violations=True,
        is_blurred=False
    )
    assert risk_output["risk_rating"] in ["MEDIUM", "HIGH"]
    assert risk_output["requires_human_review"] is True

# ----------------------------------------------------
# 4. DETERMINISTIC RULE ENGINE TESTS
# ----------------------------------------------------

def test_rule_engine_compliant_package():
    data = StructuredProductData(
        product_name="Lakmé Sunscreen Gel",
        commodity_name="Sunscreen Gel",
        manufacturer=AddressInfo(
            name="Aero Care",
            full_address="Survey 284/2, Naroli 396235, D&NH",
            pin_code="396235",
            has_valid_pin=True
        ),
        net_quantity=NetQuantityInfo(
            raw_text="50 g",
            value=50.0,
            unit="g",
            complies_standard_units=True
        ),
        mrp=MrpInfo(
            raw_text="MRP ₹ 499.00 (inclusive of all taxes)",
            amount=499.0,
            tax_inclusive_statement_present=True,
            complies_tax_phrase=True
        ),
        mfd=DateInfo(raw_text="08/2024", month="08", year="2024", complies_format=True),
        consumer_care=ConsumerCareInfo(phone="1800-10-22-221", email="care@unilever.com")
    )

    checks, score, overall = evaluate_legal_metrology_rules(data)
    assert score >= 90
    assert overall == "COMPLIANT"
    
    # Verify mandatory rules PASS
    rule_map = {c.rule_no: c.status for c in checks}
    assert rule_map.get("RULE 6(1)(a)") == "PASS"  # Manufacturer
    assert rule_map.get("RULE 6(1)(c)") == "PASS"  # Net Qty
    assert rule_map.get("RULE 6(1)(e)") == "PASS"  # MRP

def test_rule_engine_prohibited_units_violation():
    data = StructuredProductData(
        product_name="Digestive Biscuits",
        net_quantity=NetQuantityInfo(
            raw_text="250 gms",
            value=250.0,
            unit="gms",
            complies_standard_units=False,
            prohibited_unit_detected="gms"
        )
    )
    checks, score, overall = evaluate_legal_metrology_rules(data)
    rule_map = {c.rule_no: c.status for c in checks}
    assert rule_map.get("RULE 6(1)(c)") == "FAIL"
    assert rule_map.get("RULE 13") == "FAIL"
    assert overall == "NON_COMPLIANT"

def test_rule_engine_missing_mrp_tax_phrase():
    data = StructuredProductData(
        product_name="Mustard Oil",
        mrp=MrpInfo(
            raw_text="MRP Rs. 145.00",
            amount=145.0,
            tax_inclusive_statement_present=False,
            complies_tax_phrase=False
        )
    )
    checks, score, overall = evaluate_legal_metrology_rules(data)
    rule_map = {c.rule_no: c.status for c in checks}
    assert rule_map.get("RULE 6(1)(e)") == "FAIL"
    assert overall == "NON_COMPLIANT"

# ----------------------------------------------------
# 5. DATABASE CRUD & PERSISTENCE TESTS
# ----------------------------------------------------

def test_database_crud_operations():
    test_docket_id = "TEST-DOCKET-9999"
    payload = {
        "scan_id": test_docket_id,
        "product_name": "Test Commodity Soap",
        "brand": "TestBrand",
        "manufacturer": "Plot 12, Industrial Area, Solan 173212, HP",
        "overall_status": "COMPLIANT",
        "compliance_score": 95,
        "officer_notes": "Panchnama recorded without objection.",
        "final_decision": "Accepted"
    }

    # 1. Save docket
    save_res = save_case_docket(payload)
    assert save_res["status"] == "Saved"

    # 2. Get docket
    fetched = get_case_docket_by_id(test_docket_id)
    assert fetched is not None
    assert fetched["product_name"] == "Test Commodity Soap"
    assert fetched["compliance_score"] == 95

    # 3. List dockets
    dockets = list_case_dockets(limit=10)
    assert any(d["id"] == test_docket_id for d in dockets)

    # 4. Metrics
    metrics = get_dashboard_metrics()
    assert metrics["total_scans"] >= 1

    # 5. Delete docket
    del_ok = delete_case_docket(test_docket_id)
    assert del_ok is True
    assert get_case_docket_by_id(test_docket_id) is None

# ----------------------------------------------------
# 6. FASTAPI REST API ENDPOINT TESTS
# ----------------------------------------------------

def test_api_system_status():
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert "version" in data

def test_api_rules_list():
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 30

def test_api_dashboard_stats():
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    res = resp.json()
    assert res["success"] is True
    assert "total_scans" in res["data"]
    assert "compliance_rate" in res["data"]

def test_api_scans_and_reports_endpoints():
    resp_scans = client.get("/api/scans")
    assert resp_scans.status_code == 200
    assert resp_scans.json()["success"] is True

    resp_reports = client.get("/api/reports")
    assert resp_reports.status_code == 200
    assert resp_reports.json()["success"] is True

def test_api_scan_process_end_to_end():
    compliant_path = os.path.join(SAMPLE_DIR, "sample_1_fully_compliant.png")
    with open(compliant_path, "rb") as f:
        b64_data = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    payload = {
        "images": [
            {
                "data": b64_data,
                "surface": "Front (PDP)",
                "file_name": "sample_1_fully_compliant.png",
                "text_lines": [
                    "LAKME SUN EXPERT ULTRA MATTE GEL SPF 50",
                    "Net Qty: 50 g",
                    "MRP: Rs. 499.00 (inclusive of all taxes)",
                    "USP: Rs. 9.98 / g",
                    "Mfd: 08/2024 • Exp: 08/2026",
                    "Batch: B-LK8942",
                    "Mfd by: Aero Care Personal Products, Survey 284/2, Naroli 396235, D&NH",
                    "Consumer Care: 1800-10-22-221 • care@unilever.com",
                    "Country of Origin: India"
                ]
            }
        ],
        "jurisdiction": {
            "country": "India",
            "state": "Maharashtra",
            "city": "Nashik",
            "pinCode": "422001"
        }
    }

    resp = client.post("/api/scan/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "scan_id" in data
    assert data["scan_id"].startswith("INSP-")
    assert len(data["compliance_checks"]) >= 30
    assert data["overall_status"] in ["COMPLIANT", "NON_COMPLIANT", "NEEDS_REVIEW"]
    assert len(data["preprocessing_variants"]) >= 10
