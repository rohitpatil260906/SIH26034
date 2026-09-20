"""
Stage 3: Corporate Entity, Brand, & Address Semantic Interpreter
================================================================
Interprets commercial organizations, brand names, and addresses:
- MANUFACTURER_NAME vs PACKER_NAME vs MARKETER_NAME vs IMPORTER_NAME
- BRAND_NAME (Never automatically assumed to be Manufacturer)
- MANUFACTURER_ADDRESS / PACKER_ADDRESS / MARKETER_ADDRESS
- POSTAL_PIN (Strictly guarded: a standalone 6-digit number without address context is NOT a PIN)
- CRITICAL SHIELD: An INGREDIENTS section must NEVER become an ADDRESS!
"""

import re
from typing import Dict, Any, Tuple, Optional, List
from ...models import Stage3CandidateType


class EntityInterpretationService:
    """Disambiguates corporate organizations, brands, addresses, and PIN codes."""

    ORG_SUFFIX_REGEX = re.compile(
        r'\b(?:pvt\.?\s*ltd\.?|private\s+limited|ltd\.?|limited|llp|inc\.?|corp\.?|corporation|industries|enterprises|laboratories|labs|foods|pharma|cosmetics|confectionery|beverages|products)\b',
        re.I
    )

    ADDRESS_KEYWORD_REGEX = re.compile(
        r'\b(?:plot|survey|khasra|building|floor|bldg|industrial\s+area|ind\.\s*area|g\.?i\.?d\.?c\.?|m\.?i\.?d\.?c\.?|estate|sector|phase|nagar|marg|road|street|lane|chowk|village|dist\.?|district|taluka|tehsil|near|opp\.?|opposite|post|p\.?o\.?|state)\b',
        re.I
    )

    PIN_CODE_REGEX = re.compile(
        r'\b([1-9][0-9]{5})\b'
    )

    INDIAN_STATES = {
        "maharashtra", "delhi", "karnataka", "tamil nadu", "gujarat", "uttar pradesh",
        "west bengal", "rajasthan", "telangana", "andhra pradesh", "kerala", "punjab",
        "haryana", "bihar", "odisha", "assam", "goa", "madhya pradesh", "jharkhand",
        "uttarakhand", "himachal pradesh", "mumbai", "bengaluru", "chennai", "kolkata",
        "hyderabad", "pune", "ahmedabad", "gurugram", "noida", "new delhi"
    }

    def interpret_entity_or_address(
        self,
        text: str,
        section_type: str = "OTHER",
        heading_type: Optional[str] = None
    ) -> Tuple[str, str, float, List[Stage3CandidateType]]:
        """Interprets whether a text region represents an organization, address, PIN, or brand.
        
        Returns:
            (semantic_type, extracted_value, confidence, candidate_types)
        """
        # CRITICAL REGRESSION SHIELD:
        # INGREDIENTS must NEVER become an ADDRESS or COMPANY!
        if section_type == "INGREDIENTS":
            return "INGREDIENTS", text.strip(), 0.98, [
                Stage3CandidateType(type="INGREDIENTS", confidence=0.98)
            ]

        # 1. Postal PIN Evaluation
        pin_match = self.PIN_CODE_REGEX.search(text)
        has_pin = pin_match is not None
        pin_val = pin_match.group(1) if pin_match else ""

        # Standalone 6-digit number with no surrounding address keywords or company
        clean_text = text.strip()
        if has_pin and clean_text == pin_val:
            # Standalone 6-digit number without address context
            # MUST NOT automatically classify as PIN!
            if heading_type in ("MANUFACTURER_ADDRESS", "PACKER_ADDRESS", "MARKETER_ADDRESS", "ADDRESS") or section_type in ("MANUFACTURER_INFORMATION", "PACKER_INFORMATION", "MARKETER_INFORMATION"):
                return "POSTAL_PIN", pin_val, 0.90, [
                    Stage3CandidateType(type="POSTAL_PIN", confidence=0.90),
                    Stage3CandidateType(type="BATCH_NUMBER", confidence=0.10)
                ]
            else:
                return "UNKNOWN", pin_val, 0.40, [
                    Stage3CandidateType(type="POSTAL_PIN", confidence=0.45),
                    Stage3CandidateType(type="PRODUCT_CODE", confidence=0.35),
                    Stage3CandidateType(type="BATCH_NUMBER", confidence=0.20)
                ]

        # 2. Corporate Organization Name
        has_org_suffix = self.ORG_SUFFIX_REGEX.search(text) is not None
        if has_org_suffix:
            if heading_type == "MARKETER_NAME" or re.search(r'\b(?:marketed\s+by|mkt\s+by)\b', text, re.I):
                clean_name = re.sub(r'^(?:marketed\s+by|mkt\s+by)[:\s\-]*', '', text, flags=re.I).strip()
                return "MARKETER_NAME", clean_name, 0.98, [
                    Stage3CandidateType(type="MARKETER_NAME", confidence=0.98),
                    Stage3CandidateType(type="MANUFACTURER_NAME", confidence=0.02)
                ]
            elif heading_type == "PACKER_NAME" or re.search(r'\b(?:packed\s+by|pkd\s+by)\b', text, re.I):
                clean_name = re.sub(r'^(?:packed\s+by|pkd\s+by)[:\s\-]*', '', text, flags=re.I).strip()
                return "PACKER_NAME", clean_name, 0.98, [
                    Stage3CandidateType(type="PACKER_NAME", confidence=0.98),
                    Stage3CandidateType(type="MANUFACTURER_NAME", confidence=0.02)
                ]
            elif heading_type == "IMPORTER_NAME" or re.search(r'\b(?:imported\s+by|imp\s+by)\b', text, re.I):
                clean_name = re.sub(r'^(?:imported\s+by|imp\s+by)[:\s\-]*', '', text, flags=re.I).strip()
                return "IMPORTER_NAME", clean_name, 0.98, [
                    Stage3CandidateType(type="IMPORTER_NAME", confidence=0.98)
                ]
            elif heading_type == "MANUFACTURER_NAME" or re.search(r'\b(?:manufactured\s+by|mfd\s+by|produced\s+by)\b', text, re.I):
                clean_name = re.sub(r'^(?:manufactured\s+by|mfd\s+by|produced\s+by)[:\s\-]*', '', text, flags=re.I).strip()
                return "MANUFACTURER_NAME", clean_name, 0.98, [
                    Stage3CandidateType(type="MANUFACTURER_NAME", confidence=0.98),
                    Stage3CandidateType(type="MARKETER_NAME", confidence=0.02)
                ]
            elif section_type == "MARKETER_INFORMATION":
                return "MARKETER_NAME", text.strip(), 0.95, [Stage3CandidateType(type="MARKETER_NAME", confidence=0.95)]
            elif section_type == "PACKER_INFORMATION":
                return "PACKER_NAME", text.strip(), 0.95, [Stage3CandidateType(type="PACKER_NAME", confidence=0.95)]
            elif section_type == "MANUFACTURER_INFORMATION":
                return "MANUFACTURER_NAME", text.strip(), 0.95, [Stage3CandidateType(type="MANUFACTURER_NAME", confidence=0.95)]
            else:
                # Company without role label
                return "MANUFACTURER_NAME", text.strip(), 0.80, [
                    Stage3CandidateType(type="MANUFACTURER_NAME", confidence=0.50),
                    Stage3CandidateType(type="MARKETER_NAME", confidence=0.30),
                    Stage3CandidateType(type="PACKER_NAME", confidence=0.20)
                ]

        # 3. Address Identification
        has_addr_kw = self.ADDRESS_KEYWORD_REGEX.search(text) is not None
        has_state = any(s in text.lower() for s in self.INDIAN_STATES)

        if has_addr_kw or (has_state and has_pin) or (has_state and "," in text):
            # Check role from section or heading
            if heading_type == "MARKETER_NAME" or section_type == "MARKETER_INFORMATION":
                addr_type = "MARKETER_ADDRESS"
            elif heading_type == "PACKER_NAME" or section_type == "PACKER_INFORMATION":
                addr_type = "PACKER_ADDRESS"
            elif heading_type == "IMPORTER_NAME" or section_type == "IMPORTER_INFORMATION":
                addr_type = "IMPORTER_ADDRESS"
            else:
                addr_type = "MANUFACTURER_ADDRESS"

            return addr_type, text.strip(), 0.94, [
                Stage3CandidateType(type=addr_type, confidence=0.94),
                Stage3CandidateType(type="REGISTERED_ADDRESS", confidence=0.80)
            ]

        # 4. Postal PIN inside multi-token line
        if has_pin and (has_state or has_addr_kw):
            return "POSTAL_PIN", pin_val, 0.95, [
                Stage3CandidateType(type="POSTAL_PIN", confidence=0.95)
            ]

        # Inconclusive
        return "UNKNOWN", text.strip(), 0.20, []
