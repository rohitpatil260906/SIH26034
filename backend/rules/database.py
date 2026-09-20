"""
Stage 8: Rule Engine Database & ORM Schemas
===========================================
Defines SQLite/SQLAlchemy tables for:
- rule_registry
- rule_versions
- rule_sources
- rule_applicability
- rule_evaluations
- rule_evidence
- rule_trace
- rule_exceptions
- rule_verification
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class RuleRegistryModel(Base):
    __tablename__ = "rule_registry"

    rule_id = Column(String(100), primary_key=True)
    act_name = Column(String(255), nullable=False)
    rules_name = Column(String(255), nullable=False)
    rule_number = Column(String(100), nullable=False)
    sub_rule = Column(String(100))
    clause = Column(String(100))
    title = Column(String(255), nullable=False)
    requirement_text = Column(Text, nullable=False)
    requirement_type = Column(String(50), default="DECLARATION")
    applicable_categories = Column(Text)  # JSON or comma-separated
    effective_from = Column(String(50))
    effective_until = Column(String(50))
    jurisdiction = Column(String(50), default="INDIA")
    source_name = Column(String(255))
    source_version = Column(String(50), default="2024.1")
    verification_status = Column(String(50), default="VERIFIED")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RuleEvaluationModel(Base):
    __tablename__ = "rule_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False)
    product_id = Column(String(100), nullable=False)
    rule_id = Column(String(100), ForeignKey("rule_registry.rule_id"))
    rule_number = Column(String(100))
    applicability_status = Column(String(50))
    evaluation_status = Column(String(50))
    confidence = Column(Float, default=0.90)
    rule_source = Column(String(255))
    rule_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class RuleTraceModel(Base):
    __tablename__ = "rule_traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("rule_evaluations.id"))
    rule_id = Column(String(100))
    observed_field = Column(String(100))
    observed_value = Column(Text)
    evaluation_status = Column(String(50))
    confidence = Column(Float)
    trace_steps = Column(Text)  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)
