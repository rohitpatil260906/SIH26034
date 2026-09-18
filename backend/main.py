import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .models import (
    ImageQualityMetrics,
    ScanProcessRequest,
    ScanProcessResponse,
    ComplianceCheckItem,
    StructuredProductData
)
from .services.image_enhancement import (
    decode_base64_image,
    analyze_image_quality,
    enhance_image_for_ocr,
    encode_image_to_base64
)
from .services.ai_extraction import extract_structured_product_from_surfaces
from .services.rule_engine import evaluate_legal_metrology_rules

app = FastAPI(
    title="AI Legal Metrology Label Scanner API",
    description="Statutory Legal Metrology (Packaged Commodities) Rules 2011 AI label compliance engine",
    version="2.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory scan store
SCANS_DB: Dict[str, ScanProcessResponse] = {}

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Legal Metrology Label Inspection System API",
        "rules_supported": 34,
        "version": "2.0.0"
    }

@app.post("/api/scan/quality", response_model=ImageQualityMetrics)
def check_image_quality(payload: Dict[str, str]):
    """Analyzes image sharpness, blur, and lighting conditions."""
    image_data = payload.get("data")
    if not image_data:
        raise HTTPException(status_code=400, detail="Missing base64 image data")
    
    try:
        pil_img = decode_base64_image(image_data)
        metrics = analyze_image_quality(pil_img)
        return ImageQualityMetrics(**metrics)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Image processing error: {str(e)}")

@app.post("/api/scan/process", response_model=ScanProcessResponse)
def process_scan(request: ScanProcessRequest):
    """Processes single or multi-surface label images through the AI pipeline."""
    if not request.images:
        raise HTTPException(status_code=400, detail="At least one label image required")
    
    scan_id = f"SCAN-{uuid.uuid4().hex[:8].upper()}"
    surfaces_processed = list(set([img.get("surface", "Front (PDP)") for img in request.images]))
    
    # Analyze quality of the primary image
    quality_metrics = None
    first_img_data = request.images[0].get("data")
    if first_img_data and len(first_img_data) > 100:
        try:
            pil_img = decode_base64_image(first_img_data)
            q_dict = analyze_image_quality(pil_img)
            quality_metrics = ImageQualityMetrics(**q_dict)
        except Exception:
            pass

    # Extract structured product info across surfaces
    product_data, canonical_fields, extracted_lines = extract_structured_product_from_surfaces(
        request.images
    )
    
    # Evaluate 34 statutory rules
    compliance_checks, compliance_score, overall_status = evaluate_legal_metrology_rules(product_data)
    
    response = ScanProcessResponse(
        scan_id=scan_id,
        product_info=product_data,
        canonical_fields=canonical_fields,
        compliance_checks=compliance_checks,
        compliance_score=compliance_score,
        overall_status=overall_status,
        extracted_lines=extracted_lines,
        surfaces_processed=surfaces_processed,
        image_quality=quality_metrics,
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Cache in database
    SCANS_DB[scan_id] = response
    return response

@app.get("/api/scan/{scan_id}", response_model=ScanProcessResponse)
def get_scan(scan_id: str):
    """Retrieves an existing inspection docket."""
    if scan_id not in SCANS_DB:
        raise HTTPException(status_code=404, detail="Scan record not found")
    return SCANS_DB[scan_id]

@app.get("/api/rules")
def get_legal_rules():
    """Lists statutory rules 1 to 34."""
    from .services.rule_engine import evaluate_legal_metrology_rules
    # Return dummy baseline for rules catalog
    dummy = StructuredProductData()
    checks, _, _ = evaluate_legal_metrology_rules(dummy)
    return [
        {
            "rule_no": c.rule_no,
            "rule_title": c.rule_title,
            "sub_rule": c.sub_rule,
            "requirement": c.statutory_requirement,
            "penalty": c.section_penalty
        }
        for c in checks
    ]

@app.get("/api/reports/{scan_id}")
def get_statutory_report(scan_id: str):
    """Generates official inspection report summary."""
    if scan_id not in SCANS_DB:
        raise HTTPException(status_code=404, detail="Scan docket not found")
    scan = SCANS_DB[scan_id]
    infractions = [c for c in scan.compliance_checks if c.status == "FAIL"]
    reviews = [c for c in scan.compliance_checks if c.status == "NEEDS REVIEW"]
    
    return {
        "report_id": f"REP-{scan.scan_id}",
        "scan_id": scan.scan_id,
        "timestamp": scan.timestamp,
        "product_name": scan.product_info.product_name,
        "compliance_score": scan.compliance_score,
        "overall_status": scan.overall_status,
        "total_rules_evaluated": len(scan.compliance_checks),
        "infractions_count": len(infractions),
        "needs_review_count": len(reviews),
        "infractions": infractions,
        "notice_issuance_recommended": len(infractions) > 0
    }
