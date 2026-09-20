import re
from typing import List, Dict, Any, Tuple, Optional

class DeclarationClassifier:
    """Classifies raw text lines into Legal Metrology statutory declaration categories."""

    DECLARATION_TAXONOMY = {
        "MRP": [r'\bmrp\b', r'm\.r\.p', r'retail\s*price', r'₹', r'rs\.?', r'inr', r'incl.*taxes'],
        "NET_QUANTITY": [r'net\s*qty', r'net\s*wt', r'net\s*content', r'net\s*volume', r'\b(?:g|kg|ml|l|ltr|gms|kgs)\b'],
        "MANUFACTURER": [r'mfd\s*by', r'manufactured\s*by', r'marketed\s*by', r'mfg\b', r'factory', r'plot\s*no', r'industrial\s*area'],
        "PACKER": [r'packed\s*by', r'pkd\s*by', r'packer\b', r'packaging\s*unit'],
        "IMPORTER": [r'imported\s*by', r'import\s*license', r'importer\b', r'country\s*of\s*origin'],
        "CONSUMER_CARE": [r'consumer\s*care', r'customer\s*care', r'toll\s*free', r'helpline', r'care@', r'feedback', r'complaints'],
        "DATE_DECLARATION": [r'mfd[:.\s]', r'mfg[:.\s]', r'packed[:.\s]', r'pkd[:.\s]', r'exp[:.\s]', r'expiry', r'best\s*before', r'use\s*by'],
        "BATCH_NUMBER": [r'batch\s*no', r'b\.?\s*no', r'lot\s*no', r'batch\b', r'lot\b'],
        "COUNTRY_OF_ORIGIN": [r'country\s*of\s*origin', r'made\s*in', r'origin[:\s]'],
        "INGREDIENTS": [r'ingredients?[:\s]', r'composition', r'contains\b'],
        "BARCODE_EAN": [r'\b890[0-9]{10}\b', r'ean-?13', r'barcode']
    }

    def predict_line_category(self, line_text: str) -> Tuple[str, float]:
        """Returns (predicted_category, confidence) for a text line."""
        text = line_text.strip().lower()
        if not text:
            return "OTHER", 0.0

        scores = {}
        for category, patterns in self.DECLARATION_TAXONOMY.items():
            matched = 0
            for pat in patterns:
                if re.search(pat, text):
                    matched += 1
            if matched > 0:
                # Score based on pattern match density
                scores[category] = min(0.95, 0.60 + (matched * 0.15))

        if not scores:
            return "OTHER", 0.30

        best_category = max(scores, key=scores.get)
        return best_category, scores[best_category]

    def classify_all_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Classifies an entire sequence of OCR lines."""
        results = []
        for idx, line in enumerate(lines):
            category, conf = self.predict_line_category(line)
            results.append({
                "line_index": idx + 1,
                "text": line,
                "predicted_category": category,
                "confidence": conf
            })
        return results


class ProductCategoryClassifier:
    """Classifies a commodity into statutory Legal Metrology Schedule domains."""

    CATEGORY_SIGNATURES = {
        "Cosmetics & Personal Care": [
            "spf", "sunscreen", "gel", "cream", "lotion", "shampoo", "soap",
            "serum", "face wash", "perfume", "deodorant", "moisturizer", "cosmetic"
        ],
        "Food & Beverages": [
            "oil", "mustard", "edible", "biscuit", "cookie", "tea", "coffee",
            "flour", "atta", "rice", "salt", "spice", "juice", "drink", "snack",
            "fssai", "nutritional", "energy", "protein", "carbohydrate", "fat"
        ],
        "Household Cleaning & Detergents": [
            "detergent", "powder", "washing", "bleach", "disinfectant", "cleaner",
            "floor cleaner", "toilet cleaner", "dishwash", "bar"
        ],
        "General Packaged Commodity": []
    }

    def predict_category(self, text_corpus: str, product_name: str = "") -> Tuple[str, float]:
        corpus = f"{product_name} {text_corpus}".lower()
        scores = {}
        for cat, keywords in self.CATEGORY_SIGNATURES.items():
            if not keywords:
                continue
            hits = sum(1 for kw in keywords if re.search(rf'\b{re.escape(kw)}\b', corpus))
            if hits > 0:
                scores[cat] = min(0.98, 0.65 + (hits * 0.10))

        if not scores:
            return "General Packaged Commodity", 0.70

        best_cat = max(scores, key=scores.get)
        return best_cat, scores[best_cat]


class RiskConfidenceModule:
    """Calculates risk level, anomaly scores, and flags items requiring human physical verification."""

    def evaluate_risk(
        self,
        ocr_confidence: float,
        extracted_fields: Dict[str, Any],
        has_violations: bool,
        is_blurred: bool = False
    ) -> Dict[str, Any]:
        risk_score = 0.0
        review_reasons = []

        if is_blurred:
            risk_score += 0.40
            review_reasons.append("Low optical clarity or motion blur detected on surface.")

        if ocr_confidence < 0.70:
            risk_score += 0.30
            review_reasons.append("Mean OCR text confidence is below acceptable 70% threshold.")

        # Check critical fields
        net_qty = extracted_fields.get("net_quantity", {})
        if isinstance(net_qty, dict) and not net_qty.get("complies_standard_units", True):
            risk_score += 0.35
            review_reasons.append("Prohibited non-standard metric unit detected (Rule 13).")

        mrp = extracted_fields.get("mrp", {})
        if isinstance(mrp, dict) and not mrp.get("tax_inclusive_statement_present", True):
            risk_score += 0.30
            review_reasons.append("Missing statutory '(inclusive of all taxes)' declaration.")

        if has_violations:
            risk_score += 0.30

        normalized_risk = min(1.0, round(risk_score, 2))
        risk_rating = "HIGH" if normalized_risk >= 0.60 else ("MEDIUM" if normalized_risk >= 0.35 else "LOW")
        requires_human_review = (normalized_risk >= 0.40 or ocr_confidence < 0.75 or is_blurred)

        return {
            "risk_rating": risk_rating,
            "risk_score": normalized_risk,
            "requires_human_review": requires_human_review,
            "review_reasons": review_reasons
        }


class MLService:
    """Unified facade coordinating declaration classification, category prediction, and risk evaluation."""

    def __init__(self):
        self.declaration_classifier = DeclarationClassifier()
        self.category_classifier = ProductCategoryClassifier()
        self.risk_module = RiskConfidenceModule()

    def process_ml_pipeline(
        self,
        lines: List[str],
        raw_transcript: str,
        product_name: str,
        extracted_fields: Dict[str, Any],
        mean_ocr_conf: float,
        is_blurred: bool = False
    ) -> Dict[str, Any]:
        classified_lines = self.declaration_classifier.classify_all_lines(lines)
        category, cat_conf = self.category_classifier.predict_category(raw_transcript, product_name)
        risk = self.risk_module.evaluate_risk(
            ocr_confidence=mean_ocr_conf,
            extracted_fields=extracted_fields,
            has_violations=False,
            is_blurred=is_blurred
        )

        return {
            "classified_lines": classified_lines,
            "predicted_category": category,
            "category_confidence": cat_conf,
            "risk_assessment": risk
        }

# Global singleton
ml_service = MLService()
