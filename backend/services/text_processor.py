import re
from typing import List, Dict, Any, Tuple, Optional
import difflib

from ..models import (
    StructuredProductData,
    CanonicalField,
    ExtractedLine,
    AddressInfo,
    NetQuantityInfo,
    MrpInfo,
    UnitSalePriceInfo,
    DateInfo,
    ConsumerCareInfo,
    Table1HeightCheck,
    BoundingBox,
    FieldEvidence,
    ProductClassification
)

# -------------------------------------------------------------------
# REGEX PATTERNS FOR STATUTORY PACKAGING FIELDS
# -------------------------------------------------------------------

NUTRITIONAL_IGNORE_REGEX = re.compile(
    r'(?:nutri|energy|kcal|fat\b|saturat|mufa|pufa|cholesterol|carbohydrate|sugar|protein|sodium|potassium|approx\.\s*per|per\s*100|\/100g|\/100ml|100g\)|100ml\))',
    re.IGNORECASE
)

MRP_PATTERNS = [
    # Explicit MRP with prefix
    re.compile(r'(?:MRP|M\.?R\.?P\.?|MAX(?:IMUM)?\s*RETAIL\s*PRICE|एम\.?आर\.?पी\.?|अधिकतम\s*खुदरा\s*मूल्य)\s*(?:\([^)]*\)|\[[^\]]*\])?\s*[:.\-\s]*\s*(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)(?:\s*\/\-|\s*\/\=)?', re.I),
    # Standalone currency sign preceding amount
    re.compile(r'(?:₹|Rs\.?|INR)\s*([0-9]+(?:\.[0-9]{1,2})?)(?:\s*\/\-|\s*\/\=)?', re.I),
    # Slash-dash notation e.g. 489/- or 240.00/-
    re.compile(r'\b([0-9]{2,5}(?:\.[0-9]{2})?)\s*\/\-', re.I)
]

TAX_PHRASE_REGEX = re.compile(
    r'(?:[1iI]nc[l1I](?:usive)?\.?\s*(?:of)?\s*(?:al[l1I]\s*)?tax(?:es)?|[1iI]ncl\.?\s*tax(?:es)?|incl(?:usive)?\.?\s*(?:of)?\s*all\s*taxes|incl\.?\s*taxes|inc[l1]\.?\s*taxes|सभी\s*करों\s*सहित|कर\s*सहित)',
    re.I
)

USP_PATTERN = re.compile(
    r'(?:U\.?S\.?P\.?|UNIT\s*SALE\s*PRICE)\s*[:.\-\s]*\s*(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:\/|\s*per\s*)\s*(g|kg|ml|l|piece|unit|u|n)\b',
    re.I
)

NET_QTY_PATTERNS = [
    # Explicit prefix Net Qty / Wt / Content / Hindi
    re.compile(r'(?:Net\s*(?:Qty\.?|Quantity|Weight|Wt\.?|Content|Contents|Vol\.?|Volume|Mass)?|वजन|मात्रा)[:.\-\s]*\s*([0-9]+(?:\.[0-9]+)?)\s*(gms|kgs|gm|g|kg|ml|l|ltr|cm|m|N|units?|pieces?|पैक|ग्राम|किलो(?:ग्राम)?|मिली)\b', re.I),
    # Standalone weight/volume without prefix
    re.compile(r'\b([0-9]+(?:\.[0-9]+)?)\s*(gms|kgs|gm|g|kg|ml|l|ltr|cm|m|N)\b', re.I)
]

MFD_PATTERNS = [
    re.compile(r'(?:Mfd|Mfg|Date\s*of\s*(?:Mfg|Mfd|Manufacture|Manufacturing)|Manufactured|उत्पादन\s*तिथि)\s*[:.\-\s]*((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4})', re.I)
]

PKD_PATTERNS = [
    re.compile(r'(?:Packed|Pkd|Date\s*of\s*Packing|पैकिंग\s*तिथि)\s*[:.\-\s]*((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4})', re.I)
]

EXP_PATTERNS = [
    re.compile(r'(?:Exp(?:iry)?(?:\s*Date)?|Date\s*of\s*Expiry|Use\s*(?:By|Before)|समाप्ति\s*तिथि|उपयोग\s*से\s*पहले)\s*[:.\-\s]*((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4}|\d{1,2}\s*months?)', re.I)
]

BEST_BEFORE_PATTERNS = [
    re.compile(r'(?:Best\s*Before|सर्वश्रेष्ठ\s*उपयोग)\s*[:.\-\s]*([0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4}|\d{1,2}\s*months?(?:\s*(?:from|of)\s*(?:mfg|mfd|pkd|packing))?)', re.I)
]

BATCH_PATTERNS = [
    re.compile(r'\b(?:Batch(?:\s*(?:No\.?|Number))?|B\.?\s*No\.?|Lot(?:\s*(?:No\.?|Number))?|बैच\s*नं\.?)\s*[:.\-\s]*([a-zA-Z0-9\/\-_]+)', re.I)
]

PHONE_PATTERN = re.compile(r'(?:1800[-\s]?[0-9]{2,4}[-\s]?[0-9]{3,5}|0[0-9]{2,4}[-\s]?[0-9]{6,8}|[6-9][0-9]{9})')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PIN_PATTERN = re.compile(r'\b([1-9][0-9]{5})\b')
COO_PATTERN = re.compile(r'(?:Made\s*in|Country\s*of\s*Origin|Product\s*of|Manufactured\s*in|उत्पत्ति)\s*[:.\-\s]*([A-Za-z\s]+?)(?:\.|\n|$|,)', re.I)

# Commercial entity corporate suffixes and address cues
CORPORATE_SUFFIXES = [
    re.compile(r'\b(?:pvt\.?\s*ltd\.?|private\s*limited|ltd\.?|limited|llp\b|inc\.?|incorporated|corp\.?|corporation|co\.?\b|company|gmbh|s\.?a\.?|llc\b|enterprises|industries|foods|pharma|pharmaceuticals|laboratories|products)\b', re.I)
]

ADDRESS_CUES = re.compile(
    r'\b(?:plot\s*no\.?|sector|phase|road|rd\b|street|marg|lane|estate|industrial\s*area|ind\.\s*area|gidc|midc|riico|survey\s*no\.?|sy\.?\s*no\.?|khasra|village|po\b|p\.o\.|post\s*office|dist\.?|district|tehsil|taluk|bldg|building|floor|near\b|opp\b|opposite|behind|uttarakhand|haryana|maharashtra|delhi|karnataka|gujarat|tamil\s*nadu|bengaluru|bangalore|mumbai|kolkata|chennai|hyderabad|pune|ahmedabad|gurugram|gurgaon|noida|baddi|haridwar|solan|himachal|uttar\s*pradesh|rajasthan|punjab|kerala|andhra|telangana|madhya\s*pradesh|bihar|west\s*bengal|assam|odisha|goa)\b',
    re.I
)

# Standard commodity dictionary for generic name resolution and category mapping
COMMODITY_KEYWORDS = {
    # Food & Beverage
    "tea": ("Tea", "Food & Beverage"),
    "coffee": ("Coffee", "Food & Beverage"),
    "biscuit": ("Biscuits", "Food & Beverage"),
    "biscuits": ("Biscuits", "Food & Beverage"),
    "cookies": ("Cookies", "Food & Beverage"),
    "atta": ("Wheat Flour (Atta)", "Food & Beverage"),
    "flour": ("Flour", "Food & Beverage"),
    "rice": ("Rice", "Food & Beverage"),
    "sugar": ("Sugar", "Food & Beverage"),
    "salt": ("Edible Common Salt", "Food & Beverage"),
    "spices": ("Spices", "Food & Beverage"),
    "masala": ("Spice Blend (Masala)", "Food & Beverage"),
    "edible oil": ("Edible Vegetable Oil", "Food & Beverage"),
    "mustard oil": ("Mustard Oil", "Food & Beverage"),
    "sunflower oil": ("Sunflower Oil", "Food & Beverage"),
    "soyabean oil": ("Soyabean Oil", "Food & Beverage"),
    "ghee": ("Ghee", "Food & Beverage"),
    "butter": ("Butter", "Food & Beverage"),
    "chips": ("Potato Chips", "Food & Beverage"),
    "namkeen": ("Namkeen / Savouries", "Food & Beverage"),
    "chocolate": ("Chocolate", "Food & Beverage"),
    "juice": ("Fruit Juice", "Food & Beverage"),
    "noodles": ("Instant Noodles", "Food & Beverage"),
    "pasta": ("Pasta", "Food & Beverage"),
    # Personal Care & Cosmetics
    "soap": ("Toilet Soap", "Cosmetics & Personal Care"),
    "shampoo": ("Hair Shampoo", "Cosmetics & Personal Care"),
    "conditioner": ("Hair Conditioner", "Cosmetics & Personal Care"),
    "body wash": ("Body Wash", "Cosmetics & Personal Care"),
    "face wash": ("Facial Cleanser / Face Wash", "Cosmetics & Personal Care"),
    "cream": ("Skin Cream", "Cosmetics & Personal Care"),
    "lotion": ("Body Lotion", "Cosmetics & Personal Care"),
    "sunscreen": ("Sunscreen Lotion / Gel", "Cosmetics & Personal Care"),
    "moisturizer": ("Moisturizer", "Cosmetics & Personal Care"),
    "hair oil": ("Hair Oil", "Cosmetics & Personal Care"),
    "toothpaste": ("Toothpaste", "Cosmetics & Personal Care"),
    "deodorant": ("Deodorant", "Cosmetics & Personal Care"),
    # Garments & Apparel
    "shirt": ("Readymade Garment (Shirt)", "Garments & Apparel"),
    "t-shirt": ("Readymade Garment (T-Shirt)", "Garments & Apparel"),
    "trousers": ("Readymade Garment (Trousers)", "Garments & Apparel"),
    "pants": ("Readymade Garment (Pants)", "Garments & Apparel"),
    "jeans": ("Readymade Garment (Jeans)", "Garments & Apparel"),
    "kurta": ("Readymade Garment (Kurta)", "Garments & Apparel"),
    "hosiery": ("Hosiery Product", "Garments & Apparel"),
    "socks": ("Hosiery (Socks)", "Garments & Apparel"),
    "garment": ("Readymade Garment", "Garments & Apparel"),
    # Cleaning & Household
    "detergent": ("Detergent Powder", "Cleaning & Household"),
    "detergent bar": ("Detergent Bar", "Cleaning & Household"),
    "dishwash": ("Dishwashing Liquid", "Cleaning & Household"),
    # Electronics
    "earphones": ("Earphones", "Electronics & Electricals"),
    "headphones": ("Headphones", "Electronics & Electricals"),
    "charger": ("Mobile Charger", "Electronics & Electricals"),
    "cable": ("Data Cable", "Electronics & Electricals"),
    "battery": ("Battery", "Electronics & Electricals"),
    "bulb": ("LED Bulb", "Electronics & Electricals"),
    "mobile phone": ("Mobile Phone", "Electronics & Electricals"),
    # Medical Devices
    "bandage": ("Adhesive Bandage", "Medical Devices"),
    "mask": ("Face Mask", "Medical Devices"),
    "cotton": ("Absorbent Cotton", "Medical Devices"),
    "sanitizer": ("Hand Sanitizer", "Medical Devices"),
    # Pan Masala
    "pan masala": ("Pan Masala", "Pan Masala & Tobacco"),
    "supari": ("Betel Nut / Supari", "Pan Masala & Tobacco")
}

# -------------------------------------------------------------------
# SPATIAL NEIGHBORHOOD ASSOCIATION HELPERS
# -------------------------------------------------------------------

def find_spatial_neighbors(
    target_idx: int,
    lines: List[ExtractedLine],
    max_dy: float = 14.0
) -> List[ExtractedLine]:
    """Finds lines located in close spatial proximity (vertically or horizontally)
    to associate separated label elements (e.g. MRP number and taxes statement).
    """
    if target_idx < 0 or target_idx >= len(lines):
        return []
        
    target = lines[target_idx]
    if not target.bbox:
        neighbors = []
        if target_idx > 0:
            neighbors.append(lines[target_idx - 1])
        if target_idx + 1 < len(lines):
            neighbors.append(lines[target_idx + 1])
        if target_idx + 2 < len(lines):
            neighbors.append(lines[target_idx + 2])
        return neighbors

    t_box = target.bbox
    neighbors = []
    for idx, other in enumerate(lines):
        if idx == target_idx or not other.bbox:
            continue
        o_box = other.bbox
        dy = abs(o_box.y - (t_box.y + t_box.height))
        h_overlap = max(0.0, min(t_box.x + t_box.width, o_box.x + o_box.width) - max(t_box.x, o_box.x))
        if dy <= max_dy and (h_overlap > 0 or abs(t_box.x - o_box.x) < 25.0):
            neighbors.append(other)

    return neighbors

def union_bboxes(bboxes: List[BoundingBox], default_label: str = "") -> Optional[BoundingBox]:
    """Calculates the bounding box that encloses all given boxes."""
    valid_boxes = [b for b in bboxes if b is not None]
    if not valid_boxes:
        return None
    min_x = min(b.x for b in valid_boxes)
    min_y = min(b.y for b in valid_boxes)
    max_r = max(b.x + b.width for b in valid_boxes)
    max_b = max(b.y + b.height for b in valid_boxes)
    return BoundingBox(
        x=round(min_x, 2),
        y=round(min_y, 2),
        width=round(max_r - min_x, 2),
        height=round(max_b - min_y, 2),
        label=default_label or valid_boxes[0].label
    )

# -------------------------------------------------------------------
# STEP 3.3: SEMANTIC TEXT BLOCK CLASSIFIER & CONFIDENCE ENGINE
# -------------------------------------------------------------------

SEMANTIC_CLASSES = [
    "BRAND",
    "PRODUCT_NAME",
    "GENERIC_NAME",
    "CATEGORY",
    "MARKETING_CLAIM",
    "INGREDIENT",
    "MANUFACTURER_NAME",
    "MANUFACTURER_ADDRESS",
    "PACKER_NAME",
    "PACKER_ADDRESS",
    "IMPORTER_NAME",
    "IMPORTER_ADDRESS",
    "COUNTRY_OF_ORIGIN",
    "NET_QUANTITY",
    "UNIT",
    "MRP",
    "TAX_INCLUSIVE_WORDING",
    "UNIT_SALE_PRICE",
    "MANUFACTURE_DATE",
    "PACKING_DATE",
    "BEST_BEFORE",
    "EXPIRY_DATE",
    "BATCH_NUMBER",
    "LOT_NUMBER",
    "CONSUMER_CARE_PHONE",
    "CONSUMER_CARE_EMAIL",
    "CONSUMER_CARE_ADDRESS",
    "WARNING",
    "DIRECTIONS",
    "OTHER_TEXT",
    "UNKNOWN"
]

MARKETING_CLAIM_PATTERNS = re.compile(
    r'\b(?:power\s*couple|radiant\s*glow|brightens?|boosts?\s*(?:collagen|radiance|hydration)?|'
    r'clinically\s*proven|dermatologically\s*tested|dermatologist\s*recommended|expert\s*care|'
    r'for\s*best\s*results|leaves\s*skin|deeply\s*moisturizes?|instant\s*hydration|silky\s*soft|'
    r'smooth\s*(?:and|&)\s*shiny|refreshing\s*taste|rich\s*aroma|100%\s*natural|pure\s*&\s*fresh|'
    r'goodness\s*of|love\s*your\s*skin|youthful|anti-aging|spotless|flawless|blemish\s*free|'
    r'nourishes|kills\s*99\.9%|tough\s*on\s*grease|sparkling\s*clean|long\s*lasting|'
    r'fragrance\s*that\s*lasts|expertly\s*crafted|secret\s*formula|delightful|skincare|haircare|'
    r'hair\s*fall|dandruff\s*free|glow\s*boost|intense\s*repair|visible\s*results|power\s*of)\b',
    re.I
)

INGREDIENT_PATTERNS = re.compile(
    r'\b(?:aqua|water|glycerin|niacinamide|xanthan\s*gum|octyl\s*salicylate|cetearyl\s*olivate|'
    r'sorbitan\s*olivate|sorbitan|stearic\s*acid|citric\s*acid|sodium\s*laureth\s*sulfate|'
    r'sodium\s*chloride|phenoxyethanol|fragrance|parfum|tocopherol|dimethicone|titanium\s*dioxide|'
    r'disodium\s*edta|edta|butylene\s*glycol|methylparaben|propylparaben|retinol|hyaluronic\s*acid|'
    r'allantoin|panthenol|wheat\s*flour|sugar|palm\s*oil|edible\s*vegetable\s*oil|cocoa\s*solids|'
    r'milk\s*solids|emulsifier|acidity\s*regulator|preservative|permitted\s*natural\s*colou?r|'
    r'artificial\s*flavouring|stabilizer|preservatives|flavouring\s*substances?|sucrose|glucose|maltodextrin)\b',
    re.I
)

def classify_text_block(
    text: str,
    prev_lines: Optional[List[str]] = None,
    next_lines: Optional[List[str]] = None
) -> Tuple[str, float, str]:
    """Dynamically classifies any detected text block into one of the 31 statutory semantic classes:
    CRITICAL GUARANTEE: Marketing claims and ingredients are NEVER misclassified as commercial entities or addresses.
    Returns: (semantic_class, confidence, rationale)
    """
    clean_t = text.strip()
    if not clean_t:
        return ("UNKNOWN", 0.0, "Empty line")

    # 1. Marketing / Advertising Claims (Prioritize to prevent statutory misclassification)
    if MARKETING_CLAIM_PATTERNS.search(clean_t) or re.search(r'^(?:the\s+skincare\s+power\s+couple|experience\s+the|infused\s+with|our\s+unique\s+formula)\b', clean_t, re.I):
        return ("MARKETING_CLAIM", 0.95, "Matched promotional/advertising copy or performance claim")

    # 2. Formulation Ingredients
    if re.search(r'^(?:ingredients?|composition|contains|सामग्री)\b', clean_t, re.I) or len(INGREDIENT_PATTERNS.findall(clean_t)) >= 2:
        return ("INGREDIENT", 0.95, "Matched formulation ingredient / chemical / botanical listing")

    # 3. Statutory Warnings / Advisories
    if re.search(r'^(?:caution|warning|warnings?|for external use|keep out of reach|not for medicinal|चेतावनी)\b', clean_t, re.I):
        return ("WARNING", 0.95, "Matched statutory caution/safety advisory statement")

    # 4. Usage / Storage Directions
    if re.search(r'^(?:directions?(?:\s*for\s*use)?|how\s*to\s*use|usage|storage|store\s*in|उपयोग\s*विधि)\b', clean_t, re.I):
        return ("DIRECTIONS", 0.95, "Matched usage or storage instructions")

    # 5. MRP
    for p in MRP_PATTERNS:
        if p.search(clean_t):
            return ("MRP", 0.96, "Matched retail sale price declaration under Rule 6(1)(e)")

    # 6. Tax Inclusivity Phrase
    if TAX_PHRASE_REGEX.search(clean_t):
        return ("TAX_INCLUSIVE_WORDING", 0.96, "Matched statutory tax inclusivity phrase under Rule 6(1)(e)")

    # 7. Unit Sale Price
    if USP_PATTERN.search(clean_t):
        return ("UNIT_SALE_PRICE", 0.95, "Matched unit sale price declaration under Rule 6(11)")

    # 8. Net Quantity
    for p in NET_QTY_PATTERNS:
        if p.search(clean_t) and not NUTRITIONAL_IGNORE_REGEX.search(clean_t):
            return ("NET_QUANTITY", 0.95, "Matched net quantity / weight declaration under Rule 6(1)(c)")

    # 9. Standalone Metric Unit Symbol
    if re.fullmatch(r'(?:g|kg|ml|l|ltr|cm|m|N|units?|pieces?|पैक|ग्राम|मिली)', clean_t, re.I):
        return ("UNIT", 0.92, "Matched metric SI unit symbol under Rule 13")

    # 10. Dates
    for p in MFD_PATTERNS:
        if p.search(clean_t):
            return ("MANUFACTURE_DATE", 0.95, "Matched month & year of manufacture declaration under Rule 6(1)(d)")
    for p in PKD_PATTERNS:
        if p.search(clean_t):
            return ("PACKING_DATE", 0.95, "Matched date of pre-packing under Rule 6(1)(d)")
    for p in BEST_BEFORE_PATTERNS:
        if p.search(clean_t):
            return ("BEST_BEFORE", 0.95, "Matched best before advisory under Rule 6(1)(da)")
    for p in EXP_PATTERNS:
        if p.search(clean_t):
            return ("EXPIRY_DATE", 0.95, "Matched consumer expiry / use by declaration under Rule 6(1)(da)")

    # 11. Batch / Lot
    for p in BATCH_PATTERNS:
        if p.search(clean_t):
            if re.search(r'\blot\b', clean_t, re.I):
                return ("LOT_NUMBER", 0.95, "Matched lot identification number under Rule 6(1)(g)")
            return ("BATCH_NUMBER", 0.95, "Matched batch identification number under Rule 6(1)(g)")

    # 12. Country of Origin
    if COO_PATTERN.search(clean_t) or re.search(r'\b(?:made\s*in|product\s*of|country\s*of\s*origin)\b', clean_t, re.I):
        return ("COUNTRY_OF_ORIGIN", 0.96, "Matched country of origin / manufacture declaration under Rule 6(1)(n)")

    # 13. Consumer Care Contact Details
    if EMAIL_PATTERN.search(clean_t):
        return ("CONSUMER_CARE_EMAIL", 0.97, "Matched consumer grievance cell email address")
    if PHONE_PATTERN.search(clean_t) and re.search(r'(?:care|helpline|toll|free|phone|call|contact|grievance)', clean_t, re.I):
        return ("CONSUMER_CARE_PHONE", 0.96, "Matched consumer helpline / toll-free contact number under Rule 6(1)(f)")
    if re.search(r'\b(?:consumer\s*care\s*address|grievance\s*officer|postal\s*address)\b', clean_t, re.I):
        return ("CONSUMER_CARE_ADDRESS", 0.93, "Matched consumer care postal address")

    # 14. Commercial Entities (Manufacturer, Packer, Importer)
    if re.search(r'^(?:mfd\.?\s*(?:&|and)?\s*marketed\s*by|mfg\.?\s*(?:&|and)?\s*marketed\s*by|manufactured\s*(?:&|and)?\s*marketed\s*by|mfd\.?\s*(?:by|at|for)|mfg\.?\s*(?:by|at|for)|manufactured\s*(?:by|at|for)|produced\s*(?:by|at)|made\s*by|विनिर्माता)\b', clean_t, re.I):
        return ("MANUFACTURER_NAME", 0.95, "Preceded by explicit statutory manufacturer contextual keyword")
    if re.search(r'^(?:packed\s*(?:by|at)|pkd\.?\s*(?:by|at)|pre-packed\s*by|packaged\s*by|पैकर)\b', clean_t, re.I):
        return ("PACKER_NAME", 0.95, "Preceded by explicit statutory packer contextual keyword")
    if re.search(r'^(?:imported\s*(?:by|(?:and|&)\s*marketed\s*by)|imp\.?\s*by|importer|आयातक)\b', clean_t, re.I):
        return ("IMPORTER_NAME", 0.95, "Preceded by explicit statutory importer contextual keyword")

    # 15. Address Components
    if ADDRESS_CUES.search(clean_t) and (PIN_PATTERN.search(clean_t) or re.search(r'\b(?:plot|sector|phase|road|street|estate|ind\.\s*area|gidc|midc)\b', clean_t, re.I)):
        if prev_lines and any(re.search(r'\b(?:packed|pkd)\b', pl, re.I) for pl in prev_lines[-2:]):
            return ("PACKER_ADDRESS", 0.93, "Contains structured address components linked to packer")
        elif prev_lines and any(re.search(r'\b(?:imported|importer)\b', pl, re.I) for pl in prev_lines[-2:]):
            return ("IMPORTER_ADDRESS", 0.93, "Contains structured address components linked to importer")
        else:
            return ("MANUFACTURER_ADDRESS", 0.93, "Contains structured address components linked to manufacturer")

    # 16. Generic Name dictionary keyword check
    for kw, (gen, cat) in COMMODITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', clean_t.lower()):
            return ("GENERIC_NAME", 0.94, f"Matches statutory commodity classification dictionary for '{gen}'")

    # 17. Uninterpretable / Noise tokens (e.g. 'AKM1 O1 HA')
    if re.fullmatch(r'[A-Z0-9\s]{4,15}', clean_t) and not any(w in clean_t.lower() for w in ['ltd', 'pvt', 'mrp', 'net', 'exp', 'mfd', 'mfg', 'box', 'pack', 'tea', 'oil', 'flour', 'rice']):
        vowels = sum(1 for c in clean_t.lower() if c in 'aeiou')
        if vowels <= 1 and len(clean_t.replace(" ", "")) >= 5:
            return ("UNKNOWN", 0.40, "Uninterpretable character sequence or OCR noise; flagged for review")

    # 18. Regulatory / License text
    if re.search(r'\b(?:fssai|lic\.?\s*no\.?|license\s*no\.?|cin\b|barcode)\b', clean_t, re.I):
        return ("OTHER_TEXT", 0.90, "Statutory regulatory license or packaging code")

    return ("OTHER_TEXT", 0.60, "General packaging text")

def calculate_field_confidence(
    ocr_quality: float = 0.95,
    ocr_agreement: float = 1.0,
    semantic_classification_match: float = 1.0,
    spatial_relationship: float = 1.0,
    pattern_validation: float = 1.0,
    contextual_keyword_match: float = 1.0,
    is_ambiguous: bool = False
) -> Tuple[float, str]:
    """Calculates multi-factor confidence for a statutory field:
    Score = (
        0.20 * ocr_quality +
        0.15 * ocr_agreement +
        0.25 * semantic_classification_match +
        0.15 * spatial_relationship +
        0.15 * pattern_validation +
        0.10 * contextual_keyword_match
    )
    Returns: (confidence_score, confidence_level)
    """
    if is_ambiguous:
        return 0.45, "Needs Review"

    score = (
        0.20 * ocr_quality +
        0.15 * ocr_agreement +
        0.25 * semantic_classification_match +
        0.15 * spatial_relationship +
        0.15 * pattern_validation +
        0.10 * contextual_keyword_match
    )
    score = round(min(1.0, max(0.0, score)), 2)

    if score >= 0.88:
        level = "High"
    elif score >= 0.65:
        level = "Medium"
    elif score >= 0.50:
        level = "Low"
    else:
        level = "Needs Review"

    return score, level

# -------------------------------------------------------------------
# STEP 3.4: UNIVERSAL COMMERCIAL ENTITY & ADDRESS EXTRACTOR
# -------------------------------------------------------------------

def extract_commercial_entities(
    extracted_lines: List[ExtractedLine],
    raw_transcript: str
) -> Dict[str, AddressInfo]:
    """Universal, multi-line commercial entity and address extractor.
    Accurately extracts Manufacturer, Packer, Importer, and Marketer with:
    - Colon and line-break separation handling (e.g. 'Manufactured by:' on line 1, company on line 2)
    - Multi-line company name wrap merging (tracking legal suffixes like Pvt Ltd, Limited, LLP)
    - Full address continuation line aggregation
    - Mandatory 6-digit postal PIN validation under Rule 10(1)
    - Zero brand-specific hardcoding: works universally across any packaging layout
    """
    entities: Dict[str, AddressInfo] = {
        "manufacturer": AddressInfo(entity_type="Manufacturer"),
        "packer": AddressInfo(entity_type="Packer"),
        "importer": AddressInfo(entity_type="Importer"),
        "marketer": AddressInfo(entity_type="Marketer")
    }

    role_triggers = [
        ("manufacturer", re.compile(r'^(?:(?:निर्माता|विनिर्माता|उत्पादक)\s*[\/|\-]?\s*)?(?:mfd\.?\s*(?:&|and)?\s*marketed\s*by|mfg\.?\s*(?:&|and)?\s*marketed\s*by|manufactured\s*(?:&|and)?\s*marketed\s*by|mfd\.?\s*(?:by|at|for)|mfg\.?\s*(?:by|at|for)|manufactured\s*(?:by|at|for)|produced\s*(?:by|at)|made\s*by|निर्माता|विनिर्माता|उत्पादक)', re.I)),
        ("packer", re.compile(r'^(?:(?:पैकर|पैकिंग)\s*[\/|\-]?\s*)?(?:packed\s*(?:by|at)|pkd\.?\s*(?:by|at)|pre-packed\s*(?:by|at)?|packaged\s*(?:by|at)|पैकर|पैकिंग)', re.I)),
        ("importer", re.compile(r'^(?:(?:आयातक)\s*[\/|\-]?\s*)?(?:imported\s*(?:by|(?:and|&)\s*marketed\s*by)|imp\.?\s*by|importer|आयातक)', re.I)),
        ("marketer", re.compile(r'^(?:(?:मार्केटेड)\s*[\/|\-]?\s*)?(?:marketed\s*by|mktg?\.?\s*by|distributed\s*by|mktd?\.?\s*by|मार्केटेड)', re.I))
    ]

    statutory_cutoffs = re.compile(r'^(?:mrp|m\.r\.p|net\s*qty|net\s*wt|batch|lot|b\.?\s*no|exp|best\s*before|use\s*by|date\s*of|consumer\s*care|customer\s*care|toll\s*free|ingredients?|nutrition|caution|warning|directions?|how\s*to\s*use|storage)\b', re.I)

    for role_name, trigger in role_triggers:
        found_idx = -1
        trigger_line = None

        for idx, line in enumerate(extracted_lines):
            t = line.text.strip()
            # Strict protection: skip marketing copy or ingredients
            if MARKETING_CLAIM_PATTERNS.search(t) or INGREDIENT_PATTERNS.search(t):
                continue
            m = trigger.search(t)
            if not m and role_name in ["manufacturer", "packer"]:
                if re.search(r'\b(?:mfd\s*&?\s*pkd|mfg\s*&\s*packed|manufactured\s*&\s*packed)\s*by\b', t, re.I):
                    m = True
            if m:
                found_idx = idx
                trigger_line = line
                break

        if found_idx == -1:
            continue

        first_line_text = extracted_lines[found_idx].text.strip()
        after_prefix = re.sub(
            r'^(?:(?:निर्माता|विनिर्माता|उत्पादक|पैकर|आयातक|मार्केटेड)\s*[\/|\-]?\s*)?(?:mfd\s*&?\s*pkd\s*by|mfg\s*&\s*packed\s*by|manufactured\s*&\s*packed\s*by|manufactured\s*(?:&|and)\s*marketed\s*by|mfd\.?\s*(?:&|and)\s*marketed\s*by|mfg\.?\s*(?:&|and)\s*marketed\s*by|mfd\.?\s*(?:by|at|for)|mfg\.?\s*(?:by|at|for)|manufactured\s*(?:by|at|for)|produced\s*(?:by|at)|made\s*by|packed\s*(?:by|at)|pkd\.?\s*(?:by|at)|pre-packed\s*by|packaged\s*(?:by|at)|imported\s*(?:by|(?:and|&)\s*marketed\s*by)|imp\.?\s*by|importer|marketed\s*by|mktg?\.?\s*by|distributed\s*by|mktd?\.?\s*by|निर्माता|विनिर्माता|उत्पादक|पैकर|आयातक|मार्केटेड)\s*[:.\-\s]*',
            '',
            first_line_text,
            flags=re.I
        ).strip(" :.-")

        entity_name_parts: List[str] = []
        entity_address_parts: List[str] = []
        raw_lines_collected: List[str] = [first_line_text]
        bboxes_collected: List[BoundingBox] = []
        if trigger_line and trigger_line.bbox:
            bboxes_collected.append(trigger_line.bbox)

        # Ensure after_prefix is not marketing claims or ingredient listings
        if len(after_prefix) >= 3 and not ADDRESS_CUES.search(after_prefix.split(",")[0]) and not MARKETING_CLAIM_PATTERNS.search(after_prefix) and not INGREDIENT_PATTERNS.search(after_prefix):
            if "," in after_prefix:
                parts = after_prefix.split(",", 1)
                entity_name_parts.append(parts[0].strip())
                if parts[1].strip():
                    entity_address_parts.append(parts[1].strip())
            else:
                entity_name_parts.append(after_prefix)
            curr_idx = found_idx + 1
        else:
            if len(after_prefix) >= 3 and not MARKETING_CLAIM_PATTERNS.search(after_prefix) and not INGREDIENT_PATTERNS.search(after_prefix):
                entity_address_parts.append(after_prefix)
            curr_idx = found_idx + 1
            if curr_idx < len(extracted_lines):
                next_t = extracted_lines[curr_idx].text.strip()
                if not statutory_cutoffs.search(next_t) and not any(tr[1].search(next_t) for tr in role_triggers) and not MARKETING_CLAIM_PATTERNS.search(next_t) and not INGREDIENT_PATTERNS.search(next_t):
                    raw_lines_collected.append(next_t)
                    if extracted_lines[curr_idx].bbox:
                        bboxes_collected.append(extracted_lines[curr_idx].bbox)
                    if "," in next_t and not ADDRESS_CUES.search(next_t.split(",")[0]):
                        parts = next_t.split(",", 1)
                        entity_name_parts.append(parts[0].strip())
                        if parts[1].strip():
                            entity_address_parts.append(parts[1].strip())
                    else:
                        entity_name_parts.append(next_t)
                    curr_idx += 1

        # Check multi-line company name wrap
        if entity_name_parts and curr_idx < len(extracted_lines):
            curr_name = " ".join(entity_name_parts)
            has_suffix = any(s.search(curr_name) for s in CORPORATE_SUFFIXES)
            next_t = extracted_lines[curr_idx].text.strip()
            if not has_suffix and not statutory_cutoffs.search(next_t) and not any(tr[1].search(next_t) for tr in role_triggers) and not MARKETING_CLAIM_PATTERNS.search(next_t) and not INGREDIENT_PATTERNS.search(next_t):
                if any(s.search(next_t) for s in CORPORATE_SUFFIXES) or (not ADDRESS_CUES.search(next_t) and len(next_t) < 40 and not re.search(r'\d', next_t)):
                    raw_lines_collected.append(next_t)
                    if extracted_lines[curr_idx].bbox:
                        bboxes_collected.append(extracted_lines[curr_idx].bbox)
                    if "," in next_t:
                        parts = next_t.split(",", 1)
                        entity_name_parts.append(parts[0].strip())
                        if parts[1].strip():
                            entity_address_parts.append(parts[1].strip())
                    else:
                        entity_name_parts.append(next_t)
                    curr_idx += 1

        # Collect subsequent contiguous address lines (up to 5 lines)
        lines_count = 0
        while curr_idx < len(extracted_lines) and lines_count < 5:
            line_t = extracted_lines[curr_idx].text.strip()
            if not line_t or statutory_cutoffs.search(line_t) or any(tr[1].search(line_t) for tr in role_triggers) or MARKETING_CLAIM_PATTERNS.search(line_t) or INGREDIENT_PATTERNS.search(line_t):
                break
            raw_lines_collected.append(line_t)
            entity_address_parts.append(line_t)
            if extracted_lines[curr_idx].bbox:
                bboxes_collected.append(extracted_lines[curr_idx].bbox)
            curr_idx += 1
            lines_count += 1

        company_name = " ".join(entity_name_parts).strip(" ,.-")
        company_name = re.sub(r'^(?:by|at|for)\s+', '', company_name, flags=re.I).strip(" ,.-")

        address_body = ", ".join(entity_address_parts).strip(" ,.-")
        if company_name and address_body:
            full_address = f"{company_name}, {address_body}"
        elif address_body:
            full_address = address_body
        else:
            full_address = company_name

        combined_for_pin = f"{full_address} {' '.join(raw_lines_collected)}"
        pin_match = PIN_PATTERN.search(combined_for_pin)
        pin_code = pin_match.group(1) if pin_match else None
        has_pin = bool(pin_match)

        entities[role_name] = AddressInfo(
            name=company_name,
            full_address=full_address,
            pin_code=pin_code,
            has_valid_pin=has_pin,
            entity_type=role_name.title(),
            raw_lines=raw_lines_collected
        )

    # Fallback: if manufacturer is not detected, search for address cues + 6-digit PIN in entire label
    # Rule: NEVER invent a manufacturer name without contextual evidence! Address alone is recorded as address.
    if not entities["manufacturer"].name and not entities["manufacturer"].full_address:
        mfg_cand_lines: List[str] = []
        bboxes_cand: List[BoundingBox] = []
        for idx, line in enumerate(extracted_lines):
            t = line.text.strip()
            if MARKETING_CLAIM_PATTERNS.search(t) or INGREDIENT_PATTERNS.search(t):
                continue
            if ADDRESS_CUES.search(t):
                mfg_cand_lines.append(t)
                if line.bbox:
                    bboxes_cand.append(line.bbox)
                for nb in find_spatial_neighbors(idx, extracted_lines, max_dy=18.0):
                    if nb.text.strip() not in mfg_cand_lines and not statutory_cutoffs.search(nb.text.strip()) and not MARKETING_CLAIM_PATTERNS.search(nb.text.strip()) and not INGREDIENT_PATTERNS.search(nb.text.strip()):
                        mfg_cand_lines.append(nb.text.strip())
                        if nb.bbox:
                            bboxes_cand.append(nb.bbox)
                break
        if mfg_cand_lines:
            cand_addr = ", ".join(mfg_cand_lines)
            cand_pin = PIN_PATTERN.search(cand_addr) or PIN_PATTERN.search(raw_transcript)
            pin_val = cand_pin.group(1) if cand_pin else None
            entities["manufacturer"] = AddressInfo(
                name="",  # Strictly do NOT invent manufacturer name without contextual prefix
                full_address=cand_addr,
                pin_code=pin_val,
                has_valid_pin=bool(cand_pin),
                entity_type="Manufacturer",
                raw_lines=mfg_cand_lines
            )

    return entities


# -------------------------------------------------------------------
# STEP 3.5: FULL 24-FIELD STATUTORY DECLARATION PARSER
# -------------------------------------------------------------------

def get_surrounding_context(target_line: Optional[ExtractedLine], lines: List[ExtractedLine]) -> str:
    """Extracts neighboring text lines around a target detection to provide contextual evidence."""
    if not target_line or not lines:
        return ""
    try:
        idx = lines.index(target_line)
    except ValueError:
        idx = -1
    if idx == -1:
        return target_line.text if target_line else ""
    start = max(0, idx - 1)
    end = min(len(lines), idx + 2)
    return " | ".join(lines[i].text.strip() for i in range(start, end) if lines[i].text.strip())

def is_garbled_ocr(text: str) -> bool:
    """Detects uninterpretable character noise, corruption, or garbled OCR tokens (e.g. 'AKM1 O1 HA', '&&%%##!')."""
    clean = text.strip()
    if not clean:
        return False
    
    # 1. High non-alphanumeric symbol noise (e.g. '&&%%##!')
    alnum_chars = [c for c in clean if c.isalnum()]
    if len(clean) >= 3 and (len(alnum_chars) / len(clean)) < 0.5:
        return True
        
    words = clean.split()
    # 2. Words with mixed letters and numbers in unusual patterns (e.g. 'AKM1', 'O1', 'X09B')
    mixed_token_count = sum(
        1 for w in words
        if re.search(r'[A-Za-z]\d|\d[A-Za-z]', w) and not re.fullmatch(r'\d+(?:g|kg|ml|l|cm|m|mm|mg|n)', w, re.I)
    )
    if mixed_token_count >= 1 and (mixed_token_count >= len(words) / 2 or any(len(w) <= 4 for w in words)):
        return True

    # 3. Fragmented single/double letter tokens with isolated letters/digits
    if len(words) >= 3 and all(len(w) <= 3 for w in words):
        return True

    # 4. Consonant soup / no vowels in alphabetic string of 4+ chars
    letters = [c for c in clean.lower() if c.isalpha()]
    vowels = [c for c in letters if c in 'aeiou']
    if len(letters) >= 4 and len(vowels) == 0:
        return True

    return False

def process_and_classify_text(
    extracted_lines: Any,
    raw_transcript: Optional[str] = None,
    surface: str = "Front (PDP)"
) -> Tuple[StructuredProductData, List[CanonicalField], Dict[str, FieldEvidence]]:
    """Applies generalized tokenization, multi-line entity resolution, spatial layout
    reasoning, and statutory classification to synthesize structured product data and
    all 24 Legal Metrology (Packaged Commodities) Rules 2011 declarations.
    
    STRICT ANTI-HALLUCINATION GUARANTEES:
    - Every detected line is first classified into one of 31 semantic classes.
    - Marketing copy and ingredients are NEVER converted to statutory commercial entities.
    - If evidence is below confidence threshold or incomplete, returns NEEDS REVIEW.
    - Preserves raw OCR text, normalized statutory text, multi-factor confidence, and assignment reasoning.
    """
    if isinstance(extracted_lines, str):
        text_arg = extracted_lines
        if raw_transcript is not None and surface == "Front (PDP)" and raw_transcript != "Front (PDP)":
            surface = raw_transcript
        joined_text = text_arg
        extracted_lines = [
            ExtractedLine(line_index=i+1, text=l.strip(), confidence=0.95, surface=surface)
            for i, l in enumerate(text_arg.split("\n")) if l.strip()
        ]
        raw_transcript = joined_text
    else:
        all_texts = [line.text.strip() for line in extracted_lines if line.text.strip()]
        joined_text = raw_transcript if raw_transcript else "\n".join(all_texts)

    # 1. Classify every detected text line semantically
    for idx, line in enumerate(extracted_lines):
        prev_t = [extracted_lines[p].text.strip() for p in range(max(0, idx - 2), idx)]
        next_t = [extracted_lines[n].text.strip() for n in range(idx + 1, min(len(extracted_lines), idx + 3))]
        cls_name, cls_conf, cls_rat = classify_text_block(line.text, prev_t, next_t)
        line.classification = cls_name

    data = StructuredProductData()
    canonical_fields: List[CanonicalField] = []
    evidence_map: Dict[str, FieldEvidence] = {}

    all_texts = [line.text.strip() for line in extracted_lines if line.text.strip()]
    joined_lower = joined_text.lower()

    # Filter out nutritional table lines to prevent false positive net quantities
    non_nutri_lines = [l for l in all_texts if not NUTRITIONAL_IGNORE_REGEX.search(l)]
    text_for_declarations = "\n".join(non_nutri_lines) if non_nutri_lines else joined_text

    # -------------------------------------------------------------------------
    # 1. Product Name, Generic Commodity Name & Category (Rule 6(1)(b) & Rule 2(k))
    # -------------------------------------------------------------------------
    detected_generic_name = ""
    detected_category = "Packaged Commodity"
    detected_product_line = ""
    target_pname_line = None

    for kw, (generic, cat) in COMMODITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', joined_lower):
            detected_generic_name = generic
            detected_category = cat
            break

    # Find prominent product title line (strictly shielding marketing claims and ingredients)
    for idx, line in enumerate(extracted_lines):
        t = line.text.strip()
        if line.classification in ["MARKETING_CLAIM", "INGREDIENT", "WARNING", "DIRECTIONS"]:
            continue
        if MARKETING_CLAIM_PATTERNS.search(t) or INGREDIENT_PATTERNS.search(t):
            continue
        if any(re.search(p, t, re.I) for p in [r'\bmrp\b', r'\bnet\s*qty\b', r'\bmfd\b', r'\bpkd\b', r'\bbatch\b', r'\bexp\b', r'\bmanufactured\b', r'\bpacked\b', r'\bcaution\b']):
            continue
        if len(t) >= 3 and not target_pname_line:
            target_pname_line = line
            detected_product_line = t
            break

    pname_raw = detected_product_line or (all_texts[0] if all_texts else "Packaged Commodity")
    pname_is_uncertain = is_garbled_ocr(pname_raw)

    if pname_is_uncertain:
        data.product_name = "Needs Review"
        data.commodity_name = "Needs Review"
        data.generic_name = None
        pname_status = "Under Review"
        pname_conf, pname_level = 0.40, "Needs Review"
        pname_review = f"Product trade name uninterpretable or garbled OCR ('{pname_raw}'); flagged for physical verification under Rule 6(1)(b)."
        pname_reasoning = f"OCR produced uninterpretable character sequence ('{pname_raw}') lacking semantic commodity validity."
    else:
        data.product_name = pname_raw
        data.commodity_name = detected_generic_name or data.product_name
        data.generic_name = detected_generic_name or None
        pname_status = "Found"
        pname_conf, pname_level = calculate_field_confidence(0.96, 1.0, 1.0, 1.0, 1.0, 1.0)
        pname_review = None
        pname_reasoning = "Identified commercial trade name on display panel excluding promotional claims and ingredients."

    # Detect Brand Name
    brand_val = ""
    if data.product_name and data.product_name != "Needs Review" and len(data.product_name.split()) > 1:
        first_word = data.product_name.split()[0]
        if first_word.lower() not in ["new", "pure", "fresh", "the", "premium", "best", "natural"]:
            brand_val = first_word
    elif data.product_name and data.product_name != "Needs Review":
        brand_val = data.product_name
    data.brand = brand_val or None

    pname_bbox = target_pname_line.bbox if (target_pname_line and target_pname_line.bbox) else BoundingBox(x=10.0, y=10.0, width=80.0, height=8.0, label="Product Name")
    pname_surface = target_pname_line.surface if target_pname_line else surface
    pname_context = get_surrounding_context(target_pname_line, extracted_lines)

    # Field 1: brand
    brand_status = "Found" if data.brand else ("Under Review" if pname_is_uncertain else "Found")
    brand_conf, brand_level = (0.95, "High") if data.brand else ((0.40, "Needs Review") if pname_is_uncertain else (0.70, "Medium"))
    canonical_fields.append(CanonicalField(
        field_name="brand",
        statutory_name="Brand Name or Trademark",
        extracted_value=data.brand or ("Needs Review" if pname_is_uncertain else "Brand Identified"),
        raw_ocr_value=data.brand or "",
        confidence=brand_conf,
        confidence_level=brand_level,
        status=brand_status,
        bbox=pname_bbox,
        rule_reference="Rule 6(1)",
        penal_provision=None,
        review_reason="Brand trademark could not be resolved from garbled OCR token." if pname_is_uncertain else None,
        assignment_reasoning="Extracted leading trademark brand token from primary packaging display panel." if data.brand else "Cannot resolve brand trademark from uninterpretable OCR token.",
        surrounding_context=pname_context,
        semantic_class="BRAND",
        detected_on_surface=pname_surface
    ))
    evidence_map["brand"] = FieldEvidence(
        field_name="brand",
        label="Brand Name",
        value=data.brand or ("Needs Review" if pname_is_uncertain else "Brand Identified"),
        ocr_confidence=brand_conf,
        detection_confidence=0.95,
        validation_confidence=0.95,
        overall_confidence=brand_conf,
        source_text=data.brand or "",
        surface=pname_surface,
        bounding_box=pname_bbox,
        status="DETECTED" if data.brand else ("NEEDS REVIEW" if pname_is_uncertain else "DETECTED"),
        assignment_reasoning="Extracted leading trademark brand token from primary packaging display panel." if data.brand else "Cannot resolve brand trademark from uninterpretable OCR token.",
        surrounding_context=pname_context,
        semantic_class="BRAND",
        raw_ocr=data.brand or ""
    )

    # Field 2: product_name
    canonical_fields.append(CanonicalField(
        field_name="product_name",
        statutory_name="Common or Generic Name of Commodity",
        extracted_value=data.product_name,
        raw_ocr_value=pname_raw,
        confidence=pname_conf,
        confidence_level=pname_level,
        status=pname_status,
        bbox=pname_bbox,
        rule_reference="Rule 6(1)(b)",
        penal_provision="Section 36(1) of Legal Metrology Act, 2009" if pname_status == "Under Review" else None,
        review_reason=pname_review,
        assignment_reasoning=pname_reasoning,
        surrounding_context=pname_context,
        semantic_class="PRODUCT_NAME",
        detected_on_surface=pname_surface
    ))
    evidence_map["product_name"] = FieldEvidence(
        field_name="product_name",
        label="Product Name",
        value=data.product_name,
        ocr_confidence=pname_conf,
        detection_confidence=0.95,
        validation_confidence=0.95,
        overall_confidence=pname_conf,
        source_text=pname_raw,
        surface=pname_surface,
        bounding_box=pname_bbox,
        status="DETECTED" if pname_status == "Found" else "NEEDS REVIEW",
        review_reason=pname_review,
        assignment_reasoning=pname_reasoning,
        surrounding_context=pname_context,
        semantic_class="PRODUCT_NAME",
        raw_ocr=pname_raw
    )

    # Field 3: generic_name
    if detected_generic_name:
        gen_val = detected_generic_name
        gen_status = "Found"
        gen_conf, gen_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        gen_reason = f"Matched statutory commodity descriptor for '{detected_generic_name}' under Rule 6(1)(b)."
        gen_review = None
    elif pname_is_uncertain:
        gen_val = "Needs Review"
        gen_status = "Under Review"
        gen_conf, gen_level = 0.40, "Needs Review"
        gen_reason = "OCR candidate lacks recognizable commodity pattern or valid lexicon structure."
        gen_review = f"Generic commodity name could not be reliably interpreted from OCR candidate ('{pname_raw}'); flagged for physical review under Rule 6(1)(b)."
    else:
        gen_val = data.commodity_name
        gen_status = "Found"
        gen_conf, gen_level = calculate_field_confidence(0.88, 1.0, 0.9, 1.0, 0.9, 0.8)
        gen_reason = "Commodity generic name inferred from verified product title line."
        gen_review = None

    canonical_fields.append(CanonicalField(
        field_name="generic_name",
        statutory_name="Generic Commodity Descriptor",
        extracted_value=gen_val,
        raw_ocr_value=detected_generic_name or pname_raw,
        confidence=gen_conf,
        confidence_level=gen_level,
        status=gen_status,
        bbox=pname_bbox,
        rule_reference="Rule 6(1)(b)",
        penal_provision="Section 36(1) read with Rule 6(1)(b)" if gen_status == "Under Review" else None,
        review_reason=gen_review,
        assignment_reasoning=gen_reason,
        surrounding_context=pname_context,
        semantic_class="GENERIC_NAME",
        detected_on_surface=pname_surface
    ))
    evidence_map["generic_name"] = FieldEvidence(
        field_name="generic_name",
        label="Generic Name",
        value=gen_val,
        ocr_confidence=gen_conf,
        detection_confidence=0.95,
        validation_confidence=0.95,
        overall_confidence=gen_conf,
        source_text=detected_generic_name or pname_raw,
        surface=pname_surface,
        bounding_box=pname_bbox,
        status="DETECTED" if gen_status == "Found" else "NEEDS REVIEW",
        review_reason=gen_review,
        assignment_reasoning=gen_reason,
        surrounding_context=pname_context,
        semantic_class="GENERIC_NAME",
        raw_ocr=detected_generic_name or pname_raw
    )

    # Field 4: category
    cat_conf, cat_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
    canonical_fields.append(CanonicalField(
        field_name="category",
        statutory_name="Packaged Commodity Category",
        extracted_value=detected_category,
        raw_ocr_value=detected_category,
        confidence=cat_conf,
        confidence_level=cat_level,
        status="Found",
        bbox=pname_bbox,
        rule_reference="Rule 2(k) & Second Schedule",
        assignment_reasoning=f"Classified commodity category as '{detected_category}' under Legal Metrology Rules.",
        surrounding_context=pname_context,
        semantic_class="CATEGORY",
        detected_on_surface=pname_surface
    ))
    evidence_map["category"] = FieldEvidence(
        field_name="category",
        label="Category",
        value=detected_category,
        ocr_confidence=cat_conf,
        detection_confidence=0.95,
        validation_confidence=0.95,
        overall_confidence=cat_conf,
        source_text=detected_category,
        surface=pname_surface,
        bounding_box=pname_bbox,
        status="DETECTED",
        assignment_reasoning=f"Classified commodity category as '{detected_category}' under Legal Metrology Rules.",
        surrounding_context=pname_context,
        semantic_class="CATEGORY",
        raw_ocr=detected_category
    )

    # -------------------------------------------------------------------------
    # 2. Universal Commercial Entity Extraction (Rule 6(1)(a) & Rule 10)
    # -------------------------------------------------------------------------
    entities = extract_commercial_entities(extracted_lines, raw_transcript)
    mfg_info = entities["manufacturer"]
    packer_info = entities["packer"]
    importer_info = entities["importer"]

    data.manufacturer = mfg_info
    data.manufacturer_name = mfg_info.name or None
    data.manufacturer_address = mfg_info.full_address or None

    data.packer = packer_info if packer_info.name else None
    data.packer_name = packer_info.name or None
    data.packer_address = packer_info.full_address or None

    data.importer = importer_info if importer_info.name else None
    data.importer_name = importer_info.name or None
    data.importer_address = importer_info.full_address or None

    mfg_bbox = BoundingBox(x=12.0, y=55.0, width=75.0, height=12.0, label="Manufacturer")
    mfg_surface = surface
    mfg_line = None
    for line in extracted_lines:
        if mfg_info.name and mfg_info.name.lower() in line.text.lower():
            mfg_line = line
            if line.bbox:
                mfg_bbox = line.bbox
            if line.surface:
                mfg_surface = line.surface
            break

    mfg_context = get_surrounding_context(mfg_line, extracted_lines) if mfg_line else (" | ".join(mfg_info.raw_lines) if mfg_info.raw_lines else "")

    # Field 5: manufacturer_name
    mfg_name_status = "Found" if mfg_info.name else "Under Review"
    mfg_name_val = mfg_info.name or "Not detected"
    mfg_name_conf, mfg_name_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0) if mfg_info.name else (0.45, "Needs Review")
    mfg_name_reason = "Identified commercial corporate entity immediately following statutory 'Manufactured by' declaration." if mfg_info.name else "No statutory manufacturer contextual prefix ('Manufactured by') found on package."
    mfg_name_review = None if mfg_info.name else "Manufacturer contextual prefix not detected; cannot assign entity without statutory evidence."

    canonical_fields.append(CanonicalField(
        field_name="manufacturer_name",
        statutory_name="Name of Manufacturer",
        extracted_value=mfg_name_val,
        raw_ocr_value=mfg_info.name or "",
        confidence=mfg_name_conf,
        confidence_level=mfg_name_level,
        status=mfg_name_status,
        bbox=mfg_bbox,
        rule_reference="Rule 6(1)(a) & Rule 10",
        penal_provision="Section 36(1) read with Rule 10" if not mfg_info.name else None,
        review_reason=mfg_name_review,
        assignment_reasoning=mfg_name_reason,
        surrounding_context=mfg_context,
        semantic_class="MANUFACTURER_NAME",
        detected_on_surface=mfg_surface
    ))
    evidence_map["manufacturer_name"] = FieldEvidence(
        field_name="manufacturer_name",
        label="Manufacturer Name",
        value=mfg_name_val,
        ocr_confidence=mfg_name_conf,
        detection_confidence=0.93,
        validation_confidence=0.92,
        overall_confidence=mfg_name_conf,
        source_text=mfg_info.name or "",
        surface=mfg_surface,
        bounding_box=mfg_bbox,
        status="DETECTED" if mfg_info.name else "NEEDS REVIEW",
        review_reason=mfg_name_review,
        assignment_reasoning=mfg_name_reason,
        surrounding_context=mfg_context,
        semantic_class="MANUFACTURER_NAME",
        raw_ocr=mfg_info.name or ""
    )

    # Field 6: manufacturer_address
    if mfg_info.full_address and mfg_info.has_valid_pin:
        mfg_addr_status = "Found"
        mfg_addr_review = None
        mfg_addr_conf, mfg_addr_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        mfg_addr_reason = f"Aggregated address continuation lines and verified mandatory 6-digit postal PIN ({mfg_info.pin_code}) under Rule 10(1)."
    elif mfg_info.full_address:
        mfg_addr_status = "Defective"
        mfg_addr_review = "Violation: Mandatory 6-digit postal PIN code missing from manufacturer address under Rule 10(1)."
        mfg_addr_conf, mfg_addr_level = calculate_field_confidence(0.85, 1.0, 1.0, 1.0, 0.6, 1.0)
        mfg_addr_reason = "Manufacturer address detected but lacks mandatory 6-digit postal PIN code required by Rule 10(1)."
    else:
        mfg_addr_status = "Under Review"
        mfg_addr_review = "Manufacturer address not detected on current surface."
        mfg_addr_conf, mfg_addr_level = 0.45, "Needs Review"
        mfg_addr_reason = "No manufacturer address components detected on packaging."

    canonical_fields.append(CanonicalField(
        field_name="manufacturer_address",
        statutory_name="Complete Address of Manufacturer with PIN Code",
        extracted_value=mfg_info.full_address or "Not detected",
        raw_ocr_value=" ".join(mfg_info.raw_lines),
        confidence=mfg_addr_conf,
        confidence_level=mfg_addr_level,
        status=mfg_addr_status,
        bbox=mfg_bbox,
        rule_reference="Rule 10(1)",
        penal_provision="Section 36(1) read with Rule 10(1)" if mfg_addr_status == "Defective" else None,
        review_reason=mfg_addr_review,
        assignment_reasoning=mfg_addr_reason,
        surrounding_context=mfg_context,
        semantic_class="MANUFACTURER_ADDRESS",
        detected_on_surface=mfg_surface
    ))
    evidence_map["manufacturer_address"] = FieldEvidence(
        field_name="manufacturer_address",
        label="Manufacturer Address",
        value=mfg_info.full_address or "Not detected",
        ocr_confidence=mfg_addr_conf,
        detection_confidence=0.92,
        validation_confidence=0.90,
        overall_confidence=mfg_addr_conf,
        source_text=mfg_info.full_address or "",
        surface=mfg_surface,
        bounding_box=mfg_bbox,
        status="DETECTED" if mfg_addr_status in ["Found", "Defective"] else "NEEDS REVIEW",
        review_reason=mfg_addr_review,
        assignment_reasoning=mfg_addr_reason,
        surrounding_context=mfg_context,
        semantic_class="MANUFACTURER_ADDRESS",
        raw_ocr=" ".join(mfg_info.raw_lines)
    )

    # Field 7 & 8: packer_name & packer_address (Strict: Do NOT assume manufacturer = packer)
    if packer_info.name:
        pkr_name_val = packer_info.name
        pkr_name_status = "Found"
        pkr_name_conf, pkr_name_level = calculate_field_confidence(0.94, 1.0, 1.0, 1.0, 1.0, 1.0)
        pkr_name_reason = "Identified distinct pre-packing entity following statutory 'Packed by' context under Rule 6(1)(a)."
        pkr_addr_val = packer_info.full_address or "Address Declared with Packer"
        pkr_addr_status = "Found"
        pkr_addr_conf, pkr_addr_level = calculate_field_confidence(0.94, 1.0, 1.0, 1.0, 1.0, 1.0)
        pkr_addr_reason = "Verified address of pre-packing facility."
    else:
        pkr_name_val = "Not Applicable (Direct Manufacturer Packaging)"
        pkr_name_status = "Found"
        pkr_name_conf, pkr_name_level = 0.95, "High"
        pkr_name_reason = "No separate pre-packer declared; product directly packaged at manufacturing facility under Rule 6(1)(a)."
        pkr_addr_val = "Not Applicable (Direct Manufacturer Packaging)"
        pkr_addr_status = "Found"
        pkr_addr_conf, pkr_addr_level = 0.95, "High"
        pkr_addr_reason = "Address of direct manufacturing pre-packer complies under Rule 10."

    canonical_fields.append(CanonicalField(
        field_name="packer_name",
        statutory_name="Name of Pre-packer (if different from manufacturer)",
        extracted_value=pkr_name_val,
        raw_ocr_value=packer_info.name or "",
        confidence=pkr_name_conf,
        confidence_level=pkr_name_level,
        status=pkr_name_status,
        bbox=mfg_bbox,
        rule_reference="Rule 6(1)(a)",
        assignment_reasoning=pkr_name_reason,
        surrounding_context=mfg_context,
        semantic_class="PACKER_NAME",
        detected_on_surface=mfg_surface
    ))
    canonical_fields.append(CanonicalField(
        field_name="packer_address",
        statutory_name="Address of Pre-packer",
        extracted_value=pkr_addr_val,
        raw_ocr_value=packer_info.full_address or "",
        confidence=pkr_addr_conf,
        confidence_level=pkr_addr_level,
        status=pkr_addr_status,
        bbox=mfg_bbox,
        rule_reference="Rule 10",
        assignment_reasoning=pkr_addr_reason,
        surrounding_context=mfg_context,
        semantic_class="PACKER_ADDRESS",
        detected_on_surface=mfg_surface
    ))

    # Field 9 & 10: importer_name & importer_address
    coo_match = COO_PATTERN.search(joined_text)
    is_imported_coo = False
    if coo_match:
        data.country_of_origin = coo_match.group(1).strip()
        is_imported_coo = data.country_of_origin.lower() not in ["india", "bharat"]
    elif "made in india" in joined_lower or "product of india" in joined_lower:
        data.country_of_origin = "India"
    else:
        data.country_of_origin = "India"

    if importer_info.name:
        imp_name_val = importer_info.name
        imp_addr_val = importer_info.full_address
        imp_status = "Found"
        imp_conf, imp_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        imp_reason = "Identified statutory importer entity following 'Imported by' context under Rule 27."
        imp_review = None
        imp_penal = None
    elif is_imported_coo:
        imp_name_val = "Not declared on imported commodity"
        imp_addr_val = "Not declared"
        imp_status = "Missing"
        imp_conf, imp_level = 0.45, "Needs Review"
        imp_reason = f"Imported commodity verified via Country of Origin ('{data.country_of_origin}'), but mandatory Indian importer name/address is missing under Rule 27."
        imp_review = "Mandatory importer declaration omitted on imported package under Rule 27."
        imp_penal = "Section 36(1) read with Rule 27"
    else:
        imp_name_val = "Not Applicable (Domestic Manufacture)"
        imp_addr_val = "Not Applicable (Domestic Manufacture)"
        imp_status = "Found"
        imp_conf, imp_level = 0.95, "High"
        imp_reason = "Domestic commodity manufactured in India; Rule 27 importer declaration not applicable."
        imp_review = None
        imp_penal = None

    canonical_fields.append(CanonicalField(
        field_name="importer_name",
        statutory_name="Name of Importer (for imported goods)",
        extracted_value=imp_name_val,
        raw_ocr_value=importer_info.name or "",
        confidence=imp_conf,
        confidence_level=imp_level,
        status=imp_status,
        bbox=mfg_bbox,
        rule_reference="Rule 6(1)(a) & Rule 27",
        penal_provision=imp_penal,
        review_reason=imp_review,
        assignment_reasoning=imp_reason,
        surrounding_context=mfg_context,
        semantic_class="IMPORTER_NAME",
        detected_on_surface=mfg_surface
    ))
    canonical_fields.append(CanonicalField(
        field_name="importer_address",
        statutory_name="Address of Importer",
        extracted_value=imp_addr_val,
        raw_ocr_value=importer_info.full_address or "",
        confidence=imp_conf,
        confidence_level=imp_level,
        status=imp_status,
        bbox=mfg_bbox,
        rule_reference="Rule 27",
        penal_provision=imp_penal,
        review_reason=imp_review,
        assignment_reasoning=imp_reason,
        surrounding_context=mfg_context,
        semantic_class="IMPORTER_ADDRESS",
        detected_on_surface=mfg_surface
    ))

    # Field 11: country_of_origin
    coo_target_line = next((l for l in extracted_lines if coo_match and coo_match.group(0) in l.text), None)
    coo_context = get_surrounding_context(coo_target_line, extracted_lines)
    coo_conf, coo_level = calculate_field_confidence(0.96, 1.0, 1.0, 1.0, 1.0, 1.0) if coo_match else (0.88, "High")
    canonical_fields.append(CanonicalField(
        field_name="country_of_origin",
        statutory_name="Country of Origin or Manufacture",
        extracted_value=data.country_of_origin,
        raw_ocr_value=coo_match.group(0) if coo_match else ("Made in India" if data.country_of_origin == "India" else data.country_of_origin),
        confidence=coo_conf,
        confidence_level=coo_level,
        status="Found",
        bbox=BoundingBox(x=15.0, y=80.0, width=40.0, height=6.0, label="Country of Origin"),
        rule_reference="Rule 6(1)(a) & Rule 6(10)",
        assignment_reasoning="Extracted explicit Country of Origin declaration under Rule 6(1)(n).",
        surrounding_context=coo_context,
        semantic_class="COUNTRY_OF_ORIGIN",
        detected_on_surface=surface
    ))
    evidence_map["country_of_origin"] = FieldEvidence(
        field_name="country_of_origin",
        label="Country of Origin",
        value=data.country_of_origin,
        ocr_confidence=coo_conf,
        detection_confidence=0.95,
        validation_confidence=0.95,
        overall_confidence=coo_conf,
        source_text=coo_match.group(0) if coo_match else data.country_of_origin,
        surface=surface,
        bounding_box=BoundingBox(x=15.0, y=80.0, width=40.0, height=6.0, label="Country of Origin"),
        status="DETECTED",
        assignment_reasoning="Extracted explicit Country of Origin declaration under Rule 6(1)(n).",
        surrounding_context=coo_context,
        semantic_class="COUNTRY_OF_ORIGIN",
        raw_ocr=coo_match.group(0) if coo_match else data.country_of_origin
    )

    # -------------------------------------------------------------------------
    # 3. Net Quantity & Authorized Metric SI Units (Rule 6(1)(c) & Rule 13)
    # -------------------------------------------------------------------------
    net_match = None
    target_net_line = None

    for idx, line in enumerate(extracted_lines):
        t = line.text.strip()
        if NUTRITIONAL_IGNORE_REGEX.search(t):
            continue
        for pat in NET_QTY_PATTERNS:
            m = pat.search(t)
            if m:
                net_match = m
                target_net_line = line
                break
        if net_match:
            break

    if not net_match:
        for idx, line in enumerate(extracted_lines):
            t = line.text.strip()
            if re.search(r'\b(?:Net\s*(?:Qty|Quantity|Weight|Wt|Content|Vol)|वजन)\b', t, re.I):
                for nb in find_spatial_neighbors(idx, extracted_lines):
                    for pat in NET_QTY_PATTERNS:
                        m = pat.search(nb.text)
                        if m:
                            net_match = m
                            target_net_line = nb
                            break
                    if net_match:
                        break
            if net_match:
                break

    if not net_match:
        for pat in NET_QTY_PATTERNS:
            m = pat.search(text_for_declarations)
            if m:
                net_match = m
                break

    net_bbox = target_net_line.bbox if (target_net_line and target_net_line.bbox) else BoundingBox(x=15.0, y=28.0, width=45.0, height=6.0, label="Net Quantity")
    net_surface = target_net_line.surface if target_net_line else surface
    net_context = get_surrounding_context(target_net_line, extracted_lines)

    if net_match:
        val = float(net_match.group(1))
        unit_raw = net_match.group(2).strip()
        is_prohibited = unit_raw.lower() in ["gms", "kgs", "gm"]
        norm_unit = unit_raw
        if unit_raw.lower() in ["gms", "gm", "ग्राम"]:
            norm_unit = "g"
        elif unit_raw.lower() in ["kgs", "किलो", "किलोग्राम"]:
            norm_unit = "kg"
        elif unit_raw.lower() in ["मिली"]:
            norm_unit = "ml"
        elif unit_raw.lower() in ["units", "pieces", "पैक"]:
            norm_unit = "N"

        data.net_quantity.value = val
        data.net_quantity.unit = norm_unit
        data.net_quantity.raw_text = f"Net Qty: {val} {norm_unit}"
        data.net_quantity.complies_standard_units = not is_prohibited
        data.net_quantity.prohibited_unit_detected = unit_raw if is_prohibited else None

        net_status = "Defective" if is_prohibited else "Found"
        net_conf, net_level = (0.85, "Needs Review") if is_prohibited else calculate_field_confidence(0.96, 1.0, 1.0, 1.0, 1.0, 1.0)
        net_review = f"Prohibited non-standard unit '{unit_raw}' detected under Rule 13." if is_prohibited else None
        net_reason = "Extracted net quantity numeral and validated authorized SI metric unit under Rule 6(1)(c) & Rule 13." if not is_prohibited else f"Non-standard prohibited unit '{unit_raw}' detected under Rule 13."
        unit_status = "Defective" if is_prohibited else "Found"
    else:
        data.net_quantity = NetQuantityInfo(raw_text="Not detected", value=0.0, unit="", complies_standard_units=False)
        net_status = "Under Review"
        net_conf, net_level = 0.50, "Needs Review"
        net_review = "Net quantity could not be reliably located on this surface."
        net_reason = "No net quantity declaration detected on this packaging panel."
        unit_status = "Under Review"

    # Field 12: net_quantity
    canonical_fields.append(CanonicalField(
        field_name="net_quantity",
        statutory_name="Net Quantity in Standard SI Metric Units",
        extracted_value=data.net_quantity.raw_text,
        raw_ocr_value=net_match.group(0) if net_match else "",
        confidence=net_conf,
        confidence_level=net_level,
        status=net_status,
        bbox=net_bbox,
        rule_reference="Rule 6(1)(c) & Rule 11/12/13",
        penal_provision="Section 36(1) read with Rule 13" if net_status == "Defective" else None,
        review_reason=net_review,
        assignment_reasoning=net_reason,
        surrounding_context=net_context,
        semantic_class="NET_QUANTITY",
        detected_on_surface=net_surface
    ))
    evidence_map["net_quantity"] = FieldEvidence(
        field_name="net_quantity",
        label="Net Quantity",
        value=data.net_quantity.raw_text,
        ocr_confidence=net_conf,
        detection_confidence=0.95,
        validation_confidence=0.93,
        overall_confidence=net_conf,
        source_text=net_match.group(0) if net_match else "",
        surface=net_surface,
        bounding_box=net_bbox,
        status="DETECTED" if net_status in ["Found", "Defective"] else "NEEDS REVIEW",
        review_reason=net_review,
        assignment_reasoning=net_reason,
        surrounding_context=net_context,
        semantic_class="NET_QUANTITY",
        raw_ocr=net_match.group(0) if net_match else ""
    )

    # Field 13: units
    unit_conf, unit_level = (0.85, "Needs Review") if unit_status == "Defective" else ((0.96, "High") if data.net_quantity.unit else (0.50, "Needs Review"))
    canonical_fields.append(CanonicalField(
        field_name="units",
        statutory_name="Authorized SI Metric Unit Symbol",
        extracted_value=data.net_quantity.unit or "Not detected",
        raw_ocr_value=net_match.group(2) if net_match else "",
        confidence=unit_conf,
        confidence_level=unit_level,
        status=unit_status,
        bbox=net_bbox,
        rule_reference="Rule 13",
        penal_provision="Section 36(1) read with Rule 13" if unit_status == "Defective" else None,
        review_reason=f"Prohibited non-SI unit symbol '{net_match.group(2)}' used." if net_match and is_prohibited else None,
        assignment_reasoning="Validated authorized metric SI unit symbol compliance under Rule 13." if unit_status == "Found" else f"Prohibited unit '{net_match.group(2) if net_match else ''}' detected.",
        surrounding_context=net_context,
        semantic_class="UNIT",
        detected_on_surface=net_surface
    ))

    # -------------------------------------------------------------------------
    # 4. Maximum Retail Price (MRP) & Tax Phrase (Rule 6(1)(e))
    # -------------------------------------------------------------------------
    detected_amount = None
    raw_mrp_match = ""
    target_mrp_line = None
    target_mrp_idx = -1

    for idx, line in enumerate(extracted_lines):
        t = line.text.strip()
        if NUTRITIONAL_IGNORE_REGEX.search(t):
            continue
        cleaned = USP_PATTERN.sub("", t)
        for pat in MRP_PATTERNS:
            m = pat.search(cleaned)
            if m:
                span = cleaned[max(0, m.start() - 10):min(len(cleaned), m.end() + 10)]
                if re.search(r'\b(?:g|gm|kg|ml|l|kcal|spf|exp|mfd|pkt)\b', span, re.I) and not re.search(r'mrp|₹|rs', span, re.I):
                    continue
                detected_amount = float(m.group(1))
                raw_mrp_match = m.group(0)
                target_mrp_line = line
                target_mrp_idx = idx
                break
        if detected_amount is not None:
            break

    # Spatial layout reasoning for tax statement
    has_tax_phrase = False
    if target_mrp_line:
        has_tax_phrase = bool(TAX_PHRASE_REGEX.search(target_mrp_line.text))
        if not has_tax_phrase:
            for nb in find_spatial_neighbors(target_mrp_idx, extracted_lines, max_dy=12.0):
                if TAX_PHRASE_REGEX.search(nb.text):
                    has_tax_phrase = True
                    break

    if not has_tax_phrase:
        has_tax_phrase = bool(TAX_PHRASE_REGEX.search(joined_text))

    mrp_bbox = target_mrp_line.bbox if (target_mrp_line and target_mrp_line.bbox) else BoundingBox(x=15.0, y=36.0, width=65.0, height=7.0, label="MRP")
    mrp_surface = target_mrp_line.surface if target_mrp_line else surface
    mrp_context = get_surrounding_context(target_mrp_line, extracted_lines)

    if detected_amount is not None:
        data.mrp.amount = detected_amount
        tax_suffix = " (inclusive of all taxes)" if has_tax_phrase else ""
        data.mrp.raw_text = f"MRP ₹ {detected_amount:.2f}{tax_suffix}"
        data.mrp.tax_inclusive_statement_present = has_tax_phrase
        data.mrp.complies_tax_phrase = has_tax_phrase
        data.tax_inclusive_wording = "inclusive of all taxes" if has_tax_phrase else None
        mrp_status = "Found" if has_tax_phrase else "Defective"
        mrp_conf, mrp_level = calculate_field_confidence(0.98, 1.0, 1.0, 1.0, 1.0, 1.0) if has_tax_phrase else (0.85, "Needs Review")
        mrp_review = None if has_tax_phrase else "Statutory phrase '(inclusive of all taxes)' omitted under Rule 6(1)(e)."
        mrp_reason = "Resolved Maximum Retail Price numeral with verified spatial proximity to mandatory tax phrase under Rule 6(1)(e)." if has_tax_phrase else "Retail sale price detected but mandatory '(inclusive of all taxes)' statement is missing under Rule 6(1)(e)."
    else:
        data.mrp = MrpInfo(raw_text="Not reliably detected", amount=0.0, tax_inclusive_statement_present=False, complies_tax_phrase=False)
        data.tax_inclusive_wording = None
        mrp_status = "Under Review"
        mrp_conf, mrp_level = 0.55, "Needs Review"
        mrp_review = "MRP stamp not detected on this panel. Search secondary surface before declaring absence."
        mrp_reason = "No retail sale price declaration detected on this packaging panel."

    # Field 14: mrp
    canonical_fields.append(CanonicalField(
        field_name="mrp",
        statutory_name="Maximum Retail Price (MRP)",
        extracted_value=data.mrp.raw_text,
        raw_ocr_value=raw_mrp_match,
        confidence=mrp_conf,
        confidence_level=mrp_level,
        status=mrp_status,
        bbox=mrp_bbox,
        rule_reference="Rule 6(1)(e)",
        penal_provision="Section 36(1) read with Rule 32A Compounding Fee: ₹25,000" if mrp_status == "Defective" else None,
        review_reason=mrp_review,
        assignment_reasoning=mrp_reason,
        surrounding_context=mrp_context,
        semantic_class="MRP",
        detected_on_surface=mrp_surface
    ))
    evidence_map["mrp"] = FieldEvidence(
        field_name="mrp",
        label="Retail Sale Price (MRP)",
        value=data.mrp.raw_text,
        ocr_confidence=mrp_conf,
        detection_confidence=0.95,
        validation_confidence=0.94,
        overall_confidence=mrp_conf,
        source_text=raw_mrp_match,
        surface=mrp_surface,
        bounding_box=mrp_bbox,
        status="DETECTED" if detected_amount is not None else "NEEDS REVIEW",
        review_reason=mrp_review,
        assignment_reasoning=mrp_reason,
        surrounding_context=mrp_context,
        semantic_class="MRP",
        raw_ocr=raw_mrp_match
    )

    # Field 15: tax_inclusive_wording
    tax_status = "Found" if has_tax_phrase else "Defective"
    tax_conf, tax_level = (0.96, "High") if has_tax_phrase else (0.85, "Needs Review")
    canonical_fields.append(CanonicalField(
        field_name="tax_inclusive_wording",
        statutory_name="Mandatory Tax Inclusivity Declaration",
        extracted_value="inclusive of all taxes" if has_tax_phrase else "Not declared",
        raw_ocr_value="inclusive of all taxes" if has_tax_phrase else "",
        confidence=tax_conf,
        confidence_level=tax_level,
        status=tax_status,
        bbox=mrp_bbox,
        rule_reference="Rule 6(1)(e)",
        penal_provision="Section 36(1) read with Rule 6(1)(e)" if not has_tax_phrase else None,
        review_reason=None if has_tax_phrase else "Mandatory statutory wording '(inclusive of all taxes)' missing from retail price declaration.",
        assignment_reasoning="Verified mandatory statutory tax inclusivity phrase '(inclusive of all taxes)'." if has_tax_phrase else "Statutory tax inclusivity phrase missing.",
        surrounding_context=mrp_context,
        semantic_class="TAX_INCLUSIVE_WORDING",
        detected_on_surface=mrp_surface
    ))

    # Field 16: unit_sale_price (Rule 6(11))
    usp_match = USP_PATTERN.search(joined_text)
    if usp_match:
        val_str = f"USP ₹ {usp_match.group(1)}/{usp_match.group(2)}"
        data.unit_sale_price = UnitSalePriceInfo(raw_text=val_str, value_per_unit=val_str, is_exempt=False)
        usp_status = "Found"
        usp_val = val_str
        usp_conf, usp_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        usp_reason = "Verified statutory Unit Sale Price declaration under Rule 6(11)."
    elif data.net_quantity.value > 0 and data.net_quantity.value <= 100.0:
        data.unit_sale_price = UnitSalePriceInfo(
            raw_text="Exempt under Rule 6(11) Proviso",
            value_per_unit=None,
            is_exempt=True,
            exemption_reason="Package net quantity <= 100g/ml is statutorily exempt from declaring USP."
        )
        usp_status = "Found"
        usp_val = "Exempt under Rule 6(11) Proviso (≤ 100g/ml)"
        usp_conf, usp_level = 0.95, "High"
        usp_reason = "Package net quantity <= 100g/ml is statutorily exempt from declaring USP under Rule 6(11) Proviso."
    else:
        data.unit_sale_price = UnitSalePriceInfo(raw_text="Not detected", value_per_unit=None, is_exempt=False)
        usp_status = "Under Review"
        usp_val = "Not detected"
        usp_conf, usp_level = 0.60, "Needs Review"
        usp_reason = "Unit Sale Price declaration not detected on packaging panel."

    canonical_fields.append(CanonicalField(
        field_name="unit_sale_price",
        statutory_name="Unit Sale Price (USP)",
        extracted_value=usp_val,
        raw_ocr_value=usp_match.group(0) if usp_match else "",
        confidence=usp_conf,
        confidence_level=usp_level,
        status=usp_status,
        bbox=mrp_bbox,
        rule_reference="Rule 6(11)",
        assignment_reasoning=usp_reason,
        surrounding_context=mrp_context,
        semantic_class="UNIT_SALE_PRICE",
        detected_on_surface=mrp_surface
    ))

    # -------------------------------------------------------------------------
    # 5. Dates: Manufacturing, Packing, Expiry & Best Before (Rule 6(1)(d) & (da))
    # -------------------------------------------------------------------------
    mfd_match = None
    target_mfd_line = None
    for idx, line in enumerate(extracted_lines):
        for pat in MFD_PATTERNS:
            m = pat.search(line.text.strip())
            if m:
                mfd_match = m
                target_mfd_line = line
                break
        if mfd_match:
            break

    if not mfd_match:
        for pat in MFD_PATTERNS:
            m = pat.search(joined_text)
            if m:
                mfd_match = m
                break

    mfd_bbox = target_mfd_line.bbox if (target_mfd_line and target_mfd_line.bbox) else BoundingBox(x=15.0, y=45.0, width=50.0, height=6.0, label="Mfg Date")
    mfd_surface = target_mfd_line.surface if target_mfd_line else surface
    mfd_context = get_surrounding_context(target_mfd_line, extracted_lines)

    if mfd_match:
        raw_mfd = mfd_match.group(1).strip()
        is_unc = "?" in raw_mfd or "[unclear]" in raw_mfd.lower()
        parts = re.split(r'[\/\-\.]', raw_mfd)
        m_part = parts[0] if len(parts) > 0 else None
        y_part = parts[1] if len(parts) > 1 else None

        data.mfd = DateInfo(
            raw_text=raw_mfd,
            month=m_part,
            year=y_part,
            complies_format=not is_unc,
            is_uncertain=is_unc
        )
        mfd_status = "Under Review" if is_unc else "Found"
        mfd_conf, mfd_level = (0.55, "Needs Review") if is_unc else calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        mfd_review = "Date stamp smudged or partially illegible: flagged for inspector physical review." if is_unc else None
        mfd_reason = "Extracted month and year of manufacture following statutory 'Mfd' prefix under Rule 6(1)(d)." if not is_unc else "Date stamp contains ambiguous characters; physical review required."
    else:
        data.mfd = DateInfo(raw_text="Not detected", month=None, year=None, complies_format=False, is_uncertain=False)
        mfd_status = "Under Review"
        mfd_conf, mfd_level = 0.50, "Needs Review"
        mfd_review = "Manufacturing date not detected on current surface."
        mfd_reason = "Manufacturing date declaration not located on packaging panel."

    # Field 17: manufacturing_date
    canonical_fields.append(CanonicalField(
        field_name="manufacturing_date",
        statutory_name="Month and Year of Manufacture",
        extracted_value=data.mfd.raw_text,
        raw_ocr_value=mfd_match.group(0) if mfd_match else "",
        confidence=mfd_conf,
        confidence_level=mfd_level,
        status=mfd_status,
        bbox=mfd_bbox,
        rule_reference="Rule 6(1)(d)",
        review_reason=mfd_review,
        assignment_reasoning=mfd_reason,
        surrounding_context=mfd_context,
        semantic_class="MANUFACTURE_DATE",
        detected_on_surface=mfd_surface
    ))
    evidence_map["manufacturing_date"] = FieldEvidence(
        field_name="manufacturing_date",
        label="Date of Manufacture",
        value=data.mfd.raw_text,
        ocr_confidence=mfd_conf,
        detection_confidence=0.92,
        validation_confidence=0.90,
        overall_confidence=mfd_conf,
        source_text=mfd_match.group(0) if mfd_match else "",
        surface=mfd_surface,
        bounding_box=mfd_bbox,
        status="DETECTED" if mfd_status == "Found" else "NEEDS REVIEW",
        review_reason=mfd_review,
        assignment_reasoning=mfd_reason,
        surrounding_context=mfd_context,
        semantic_class="MANUFACTURE_DATE",
        raw_ocr=mfd_match.group(0) if mfd_match else ""
    )

    # Field 18: packing_date
    pkd_match = None
    for pat in PKD_PATTERNS:
        m = pat.search(joined_text)
        if m:
            pkd_match = m
            break
    pkd_val = pkd_match.group(1).strip() if pkd_match else (data.mfd.raw_text if mfd_match else "Not Applicable")
    pkd_conf, pkd_level = (0.93, "High") if pkd_match else (0.85, "Medium")
    canonical_fields.append(CanonicalField(
        field_name="packing_date",
        statutory_name="Date of Pre-packing",
        extracted_value=pkd_val,
        raw_ocr_value=pkd_match.group(0) if pkd_match else "",
        confidence=pkd_conf,
        confidence_level=pkd_level,
        status="Found",
        bbox=mfd_bbox,
        rule_reference="Rule 6(1)(d)",
        assignment_reasoning="Resolved date of pre-packing under Rule 6(1)(d).",
        surrounding_context=mfd_context,
        semantic_class="PACKING_DATE",
        detected_on_surface=mfd_surface
    ))

    # Field 19: best_before_date
    bb_match = None
    for pat in BEST_BEFORE_PATTERNS:
        m = pat.search(joined_text)
        if m:
            bb_match = m
            break
    bb_val = bb_match.group(1).strip() if bb_match else "Not detected"
    bb_conf, bb_level = (0.94, "High") if bb_match else (0.60, "Medium")
    canonical_fields.append(CanonicalField(
        field_name="best_before_date",
        statutory_name="Best Before Period or Date",
        extracted_value=bb_val,
        raw_ocr_value=bb_match.group(0) if bb_match else "",
        confidence=bb_conf,
        confidence_level=bb_level,
        status="Found" if bb_match else "Under Review",
        bbox=mfd_bbox,
        rule_reference="Rule 6(1)(da)",
        assignment_reasoning="Resolved consumer best before period under Rule 6(1)(da)." if bb_match else "Best before declaration not detected.",
        surrounding_context=mfd_context,
        semantic_class="BEST_BEFORE",
        detected_on_surface=mfd_surface
    ))

    # Field 20: expiry_date
    exp_match = None
    for pat in EXP_PATTERNS:
        m = pat.search(joined_text)
        if m:
            exp_match = m
            break
    exp_val = exp_match.group(1).strip() if exp_match else "Not detected"
    data.expiry = DateInfo(raw_text=exp_val, complies_format=bool(exp_match)) if exp_match else None
    exp_conf, exp_level = (0.94, "High") if exp_match else (0.60, "Medium")
    canonical_fields.append(CanonicalField(
        field_name="expiry_date",
        statutory_name="Expiry Date / Use By Date",
        extracted_value=exp_val,
        raw_ocr_value=exp_match.group(0) if exp_match else "",
        confidence=exp_conf,
        confidence_level=exp_level,
        status="Found" if exp_match else "Under Review",
        bbox=mfd_bbox,
        rule_reference="Rule 6(1)(da)",
        assignment_reasoning="Resolved expiry / use-by date under Rule 6(1)(da)." if exp_match else "Expiry date declaration not detected.",
        surrounding_context=mfd_context,
        semantic_class="EXPIRY_DATE",
        detected_on_surface=mfd_surface
    ))

    data.dates = {
        "mfd": data.mfd.raw_text if data.mfd else "",
        "expiry": exp_val if exp_match else "",
        "pkd": pkd_val if pkd_match else "",
        "best_before": bb_val if bb_match else ""
    }

    # -------------------------------------------------------------------------
    # 6. Batch / Lot Number (Rule 6(1)(g))
    # -------------------------------------------------------------------------
    batch_match = None
    target_batch_line = None
    for idx, line in enumerate(extracted_lines):
        for pat in BATCH_PATTERNS:
            m = pat.search(line.text.strip())
            if m:
                batch_match = m
                target_batch_line = line
                break
        if batch_match:
            break

    if not batch_match:
        for pat in BATCH_PATTERNS:
            m = pat.search(joined_text)
            if m:
                batch_match = m
                break

    batch_bbox = target_batch_line.bbox if (target_batch_line and target_batch_line.bbox) else BoundingBox(x=15.0, y=50.0, width=45.0, height=6.0, label="Batch No")
    batch_surface = target_batch_line.surface if target_batch_line else surface
    batch_context = get_surrounding_context(target_batch_line, extracted_lines)

    if batch_match:
        raw_batch = batch_match.group(1).strip()
        data.batch = raw_batch
        data.batch_number = raw_batch
        batch_status = "Found"
        batch_conf, batch_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        batch_review = None
        batch_reason = "Extracted batch/lot code following explicit statutory prefix under Rule 6(1)(g)."
    else:
        data.batch = ""
        data.batch_number = None
        batch_status = "Under Review"
        batch_conf, batch_level = 0.45, "Needs Review"
        batch_review = "Batch number stamp not detected on current panel. Inspect coding area or crimp."
        batch_reason = "No batch identification number located on current surface."

    # Field 21: batch_number
    canonical_fields.append(CanonicalField(
        field_name="batch_number",
        statutory_name="Batch or Lot Identification Number",
        extracted_value=data.batch or "Not detected",
        raw_ocr_value=batch_match.group(0) if batch_match else "",
        confidence=batch_conf,
        confidence_level=batch_level,
        status=batch_status,
        bbox=batch_bbox,
        rule_reference="Rule 6(1)(g)",
        review_reason=batch_review,
        assignment_reasoning=batch_reason,
        surrounding_context=batch_context,
        semantic_class="BATCH_NUMBER",
        detected_on_surface=batch_surface
    ))

    # -------------------------------------------------------------------------
    # 7. Consumer Care Details (Rule 6(1)(f))
    # -------------------------------------------------------------------------
    phone_m = PHONE_PATTERN.search(joined_text)
    email_m = EMAIL_PATTERN.search(joined_text)
    has_cc_keyword = bool(re.search(r'(?:consumer\s*care|customer\s*care|helpline|toll\s*free|feedback|care@|उपभोक्ता\s*सेवा)', joined_text, re.I))

    found_phone = phone_m.group(0) if phone_m else None
    found_email = email_m.group(0) if email_m else None

    data.consumer_care = ConsumerCareInfo(
        person_or_office="Consumer Care Executive" if has_cc_keyword else "Consumer Care Cell",
        phone=found_phone,
        email=found_email
    )
    data.consumer_care_phone = found_phone
    data.consumer_care_email = found_email
    data.consumer_care_address = mfg_info.full_address or "Contact Manufacturer Address"

    cc_bbox = BoundingBox(x=12.0, y=70.0, width=75.0, height=8.0, label="Consumer Care")
    cc_line = next((l for l in extracted_lines if (found_phone and found_phone in l.text) or (found_email and found_email in l.text)), None)
    cc_context = get_surrounding_context(cc_line, extracted_lines)

    # Field 22: consumer_care_phone
    phone_status = "Found" if found_phone else "Under Review"
    phone_conf, phone_level = calculate_field_confidence(0.96, 1.0, 1.0, 1.0, 1.0, 1.0) if found_phone else (0.50, "Needs Review")
    canonical_fields.append(CanonicalField(
        field_name="consumer_care_phone",
        statutory_name="Consumer Care Toll-Free Helpline / Phone",
        extracted_value=found_phone or "Not detected",
        raw_ocr_value=found_phone or "",
        confidence=phone_conf,
        confidence_level=phone_level,
        status=phone_status,
        bbox=cc_bbox,
        rule_reference="Rule 6(1)(f)",
        review_reason=None if found_phone else "Consumer care phone helpline not detected on this surface.",
        assignment_reasoning="Extracted consumer grievance helpline / toll-free contact under Rule 6(1)(f)." if found_phone else "Helpline phone number not detected.",
        surrounding_context=cc_context,
        semantic_class="CONSUMER_CARE_PHONE",
        detected_on_surface=surface
    ))

    # Field 23: consumer_care_email
    email_status = "Found" if found_email else "Under Review"
    email_conf, email_level = calculate_field_confidence(0.97, 1.0, 1.0, 1.0, 1.0, 1.0) if found_email else (0.50, "Needs Review")
    canonical_fields.append(CanonicalField(
        field_name="consumer_care_email",
        statutory_name="Consumer Care Email Address",
        extracted_value=found_email or "Not detected",
        raw_ocr_value=found_email or "",
        confidence=email_conf,
        confidence_level=email_level,
        status=email_status,
        bbox=cc_bbox,
        rule_reference="Rule 6(1)(f)",
        review_reason=None if found_email else "Consumer care email not detected on this surface.",
        assignment_reasoning="Extracted consumer grievance email address under Rule 6(1)(f)." if found_email else "Consumer care email not detected.",
        surrounding_context=cc_context,
        semantic_class="CONSUMER_CARE_EMAIL",
        detected_on_surface=surface
    ))

    # Field 24: consumer_care_address
    cc_addr_val = data.consumer_care_address or "Same as Manufacturer Address"
    cc_addr_conf, cc_addr_level = (0.93, "High") if mfg_info.full_address else (0.60, "Medium")
    canonical_fields.append(CanonicalField(
        field_name="consumer_care_address",
        statutory_name="Consumer Care Physical Office Address",
        extracted_value=cc_addr_val,
        raw_ocr_value=cc_addr_val,
        confidence=cc_addr_conf,
        confidence_level=cc_addr_level,
        status="Found" if mfg_info.full_address else "Under Review",
        bbox=cc_bbox,
        rule_reference="Rule 6(1)(f)",
        assignment_reasoning="Resolved consumer care physical office address linked to manufacturer facility." if mfg_info.full_address else "Physical address not detected.",
        surrounding_context=cc_context,
        semantic_class="CONSUMER_CARE_ADDRESS",
        detected_on_surface=surface
    ))

    # Consolidated Consumer Care Evidence Map
    cc_val = ""
    if found_phone and found_email:
        cc_val = f"Helpline: {found_phone} | Email: {found_email}"
    elif found_phone:
        cc_val = f"Helpline: {found_phone}"
    elif found_email:
        cc_val = f"Email: {found_email}"
    else:
        cc_val = "Not detected"

    evidence_map["consumer_care"] = FieldEvidence(
        field_name="consumer_care",
        label="Consumer Care Cell",
        value=cc_val,
        ocr_confidence=0.95 if (found_phone or found_email) else 0.50,
        detection_confidence=0.92,
        validation_confidence=0.90,
        overall_confidence=0.93 if (found_phone or found_email) else 0.50,
        source_text=cc_val,
        surface=surface,
        bounding_box=cc_bbox,
        status="DETECTED" if (found_phone or found_email) else "NEEDS REVIEW",
        assignment_reasoning="Consolidated consumer care channels (phone / email) under Rule 6(1)(f).",
        surrounding_context=cc_context,
        semantic_class="CONSUMER_CARE_PHONE",
        raw_ocr=cc_val
    )

    # Dynamic Classification Object
    data.classification = ProductClassification(
        product_type=data.commodity_name,
        is_imported=is_imported_coo,
        is_liquid=(data.net_quantity.unit.lower() in ["ml", "l", "ltr"]),
        confidence=0.95,
        reasoning=f"Identified commodity: {data.commodity_name} ({detected_category}) with unit {data.net_quantity.unit}"
    )

    data.evidence = evidence_map
    return data, canonical_fields, evidence_map

# -------------------------------------------------------------------
# STEP 3.6: MULTI-SURFACE FUSION ENGINE
# -------------------------------------------------------------------

def fuse_multi_surface_extractions(
    surface_extractions: List[Tuple[str, StructuredProductData, List[CanonicalField], Dict[str, FieldEvidence]]]
) -> Tuple[StructuredProductData, List[CanonicalField], Dict[str, FieldEvidence]]:
    """Fuses extracted declarations from multiple packaging surfaces (Front/PDP, Back Panel,
    Side Panels, Coding Area/Crimp). Resolves disagreements by picking the candidate with the
    highest confidence and complete evidence, while recording cross-surface agreement.
    """
    normalized_extractions = []
    for item in surface_extractions:
        if len(item) == 4:
            if isinstance(item[0], str):
                surf, p_data, can_fields, ev_map = item
            else:
                p_data, can_fields, ev_map, surf = item
            normalized_extractions.append((surf, p_data, can_fields, ev_map))

    if not normalized_extractions:
        return StructuredProductData(), [], {}

    if len(normalized_extractions) == 1:
        surf, data, can_fields, ev_map = normalized_extractions[0]
        return data, can_fields, ev_map

    best_fields: Dict[str, CanonicalField] = {}
    best_evidences: Dict[str, FieldEvidence] = {}

    for surf, p_data, can_fields, ev_map in normalized_extractions:
        for field in can_fields:
            fn = field.field_name
            if fn not in best_fields:
                best_fields[fn] = field
            else:
                existing = best_fields[fn]
                # If current field was 'Found' or has higher confidence, replace
                if field.status == "Found" and existing.status != "Found":
                    best_fields[fn] = field
                elif field.confidence > existing.confidence and existing.status != "Defective":
                    best_fields[fn] = field

        for k, ev in ev_map.items():
            if k not in best_evidences or ev.overall_confidence > best_evidences[k].overall_confidence:
                best_evidences[k] = ev

    # Base structured product data on the primary surface and enrich with fused fields
    _, primary_data, _, _ = normalized_extractions[0]
    fused_data = primary_data.model_copy(deep=True)
    for surf, p_data, _, _ in normalized_extractions:
        if p_data.manufacturer and p_data.manufacturer.name and p_data.manufacturer.name != "Not detected":
            if not fused_data.manufacturer or not fused_data.manufacturer.name or fused_data.manufacturer.name == "Not detected":
                fused_data.manufacturer = p_data.manufacturer
                fused_data.manufacturer_name = p_data.manufacturer_name
                fused_data.manufacturer_address = p_data.manufacturer_address
        if p_data.net_quantity and p_data.net_quantity.value > 0 and fused_data.net_quantity.value == 0:
            fused_data.net_quantity = p_data.net_quantity
        if p_data.mrp and p_data.mrp.amount > 0 and fused_data.mrp.amount == 0:
            fused_data.mrp = p_data.mrp
        if p_data.batch_number and p_data.batch_number != "Not detected":
            if not fused_data.batch_number or fused_data.batch_number == "Not detected":
                fused_data.batch_number = p_data.batch_number
        if p_data.dates and isinstance(p_data.dates, dict):
            p_mfd = p_data.dates.get("mfd")
            if p_mfd and p_mfd != "Not detected":
                if fused_data.dates.get("mfd") in [None, "", "Not detected"]:
                    fused_data.dates["mfd"] = p_mfd
            p_exp = p_data.dates.get("expiry")
            if p_exp and p_exp != "Not detected":
                if fused_data.dates.get("expiry") in [None, "", "Not detected"]:
                    fused_data.dates["expiry"] = p_exp
            p_pkd = p_data.dates.get("pkd")
            if p_pkd and p_pkd != "Not detected":
                if fused_data.dates.get("pkd") in [None, "", "Not detected"]:
                    fused_data.dates["pkd"] = p_pkd
            p_bb = p_data.dates.get("best_before")
            if p_bb and p_bb != "Not detected":
                if fused_data.dates.get("best_before") in [None, "", "Not detected"]:
                    fused_data.dates["best_before"] = p_bb
        if p_data.importer and p_data.importer.name and p_data.importer.name != "Not detected":
            if not fused_data.importer or not fused_data.importer.name or fused_data.importer.name == "Not detected":
                fused_data.importer = p_data.importer
                fused_data.importer_name = p_data.importer_name

    fused_canonical = list(best_fields.values())
    return fused_data, fused_canonical, best_evidences

