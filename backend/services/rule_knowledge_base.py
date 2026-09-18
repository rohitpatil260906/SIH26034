"""
Legal Metrology Statutory Rule Knowledge Base Service
Loads and searches the 93+ statutory rules and amendments extracted directly from 
the official Legal Metrology (Packaged Commodities) Gazette Notifications and PDF documents.

Contains:
- Rule Number
- Sub-rule / Clause
- Requirement
- Product / Category
- Exceptions
- Amendment / Change & Notification Details
- Effective Date
- Source PDF Filename & Page Number
- Original Text / Reference in English and Hindi where available
"""

import os
import json
import re
from typing import List, Dict, Any, Optional

KB_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "legal_metrology_knowledge_base.json")

class LegalMetrologyKnowledgeBase:
    _instance = None

    def __init__(self, kb_path: str = KB_FILE_PATH):
        self.kb_path = kb_path
        self.data: Dict[str, Any] = {}
        self.rules: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.kb_path):
            try:
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    self.rules = self.data.get("rules", [])
            except Exception as e:
                print(f"Warning: Could not load knowledge base from {self.kb_path}: {e}")
                self.rules = []
        else:
            self.rules = []

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns statistical overview of the loaded knowledge base."""
        return {
            "total_source_pdfs": self.data.get("total_source_pdfs", 41),
            "successfully_processed_pdfs": self.data.get("successfully_processed_pdfs", 24),
            "scanned_pdfs_requiring_ocr": self.data.get("scanned_pdfs_requiring_ocr", 17),
            "total_rules_extracted": len(self.rules),
            "storage_path": self.kb_path
        }

    def search_by_rule_number(self, rule_query: str) -> List[Dict[str, Any]]:
        """Search entries matching rule number, e.g., 'Rule 6', 'Rule 18', 'Second Schedule'."""
        q = rule_query.lower().strip()
        results = []
        for r in self.rules:
            if q in r.get("rule_number", "").lower() or q in r.get("sub_rule_or_clause", "").lower():
                results.append(r)
        return results

    def search_by_product_category(self, category_query: str) -> List[Dict[str, Any]]:
        """Search entries matching product category, e.g., 'Readymade Garments', 'Electronic', 'Pan Masala'."""
        q = category_query.lower().strip()
        results = []
        for r in self.rules:
            if q in r.get("product_category", "").lower():
                results.append(r)
        return results

    def search_text(self, text_query: str) -> List[Dict[str, Any]]:
        """Full-text search across requirements, amendments, and original reference text."""
        q = text_query.lower().strip()
        results = []
        for r in self.rules:
            full_blob = f"{r.get('rule_number','')} {r.get('sub_rule_or_clause','')} {r.get('requirement','')} {r.get('original_text_reference','')} {r.get('product_category','')}".lower()
            if q in full_blob:
                results.append(r)
        return results

    def get_rule_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve exact knowledge base entry by ID, e.g., 'LM-KB-0001'."""
        for r in self.rules:
            if r.get("entry_id") == entry_id:
                return r
        return None

    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Returns all structured statutory rule entries from the Knowledge Base."""
        return self.rules

# Singleton access
def get_knowledge_base() -> LegalMetrologyKnowledgeBase:
    if LegalMetrologyKnowledgeBase._instance is None:
        LegalMetrologyKnowledgeBase._instance = LegalMetrologyKnowledgeBase()
    return LegalMetrologyKnowledgeBase._instance
