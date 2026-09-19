from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime

# ----------------------------------------------------
# LM-COMPASS: CATEGORY, REGION & UNIVERSAL DECISION CONSTANTS
# ----------------------------------------------------

class ProductCategory:
    """Categories A through R as defined in Universal Legal Metrology Vision Engine Master Specification."""
    FOOD = "Category A — Food & Food Products"                                  # A
    BEVERAGES = "Category B — Beverages & Bottled Liquids"                      # B
    COSMETICS = "Category C — Cosmetics & Personal Care"                        # C
    CLEANING = "Category D — Cleaning, Detergents & Household Care"             # D
    PHARMA = "Category E — Pharmaceuticals, Medical Devices & Healthcare"       # E
    ELECTRONICS = "Category F — Electronics, Electrical Appliances & IT Goods"  # F
    STATIONERY = "Category G — Stationery, Paper, Office & School Supplies"     # G
    TOYS = "Category H — Toys, Baby Gear & Infant Products"                     # H
    TEXTILES = "Category I — Textiles, Apparel, Footwear & Accessories"         # I
    HARDWARE = "Category J — Hardware, Construction, Paint & Tools"             # J
    AUTOMOTIVE = "Category K — Automotive Parts, Lubricants & Accessories"      # K
    AGRICULTURAL = "Category L — Agricultural, Seeds, Fertilizers & Pesticides" # L
    PET = "Category M — Pet Food & Animal Care Products"                        # M
    TOBACCO = "Category N — Tobacco, Pan Masala & Related Commodities"          # N
    INDUSTRIAL = "Category O — Industrial Raw Materials & Bulk Packaged Goods"  # O
    IMPORTED = "Category P — Imported Commodities (Special Provisions)"         # P
    ECOMMERCE = "Category Q — E-Commerce / Outer Delivery Packages"             # Q
    UNKNOWN = "Category R — Unknown / Uncertain / Ambiguous Commodity"          # R

    # Backward compatibility aliases
    FOOD_BEVERAGE = FOOD
    COSMETICS_PERSONAL_CARE = COSMETICS
    HOUSEHOLD_CLEANING = CLEANING
    TOILETRIES = CLEANING
    HEALTH_WELLNESS = PHARMA
    PACKAGED_HOUSEHOLD_GOODS = CLEANING
    GARMENTS_TEXTILES = TEXTILES
    FOOTWEAR = TEXTILES
    HARDWARE_TOOLS = HARDWARE
    PACKAGED_INDUSTRIAL = INDUSTRIAL
    PET_FOOD = PET
    OTHER = ECOMMERCE

class SemanticRegionType:
    """38 statutory semantic region classifications."""
    PRODUCT_NAME = "PRODUCT_NAME"
    BRAND_NAME = "BRAND_NAME"
    VARIANT = "VARIANT"
    DESCRIPTION = "DESCRIPTION"
    NET_QUANTITY = "NET_QUANTITY"
    MRP = "MRP"
    UNIT_PRICE = "UNIT_PRICE"
    MANUFACTURER = "MANUFACTURER"
    PACKER = "PACKER"
    IMPORTER = "IMPORTER"
    MARKETER = "MARKETER"
    ADDRESS = "ADDRESS"
    POSTAL_PIN = "POSTAL_PIN"
    COUNTRY_OF_ORIGIN = "COUNTRY_OF_ORIGIN"
    CONSUMER_CARE = "CONSUMER_CARE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    WEBSITE = "WEBSITE"
    BATCH_NUMBER = "BATCH_NUMBER"
    LOT_NUMBER = "LOT_NUMBER"
    DATE_OF_MANUFACTURE = "DATE_OF_MANUFACTURE"
    DATE_OF_PACKING = "DATE_OF_PACKING"
    MONTH_YEAR = "MONTH_YEAR"
    EXPIRY = "EXPIRY"
    BEST_BEFORE = "BEST_BEFORE"
    USE_BY = "USE_BY"
    INGREDIENTS = "INGREDIENTS"
    POSSIBLE_INGREDIENTS = "POSSIBLE_INGREDIENTS"
    DIRECTIONS = "DIRECTIONS"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    PRECAUTION = "PRECAUTION"
    USAGE = "USAGE"
    NUTRITION_INFORMATION = "NUTRITION_INFORMATION"
    ALLERGEN_INFORMATION = "ALLERGEN_INFORMATION"
    STORAGE_INFORMATION = "STORAGE_INFORMATION"
    LICENSE_INFORMATION = "LICENSE_INFORMATION"
    BARCODE = "BARCODE"
    QR_CODE = "QR_CODE"
    OTHER_DECLARATIONS = "OTHER_DECLARATIONS"

class UniversalFieldStatus:
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNCERTAIN = "UNCERTAIN"
    CONFLICT = "CONFLICT"

class UniversalComplianceStatus:
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# ----------------------------------------------------
# STAGE 2: COMPUTER VISION BRANCH MODELS
# ----------------------------------------------------

class BoundingBox(BaseModel):
    x: float = 0.0  # percentage 0-100 or pixel coordinate
    y: float = 0.0  # percentage 0-100 or pixel coordinate
    width: float = 0.0
    height: float = 0.0
    label: Optional[str] = None
    pixel_coords: Optional[List[int]] = None  # [x1, y1, x2, y2]

class LabelMeShape(BaseModel):
    label: str
    points: List[List[float]]  # [[x1, y1], [x2, y2]]
    group_id: Optional[int] = None
    description: Optional[str] = None
    shape_type: str = "rectangle"
    flags: Dict[str, Any] = Field(default_factory=dict)
    detection_confidence: float = 0.95
    ocr_confidence: float = 0.95

class LabelMeAnnotation(BaseModel):
    version: str = "5.2.1"
    flags: Dict[str, Any] = Field(default_factory=dict)
    shapes: List[LabelMeShape] = Field(default_factory=list)
    imagePath: str = ""
    imageData: Optional[str] = None
    imageHeight: int = 1000
    imageWidth: int = 1000

class ImageQualityMetrics(BaseModel):
    """14 statutory & optical image quality assessment metrics."""
    resolution_megapixels: float = 0.0
    width: int = 0
    height: int = 0
    resolution: Optional[str] = None
    blur_laplacian_variance: float = 0.0
    is_blurred: bool = False
    focus_score: float = 85.0
    noise_variance: float = 0.0
    is_noisy: bool = False
    mean_brightness: float = 0.0
    brightness: Optional[float] = None
    contrast_std_dev: float = 0.0
    contrast: Optional[float] = None
    glare_percentage: float = 0.0
    is_glare_detected: bool = False
    shadow_detected: bool = False
    rotation_angle_deg: float = 0.0
    perspective_distortion_detected: bool = False
    skew_angle_deg: float = 0.0
    skew_angle: Optional[float] = None
    estimated_text_size_px: float = 14.0
    estimated_glyph_height_px: Optional[float] = None
    margin_clipping_risk: Optional[str] = "Low"
    background_interference_score: float = 0.0
    text_visibility: str = "Optimal"
    image_completeness: str = "Complete (100% visible)"
    overall_quality_score: int = 85
    advisory: Optional[str] = None

class PreprocessingVariantInfo(BaseModel):
    variant_id: str
    name: str
    description: str
    base64_image: Optional[str] = None
    width: int = 0
    height: int = 0
    processing_time_ms: float = 0.0

class DetectedRegion(BaseModel):
    region_id: str
    category: str  # MRP, Net quantity, Mfg date, Expiry, Manufacturer, Packer, Importer, etc.
    bbox: BoundingBox
    detection_confidence: float = 0.95
    ocr_confidence: float = 0.95
    cropped_image_base64: Optional[str] = None
    ocr_candidates: Dict[str, str] = Field(default_factory=dict)  # engine -> extracted text
    selected_text: str = ""
    method_used: str = ""
    status: str = "VERIFIED"  # 'VERIFIED', 'NEEDS REVIEW', 'UNCERTAIN'

class MeasurementValidation(BaseModel):
    reference_detected: bool = False
    reference_type: Optional[str] = None
    pixel_to_mm_ratio: Optional[float] = None
    estimated_font_height_mm: Optional[float] = None
    table1_required_height_mm: float = 2.0
    table1_complies: bool = True
    status_message: str = "Measurement unavailable — requires calibrated reference"

# ----------------------------------------------------
# STAGE 3: OCR + NLP + RULES ENGINE MODELS
# ----------------------------------------------------

class ExtractedLine(BaseModel):
    line_index: int
    text: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    is_uncertain: bool = False
    surface: str = "Front (PDP)"
    matched_rule: Optional[str] = None
    classification: Optional[str] = None
    raw_text: Optional[str] = None
    preprocessing_version: Optional[str] = None
    engine: Optional[str] = None

class CanonicalField(BaseModel):
    field_name: str
    statutory_name: str
    extracted_value: str
    confidence: float
    status: str  # 'Found', 'Defective', 'Missing', 'Under Review', 'Not Applicable'
    bbox: Optional[BoundingBox] = None
    rule_reference: str
    penal_provision: Optional[str] = None
    is_uncertain: bool = False
    detected_on_surface: str = "Front (PDP)"
    raw_ocr_value: Optional[str] = None
    evidence_crop_base64: Optional[str] = None
    confidence_level: Optional[str] = None  # 'High', 'Medium', 'Low', 'Needs Review'
    review_reason: Optional[str] = None
    assignment_reasoning: Optional[str] = None
    surrounding_context: Optional[str] = None
    semantic_class: Optional[str] = None
    image_quality_confidence: float = 0.95
    ocr_confidence: float = 0.95
    region_classification_confidence: float = 0.95
    field_extraction_confidence: float = 0.95
    rule_validation_confidence: float = 0.95
    overall_confidence: float = 0.95

class AddressInfo(BaseModel):
    name: str = ""
    full_address: str = ""
    pin_code: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    has_valid_pin: bool = False
    entity_type: str = "Manufacturer"  # Manufacturer, Packer, Importer, Marketer
    raw_lines: List[str] = Field(default_factory=list)

CommercialEntity = AddressInfo

class NetQuantityInfo(BaseModel):
    raw_text: str = ""
    value: float = 0.0
    unit: str = ""
    unit_type: str = "weight"  # weight, volume, length, count
    font_height_mm: float = 3.0
    complies_standard_units: bool = True
    prohibited_unit_detected: Optional[str] = None
    has_contradiction: bool = False
    contradiction_note: Optional[str] = None

class MrpInfo(BaseModel):
    raw_text: str = ""
    currency: str = "INR"
    amount: float = 0.0
    tax_inclusive_statement_present: bool = True
    complies_tax_phrase: bool = True
    is_uncertain: bool = False
    has_contradiction: bool = False
    contradiction_note: Optional[str] = None

class UnitSalePriceInfo(BaseModel):
    raw_text: Optional[str] = None
    value_per_unit: Optional[str] = None
    is_exempt: bool = False
    exemption_reason: Optional[str] = None

class DateInfo(BaseModel):
    raw_text: str = ""
    month: Optional[str] = None
    year: Optional[str] = None
    complies_format: bool = True
    is_uncertain: bool = False

class ConsumerCareInfo(BaseModel):
    person_or_office: str = "Consumer Care Cell"
    phone: Optional[str] = None
    email: Optional[str] = None
    postal_address: Optional[str] = None
    website: Optional[str] = None

class Table1HeightCheck(BaseModel):
    detected_height_mm: float = 3.0
    required_height_mm: float = 2.0
    complies: bool = True
    is_calibrated: bool = True
    calibration_basis: Optional[str] = "Optical Scale Calibration"

class ProductClassification(BaseModel):
    product_type: str = "Other packaged commodity"
    category_code: str = "Q"
    is_imported: bool = False
    is_multipack: bool = False
    is_liquid: bool = False
    is_perishable: bool = False
    is_scheduled_commodity: bool = False
    pdp_area_cm2: float = 120.0
    confidence: float = 0.95
    status: str = "COMPLETED"
    reasoning: str = ""

class FieldEvidence(BaseModel):
    field_name: str
    label: str
    value: str
    ocr_confidence: float = 0.95
    detection_confidence: float = 0.95
    validation_confidence: float = 0.95
    overall_confidence: float = 0.95
    image_quality_confidence: float = 0.95
    region_classification_confidence: float = 0.95
    field_extraction_confidence: float = 0.95
    rule_validation_confidence: float = 0.95
    source_text: str = ""
    image_id: Optional[str] = None
    surface: str = "Front (PDP)"
    bounding_box: Optional[BoundingBox] = None
    cropped_image_base64: Optional[str] = None
    processing_method: str = "Multi-Engine OCR Ensemble"
    ocr_candidates: Dict[str, str] = Field(default_factory=dict)
    disagreement_detected: bool = False
    status: str = "DETECTED"  # 'DETECTED', 'NOT DETECTED', 'UNREADABLE', 'NEEDS REVIEW', 'NOT APPLICABLE'
    rule_reference: Optional[str] = None
    review_reason: Optional[str] = None
    notes: Optional[str] = None
    assignment_reasoning: Optional[str] = None
    surrounding_context: Optional[str] = None
    semantic_class: Optional[str] = None
    raw_ocr: Optional[str] = None

class StructuredProductData(BaseModel):
    product_name: str = ""
    commodity_name: str = ""
    product_category: str = "Other Packaged Commodity"
    category_code: str = "Q"
    classification_status: str = "COMPLETED"
    brand: Optional[str] = None
    generic_name: Optional[str] = None
    variant: Optional[str] = None
    manufacturer: AddressInfo = Field(default_factory=AddressInfo)
    manufacturer_name: Optional[str] = None
    manufacturer_address: Optional[str] = None
    packer: Optional[AddressInfo] = None
    packer_name: Optional[str] = None
    packer_address: Optional[str] = None
    importer: Optional[AddressInfo] = None
    importer_name: Optional[str] = None
    importer_address: Optional[str] = None
    marketer: Optional[AddressInfo] = None
    marketer_name: Optional[str] = None
    marketer_address: Optional[str] = None
    postal_pin: Optional[str] = None
    ingredients_text: Optional[str] = None
    directions_text: Optional[str] = None
    warnings_text: Optional[str] = None
    nutrition_text: Optional[str] = None
    brand_owner: Optional[str] = None
    net_quantity: NetQuantityInfo = Field(default_factory=NetQuantityInfo)
    mrp: MrpInfo = Field(default_factory=MrpInfo)
    tax_inclusive_wording: Optional[str] = None
    unit_sale_price: Optional[UnitSalePriceInfo] = None
    mfd: DateInfo = Field(default_factory=DateInfo)
    expiry: Optional[DateInfo] = None
    dates: Optional[Dict[str, str]] = None
    batch: str = ""
    batch_number: Optional[str] = None
    consumer_care: ConsumerCareInfo = Field(default_factory=ConsumerCareInfo)
    consumer_care_phone: Optional[str] = None
    consumer_care_email: Optional[str] = None
    consumer_care_address: Optional[str] = None
    country_of_origin: str = "India"
    table1_numeral_height: Table1HeightCheck = Field(default_factory=Table1HeightCheck)
    other_declarations: List[str] = Field(default_factory=list)
    other_text: Optional[str] = None
    classification: Optional[ProductClassification] = None
    evidence: Optional[Dict[str, FieldEvidence]] = None

class ComplianceCheckItem(BaseModel):
    rule_no: str
    rule_title: str
    sub_rule: str
    status: str  # 'PASS', 'FAIL', 'WARN', 'NEEDS REVIEW', 'NOT APPLICABLE', 'NOT DETECTED'
    detected_declaration: str
    statutory_requirement: str
    font_size_or_unit_check: str
    section_penalty: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    surface: str = "Front (PDP)"
    is_applicable: bool = True
    applicability_reason: Optional[str] = None
    evidence_crop_base64: Optional[str] = None
    source_pdf: Optional[str] = None
    source_pdf_page: Optional[int] = None
    amendment_citation: Optional[str] = None
    effective_date: Optional[str] = None
    original_text: Optional[str] = None
    confidence: float = 0.95
    violation_evidence_text: Optional[str] = None
    violation_evidence_bbox: Optional[BoundingBox] = None

# ----------------------------------------------------
# LM-COMPASS SECTION 27: STRUCTURED COMPLIANCE DOSSIER MODELS
# ----------------------------------------------------

class LmCompassFieldItem(BaseModel):
    field: str
    extracted_value: str
    semantic_region: str
    bbox: Optional[BoundingBox] = None
    ocr_confidence: float = 0.95
    classification_confidence: float = 0.95
    extraction_confidence: float = 0.95
    status: str = "DETECTED"  # DETECTED, NOT_DETECTED, NOT_APPLICABLE, UNCERTAIN, CONFLICT

class LmCompassComplianceItem(BaseModel):
    rule: str
    requirement: str
    evidence: str
    bbox: Optional[BoundingBox] = None
    status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW, NOT_APPLICABLE
    confidence: float = 0.95

class LmCompassViolationItem(BaseModel):
    violation: str
    rule: str
    evidence_text: str
    evidence_bbox: Optional[BoundingBox] = None
    explanation: str
    confidence: float = 0.95

class LmCompassNeedsReviewItem(BaseModel):
    uncertain_field: str
    reason: str
    bbox: Optional[BoundingBox] = None
    suggested_action: str

class LmCompassResult(BaseModel):
    product_name: str
    category: str
    classification_status: str = "COMPLETED"  # COMPLETED, NEEDS_REVIEW
    panels: List[str] = Field(default_factory=list)
    fields: List[LmCompassFieldItem] = Field(default_factory=list)
    compliance: List[LmCompassComplianceItem] = Field(default_factory=list)
    violations: List[LmCompassViolationItem] = Field(default_factory=list)
    needs_review: List[LmCompassNeedsReviewItem] = Field(default_factory=list)
    overall_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW
    overall_confidence: float = 0.95


# ----------------------------------------------------
# STAGE 4: PIPELINE REQUEST / RESPONSE & BENCHMARK MODELS
# ----------------------------------------------------

class ScanProcessRequest(BaseModel):
    images: List[Dict[str, Any]]  # [{"data": base64_str, "surface": "Front (PDP)", "file_name": "front.jpg"}]
    options: Optional[Dict[str, Any]] = None

class ScanProcessResponse(BaseModel):
    scan_id: str
    product_info: StructuredProductData
    canonical_fields: List[CanonicalField]
    compliance_checks: List[ComplianceCheckItem]
    compliance_score: int
    overall_status: str  # 'COMPLIANT', 'NON_COMPLIANT', 'NEEDS_REVIEW'
    extracted_lines: List[ExtractedLine]
    surfaces_processed: List[str]
    image_quality: Optional[ImageQualityMetrics] = None
    preprocessing_variants: List[PreprocessingVariantInfo] = Field(default_factory=list)
    detected_regions: List[DetectedRegion] = Field(default_factory=list)
    measurement_validation: Optional[MeasurementValidation] = None
    labelme_annotation: Optional[LabelMeAnnotation] = None
    external_verification: str = "External verification: Not available"
    lm_compass_result: Optional[LmCompassResult] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class BenchmarkEvaluationMetric(BaseModel):
    metric_name: str
    category: str
    measured_accuracy: float
    target_threshold: float
    status: str
    sample_count: int
    notes: str

class BenchmarkEvaluationResponse(BaseModel):
    benchmark_id: str
    timestamp: str
    total_test_samples: int
    test_categories: List[str]
    metrics: List[BenchmarkEvaluationMetric]
    overall_system_reliability: float
    false_positive_rate: float
    false_negative_rate: float
    disagreement_resolution_rate: float

class SystemDiagnosticStatus(BaseModel):
    status: str = "ONLINE"
    version: str = "2.4.0"
    yolo_model_loaded: bool = False
    yolo_backend: str = "CPU / PyTorch"
    tesseract_available: bool = False
    easyocr_available: bool = False
    paddleocr_available: bool = False
    opencv_version: str = ""
    database_backend: str = "SQLite / PostgreSQL"
    database_connected: bool = True
    redis_cache_backend: str = "In-Memory / Redis"
    redis_connected: bool = False
    elasticsearch_backend: str = "In-Memory / Elasticsearch"
    elasticsearch_connected: bool = False
    external_government_api: str = "External verification: Not available"
