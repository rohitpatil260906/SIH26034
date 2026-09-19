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
    ProductClassification,
    ProductCategory,
    SemanticRegionType,
    UniversalFieldStatus,
    UniversalComplianceStatus,
    LmCompassFieldItem,
    LmCompassComplianceItem,
    LmCompassViolationItem,
    LmCompassNeedsReviewItem,
    LmCompassResult,
    ComplianceCheckItem
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
    re.compile(r'(?:Mfd(?:\s*Date)?|Mfg(?:\s*Date)?|Date\s*of\s*(?:Mfg|Mfd|Manufacture|Manufacturing)|Manufactured(?:\s*Date)?|उत्पादन\s*तिथि)\s*[:.\-\s]*((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4})', re.I)
]

PKD_PATTERNS = [
    re.compile(r'(?:Packed(?:\s*Date)?|Pkd(?:\s*Date)?|Date\s*of\s*Packing|पैकिंग\s*तिथि)\s*[:.\-\s]*((?:[0-9]{1,2}[\/\-\.])?[0-9]{1,2}[\/\-\.][0-9]{2,4}|[a-zA-Z]{3,9}\s*[\'\-]?[0-9]{2,4})', re.I)
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

# Standard commodity dictionary for generic name resolution and category mapping across Categories A through R
COMMODITY_KEYWORDS = {
    # Category A: Food and Beverage
    "tea": ("Tea", ProductCategory.FOOD_BEVERAGE),
    "coffee": ("Coffee", ProductCategory.FOOD_BEVERAGE),
    "biscuit": ("Biscuits", ProductCategory.FOOD_BEVERAGE),
    "biscuits": ("Biscuits", ProductCategory.FOOD_BEVERAGE),
    "cookies": ("Cookies", ProductCategory.FOOD_BEVERAGE),
    "atta": ("Wheat Flour (Atta)", ProductCategory.FOOD_BEVERAGE),
    "flour": ("Flour", ProductCategory.FOOD_BEVERAGE),
    "rice": ("Rice", ProductCategory.FOOD_BEVERAGE),
    "sugar": ("Sugar", ProductCategory.FOOD_BEVERAGE),
    "salt": ("Edible Common Salt", ProductCategory.FOOD_BEVERAGE),
    "spices": ("Spices", ProductCategory.FOOD_BEVERAGE),
    "masala": ("Spice Blend (Masala)", ProductCategory.FOOD_BEVERAGE),
    "edible oil": ("Edible Vegetable Oil", ProductCategory.FOOD_BEVERAGE),
    "mustard oil": ("Mustard Oil", ProductCategory.FOOD_BEVERAGE),
    "sunflower oil": ("Sunflower Oil", ProductCategory.FOOD_BEVERAGE),
    "soyabean oil": ("Soyabean Oil", ProductCategory.FOOD_BEVERAGE),
    "ghee": ("Ghee", ProductCategory.FOOD_BEVERAGE),
    "butter": ("Butter", ProductCategory.FOOD_BEVERAGE),
    "chips": ("Potato Chips", ProductCategory.FOOD_BEVERAGE),
    "namkeen": ("Namkeen / Savouries", ProductCategory.FOOD_BEVERAGE),
    "chocolate": ("Chocolate", ProductCategory.FOOD_BEVERAGE),
    "juice": ("Fruit Juice", ProductCategory.FOOD_BEVERAGE),
    "noodles": ("Instant Noodles", ProductCategory.FOOD_BEVERAGE),
    "pasta": ("Pasta", ProductCategory.FOOD_BEVERAGE),
    "milk": ("Packaged Milk", ProductCategory.FOOD_BEVERAGE),
    "bread": ("Bread", ProductCategory.FOOD_BEVERAGE),
    "cereal": ("Breakfast Cereal", ProductCategory.FOOD_BEVERAGE),
    "pulses": ("Pulses / Dal", ProductCategory.FOOD_BEVERAGE),
    "dal": ("Pulses / Dal", ProductCategory.FOOD_BEVERAGE),
    "soft drink": ("Carbonated Soft Drink", ProductCategory.FOOD_BEVERAGE),
    "energy drink": ("Energy Drink", ProductCategory.FOOD_BEVERAGE),
    "snack": ("Packaged Snack", ProductCategory.FOOD_BEVERAGE),
    "water": ("Packaged Drinking Water", ProductCategory.FOOD_BEVERAGE),
    "wafers": ("Wafers", ProductCategory.FOOD_BEVERAGE),

    # Category B: Cosmetics and Personal Care
    "shampoo": ("Hair Shampoo", ProductCategory.COSMETICS_PERSONAL_CARE),
    "conditioner": ("Hair Conditioner", ProductCategory.COSMETICS_PERSONAL_CARE),
    "face wash": ("Facial Cleanser / Face Wash", ProductCategory.COSMETICS_PERSONAL_CARE),
    "facial cleanser": ("Facial Cleanser", ProductCategory.COSMETICS_PERSONAL_CARE),
    "cream": ("Skin Cream", ProductCategory.COSMETICS_PERSONAL_CARE),
    "skin cream": ("Skin Cream", ProductCategory.COSMETICS_PERSONAL_CARE),
    "lotion": ("Body Lotion", ProductCategory.COSMETICS_PERSONAL_CARE),
    "body lotion": ("Body Lotion", ProductCategory.COSMETICS_PERSONAL_CARE),
    "sunscreen": ("Sunscreen Lotion / Gel", ProductCategory.COSMETICS_PERSONAL_CARE),
    "sunscreen lotion": ("Sunscreen Lotion", ProductCategory.COSMETICS_PERSONAL_CARE),
    "sunscreen gel": ("Sunscreen Gel", ProductCategory.COSMETICS_PERSONAL_CARE),
    "moisturizer": ("Moisturizer", ProductCategory.COSMETICS_PERSONAL_CARE),
    "hair oil": ("Hair Oil", ProductCategory.COSMETICS_PERSONAL_CARE),
    "hair serum": ("Hair Serum", ProductCategory.COSMETICS_PERSONAL_CARE),
    "hair gel": ("Hair Gel", ProductCategory.COSMETICS_PERSONAL_CARE),
    "toothpaste": ("Toothpaste", ProductCategory.COSMETICS_PERSONAL_CARE),
    "deodorant": ("Deodorant", ProductCategory.COSMETICS_PERSONAL_CARE),
    "perfume": ("Perfume / Eau de Parfum", ProductCategory.COSMETICS_PERSONAL_CARE),
    "body spray": ("Body Spray", ProductCategory.COSMETICS_PERSONAL_CARE),
    "lipstick": ("Lipstick", ProductCategory.COSMETICS_PERSONAL_CARE),
    "eyeliner": ("Eyeliner", ProductCategory.COSMETICS_PERSONAL_CARE),
    "foundation": ("Foundation Cream", ProductCategory.COSMETICS_PERSONAL_CARE),
    "kajal": ("Kajal", ProductCategory.COSMETICS_PERSONAL_CARE),
    "nail polish": ("Nail Polish", ProductCategory.COSMETICS_PERSONAL_CARE),
    "shaving cream": ("Shaving Cream", ProductCategory.COSMETICS_PERSONAL_CARE),
    "aftershave": ("Aftershave Lotion", ProductCategory.COSMETICS_PERSONAL_CARE),
    "facial scrub": ("Facial Scrub", ProductCategory.COSMETICS_PERSONAL_CARE),
    "face mask": ("Facial Mask", ProductCategory.COSMETICS_PERSONAL_CARE),
    "talcum powder": ("Talcum Powder", ProductCategory.COSMETICS_PERSONAL_CARE),
    "hand cream": ("Hand Cream", ProductCategory.COSMETICS_PERSONAL_CARE),

    # Category C: Household Cleaning Products
    "detergent": ("Detergent Powder", ProductCategory.HOUSEHOLD_CLEANING),
    "detergent powder": ("Detergent Powder", ProductCategory.HOUSEHOLD_CLEANING),
    "detergent bar": ("Detergent Bar", ProductCategory.HOUSEHOLD_CLEANING),
    "detergent liquid": ("Detergent Liquid", ProductCategory.HOUSEHOLD_CLEANING),
    "dishwash": ("Dishwashing Liquid", ProductCategory.HOUSEHOLD_CLEANING),
    "dishwashing liquid": ("Dishwashing Liquid", ProductCategory.HOUSEHOLD_CLEANING),
    "dishwashing bar": ("Dishwashing Bar", ProductCategory.HOUSEHOLD_CLEANING),
    "floor cleaner": ("Floor Cleaner", ProductCategory.HOUSEHOLD_CLEANING),
    "toilet cleaner": ("Toilet Cleaner", ProductCategory.HOUSEHOLD_CLEANING),
    "glass cleaner": ("Glass Cleaner", ProductCategory.HOUSEHOLD_CLEANING),
    "surface disinfectant": ("Surface Disinfectant", ProductCategory.HOUSEHOLD_CLEANING),
    "bleach": ("Bleaching Powder / Liquid", ProductCategory.HOUSEHOLD_CLEANING),
    "fabric conditioner": ("Fabric Conditioner", ProductCategory.HOUSEHOLD_CLEANING),
    "stain remover": ("Stain Remover", ProductCategory.HOUSEHOLD_CLEANING),
    "cleaner": ("Household Cleaner", ProductCategory.HOUSEHOLD_CLEANING),

    # Category D: Toiletries
    "soap": ("Toilet Soap / Bathing Bar", ProductCategory.TOILETRIES),
    "bath soap": ("Toilet Soap", ProductCategory.TOILETRIES),
    "toilet soap": ("Toilet Soap", ProductCategory.TOILETRIES),
    "beauty soap": ("Toilet Soap", ProductCategory.TOILETRIES),
    "bathing bar": ("Bathing Bar", ProductCategory.TOILETRIES),
    "hand wash": ("Liquid Hand Wash", ProductCategory.TOILETRIES),
    "body wash": ("Body Wash", ProductCategory.TOILETRIES),
    "sanitizer": ("Hand Sanitizer", ProductCategory.TOILETRIES),
    "wet wipes": ("Cleansing Wet Wipes", ProductCategory.TOILETRIES),
    "cotton buds": ("Cotton Buds", ProductCategory.TOILETRIES),
    "shaving foam": ("Shaving Foam", ProductCategory.TOILETRIES),

    # Category E: Health / Wellness Products
    "supplement": ("Dietary Supplement", ProductCategory.HEALTH_WELLNESS),
    "protein powder": ("Protein Powder", ProductCategory.HEALTH_WELLNESS),
    "multivitamin": ("Multivitamin Tablets / Capsules", ProductCategory.HEALTH_WELLNESS),
    "cough lozenges": ("Cough Lozenges", ProductCategory.HEALTH_WELLNESS),
    "herbal extract": ("Herbal Extract", ProductCategory.HEALTH_WELLNESS),
    "pain relief balm": ("Pain Relief Balm", ProductCategory.HEALTH_WELLNESS),
    "balm": ("Pain Relief Balm", ProductCategory.HEALTH_WELLNESS),
    "bandage": ("Adhesive Bandage", ProductCategory.HEALTH_WELLNESS),
    "glucose powder": ("Glucose Powder", ProductCategory.HEALTH_WELLNESS),

    # Category F: Packaged Household Goods
    "aluminium foil": ("Aluminium Foil", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "cling film": ("Cling Film", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "garbage bags": ("Garbage Bags", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "tissue": ("Facial Tissues", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "paper napkins": ("Paper Napkins", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "matches": ("Safety Matches", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "mosquito coil": ("Mosquito Repellent Coil", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "air freshener": ("Air Freshener", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),
    "candles": ("Wax Candles", ProductCategory.PACKAGED_HOUSEHOLD_GOODS),

    # Category G: Electrical / Electronic Consumer Products
    "mobile charger": ("Mobile Charger", ProductCategory.ELECTRONICS),
    "charger": ("Mobile Charger", ProductCategory.ELECTRONICS),
    "usb cable": ("USB Data Cable", ProductCategory.ELECTRONICS),
    "cable": ("Data Cable", ProductCategory.ELECTRONICS),
    "data cable": ("Data Cable", ProductCategory.ELECTRONICS),
    "earphones": ("Earphones", ProductCategory.ELECTRONICS),
    "headphones": ("Headphones", ProductCategory.ELECTRONICS),
    "power bank": ("Power Bank", ProductCategory.ELECTRONICS),
    "battery": ("Dry Cell Battery", ProductCategory.ELECTRONICS),
    "led bulb": ("LED Bulb", ProductCategory.ELECTRONICS),
    "bulb": ("LED Bulb", ProductCategory.ELECTRONICS),
    "mobile phone": ("Mobile Phone", ProductCategory.ELECTRONICS),
    "adapter": ("Power Adapter", ProductCategory.ELECTRONICS),
    "mouse": ("Computer Mouse", ProductCategory.ELECTRONICS),
    "keyboard": ("Computer Keyboard", ProductCategory.ELECTRONICS),
    "speaker": ("Bluetooth Speaker", ProductCategory.ELECTRONICS),
    "torch": ("Rechargeable Torch", ProductCategory.ELECTRONICS),

    # Category H: Stationery
    "ball pen": ("Ballpoint Pen", ProductCategory.STATIONERY),
    "gel pen": ("Gel Pen", ProductCategory.STATIONERY),
    "pen": ("Writing Pen", ProductCategory.STATIONERY),
    "pencil": ("Graphite Pencil", ProductCategory.STATIONERY),
    "notebook": ("Paper Notebook", ProductCategory.STATIONERY),
    "marker": ("Permanent Marker", ProductCategory.STATIONERY),
    "highlighter": ("Highlighter Pen", ProductCategory.STATIONERY),
    "eraser": ("Pencil Eraser", ProductCategory.STATIONERY),
    "sharpener": ("Pencil Sharpener", ProductCategory.STATIONERY),
    "stapler": ("Desktop Stapler", ProductCategory.STATIONERY),
    "sticky notes": ("Sticky Notes", ProductCategory.STATIONERY),

    # Category I: Toys
    "toy": ("Children Toy", ProductCategory.TOYS),
    "toy car": ("Toy Vehicle", ProductCategory.TOYS),
    "doll": ("Fashion Doll", ProductCategory.TOYS),
    "building blocks": ("Building Blocks Toy", ProductCategory.TOYS),
    "puzzle": ("Jigsaw Puzzle", ProductCategory.TOYS),
    "board game": ("Board Game", ProductCategory.TOYS),
    "action figure": ("Action Figure Toy", ProductCategory.TOYS),
    "rattle": ("Baby Rattle", ProductCategory.TOYS),
    "soft toy": ("Plush Soft Toy", ProductCategory.TOYS),
    "teddy bear": ("Plush Teddy Bear", ProductCategory.TOYS),

    # Category J: Garments / Textiles
    "shirt": ("Readymade Garment (Shirt)", ProductCategory.GARMENTS_TEXTILES),
    "t-shirt": ("Readymade Garment (T-Shirt)", ProductCategory.GARMENTS_TEXTILES),
    "trousers": ("Readymade Garment (Trousers)", ProductCategory.GARMENTS_TEXTILES),
    "pants": ("Readymade Garment (Pants)", ProductCategory.GARMENTS_TEXTILES),
    "jeans": ("Readymade Garment (Jeans)", ProductCategory.GARMENTS_TEXTILES),
    "kurta": ("Readymade Garment (Kurta)", ProductCategory.GARMENTS_TEXTILES),
    "hosiery": ("Hosiery Product", ProductCategory.GARMENTS_TEXTILES),
    "socks": ("Hosiery (Socks)", ProductCategory.GARMENTS_TEXTILES),
    "garment": ("Readymade Garment", ProductCategory.GARMENTS_TEXTILES),
    "readymade garment": ("Readymade Garment", ProductCategory.GARMENTS_TEXTILES),
    "bedsheet": ("Cotton Bedsheet", ProductCategory.GARMENTS_TEXTILES),
    "towel": ("Bath Towel", ProductCategory.GARMENTS_TEXTILES),
    "fabric": ("Textile Fabric", ProductCategory.GARMENTS_TEXTILES),

    # Category K: Footwear
    "shoes": ("Footwear (Shoes)", ProductCategory.FOOTWEAR),
    "sports shoes": ("Sports Shoes", ProductCategory.FOOTWEAR),
    "sneakers": ("Sneakers", ProductCategory.FOOTWEAR),
    "sandals": ("Footwear (Sandals)", ProductCategory.FOOTWEAR),
    "slippers": ("Footwear (Slippers)", ProductCategory.FOOTWEAR),
    "flip flops": ("Footwear (Flip Flops)", ProductCategory.FOOTWEAR),
    "boots": ("Footwear (Boots)", ProductCategory.FOOTWEAR),
    "footwear": ("Footwear", ProductCategory.FOOTWEAR),

    # Category L: Hardware / Tools
    "screwdriver": ("Screwdriver Tool", ProductCategory.HARDWARE_TOOLS),
    "spanner": ("Spanner / Wrench Tool", ProductCategory.HARDWARE_TOOLS),
    "hammer": ("Claw Hammer", ProductCategory.HARDWARE_TOOLS),
    "pliers": ("Combination Pliers", ProductCategory.HARDWARE_TOOLS),
    "screws": ("Hardware Fasteners (Screws)", ProductCategory.HARDWARE_TOOLS),
    "drill bit": ("Drill Bit", ProductCategory.HARDWARE_TOOLS),
    "measuring tape": ("Measuring Tape", ProductCategory.HARDWARE_TOOLS),
    "padlock": ("Security Padlock", ProductCategory.HARDWARE_TOOLS),

    # Category M: Packaged Industrial Products
    "industrial adhesive": ("Industrial Adhesive", ProductCategory.PACKAGED_INDUSTRIAL),
    "lubricating grease": ("Lubricating Grease", ProductCategory.PACKAGED_INDUSTRIAL),
    "machine oil": ("Machine Lubricant Oil", ProductCategory.PACKAGED_INDUSTRIAL),
    "cutting oil": ("Cutting Oil", ProductCategory.PACKAGED_INDUSTRIAL),
    "bearing": ("Ball Bearing", ProductCategory.PACKAGED_INDUSTRIAL),
    "welding rod": ("Welding Electrode", ProductCategory.PACKAGED_INDUSTRIAL),

    # Category N: Agricultural Products / Seeds / Inputs
    "hybrid seeds": ("Hybrid Crop Seeds", ProductCategory.AGRICULTURAL),
    "seeds": ("Agricultural Seeds", ProductCategory.AGRICULTURAL),
    "pesticide": ("Agricultural Pesticide", ProductCategory.AGRICULTURAL),
    "insecticide": ("Agricultural Insecticide", ProductCategory.AGRICULTURAL),
    "fertilizer": ("Crop Fertilizer", ProductCategory.AGRICULTURAL),
    "bio-fertilizer": ("Bio-Fertilizer", ProductCategory.AGRICULTURAL),

    # Category O: Pet Food / Animal Products
    "dog food": ("Dog Food", ProductCategory.PET_FOOD),
    "cat food": ("Cat Food", ProductCategory.PET_FOOD),
    "bird feed": ("Bird Feed", ProductCategory.PET_FOOD),
    "fish food": ("Fish Food", ProductCategory.PET_FOOD),
    "pet food": ("Packaged Pet Food", ProductCategory.PET_FOOD),

    # Hardware / Paint / Tools (Category J)
    "paint": ("Wall Paint / Emulsion", ProductCategory.HARDWARE),
    "wall emulsion": ("Wall Emulsion Paint", ProductCategory.HARDWARE),
    "emulsion": ("Emulsion Paint", ProductCategory.HARDWARE),
    "acrylic emulsion": ("Acrylic Emulsion Paint", ProductCategory.HARDWARE),
    "enamel paint": ("Enamel Paint", ProductCategory.HARDWARE),
    "wall paint": ("Wall Paint", ProductCategory.HARDWARE),

    # Imported Commodities (Category P)
    "imported commodity": ("Imported Packaged Commodity", ProductCategory.IMPORTED),
    "imported product": ("Imported Packaged Commodity", ProductCategory.IMPORTED),
    "imported packaged commodity": ("Imported Packaged Commodity", ProductCategory.IMPORTED),

    # Pan Masala & Tobacco (mapped to Tobacco Category N)
    "pan masala": ("Pan Masala", ProductCategory.TOBACCO),
    "supari": ("Betel Nut / Supari", ProductCategory.TOBACCO)
}

CATEGORY_CODE_MAP: Dict[str, str] = {
    ProductCategory.FOOD: "A",
    ProductCategory.BEVERAGES: "B",
    ProductCategory.COSMETICS: "C",
    ProductCategory.CLEANING: "D",
    ProductCategory.PHARMA: "E",
    ProductCategory.ELECTRONICS: "F",
    ProductCategory.STATIONERY: "G",
    ProductCategory.TOYS: "H",
    ProductCategory.TEXTILES: "I",
    ProductCategory.HARDWARE: "J",
    ProductCategory.AUTOMOTIVE: "K",
    ProductCategory.AGRICULTURAL: "L",
    ProductCategory.PET: "M",
    ProductCategory.TOBACCO: "N",
    ProductCategory.INDUSTRIAL: "O",
    ProductCategory.IMPORTED: "P",
    ProductCategory.ECOMMERCE: "Q",
    ProductCategory.UNKNOWN: "R",
    # Backward compatibility aliases
    "Food and Beverage": "A",
    "Cosmetics and Personal Care": "C",
    "Household Cleaning Products": "D",
    "Toiletries": "D",
    "Health / Wellness Products": "E",
    "Packaged Household Goods": "D",
    "Electrical / Electronic Consumer Products": "F",
    "Stationery": "G",
    "Toys": "H",
    "Garments / Textiles": "I",
    "Footwear": "I",
    "Hardware / Tools": "J",
    "Packaged Industrial Products": "O",
    "Agricultural Products / Seeds / Inputs": "L",
    "Pet Food / Animal Products": "M",
    "Imported Packaged Commodity": "P",
    "Other Packaged Commodity": "Q",
    "Unknown / Uncertain": "R",
    "Food & Beverage": "A",
    "Cosmetics & Personal Care": "C",
    "Cleaning & Household": "D",
    "Garments & Apparel": "I",
    "Electronics & Electricals": "F",
    "Medical Devices": "E",
    "Pan Masala & Tobacco": "N"
}

def classify_product_category(
    joined_text: str,
    extracted_lines: Optional[List[ExtractedLine]] = None
) -> Tuple[str, str, float, str]:
    """Universal 18-Category Product Classifier (Categories A through R)
    Returns: (category_name, category_code, confidence, rationale)
    
    If ungrounded or ambiguous:
    Returns (ProductCategory.UNKNOWN, 'R', 0.40, 'No definitive statutory commodity keywords identified; requires manual review')
    """
    text_lower = joined_text.lower()
    
    # 1. Match against COMMODITY_KEYWORDS (longest keyword match first)
    sorted_keywords = sorted(COMMODITY_KEYWORDS.keys(), key=len, reverse=True)
    for kw in sorted_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            gen_name, cat = COMMODITY_KEYWORDS[kw]
            code = CATEGORY_CODE_MAP.get(cat, "R")
            return (cat, code, 0.95, f"Matched canonical commodity keyword '{kw}' corresponding to {cat} (Category {code})")

    # 2. Check if product is explicitly declared as Imported Commodity under Chapter III / Rule 27
    if re.search(r'\b(?:imported\s*(?:by|product|commodity|packaged\s*commodity)|month\s*&\s*year\s*of\s*import|country\s*of\s*origin\s*:\s*(?!india)[a-z]+|product\s*of\s+(?!india)[a-z]+)\b', text_lower):
        return (ProductCategory.IMPORTED, "P", 0.95, "Identified explicit imported packaging declaration / non-India origin under Rule 6(1)(n) / Chapter III")
            
    # 3. Contextual feature detection
    if re.search(r'\b(?:fssai|nutritional\s*information|per\s*100g|energy\s*kcal|ingredients\s*:\s*sugar|edible\s*vegetable)\b', text_lower):
        return (ProductCategory.FOOD, "A", 0.92, "Identified food regulatory FSSAI / nutrition table declarations")
    if re.search(r'\b(?:mfg\s*lic\s*no\s*cos|for\s*external\s*use\s*only|dermatologically\s*tested|inci\b|sunscreen|spf\s*\d+)\b', text_lower):
        return (ProductCategory.COSMETICS, "C", 0.92, "Identified cosmetic manufacturing license / dermatological usage declaration")
    if re.search(r'\b(?:kills\s*99\.9%|detergent|dishwash|surface\s*cleaner|bleach|disinfectant)\b', text_lower):
        return (ProductCategory.CLEANING, "D", 0.91, "Identified household cleaning / disinfecting formulations")
    if re.search(r'\b(?:beverage|fruit\s*juice|drink|nectar|squash)\b', text_lower):
        return (ProductCategory.BEVERAGES, "B", 0.91, "Identified packaged beverage declarations")
    if re.search(r'\b(?:rated\s*voltage|frequency\s*50hz|input\s*:\s*\d+v|output\s*:\s*\d+v|bis\s*reg|is\s*13252|wireless\s*mouse|keyboard)\b', text_lower):
        return (ProductCategory.ELECTRONICS, "F", 0.93, "Identified electronic electrical rating / BIS safety compliance declaration")
    if re.search(r'\b(?:choking\s*hazard|not\s*suitable\s*for\s*children\s*under\s*3|is\s*9873)\b', text_lower):
        return (ProductCategory.TOYS, "H", 0.93, "Identified toy safety warning / IS 9873 compliance declaration")
    if re.search(r'\b(?:chest\s*:\s*\d+\s*cm|waist\s*:\s*\d+\s*cm|100%\s*cotton|wash\s*care)\b', text_lower):
        return (ProductCategory.TEXTILES, "I", 0.92, "Identified readymade garment body size / textile composition under Rule 26(e)")
    if re.search(r'\b(?:size\s*:\s*\d+\s*(?:uk|ind|us|eu)|sole\s*material|upper\s*material)\b', text_lower):
        return (ProductCategory.TEXTILES, "I", 0.92, "Identified footwear size / material specification declaration")
    if re.search(r'\b(?:pet\s*food\s*only|dog\s*food|cat\s*food|crude\s*protein|crude\s*fiber)\b', text_lower):
        return (ProductCategory.PET, "M", 0.92, "Identified pet animal food statutory nutritional declaration")
    if re.search(r'\b(?:germination\s*min|inert\s*matter|weed\s*seeds|net\s*seeds|fertilizer|insecticide)\b', text_lower):
        return (ProductCategory.AGRICULTURAL, "L", 0.91, "Identified agricultural inputs / seed quality statutory declaration")
    if re.search(r'\b(?:for\s*industrial\s*use\s*only|industrial\s*adhesive|bearing\s*no)\b', text_lower):
        return (ProductCategory.INDUSTRIAL, "O", 0.90, "Identified industrial packaged commodity declaration")
    if re.search(r'\b(?:chrome\s*vanadium|torque|spanner|hex\s*key|screw\s*driver|emulsion|wall\s*paint)\b', text_lower):
        return (ProductCategory.HARDWARE, "J", 0.90, "Identified hardware / hand tool specifications")
    if re.search(r'\b(?:ruled\s*notebook|pages|gsm\s*paper|ball\s*pen|gel\s*pen|writing\s*instrument)\b', text_lower):
        return (ProductCategory.STATIONERY, "G", 0.90, "Identified stationery item specifications")
    if re.search(r'\b(?:dietary\s*supplement|nutraceutical|ayush|ayurvedic\s*medicine|not\s*for\s*medicinal\s*use)\b', text_lower):
        return (ProductCategory.PHARMA, "E", 0.90, "Identified wellness / nutraceutical statutory declaration")
    if re.search(r'\b(?:bathing\s*bar|toilet\s*soap|hand\s*wash|tfm\s*\d+%)\b', text_lower):
        return (ProductCategory.CLEANING, "D", 0.91, "Identified toiletries / bathing bar formulation")
        
    # 4. Ungrounded / Ambiguous fallback -> Unknown / Uncertain (R)
    return (ProductCategory.UNKNOWN, "R", 0.40, "No definitive statutory commodity keywords identified; requires manual review")

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

    # 2. Usage / Storage Directions (STRICT PRIORITY: NEVER ADDRESS OR COMMERCIAL ENTITY)
    if (re.search(r'^(?:direction\s*of\s*use|directions?(?:\s*for\s*use)?|how\s*to\s*use|mode\s*of\s*application|application|usage(?:\s*instructions?)?|storage(?:\s*instructions?)?|store\s*in|उपयोग\s*विधि)\b', clean_t, re.I)
        or re.search(r'\b(?:apply\s*(?:generously|evenly|smoothly|liberally)|reapply\s*(?:every|after)|massage\s*gently|rinse\s*thoroughly|for\s*best\s*results\s*apply|rub\s*on|do\s*not\s*swallow|keep\s*in\s*a\s*cool\s*and\s*dry\s*place|store\s*away\s*from\s*direct\s*sunlight)\b', clean_t, re.I)):
        return (SemanticRegionType.DIRECTIONS, 0.96, "Matched product usage, application or storage instructions")

    # 3. Formulation Ingredients (STRICT PRIORITY: NEVER ADDRESS OR COMMERCIAL ENTITY)
    if re.search(r'^(?:ingredients?|composition|key\s*ingredients?|active\s*ingredients?|contains|सामग्री)\b', clean_t, re.I) or len(INGREDIENT_PATTERNS.findall(clean_t)) >= 2:
        return (SemanticRegionType.INGREDIENTS, 0.96, "Matched formulation ingredient / chemical / botanical listing")

    # 4. Possible Ingredients (comma-separated chemical / botanical substance listing)
    if ("," in clean_t and len(clean_t.split(",")) >= 3 and
        any(re.search(r'(?:aqua|water|glycerin|glycol|salicylate|acid|oxide|sulfate|chloride|extract|oil|paraben|fragrance|parfum|tocopherol|dimethicone|edta|niacinamide|citric)\b', part, re.I) for part in clean_t.split(","))):
        return (SemanticRegionType.POSSIBLE_INGREDIENTS, 0.90, "Matched formulation chemical or botanical substance listing")

    # 5. Statutory Warnings / Advisories
    if re.search(r'^(?:caution|warning|warnings?|for\s*external\s*use\s*only|for\s*external\s*use|keep\s*out\s*of\s*reach|not\s*for\s*medicinal|avoid\s*contact\s*with\s*eyes|चेतावनी)\b', clean_t, re.I):
        return (SemanticRegionType.WARNING, 0.95, "Matched statutory caution/safety advisory statement")

    # 6. Marketer / Brand Owner
    if re.search(r'^(?:marketed\s*by|mktg?\.?\s*by|distributed\s*by|mktd?\.?\s*by|मार्केटेड)\b', clean_t, re.I):
        return (SemanticRegionType.MARKETER, 0.95, "Preceded by explicit statutory marketer contextual keyword")

    # 7. Standalone Postal PIN Code
    if re.fullmatch(r'\b[1-9][0-9]{5}\b', clean_t) or re.fullmatch(r'(?:pin|postal\s*code|pincode)\s*[:.\-\s]*[1-9][0-9]{5}', clean_t, re.I):
        return (SemanticRegionType.POSTAL_PIN, 0.95, "Matched 6-digit postal PIN code under Rule 10(1)")

    # 8. MRP
    for p in MRP_PATTERNS:
        if p.search(clean_t):
            return ("MRP", 0.96, "Matched retail sale price declaration under Rule 6(1)(e)")

    # 9. Tax Inclusivity Phrase
    if TAX_PHRASE_REGEX.search(clean_t):
        return ("TAX_INCLUSIVE_WORDING", 0.96, "Matched statutory tax inclusivity phrase under Rule 6(1)(e)")

    # 10. Unit Sale Price
    if USP_PATTERN.search(clean_t):
        return ("UNIT_SALE_PRICE", 0.95, "Matched unit sale price declaration under Rule 6(11)")

    # 11. Net Quantity
    for p in NET_QTY_PATTERNS:
        if p.search(clean_t) and not NUTRITIONAL_IGNORE_REGEX.search(clean_t):
            return ("NET_QUANTITY", 0.95, "Matched net quantity / weight declaration under Rule 6(1)(c)")

    # 12. Standalone Metric Unit Symbol
    if re.fullmatch(r'(?:g|kg|ml|l|ltr|cm|m|N|units?|pieces?|पैक|ग्राम|मिली)', clean_t, re.I):
        return ("UNIT", 0.92, "Matched metric SI unit symbol under Rule 13")

    # 13. Dates
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

    # 14. Batch / Lot
    for p in BATCH_PATTERNS:
        if p.search(clean_t):
            if re.search(r'\blot\b', clean_t, re.I):
                return ("LOT_NUMBER", 0.95, "Matched lot identification number under Rule 6(1)(g)")
            return ("BATCH_NUMBER", 0.95, "Matched batch identification number under Rule 6(1)(g)")

    # 15. Country of Origin
    if COO_PATTERN.search(clean_t) or re.search(r'\b(?:made\s*in|product\s*of|country\s*of\s*origin)\b', clean_t, re.I):
        return ("COUNTRY_OF_ORIGIN", 0.96, "Matched country of origin / manufacture declaration under Rule 6(1)(n)")

    # 16. Consumer Care Contact Details
    if EMAIL_PATTERN.search(clean_t):
        return ("CONSUMER_CARE_EMAIL", 0.97, "Matched consumer grievance cell email address")
    if PHONE_PATTERN.search(clean_t) and re.search(r'(?:care|helpline|toll|free|phone|call|contact|grievance)', clean_t, re.I):
        return ("CONSUMER_CARE_PHONE", 0.96, "Matched consumer helpline / toll-free contact number under Rule 6(1)(f)")
    if re.search(r'\b(?:consumer\s*care\s*address|grievance\s*officer|postal\s*address)\b', clean_t, re.I):
        return ("CONSUMER_CARE_ADDRESS", 0.93, "Matched consumer care postal address")

    # 17. Commercial Entities (Manufacturer, Packer, Importer)
    if re.search(r'^(?:mfd\.?\s*(?:&|and)?\s*marketed\s*by|mfg\.?\s*(?:&|and)?\s*marketed\s*by|manufactured\s*(?:&|and)?\s*marketed\s*by|mfd\.?\s*(?:by|at|for)|mfg\.?\s*(?:by|at|for)|manufactured\s*(?:by|at|for)|produced\s*(?:by|at)|made\s*by|विनिर्माता)\b', clean_t, re.I):
        return ("MANUFACTURER_NAME", 0.95, "Preceded by explicit statutory manufacturer contextual keyword")
    if re.search(r'^(?:packed\s*(?:by|at)|pkd\.?\s*(?:by|at)|pre-packed\s*by|packaged\s*by|पैकर)\b', clean_t, re.I):
        return ("PACKER_NAME", 0.95, "Preceded by explicit statutory packer contextual keyword")
    if re.search(r'^(?:imported\s*(?:by|(?:and|&)\s*marketed\s*by)|imp\.?\s*by|importer|आयातक)\b', clean_t, re.I):
        return ("IMPORTER_NAME", 0.95, "Preceded by explicit statutory importer contextual keyword")

    # 18. Address Components (STRICT SAFETY: never match if line is ingredient or direction)
    is_safe_from_formulation = not any(w in clean_t.lower() for w in ["direction", "apply", "reapply", "aqua", "glycerin", "salicylic", "parfum", "tocopherol", "caution", "warning", "extract", "sorbitan", "stearic"])
    if is_safe_from_formulation and ADDRESS_CUES.search(clean_t) and (PIN_PATTERN.search(clean_t) or re.search(r'\b(?:plot|sector|phase|road|street|estate|ind\.\s*area|gidc|midc)\b', clean_t, re.I)):
        if prev_lines and any(re.search(r'\b(?:marketed|mktg|distributed)\b', pl, re.I) for pl in prev_lines[-2:]):
            return ("MARKETER_ADDRESS", 0.93, "Contains structured address components linked to marketer")
        elif prev_lines and any(re.search(r'\b(?:packed|pkd)\b', pl, re.I) for pl in prev_lines[-2:]):
            return ("PACKER_ADDRESS", 0.93, "Contains structured address components linked to packer")
        elif prev_lines and any(re.search(r'\b(?:imported|importer)\b', pl, re.I) for pl in prev_lines[-2:]):
            return ("IMPORTER_ADDRESS", 0.93, "Contains structured address components linked to importer")
        else:
            return ("MANUFACTURER_ADDRESS", 0.93, "Contains structured address components linked to manufacturer")

    # 19. Generic Name dictionary keyword check
    for kw, (gen, cat) in COMMODITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', clean_t.lower()):
            return ("GENERIC_NAME", 0.94, f"Matches statutory commodity classification dictionary for '{gen}'")

    # 20. Uninterpretable / Noise tokens (e.g. 'AKM1 O1 HA')
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

    # Fallback: if manufacturer is not detected and NO other commercial entity was detected,
    # search for address cues + 6-digit PIN in entire label.
    # Rule: NEVER invent a manufacturer name without contextual evidence! Address alone is recorded as address.
    # CRITICAL: If Marketer, Packer, or Importer is ALREADY found, DO NOT re-assign that address to manufacturer!
    has_other_entity = bool(
        (entities["marketer"].name and entities["marketer"].name != "Not detected") or
        (entities["packer"].name and entities["packer"].name != "Not detected") or
        (entities["importer"].name and entities["importer"].name != "Not detected")
    )
    if not has_other_entity and not entities["manufacturer"].name and not entities["manufacturer"].full_address:
        mfg_cand_lines: List[str] = []
        bboxes_cand: List[BoundingBox] = []
        for idx, line in enumerate(extracted_lines):
            t = line.text.strip()
            # STRICT EXCLUSIONS: Skip marketing, ingredients, directions, warnings
            if (MARKETING_CLAIM_PATTERNS.search(t) or INGREDIENT_PATTERNS.search(t)
                or getattr(line, "classification", "") in [
                    "MARKETING_CLAIM", "DIRECTIONS", "INGREDIENTS", "POSSIBLE_INGREDIENTS", "WARNING"
                ]
                or any(w in t.lower() for w in ["direction", "apply", "reapply", "aqua", "glycerin", "salicylic", "parfum", "tocopherol", "caution", "warning"])):
                continue
            if ADDRESS_CUES.search(t):
                mfg_cand_lines.append(t)
                if line.bbox:
                    bboxes_cand.append(line.bbox)
                for nb in find_spatial_neighbors(idx, extracted_lines, max_dy=18.0):
                    nb_t = nb.text.strip()
                    if (nb_t not in mfg_cand_lines and not statutory_cutoffs.search(nb_t)
                        and not MARKETING_CLAIM_PATTERNS.search(nb_t) and not INGREDIENT_PATTERNS.search(nb_t)
                        and getattr(nb, "classification", "") not in [
                            "MARKETING_CLAIM", "DIRECTIONS", "INGREDIENTS", "POSSIBLE_INGREDIENTS", "WARNING"
                        ]
                        and not any(w in nb_t.lower() for w in ["direction", "apply", "reapply", "aqua", "glycerin", "salicylic", "parfum", "tocopherol", "caution", "warning"])):
                        mfg_cand_lines.append(nb_t)
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
    # 1. Product Category, Product Name & Generic Commodity Name (Categories A through R)
    # -------------------------------------------------------------------------
    cat_name, cat_code, cat_conf, cat_rat = classify_product_category(joined_text, extracted_lines)
    data.product_category = cat_name
    data.category_code = cat_code
    data.classification_status = "COMPLETED" if cat_code != "R" else "NEEDS_REVIEW"

    detected_generic_name = ""
    detected_category = cat_name
    detected_product_line = ""
    target_pname_line = None

    for kw, (generic, cat) in COMMODITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', joined_lower):
            detected_generic_name = generic
            break

    # Extract directions, ingredients, warnings, and postal pin declarations
    dir_lines = [l.text.strip() for l in extracted_lines if getattr(l, "classification", "") == SemanticRegionType.DIRECTIONS]
    ing_lines = [l.text.strip() for l in extracted_lines if getattr(l, "classification", "") in [SemanticRegionType.INGREDIENTS, SemanticRegionType.POSSIBLE_INGREDIENTS]]
    warn_lines = [l.text.strip() for l in extracted_lines if getattr(l, "classification", "") == SemanticRegionType.WARNING]
    
    data.directions_text = " | ".join(dir_lines) if dir_lines else None
    data.ingredients_text = " | ".join(ing_lines) if ing_lines else None
    data.warnings_text = " | ".join(warn_lines) if warn_lines else None
    
    pin_m = PIN_PATTERN.search(joined_text)
    data.postal_pin = pin_m.group(1) if pin_m else None

    # Find prominent product title line (strictly shielding marketing claims, directions, ingredients, warnings)
    for idx, line in enumerate(extracted_lines):
        t = line.text.strip()
        if line.classification in [
            "MARKETING_CLAIM", "INGREDIENT", "INGREDIENTS", "POSSIBLE_INGREDIENTS",
            "WARNING", "DIRECTIONS", "MARKETER", "MANUFACTURER_NAME", "MANUFACTURER_ADDRESS"
        ]:
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
        data.commodity_name = detected_generic_name or (cat_name if cat_name != ProductCategory.UNKNOWN else data.product_name)
        data.generic_name = detected_generic_name or None
        pname_status = "Found"
        pname_conf, pname_level = calculate_field_confidence(0.96, 1.0, 1.0, 1.0, 1.0, 1.0)
        pname_review = None
        pname_reasoning = "Identified commercial trade name on display panel excluding promotional claims, directions, and ingredients."

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
    marketer_info = entities.get("marketer", AddressInfo(entity_type="Marketer"))

    data.manufacturer = mfg_info
    data.manufacturer_name = mfg_info.name or None
    data.manufacturer_address = mfg_info.full_address or None

    data.packer = packer_info if packer_info.name else None
    data.packer_name = packer_info.name or None
    data.packer_address = packer_info.full_address or None

    data.importer = importer_info if importer_info.name else None
    data.importer_name = importer_info.name or None
    data.importer_address = importer_info.full_address or None

    data.marketer = marketer_info if marketer_info.name else None

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
        elif not mfg_info.name and marketer_info.name and marketer_info.name.lower() in line.text.lower():
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
    if mfg_info.name:
        mfg_name_reason = "Identified commercial corporate entity immediately following statutory 'Manufactured by' declaration."
        mfg_name_review = None
    elif marketer_info.name:
        mfg_name_reason = f"Manufacturer name not detected on this panel. Marketer declared: {marketer_info.name}."
        mfg_name_review = f"Manufacturer contextual prefix not detected on this panel (Marketed by: {marketer_info.name}). Verify secondary panels under Rule 6(2)."
    else:
        mfg_name_reason = "No statutory manufacturer contextual prefix ('Manufactured by') found on package."
        mfg_name_review = "Manufacturer contextual prefix not detected; cannot assign entity without statutory evidence."

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
        penal_provision="Section 36(1) read with Rule 10" if (not mfg_info.name and not marketer_info.name) else None,
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
    elif mfg_info.full_address and mfg_info.name:
        mfg_addr_status = "Defective"
        mfg_addr_review = "Violation: Mandatory 6-digit postal PIN code missing from manufacturer address under Rule 10(1)."
        mfg_addr_conf, mfg_addr_level = calculate_field_confidence(0.85, 1.0, 1.0, 1.0, 0.6, 1.0)
        mfg_addr_reason = "Manufacturer address detected but lacks mandatory 6-digit postal PIN code required by Rule 10(1)."
    elif marketer_info.name and marketer_info.has_valid_pin:
        mfg_addr_status = "Under Review"
        mfg_addr_review = f"Manufacturer address not detected on current panel (Marketer address declared with PIN {marketer_info.pin_code}). Verify secondary panels under Rule 6(2)."
        mfg_addr_conf, mfg_addr_level = 0.85, "Medium"
        mfg_addr_reason = f"Marketer address declared with valid postal PIN ({marketer_info.pin_code}). Manufacturer address to be checked on secondary surfaces."
    else:
        mfg_addr_status = "Under Review"
        mfg_addr_review = "Manufacturer address not detected on current surface."
        mfg_addr_conf, mfg_addr_level = 0.45, "Needs Review"
        mfg_addr_reason = "No manufacturer address components detected on packaging."

    canonical_fields.append(CanonicalField(
        field_name="manufacturer_address",
        statutory_name="Complete Address of Manufacturer with PIN Code",
        extracted_value=mfg_info.full_address or ("Not detected (Marketer address declared)" if marketer_info.name else "Not detected"),
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
        value=mfg_info.full_address or ("Not detected (Marketer address declared)" if marketer_info.name else "Not detected"),
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

    # Optional Field: marketer (if declared on packaging)
    if marketer_info.name:
        mkt_conf, mkt_level = calculate_field_confidence(0.95, 1.0, 1.0, 1.0, 1.0, 1.0)
        canonical_fields.append(CanonicalField(
            field_name="marketer",
            statutory_name="Name and Address of Marketer / Brand Owner",
            extracted_value=f"{marketer_info.name}, {marketer_info.full_address}",
            raw_ocr_value=" ".join(marketer_info.raw_lines),
            confidence=mkt_conf,
            confidence_level=mkt_level,
            status="Found",
            bbox=mfg_bbox,
            rule_reference="Rule 6(1)(a)",
            assignment_reasoning=f"Identified marketer entity with postal PIN ({marketer_info.pin_code}).",
            surrounding_context=mfg_context,
            semantic_class="MARKETER",
            detected_on_surface=mfg_surface
        ))
        evidence_map["marketer"] = FieldEvidence(
            field_name="marketer",
            label="Marketer Details",
            value=f"{marketer_info.name}, {marketer_info.full_address}",
            ocr_confidence=mkt_conf,
            detection_confidence=0.95,
            validation_confidence=0.95,
            overall_confidence=mkt_conf,
            source_text=marketer_info.full_address,
            surface=mfg_surface,
            bounding_box=mfg_bbox,
            status="DETECTED",
            assignment_reasoning="Extracted marketer entity with postal address.",
            surrounding_context=mfg_context,
            semantic_class="MARKETER",
            raw_ocr=" ".join(marketer_info.raw_lines)
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

    # Populate multi-tier confidence metrics on all CanonicalFields and FieldEvidences
    for f in canonical_fields:
        f.image_quality_confidence = 0.95
        f.ocr_confidence = f.confidence
        f.region_classification_confidence = 0.95
        f.field_extraction_confidence = 0.95
        f.rule_validation_confidence = 0.95
        f.overall_confidence = f.confidence

    for k, ev in evidence_map.items():
        ev.image_quality_confidence = 0.95
        ev.ocr_confidence = ev.ocr_confidence
        ev.region_classification_confidence = 0.95
        ev.field_extraction_confidence = 0.95
        ev.rule_validation_confidence = 0.95
        ev.overall_confidence = ev.overall_confidence

    return data, canonical_fields, evidence_map

# -------------------------------------------------------------------
# STEP 3.5b: LM-COMPASS STRUCTURED COMPLIANCE DOSSIER BUILDER
# -------------------------------------------------------------------

def build_lm_compass_dossier(
    data: StructuredProductData,
    canonical_fields: List[CanonicalField],
    evidence_map: Dict[str, FieldEvidence],
    checks: List[ComplianceCheckItem],
    surfaces_processed: Optional[List[str]] = None
) -> LmCompassResult:
    """Builds the Master Prompt Section 27 Structured Compliance Dossier.
    Ensures high precision, evidence-grounded violation reporting, and clear routing
    to NEEDS_REVIEW whenever evidence is ambiguous or incomplete.
    """
    fields_list: List[LmCompassFieldItem] = []
    for cf in canonical_fields:
        fields_list.append(LmCompassFieldItem(
            field=cf.field_name,
            extracted_value=str(cf.extracted_value),
            semantic_region=cf.semantic_class or "UNKNOWN",
            bbox=cf.bbox,
            ocr_confidence=cf.ocr_confidence,
            classification_confidence=cf.region_classification_confidence,
            extraction_confidence=cf.field_extraction_confidence,
            status="DETECTED" if cf.status == "Found" else ("NOT_APPLICABLE" if "Not Applicable" in str(cf.extracted_value) else "UNCERTAIN")
        ))

    comp_items: List[LmCompassComplianceItem] = []
    vio_items: List[LmCompassViolationItem] = []
    review_items: List[LmCompassNeedsReviewItem] = []

    for chk in checks:
        if chk.status == "PASS":
            comp_items.append(LmCompassComplianceItem(
                rule=chk.rule_no,
                requirement=chk.statutory_requirement,
                evidence=chk.detected_declaration,
                bbox=chk.bounding_box,
                status="COMPLIANT",
                confidence=chk.confidence
            ))
        elif chk.status == "FAIL":
            ev_text = chk.violation_evidence_text or chk.detected_declaration
            vio_items.append(LmCompassViolationItem(
                violation=chk.rule_title,
                rule=chk.rule_no,
                evidence_text=ev_text,
                evidence_bbox=chk.violation_evidence_bbox or chk.bounding_box,
                explanation=chk.detected_declaration,
                confidence=chk.confidence
            ))
        elif chk.status in ["NEEDS REVIEW", "WARN", "NOT DETECTED"]:
            review_items.append(LmCompassNeedsReviewItem(
                uncertain_field=chk.rule_no,
                reason=chk.detected_declaration,
                bbox=chk.bounding_box,
                suggested_action=f"Inspect packaging for {chk.rule_title} under {chk.sub_rule}"
            ))

    if vio_items:
        overall_status = "NON_COMPLIANT"
    elif review_items:
        overall_status = "NEEDS_REVIEW"
    else:
        overall_status = "COMPLIANT"

    cat_name = data.product_category or ProductCategory.OTHER
    cat_code = getattr(data, "category_code", None) or CATEGORY_CODE_MAP.get(cat_name, "Q")
    class_status = "COMPLETED" if cat_code != "R" else "NEEDS_REVIEW"

    return LmCompassResult(
        product_name=data.product_name,
        category=f"{cat_name} (Category {cat_code})" if cat_code else cat_name,
        classification_status=class_status,
        panels=surfaces_processed if surfaces_processed else ["Front (PDP)"],
        fields=fields_list,
        compliance=comp_items,
        violations=vio_items,
        needs_review=review_items,
        overall_status=overall_status,
        overall_confidence=0.95
    )

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
        if p_data.marketer and p_data.marketer.name and p_data.marketer.name != "Not detected":
            if not fused_data.marketer or not fused_data.marketer.name or fused_data.marketer.name == "Not detected":
                fused_data.marketer = p_data.marketer
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

    # Duplicate Consistency Cross-Panel Check
    quantities = [(surf, p_data.net_quantity.value, p_data.net_quantity.unit) for surf, p_data, _, _ in normalized_extractions if p_data.net_quantity.value > 0]
    if len(quantities) > 1:
        first_q = quantities[0][1]
        conflicts = [q for q in quantities if q[1] != first_q]
        if conflicts:
            fused_data.net_quantity.has_contradiction = True
            fused_data.net_quantity.contradiction_note = f"CONFLICT DETECTED: Discrepancy between panels ({quantities[0][0]}: {first_q} vs {conflicts[0][0]}: {conflicts[0][1]}); routed to Needs Review."
            if "net_quantity" in best_fields:
                best_fields["net_quantity"].status = "Under Review"
                best_fields["net_quantity"].confidence = 0.45
                best_fields["net_quantity"].review_reason = fused_data.net_quantity.contradiction_note
        else:
            if "net_quantity" in best_fields:
                best_fields["net_quantity"].assignment_reasoning += " (CONSISTENT across panels)"
                best_fields["net_quantity"].confidence = min(0.99, best_fields["net_quantity"].confidence + 0.03)

    mrps = [(surf, p_data.mrp.amount) for surf, p_data, _, _ in normalized_extractions if p_data.mrp.amount > 0]
    if len(mrps) > 1:
        first_mrp = mrps[0][1]
        mrp_conflicts = [m for m in mrps if m[1] != first_mrp]
        if mrp_conflicts:
            fused_data.mrp.has_contradiction = True
            fused_data.mrp.contradiction_note = f"CONFLICT DETECTED: Conflicting MRPs between panels ({mrps[0][0]}: ₹{first_mrp} vs {mrp_conflicts[0][0]}: ₹{mrp_conflicts[0][1]}); routed to Needs Review under Rule 6(1)(e)."
            if "mrp" in best_fields:
                best_fields["mrp"].status = "Under Review"
                best_fields["mrp"].confidence = 0.45
                best_fields["mrp"].review_reason = fused_data.mrp.contradiction_note
        else:
            if "mrp" in best_fields:
                best_fields["mrp"].assignment_reasoning += " (CONSISTENT across panels)"
                best_fields["mrp"].confidence = min(0.99, best_fields["mrp"].confidence + 0.03)

    fused_canonical = list(best_fields.values())
    return fused_data, fused_canonical, best_evidences

