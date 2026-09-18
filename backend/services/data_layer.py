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
