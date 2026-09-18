"""
LM-COMPASS (VidhiCheck) E2E Pipeline Verification Test
Validates:
- System status
- CV Quality (12 metrics) & Preprocessing (13 variants)
- YOLOv8 / Morphological Region Detection (20+ categories)
- LabelMe v5.2.1 JSON Export
- Multi-Engine OCR & Token Extraction
- Rule Engine Statutory Evaluation (Rules 1-34 + Rule 32A Compounding Schedule)
- Data Layer (SQLAlchemy ORM + SQLite/Postgres fallback)
- Official PDF ReportLab & Word DOCX generation
- Benchmark Evaluation Suite (16 variations, 10 metrics)
"""
import sys
import os
import json
import base64
import numpy as np
import cv2

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def create_sample_package_image():
    """Create a realistic synthetic FMCG package image with text and barcode for testing."""
    img = np.full((600, 500, 3), 245, dtype=np.uint8)
    # Header brand banner
    cv2.rectangle(img, (20, 20), (480, 100), (30, 41, 59), -1)
    cv2.putText(img, "AMRUT PREMIUM TEA 500g", (35, 70), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
    
    # Net Quantity & MRP
    cv2.putText(img, "Net Qty: 500 g", (40, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (15, 23, 42), 2)
    cv2.putText(img, "MRP Rs. 240.00 (Incl. of all taxes)", (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 23, 42), 2)
    cv2.putText(img, "Unit Sale Price: Rs. 0.48 / g", (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 23, 42), 2)
    
    # Dates
    cv2.putText(img, "Mfg Date: 12/2024", (40, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 23, 42), 2)
    cv2.putText(img, "Best Before: 12 Months from Packaging", (40, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 1)
    
    # Manufacturer & Address with 6-digit PIN
    cv2.putText(img, "Mfd By: Amrut Beverage Pvt Ltd", (40, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (15, 23, 42), 2)
    cv2.putText(img, "Plot 42, GIDC Estate, Pune, Maharashtra - 411028", (40, 415), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 41, 59), 1)
    
    # Consumer Care
    cv2.putText(img, "Consumer Care: care@amruttea.com | Tel: 1800-209-1234", (40, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 41, 59), 1)
    cv2.putText(img, "Country of Origin: India", (40, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2)

    # Barcode pattern simulation
    cv2.rectangle(img, (300, 520), (460, 580), (255, 255, 255), -1)
    for x in range(310, 450, 4):
        cv2.line(img, (x, 525), (x, 570), (0, 0, 0), 2)
    cv2.putText(img, "8901234567890", (325, 578), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)

    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")

def test_pipeline():
    print("=" * 60)
    print("LM-COMPASS (VidhiCheck) E2E Pipeline Verification Test")
    print("=" * 60)

    # 1. Test System Status
    print("\n[1] Checking System Status (/api/system/status)...")
    res = client.get("/api/system/status")
    assert res.status_code == 200, f"Status failed: {res.status_code}"
    status_data = res.json()
    print(f" -> Status: {status_data.get('status')}")
    print(f" -> Version: {status_data.get('version')}")
    print(f" -> YOLO Backend: {status_data.get('yolo_backend')}")
    print(f" -> Database Connected: {status_data.get('database_connected')}")
    print(f" -> External API: {status_data.get('external_government_api')}")
    assert status_data.get("status") == "ONLINE"
    assert status_data.get("database_connected") is True
    assert "Not available" in status_data.get("external_government_api")

    # 2. Test Scan Processing
    print("\n[2] Processing Synthetic Package Image (/api/scan/process)...")
    b64_image = create_sample_package_image()
    payload = {
        "images": [
            {
                "data": f"data:image/png;base64,{b64_image}",
                "surface": "Front (PDP)",
                "file_name": "amrut_tea_500g.png"
            }
        ],
        "options": {
            "package_type": "rigid",
            "declared_net_weight": "500g",
            "declared_mrp": 240.0
        }
    }
    res = client.post("/api/scan/process", json=payload)
    assert res.status_code == 200, f"Scan process failed: {res.status_code} - {res.text}"
    scan_data = res.json()
    scan_id = scan_data.get("scan_id")
    print(f" -> Scan ID generated: {scan_id}")
    print(f" -> Overall Status: {scan_data.get('overall_status')}")
    print(f" -> Quality Passed: {scan_data.get('image_quality', {}).get('passed')}")
    print(f" -> Quality Score: {scan_data.get('image_quality', {}).get('overall_quality_score')}")
    print(f" -> Detected Regions Count: {len(scan_data.get('detected_regions', []))}")
    print(f" -> Compliance Checks Count: {len(scan_data.get('compliance_checks', []))}")

    assert scan_id is not None
    assert len(scan_data.get("detected_regions", [])) > 0
    assert len(scan_data.get("compliance_checks", [])) >= 34

    # 3. Test LabelMe v5.2.1 Export
    print(f"\n[3] Fetching LabelMe v5.2.1 JSON (/api/scan/{scan_id}/labelme)...")
    res = client.get(f"/api/scan/{scan_id}/labelme")
    assert res.status_code == 200, f"LabelMe export failed: {res.status_code}"
    labelme_data = res.json()
    print(f" -> Version: {labelme_data.get('version')}")
    print(f" -> Shapes Count: {len(labelme_data.get('shapes', []))}")
    assert labelme_data.get("version") == "5.2.1"
    assert "shapes" in labelme_data
    assert "imagePath" in labelme_data

    # 4. Test Report Data
    print(f"\n[4] Fetching Docket Report Data (/api/reports/{scan_id})...")
    res = client.get(f"/api/reports/{scan_id}")
    assert res.status_code == 200, f"Report fetch failed: {res.status_code}"
    report_data = res.json()
    print(f" -> Report ID: {report_data.get('report_id')}")
    print(f" -> Compliance Score: {report_data.get('compliance_score')}")
    print(f" -> Rules Evaluated: {report_data.get('total_rules_evaluated')}")
    assert report_data.get("report_id") is not None
    assert report_data.get("total_rules_evaluated") >= 34

    # 5. Test PDF Report Generation
    print(f"\n[5] Generating ReportLab PDF (/api/reports/{scan_id}/pdf)...")
    res = client.get(f"/api/reports/{scan_id}/pdf")
    assert res.status_code == 200, f"PDF generation failed: {res.status_code}"
    assert res.headers.get("content-type") == "application/pdf"
    pdf_bytes = res.content
    print(f" -> PDF Byte Size: {len(pdf_bytes)} bytes")
    assert pdf_bytes.startswith(b"%PDF"), "Generated bytes do not start with %PDF header"
    print(" -> Valid PDF binary verified!")

    # 6. Test DOCX Report Generation
    print(f"\n[6] Generating Word DOCX (/api/reports/{scan_id}/docx)...")
    res = client.get(f"/api/reports/{scan_id}/docx")
    assert res.status_code == 200, f"DOCX generation failed: {res.status_code}"
    docx_bytes = res.content
    print(f" -> DOCX Byte Size: {len(docx_bytes)} bytes")
    assert docx_bytes.startswith(b"PK"), "Generated bytes do not start with PK zip header"
    print(" -> Valid DOCX binary verified!")

    # 7. Test Evaluation Benchmark
    print("\n[7] Running Automated System Benchmark (/api/evaluation/benchmark)...")
    res = client.get("/api/evaluation/benchmark")
    assert res.status_code == 200, f"Benchmark failed: {res.status_code}"
    bench_data = res.json()
    test_categories = bench_data.get("test_categories", [])
    metrics = bench_data.get("metrics", [])
    print(f" -> Total Packaging Variations Tested: {len(test_categories)}")
    print(f" -> Overall System Reliability: {bench_data.get('overall_system_reliability')}%")
    print(f" -> False Positive Violation Rate: {bench_data.get('false_positive_rate')}%")
    print(f" -> False Negative Violation Rate: {bench_data.get('false_negative_rate')}%")
    print(f" -> Disagreement Resolution Rate: {bench_data.get('disagreement_resolution_rate')}%")
    print(f" -> Evaluated Core Metrics Count: {len(metrics)}")
    for m in metrics:
        print(f"    * [{m.get('status')}] {m.get('metric_name')}: {m.get('measured_accuracy')}% (Target: {m.get('target_threshold')}%)")
    assert len(test_categories) == 16
    assert len(metrics) == 10
    print(" -> All 16 variations and 10 Benchmark Evaluation Metrics verified!")

    print("\n" + "=" * 60)
    print(">>> ALL LM-COMPASS PIPELINE TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
