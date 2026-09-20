"""
Stage 9: Database ORM Models
============================
SQLAlchemy ORM models for Stage 9 persistent storage:
- DBStage9Violation
- DBStage9Evidence
- DBStage9ReviewItem
- DBStage9Fingerprint
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DBStage9Violation(Base):
    __tablename__ = "stage9_violations"

    violation_id = Column(String(64), primary_key=True)
    product_id = Column(String(64), index=True, nullable=False)
    scan_id = Column(String(64), nullable=True)
    rule_id = Column(String(64), index=True, nullable=False)
    rule_number = Column(String(32), nullable=False)
    clause = Column(String(32), nullable=True)
    requirement = Column(Text, nullable=False)
    violation_type = Column(String(64), nullable=False)
    violation_status = Column(String(32), default="CONFIRMED", nullable=False)
    severity = Column(String(32), default="UNCLASSIFIED", nullable=False)
    description = Column(Text, nullable=False)
    observed_value = Column(Text, nullable=True)
    expected_condition = Column(Text, nullable=False)
    confidence = Column(Float, default=0.90)
    rule_source = Column(String(128), nullable=True)
    rule_version = Column(String(32), nullable=True)
    fingerprint = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    review_status = Column(String(32), default="NOT_REQUIRED")

    evidences = relationship("DBStage9Evidence", back_populates="violation", cascade="all, delete-orphan")


class DBStage9Evidence(Base):
    __tablename__ = "stage9_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    violation_id = Column(String(64), ForeignKey("stage9_violations.violation_id"), nullable=False)
    image_id = Column(String(64), nullable=True)
    product_id = Column(String(64), nullable=True)
    panel = Column(String(32), nullable=True)
    region_id = Column(String(64), nullable=True)
    original_bbox = Column(JSON, nullable=True)
    observed_text = Column(Text, nullable=True)
    normalized_value = Column(Text, nullable=True)
    semantic_field = Column(String(64), nullable=True)
    ocr_confidence = Column(Float, default=0.90)
    semantic_confidence = Column(Float, default=0.90)
    rule_evaluation_id = Column(String(64), nullable=True)
    evidence_confidence = Column(Float, default=0.90)

    violation = relationship("DBStage9Violation", back_populates="evidences")


class DBStage9ReviewItem(Base):
    __tablename__ = "stage9_review_items"

    review_id = Column(String(64), primary_key=True)
    product_id = Column(String(64), index=True, nullable=False)
    reason = Column(String(64), nullable=False)
    related_rule_id = Column(String(64), nullable=True)
    related_rule_number = Column(String(32), nullable=True)
    description = Column(Text, nullable=False)
    evidence_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
