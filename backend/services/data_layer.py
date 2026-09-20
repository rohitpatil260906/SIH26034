import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True)
SQLITE_DB_PATH = os.path.join(DB_DIR, "vidhicheck.db")

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------------------------------------
# POSTGRESQL / SQLALCHEMY MODELS
# ----------------------------------------------------

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    badge_number = Column(String(64), nullable=False)
    role = Column(String(32), default="OFFICER")
    department = Column(String(128), default="Legal Metrology Department")
    zone = Column(String(64), default="North Zone")
    email = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    status = Column(String(32), default="Active")
    last_active = Column(DateTime, default=datetime.utcnow)

class CaseDocketModel(Base):
    __tablename__ = "cases"
    id = Column(String(64), primary_key=True, index=True)
    inspection_id = Column(String(64), index=True)
    product_name = Column(String(256), nullable=False)
    brand = Column(String(128), default="")
    manufacturer = Column(String(256), default="")
    status = Column(String(32), default="Active")
    overall_status = Column(String(32), default="COMPLIANT")
    compliance_score = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    officer_id = Column(String(64), default="OFF-2026-DEL-0842")
    docket_json = Column(Text, default="{}")
    officer_notes = Column(Text, default="")
    final_decision = Column(String(64), default="Draft")

class ExtractedFieldModel(Base):
    __tablename__ = "extracted_fields"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), index=True)
    field_name = Column(String(64), nullable=False)
    statutory_name = Column(String(128), default="")
    extracted_value = Column(Text, default="")
    ocr_confidence = Column(Float, default=0.95)
    overall_confidence = Column(Float, default=0.95)
    status = Column(String(32), default="Found")
    rule_reference = Column(String(64), default="")
    surface = Column(String(64), default="Front (PDP)")
    bbox_json = Column(Text, default="{}")

class ViolationModel(Base):
    __tablename__ = "violations"
    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), index=True)
    rule_reference = Column(String(64), nullable=False)
    violation_type = Column(String(128), nullable=False)
    statutory_clause = Column(String(128), default="")
    description = Column(Text, default="")
    severity = Column(String(32), default="Medium")
    penal_section = Column(String(128), default="Section 36(1)")
    recommended_penalty = Column(String(128), default="Compounding fee: ₹25,000")
    status = Column(String(32), default="Active")

class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    officer_name = Column(String(128), default="Enforcement Officer")
    action = Column(String(128), nullable=False)
    module = Column(String(64), nullable=False)
    record_id = Column(String(64), nullable=False)
    status = Column(String(32), default="Success")
    details = Column(Text, default="")

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-migrate SQLite columns if missing
try:
    with engine.connect() as _conn:
        _cur = _conn.connection.cursor()
        _cur.execute("PRAGMA table_info(cases)")
        _existing_cols = [c[1] for c in _cur.fetchall()]
        if "docket_json" not in _existing_cols:
            _cur.execute("ALTER TABLE cases ADD COLUMN docket_json TEXT DEFAULT '{}'")
        if "officer_notes" not in _existing_cols:
            _cur.execute("ALTER TABLE cases ADD COLUMN officer_notes TEXT DEFAULT ''")
        if "final_decision" not in _existing_cols:
            _cur.execute("ALTER TABLE cases ADD COLUMN final_decision VARCHAR(64) DEFAULT 'Draft'")
        _conn.connection.commit()
except Exception as _mig_err:
    print(f"Schema migration note: {_mig_err}")

# ----------------------------------------------------
# ELASTICSEARCH ABSTRACTION (FULL-TEXT OCR SEARCH)
# ----------------------------------------------------

LOCAL_SEARCH_INDEX: List[Dict[str, Any]] = []

def index_inspection_document(
    scan_id: str,
    product_name: str,
    manufacturer: str,
    ocr_text: str,
    overall_status: str,
    compliance_score: int
) -> Dict[str, Any]:
    """Indexes inspection document and OCR transcript in Elasticsearch (or local index fallback)."""
    doc = {
        "scan_id": scan_id,
        "product_name": product_name,
        "manufacturer": manufacturer,
        "ocr_text": ocr_text,
        "overall_status": overall_status,
        "compliance_score": compliance_score,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Try live Elasticsearch if configured
    es_host = os.environ.get("ELASTICSEARCH_HOST")
    if es_host:
        try:
            from elasticsearch import Elasticsearch
            es = Elasticsearch(es_host)
            if es.ping():
                es.index(index="lm_inspections", id=scan_id, document=doc)
                return {"backend": "Elasticsearch", "status": "Indexed"}
        except Exception:
            pass
            
    # Local in-memory / file fallback
    LOCAL_SEARCH_INDEX.append(doc)
    return {"backend": "Local Search Index", "status": "Indexed"}

def search_indexed_dockets(query: str) -> List[Dict[str, Any]]:
    """Searches indexed dockets by product, manufacturer or OCR text."""
    q_lower = query.lower()
    results = []
    for doc in LOCAL_SEARCH_INDEX:
        if (
            q_lower in doc.get("product_name", "").lower() or
            q_lower in doc.get("manufacturer", "").lower() or
            q_lower in doc.get("ocr_text", "").lower() or
            q_lower in doc.get("scan_id", "").lower()
        ):
            results.append(doc)
    return results

# ----------------------------------------------------
# REDIS ABSTRACTION (CACHE & QUEUE)
# ----------------------------------------------------

LOCAL_CACHE: Dict[str, Any] = {}
LOCAL_QUEUE: List[Dict[str, Any]] = []

def set_cache_value(key: str, value: Any, ttl_seconds: int = 3600):
    """Sets cache in Redis (or in-memory fallback)."""
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.setex(key, ttl_seconds, json.dumps(value))
            return
        except Exception:
            pass
    LOCAL_CACHE[key] = {"data": value, "expires_at": time.time() + ttl_seconds}

def get_cache_value(key: str) -> Optional[Any]:
    """Gets cached value from Redis (or in-memory fallback)."""
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            val = r.get(key)
            if val:
                return json.loads(val)
        except Exception:
            pass
            
    item = LOCAL_CACHE.get(key)
    if item and item["expires_at"] > time.time():
        return item["data"]
    return None

# ----------------------------------------------------
# EXTERNAL GOVERNMENT VERIFICATION ABSTRACTION
# ----------------------------------------------------

def verify_with_external_government_source(
    identifier_type: str,
    identifier_value: str
) -> Dict[str, Any]:
    """External verification abstraction.
    
    STRICT ANTI-FABRICATION RULE:
    If no verified official government API is actively connected and permitted:
    Returns strictly:
    'External verification: Not available'
    """
    api_endpoint = os.environ.get("GOVT_LEGAL_METROLOGY_API_URL")
    if api_endpoint:
        try:
            import requests
            resp = requests.get(f"{api_endpoint}/verify/{identifier_type}/{identifier_value}", timeout=3.0)
            if resp.status_code == 200:
                return {
                    "status": "VERIFIED_OFFICIAL",
                    "source": "Ministry of Consumer Affairs Legal Metrology Registry",
                    "data": resp.json()
                }
        except Exception:
            pass
            
    return {
        "status": "NOT_AVAILABLE",
        "message": "External verification: Not available",
        "verified_at": None,
        "is_fabricated": False
    }

# ----------------------------------------------------
# DATABASE CRUD & DASHBOARD HELPERS
# ----------------------------------------------------

def save_case_docket(docket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves or updates a complete inspection docket in the SQLite database."""
    scan_id = docket_data.get("scan_id") or docket_data.get("id")
    if not scan_id:
        raise ValueError("scan_id is required")

    prod_info = docket_data.get("product_info") or {}
    prod_name = docket_data.get("product_name") or docket_data.get("productName") or (prod_info.get("product_name") if isinstance(prod_info, dict) else None) or "Packaged Commodity"
    brand = docket_data.get("brand") or (prod_info.get("brand") if isinstance(prod_info, dict) else "") or ""
    mfg_info = prod_info.get("manufacturer") or {}
    mfg_addr = mfg_info.get("full_address") if isinstance(mfg_info, dict) else str(mfg_info)
    if not mfg_addr:
        mfg_addr = docket_data.get("manufacturer") or ""

    overall_status = docket_data.get("overall_status") or docket_data.get("status") or "COMPLIANT"
    compliance_score = int(docket_data.get("compliance_score") or docket_data.get("complianceScore") or 100)
    officer_notes = docket_data.get("officer_notes") or docket_data.get("officerNotes") or ""
    final_decision = docket_data.get("final_decision") or docket_data.get("finalDecision") or "Draft"

    db = SessionLocal()
    try:
        existing = db.query(CaseDocketModel).filter(CaseDocketModel.id == scan_id).first()
        if existing:
            existing.product_name = prod_name
            existing.brand = brand
            existing.manufacturer = mfg_addr
            existing.overall_status = overall_status
            existing.compliance_score = compliance_score
            existing.officer_notes = officer_notes
            existing.final_decision = final_decision
            existing.docket_json = json.dumps(docket_data)
        else:
            new_docket = CaseDocketModel(
                id=scan_id,
                inspection_id=scan_id,
                product_name=prod_name,
                brand=brand,
                manufacturer=mfg_addr,
                status="Completed",
                overall_status=overall_status,
                compliance_score=compliance_score,
                officer_notes=officer_notes,
                final_decision=final_decision,
                docket_json=json.dumps(docket_data)
            )
            db.add(new_docket)
        db.commit()
        return {"scan_id": scan_id, "status": "Saved", "timestamp": datetime.utcnow().isoformat()}
    finally:
        db.close()

def list_case_dockets(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Lists saved inspection dockets from SQLite."""
    db = SessionLocal()
    try:
        rows = db.query(CaseDocketModel).order_by(CaseDocketModel.created_at.desc()).offset(offset).limit(limit).all()
        results = []
        for r in rows:
            docket = {}
            if r.docket_json and r.docket_json != "{}":
                try:
                    docket = json.loads(r.docket_json)
                except Exception:
                    pass
            results.append({
                "id": r.id,
                "scan_id": r.id,
                "product_name": r.product_name,
                "brand": r.brand,
                "manufacturer": r.manufacturer,
                "overall_status": r.overall_status,
                "status": "Non-Compliant" if r.overall_status in ["NON_COMPLIANT", "Non-Compliant"] else ("Compliant" if r.overall_status in ["COMPLIANT", "Compliant"] else "Under Review"),
                "compliance_score": r.compliance_score,
                "officer_notes": r.officer_notes,
                "final_decision": r.final_decision,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "docket": docket
            })
        return results
    finally:
        db.close()

def get_case_docket_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single docket by ID."""
    db = SessionLocal()
    try:
        r = db.query(CaseDocketModel).filter(CaseDocketModel.id == case_id).first()
        if not r:
            return None
        docket = {}
        if r.docket_json and r.docket_json != "{}":
            try:
                docket = json.loads(r.docket_json)
            except Exception:
                pass
        return {
            "id": r.id,
            "scan_id": r.id,
            "product_name": r.product_name,
            "brand": r.brand,
            "manufacturer": r.manufacturer,
            "overall_status": r.overall_status,
            "compliance_score": r.compliance_score,
            "officer_notes": r.officer_notes,
            "final_decision": r.final_decision,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "docket": docket
        }
    finally:
        db.close()

def delete_case_docket(case_id: str) -> bool:
    """Deletes a case docket and associated fields/violations."""
    db = SessionLocal()
    try:
        r = db.query(CaseDocketModel).filter(CaseDocketModel.id == case_id).first()
        if not r:
            return False
        db.query(ExtractedFieldModel).filter(ExtractedFieldModel.case_id == case_id).delete()
        db.query(ViolationModel).filter(ViolationModel.case_id == case_id).delete()
        db.delete(r)
        db.commit()
        return True
    finally:
        db.close()

def get_dashboard_metrics() -> Dict[str, Any]:
    """Calculates live dashboard statistics directly from SQLite database."""
    db = SessionLocal()
    try:
        total_scans = db.query(CaseDocketModel).count()
        compliant_count = db.query(CaseDocketModel).filter(CaseDocketModel.overall_status.in_(["COMPLIANT", "Compliant"])).count()
        non_compliant_count = db.query(CaseDocketModel).filter(CaseDocketModel.overall_status.in_(["NON_COMPLIANT", "Non-Compliant"])).count()
        review_count = db.query(CaseDocketModel).filter(CaseDocketModel.overall_status.in_(["NEEDS_REVIEW", "Under Review", "Needs Review"])).count()
        violations_count = db.query(ViolationModel).count()

        compliance_rate = round((compliant_count / total_scans * 100), 1) if total_scans > 0 else 0.0

        recent_rows = db.query(CaseDocketModel).order_by(CaseDocketModel.created_at.desc()).limit(5).all()
        recent_scans = [
            {
                "id": r.id,
                "product_name": r.product_name,
                "overall_status": r.overall_status,
                "compliance_score": r.compliance_score,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in recent_rows
        ]

        return {
            "total_scans": total_scans,
            "compliant_count": compliant_count,
            "non_compliant_count": non_compliant_count,
            "review_count": review_count,
            "violations_count": violations_count,
            "compliance_rate": compliance_rate,
            "recent_scans": recent_scans
        }
    finally:
        db.close()

