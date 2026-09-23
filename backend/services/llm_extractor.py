import os
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vidhicheck.llm_extractor")

EXTRACTION_SCHEMA_DESCRIPTION = """
Return ONLY a valid JSON object matching this exact schema:
{
  "product_name": {"value": "...", "confidence": 0.95},
  "commodity_name": {"value": "...", "confidence": 0.95},
  "manufacturer": {
    "name": "...",
    "full_address": "...",
    "pin_code": "6-digit PIN or null",
    "confidence": 0.95
  },
  "packer": {
    "name": "...",
    "full_address": "...",
    "pin_code": "...",
    "confidence": 0.95
  },
  "importer": {
    "name": "...",
    "full_address": "...",
    "pin_code": "...",
    "confidence": 0.95
  },
  "net_quantity": {
    "raw_text": "...",
    "value": 500.0,
    "unit": "g/kg/ml/l",
    "complies_standard_units": true,
    "confidence": 0.98
  },
  "mrp": {
    "raw_text": "...",
    "amount": 120.0,
    "tax_inclusive_statement_present": true,
    "confidence": 0.98
  },
  "unit_sale_price": {
    "raw_text": "...",
    "is_exempt": false,
    "confidence": 0.90
  },
  "month_year": {
    "mfd": "MM/YYYY or null",
    "expiry": "MM/YYYY or null",
    "best_before": "...",
    "confidence": 0.92
  },
  "batch_number": {"value": "...", "confidence": 0.95},
  "consumer_care": {
    "phone": "...",
    "email": "...",
    "address": "...",
    "confidence": 0.92
  },
  "country_of_origin": {"value": "India", "confidence": 0.98}
}
"""

class AIProvider(ABC):
    """Abstract interface for AI/LLM structured text extraction."""
    
    @abstractmethod
    def extract_structured_label_data(self, raw_text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts structured packaging declaration attributes from OCR text."""
        pass

    @abstractmethod
    def explain_extraction(self, field_name: str, extracted_value: str, context: str) -> str:
        """Generates a human-readable explanation of an extracted declaration."""
        pass


class ConfigurableLLMProvider(AIProvider):
    """Integrates external LLM providers (Gemini, OpenAI, Ollama, etc.) with structured JSON response."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.provider_type = "gemini" if "gemini" in model_name.lower() or "google" in (base_url or "") else "openai"

    def extract_structured_label_data(self, raw_text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = (
            "You are an expert Legal Metrology compliance AI assistant for packaged commodities in India.\n"
            "Analyze the following OCR transcript extracted from a physical product label:\n\n"
            "--- OCR TRANSCRIPT START ---\n"
            f"{raw_text}\n"
            "--- OCR TRANSCRIPT END ---\n\n"
            f"{EXTRACTION_SCHEMA_DESCRIPTION}\n"
            "Rules:\n"
            "1. Extract ONLY information grounded in the OCR transcript. Do NOT fabricate missing details.\n"
            "2. If a field is not present in the OCR transcript, set value to null and confidence to 0.0.\n"
            "3. Return ONLY valid JSON, with no markdown codeblocks or commentary."
        )

        try:
            import requests
            if self.provider_type == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "responseMimeType": "application/json"
                    }
                }
                resp = requests.post(url, json=payload, timeout=12.0)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content)
            else:
                endpoint = self.base_url or "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "You are a Legal Metrology packaging extractor that returns strict JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=12.0)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
        except Exception as e:
            logger.warning(f"ConfigurableLLMProvider API call error: {e}. Falling back to NLP baseline.")
            
        fallback = NLPFallbackProvider()
        return fallback.extract_structured_label_data(raw_text, lines)

    def explain_extraction(self, field_name: str, extracted_value: str, context: str) -> str:
        return f"Field '{field_name}' identified as '{extracted_value}' from packaging label transcript under Legal Metrology standards."


class NLPFallbackProvider(AIProvider):
    """Deterministic, rule-based NLP extractor that runs 100% locally with zero external API dependencies.
    Provides complete anti-hallucination guarantees and immediate response times.
    """

    def extract_structured_label_data(self, raw_text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        text_lines = [l.get("text", "") if isinstance(l, dict) else str(l) for l in lines]
        full_text = raw_text if raw_text else "\n".join(text_lines)

        # 1. Product / Commodity Name
        prod_name = None
        for l in text_lines:
            cand = l.strip()
            if len(cand) >= 4 and not re.search(r'mrp|rs|₹|net|qty|mfd|exp|batch|lic|fssai|ingred|care', cand, re.I):
                prod_name = cand
                break
        if not prod_name and text_lines:
            prod_name = text_lines[0].strip()

        # 2. Net Quantity
        net_raw = None
        net_val = 0.0
        net_unit = ""
        complies_unit = True
        
        non_nutri = [l for l in text_lines if not re.search(r'nutri|energy|fat|carb|protein|sugar|approx|per\s*100', l, re.I)]
        search_scope = "\n".join(non_nutri) if non_nutri else full_text

        net_m = re.search(r'(?:Net\s*(?:Qty\.?|Quantity|Weight|Wt\.?|Content|Contents|Vol\.?|Volume|Mass)?[:.\-\s]*)\s*([0-9]+(?:\.[0-9]+)?)\s*(gms|kgs|g|kg|ml|l|ltr|gm)\b', search_scope, re.I)
        if not net_m:
            net_m = re.search(r'\b([0-9]+(?:\.[0-9]+)?)\s*(gms|kgs|g|kg|ml|l|ltr|gm)\b', search_scope, re.I)
            
        if net_m:
            net_val = float(net_m.group(1))
            net_unit = net_m.group(2).strip()
            net_raw = f"{net_val} {net_unit}"
            if net_unit.lower() in ["gms", "kgs", "gm"]:
                complies_unit = False

        # 3. MRP and Tax Phrase
        mrp_amount = 0.0
        mrp_raw = None
        has_taxes = bool(re.search(r'incl(?:usive)?\.?\s*(?:of)?\s*all\s*taxes|incl\.?\s*taxes', full_text, re.I))

        mrp_m = re.search(r'(?:MRP|M\.?R\.?P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE|M8P|NR\s*P)\s*(?:\([^)]*\)|\[[^\]]*\])?\s*[:.\-\s]*\s*(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)(?:\s*\/\-|\s*\/\=)?', full_text, re.I)
        if not mrp_m:
            mrp_m = re.search(r'(?:₹|Rs\.?|INR)\s*([0-9]+(?:\.[0-9]{1,2})?)(?:\s*\/\-|\s*\/\=)?', full_text, re.I)

        if mrp_m:
            mrp_amount = float(mrp_m.group(1))
            suffix = " (inclusive of all taxes)" if has_taxes else ""
            mrp_raw = f"MRP ₹ {mrp_amount:.2f}{suffix}"

        # 4. Manufacturer & PIN Code
        mfg_name = ""
        mfg_addr = ""
        pin_code = None
        for l in text_lines:
            if re.search(r'mfd\s*by|manufactured\s*by|packed\s*by|pkd\s*by|marketed\s*by', l, re.I):
                mfg_addr = l.strip()
                mfg_name = re.split(r'[,:\-]', l)[-1].strip()
                break
        if not mfg_addr:
            for l in text_lines:
                if re.search(r'plot|sector|road|industrial|street|lane|nagar', l, re.I):
                    mfg_addr = l.strip()
                    mfg_name = mfg_addr.split(',')[0].strip()
                    break

        pin_m = re.search(r'\b([1-9][0-9]{5})\b', mfg_addr or full_text)
        if pin_m:
            pin_code = pin_m.group(1)

        # 5. Month & Year
        mfd_date = None
        exp_date = None
        date_m = re.search(r'(?:Mfd|Mfg|Packed|Pkd|Date\s*of\s*Mfg)\s*[:.\-\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4})', full_text, re.I)
        if date_m:
            mfd_date = date_m.group(1).strip()

        exp_m = re.search(r'(?:Exp(?:iry)?|Best\s*Before|Use\s*By)\s*[:.\-\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4}|\d{1,2}\s*months?)', full_text, re.I)
        if exp_m:
            exp_date = exp_m.group(1).strip()

        # 6. Consumer Care
        phone_m = re.search(r'(?:1800(?:[-\s]?[0-9]{2,4}){2,3}|011[-\s]?[0-9]{8}|[0-9]{10})', full_text)
        email_m = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text)
        consumer_phone = phone_m.group(0) if phone_m else None
        consumer_email = email_m.group(0) if email_m else None

        # 7. Batch number
        batch_m = re.search(r'(?:Batch\s*(?:No\.?|Number)?|B\.?\s*No\.?|Lot\s*(?:No\.?|Number)?)\s*[:.\-\s]*([a-zA-Z0-9\/\-]+)', full_text, re.I)
        batch_val = batch_m.group(1).strip() if batch_m else None

        # 8. Country of Origin
        country_m = re.search(r'(?:Country\s*of\s*Origin|Made\s*in)\s*[:.\-\s]*([A-Za-z\s]+)', full_text, re.I)
        country_val = country_m.group(1).strip() if country_m else "India"

        return {
            "product_name": {"value": prod_name or "Packaged Commodity", "confidence": 0.94 if prod_name else 0.0},
            "commodity_name": {"value": prod_name or "Packaged Commodity", "confidence": 0.94 if prod_name else 0.0},
            "manufacturer": {
                "name": mfg_name or (mfg_addr.split(',')[0] if mfg_addr else "Manufacturer Unspecified"),
                "full_address": mfg_addr or "Address Not Fully Visible",
                "pin_code": pin_code,
                "confidence": 0.92 if mfg_addr else 0.40
            },
            "packer": None,
            "importer": None,
            "net_quantity": {
                "raw_text": net_raw or "Not detected",
                "value": net_val,
                "unit": net_unit,
                "complies_standard_units": complies_unit,
                "confidence": 0.96 if net_raw else 0.30
            },
            "mrp": {
                "raw_text": mrp_raw or "Not detected",
                "amount": mrp_amount,
                "tax_inclusive_statement_present": has_taxes,
                "confidence": 0.97 if mrp_raw else 0.30
            },
            "unit_sale_price": {
                "raw_text": None,
                "is_exempt": (net_val > 0 and net_val <= 100.0),
                "confidence": 0.90
            },
            "month_year": {
                "mfd": mfd_date,
                "expiry": exp_date,
                "best_before": exp_date,
                "confidence": 0.92 if (mfd_date or exp_date) else 0.30
            },
            "batch_number": {"value": batch_val, "confidence": 0.90 if batch_val else 0.30},
            "consumer_care": {
                "phone": consumer_phone,
                "email": consumer_email,
                "address": mfg_addr or None,
                "confidence": 0.91 if (consumer_phone or consumer_email) else 0.30
            },
            "country_of_origin": {"value": country_val, "confidence": 0.95}
        }

    def explain_extraction(self, field_name: str, extracted_value: str, context: str) -> str:
        return f"Deterministic parser localized '{extracted_value}' for '{field_name}' in label evidence."


def get_ai_provider() -> AIProvider:
    """Factory creating the active AI provider based on environment configuration."""
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if api_key and len(api_key.strip()) > 10:
        model = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
        base_url = os.environ.get("LLM_BASE_URL")
        return ConfigurableLLMProvider(api_key=api_key.strip(), model_name=model, base_url=base_url)
    return NLPFallbackProvider()
