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

class UniversalSemanticField:
    """Universal semantic field classifications across packaged commodities."""
    PRODUCT_NAME = "PRODUCT_NAME"
    BRAND = "BRAND"
    VARIANT = "VARIANT"
    NET_QUANTITY = "NET_QUANTITY"
    QUANTITY_COUNT = "QUANTITY_COUNT"
    SERVING_SIZE = "SERVING_SIZE"
    INGREDIENT_QUANTITY = "INGREDIENT_QUANTITY"
    PRODUCT_DIMENSION = "PRODUCT_DIMENSION"
    WEIGHT_SPECIFICATION = "WEIGHT_SPECIFICATION"
    OTHER_QUANTITY = "OTHER_QUANTITY"
    MRP = "MRP"
    UNIT_PRICE = "UNIT_PRICE"
    PRICE_CANDIDATE = "PRICE_CANDIDATE"
    MANUFACTURER = "MANUFACTURER"
    PACKER = "PACKER"
    MARKETER = "MARKETER"
    IMPORTER = "IMPORTER"
    DISTRIBUTOR = "DISTRIBUTOR"
    BRAND_OWNER = "BRAND_OWNER"
    ADDRESS = "ADDRESS"
    CITY = "CITY"
    STATE = "STATE"
    POSTAL_PIN = "POSTAL_PIN"
    COUNTRY_OF_ORIGIN = "COUNTRY_OF_ORIGIN"
    BATCH_NUMBER = "BATCH_NUMBER"
    LOT_NUMBER = "LOT_NUMBER"
    MODEL_NUMBER = "MODEL_NUMBER"
    PRODUCT_CODE = "PRODUCT_CODE"
    SERIAL_NUMBER = "SERIAL_NUMBER"
    DATE_OF_MANUFACTURE = "DATE_OF_MANUFACTURE"
    DATE_OF_PACKING = "DATE_OF_PACKING"
    EXPIRY = "EXPIRY"
    BEST_BEFORE = "BEST_BEFORE"
    USE_BY = "USE_BY"
    OTHER_DATE = "OTHER_DATE"
    INGREDIENTS = "INGREDIENTS"
    NUTRITION_VALUE = "NUTRITION_VALUE"
    DIRECTIONS = "DIRECTIONS"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    PRECAUTION = "PRECAUTION"
    STORAGE = "STORAGE"
    CONSUMER_CARE = "CONSUMER_CARE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    WEBSITE = "WEBSITE"
    DIMENSION = "DIMENSION"
    BARCODE = "BARCODE"
    QR_CODE = "QR_CODE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

class SectionType:
    """Packaging semantic section categories."""
    PDP_HEADER = "PDP_HEADER"
    PRODUCT_DETAILS = "PRODUCT_DETAILS"
    INGREDIENTS = "INGREDIENTS"
    NUTRITION_INFORMATION = "NUTRITION_INFORMATION"
    DIRECTIONS = "DIRECTIONS"
    WARNING = "WARNING"
    MANUFACTURER = "MANUFACTURER"
    PACKER = "PACKER"
    IMPORTER = "IMPORTER"
    MARKETER = "MARKETER"
    CONSUMER_CARE = "CONSUMER_CARE"
    STORAGE = "STORAGE"
    CODING_AREA = "CODING_AREA"
    OTHER = "OTHER"

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

class UniversalFieldObject(BaseModel):
    """Structured universal semantic representation of any detected token or declaration."""
    raw_text: str
    normalized_value: Optional[Any] = None
    unit: Optional[str] = None
    candidate_fields: List[str] = Field(default_factory=list)
    selected_field: str = UniversalSemanticField.UNKNOWN
    semantic_confidence: float = 0.95
    ocr_confidence: float = 0.95
    layout_confidence: float = 0.95
    category_confidence: float = 0.95
    rule_confidence: float = 0.95
    overall_confidence: float = 0.95
    evidence_bbox: Optional[BoundingBox] = None
    evidence_context: str = ""
    source_panel: str = "Front (PDP)"
    reason: str = ""
    status: str = "RESOLVED"  # "RESOLVED", "NEEDS_REVIEW", "CONFLICT", "UNKNOWN"
    heading_association: Optional[str] = None
    section: Optional[str] = None
    spatial_relation: Optional[str] = None

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
    universal_fields: List[UniversalFieldObject] = Field(default_factory=list)


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
    universal_fields: List[UniversalFieldObject] = Field(default_factory=list)


# ----------------------------------------------------
# STAGE 4: PIPELINE REQUEST / RESPONSE & BENCHMARK MODELS
# ----------------------------------------------------

class JurisdictionInfo(BaseModel):
    country: str = "India"
    state: str = ""
    city: str = ""
    pinCode: str = ""

class ScanProcessRequest(BaseModel):
    images: List[Dict[str, Any]]  # [{"data": base64_str, "surface": "Front (PDP)", "file_name": "front.jpg"}]
    options: Optional[Dict[str, Any]] = None
    jurisdiction: Optional[JurisdictionInfo] = None

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
    jurisdiction: Optional[JurisdictionInfo] = None
    lm_compass_result: Optional[LmCompassResult] = None
    universal_fields: List[UniversalFieldObject] = Field(default_factory=list)
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

# ----------------------------------------------------
# STAGE 1: IMAGE INGESTION, QUALITY & LOCALIZATION MODELS
# ----------------------------------------------------

class Stage1InputMetadata(BaseModel):
    image_id: str
    source: str = "upload"  # upload, camera, drag-and-drop
    original_filename: str = "image.jpg"
    file_type: str = "JPEG"
    file_size_bytes: int = 0
    width: int = 0
    height: int = 0
    aspect_ratio: float = 1.0
    orientation: str = "NORMAL"  # NORMAL, ROTATED_90, ROTATED_180, ROTATED_270
    capture_timestamp: Optional[str] = None
    processing_status: str = "SUCCESS"  # SUCCESS, REJECTED, FAILED

class Stage1QualityResult(BaseModel):
    status: str = "GOOD"  # GOOD, DEGRADED, INSUFFICIENT
    overall_score: float = 85.0
    blur_score: float = 85.0
    resolution_score: float = 90.0
    contrast_score: float = 80.0
    glare_score: float = 95.0
    perspective_score: float = 90.0
    curvature_score: float = 95.0
    occlusion_score: float = 95.0
    issues: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None

class ProductInstanceBox(BaseModel):
    instance_id: str
    bbox: List[float] = Field(default_factory=list)  # [x, y, w, h] %
    polygon: List[List[float]] = Field(default_factory=list)
    confidence: float = 0.95

class Stage1PackageDetection(BaseModel):
    detected: bool = True
    bbox: List[float] = Field(default_factory=list)  # [x, y, w, h] in %
    polygon: List[List[float]] = Field(default_factory=list)
    confidence: float = 0.95
    products_count: int = 1
    product_instances: List[ProductInstanceBox] = Field(default_factory=list)
    background_removed: bool = False

class Stage1PanelInfo(BaseModel):
    type: str = "UNKNOWN_PANEL"  # FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, SIDE, UNKNOWN_PANEL
    confidence: float = 0.90
    coverage: str = "FULL"  # FULL, PARTIAL
    is_front: bool = False

class Stage1GeometryResult(BaseModel):
    perspective_detected: bool = False
    curvature_detected: bool = False
    rectification_available: bool = False
    transformation_matrix: Optional[List[List[float]]] = None
    corner_points: Optional[List[List[float]]] = None

class Stage1Response(BaseModel):
    scan_id: str
    input: Stage1InputMetadata
    quality: Stage1QualityResult
    package_detection: Stage1PackageDetection
    panel: Stage1PanelInfo
    geometry: Stage1GeometryResult
    preprocessing: Dict[str, Any] = Field(default_factory=dict)
    status: str = "READY_FOR_TEXT_DETECTION"  # READY_FOR_TEXT_DETECTION, INSUFFICIENT_QUALITY, NEEDS_REVIEW
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ----------------------------------------------------
# STAGE 2: UNIVERSAL TEXT DETECTION & OCR MODELS
# ----------------------------------------------------

class Stage2WordBox(BaseModel):
    text: str
    bbox: List[float] = Field(default_factory=list)
    confidence: float = 0.95

class Stage2TextRegion(BaseModel):
    region_id: str
    raw_text: str
    normalized_text: str
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    detection_confidence: float = 0.95
    ocr_confidence: float = 0.95
    language: str = "en"
    orientation: int = 0
    source_variant: str = "original"
    status: str = "DETECTED"  # DETECTED, OCR_UNCERTAIN
    words: List[Stage2WordBox] = Field(default_factory=list)
    competing_candidates: List[str] = Field(default_factory=list)
    reading_order_index: int = 0

class Stage2TableCell(BaseModel):
    row_index: int
    col_index: int
    row_span: int = 1
    col_span: int = 1
    text: str
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)

class Stage2TableInfo(BaseModel):
    table_id: str
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    rows_count: int = 0
    cols_count: int = 0
    cells: List[Stage2TableCell] = Field(default_factory=list)

class Stage2BarcodeRegion(BaseModel):
    barcode_id: str
    format: str = "1D_BARCODE"
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    decoded_data: Optional[str] = None
    confidence: float = 0.95

class Stage2QRRegion(BaseModel):
    qr_id: str
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    decoded_payload: Optional[str] = None
    confidence: float = 0.95

class Stage2Response(BaseModel):
    scan_id: str
    text_detection_status: str = "COMPLETED"  # COMPLETED, INSUFFICIENT_QUALITY, NEEDS_REVIEW
    regions: List[Stage2TextRegion] = Field(default_factory=list)
    uncertain_regions: List[Stage2TextRegion] = Field(default_factory=list)
    barcode_regions: List[Stage2BarcodeRegion] = Field(default_factory=list)
    qr_regions: List[Stage2QRRegion] = Field(default_factory=list)
    tables: List[Stage2TableInfo] = Field(default_factory=list)
    total_text_regions: int = 0
    estimated_coverage_pct: float = 0.0
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==============================================================================
# STAGE 3: UNIVERSAL TEXT MEANING & SEMANTIC UNDERSTANDING MODELS
# ==============================================================================

class Stage3CandidateType(BaseModel):
    type: str
    confidence: float

class Stage3SemanticField(BaseModel):
    field_id: str
    semantic_type: str  # e.g., NET_QUANTITY, SERVING_SIZE, MRP, MANUFACTURER_NAME, EXPIRY_DATE, UNKNOWN
    value: str
    normalized_value: Optional[str] = None
    heading_text: Optional[str] = None
    source_region_ids: List[str] = Field(default_factory=list)
    heading_region_ids: List[str] = Field(default_factory=list)
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    ocr_confidence: float = 0.90
    semantic_confidence: float = 0.90
    relationship_confidence: float = 0.90
    status: str = "CONFIRMED"  # CONFIRMED, NEEDS_REVIEW, SEMANTIC_UNCERTAIN
    candidate_types: List[Stage3CandidateType] = Field(default_factory=list)

class Stage3Section(BaseModel):
    section_id: str
    section_type: str  # INGREDIENTS, NUTRITION, MANUFACTURER_INFORMATION, DIRECTIONS, WARNINGS, etc.
    heading_text: Optional[str] = None
    region_ids: List[str] = Field(default_factory=list)
    bbox: List[float] = Field(default_factory=list)
    confidence: float = 0.90

class Stage3Relationship(BaseModel):
    relationship_id: str
    field_type: str
    heading_text: str
    value_text: str
    heading_region_id: Optional[str] = None
    value_region_id: Optional[str] = None
    relationship_confidence: float = 0.90
    association_type: str = "PROXIMITY"  # SAME_LINE, COLON_SEPARATOR, TABLE_ROW, PROXIMITY

class Stage3CategoryCandidate(BaseModel):
    category: str  # FOOD, BEVERAGE, COSMETIC, PERSONAL_CARE, ELECTRONICS, etc.
    confidence: float
    evidence_signals: List[str] = Field(default_factory=list)

class Stage3Statistics(BaseModel):
    total_ocr_regions: int = 0
    semantic_regions: int = 0
    unknown_regions: int = 0
    needs_review_regions: int = 0

class Stage3Response(BaseModel):
    scan_id: str
    semantic_status: str = "COMPLETED"  # COMPLETED, INSUFFICIENT_QUALITY, NEEDS_REVIEW
    sections: List[Stage3Section] = Field(default_factory=list)
    semantic_fields: List[Stage3SemanticField] = Field(default_factory=list)
    relationships: List[Stage3Relationship] = Field(default_factory=list)
    category_candidates: List[Stage3CategoryCandidate] = Field(default_factory=list)
    ambiguous_fields: List[Stage3SemanticField] = Field(default_factory=list)
    uncertain_regions: List[Stage2TextRegion] = Field(default_factory=list)
    statistics: Stage3Statistics = Field(default_factory=Stage3Statistics)
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==============================================================================
# STAGE 4: UNIVERSAL PRODUCT + COMPANY + ENTITY IDENTIFICATION MODELS
# ==============================================================================

class Stage4ValueWithStatus(BaseModel):
    value: str = "NOT_VISIBLE"
    status: str = "NOT_VISIBLE"  # CONFIRMED, PARTIAL, UNCERTAIN, NOT_VISIBLE, NEEDS_REVIEW
    confidence: float = 0.0
    source_region_ids: List[str] = Field(default_factory=list)

class Stage4CategoryInfo(BaseModel):
    value: str = "UNKNOWN"  # FOOD, BEVERAGE, COSMETIC, PERSONAL_CARE, ELECTRONICS, etc.
    confidence: float = 0.0
    evidence_signals: List[str] = Field(default_factory=list)

class Stage4Entity(BaseModel):
    role: str  # BRAND, MANUFACTURER, PACKER, MARKETER, IMPORTER, DISTRIBUTOR, SELLER, OWNER, LICENSE_HOLDER, OTHER_ORGANIZATION
    name: str
    address: Optional[str] = None
    pin: Optional[str] = None
    confidence: float = 0.90
    entity_confidence: float = 0.90
    role_confidence: float = 0.90
    partial_entity: bool = False
    source_panel: str = "UNKNOWN"  # FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, SIDE, UNKNOWN
    source_region_ids: List[str] = Field(default_factory=list)
    bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)

class Stage4EvidenceNode(BaseModel):
    node_id: str
    node_type: str  # ROLE, ENTITY_NAME, ADDRESS, PIN, BRAND, PRODUCT, MODEL, BATCH
    label: str
    region_id: Optional[str] = None

class Stage4EvidenceEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relation: str  # HAS_NAME, LOCATED_AT, HAS_PIN, OWNS_BRAND, HAS_MODEL

class Stage4EvidenceGraph(BaseModel):
    nodes: List[Stage4EvidenceNode] = Field(default_factory=list)
    edges: List[Stage4EvidenceEdge] = Field(default_factory=list)

class Stage4ProductIdentity(BaseModel):
    product_id: str = "product_001"
    product_name: Stage4ValueWithStatus = Field(default_factory=Stage4ValueWithStatus)
    brand: Stage4ValueWithStatus = Field(default_factory=Stage4ValueWithStatus)
    category: Stage4CategoryInfo = Field(default_factory=Stage4CategoryInfo)
    variant: Stage4ValueWithStatus = Field(default_factory=Stage4ValueWithStatus)
    entities: List[Stage4Entity] = Field(default_factory=list)
    model_number: Optional[str] = None
    sku: Optional[str] = None
    article_number: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    serial_number: Optional[str] = None
    country_of_origin: Optional[str] = None
    barcode_value: Optional[str] = None
    barcode_type: Optional[str] = None
    qr_value: Optional[str] = None
    decode_confidence: float = 0.0
    evidence_graph: Optional[Stage4EvidenceGraph] = None
    source_panel: str = "UNKNOWN"
    bbox: List[float] = Field(default_factory=list)

class Stage4Response(BaseModel):
    scan_id: str
    identity_status: str = "CONFIRMED"  # CONFIRMED, PARTIAL, UNCERTAIN, NEEDS_REVIEW
    identity: Stage4ProductIdentity = Field(default_factory=Stage4ProductIdentity)
    products: List[Stage4ProductIdentity] = Field(default_factory=list)
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==============================================================================
# STAGE 5: ADVANCED CURVED / DISTORTED LABEL RECOVERY & DIFFICULT IMAGE PROCESSING
# ==============================================================================

class Stage5TransformationStep(BaseModel):
    operation: str  # perspective_homography, cylindrical_unwrap, rotate, crop, upscale, unsharp_mask, etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)
    matrix: Optional[List[List[float]]] = None
    inv_matrix: Optional[List[List[float]]] = None
    input_shape: Optional[List[int]] = None
    output_shape: Optional[List[int]] = None

class Stage5VariantQuality(BaseModel):
    visibility: float = 0.0
    sharpness: float = 0.0
    contrast: float = 0.0
    text_readability: float = 0.0
    geometry_quality: float = 0.0
    ocr_support: float = 0.0

class Stage5VariantInfo(BaseModel):
    variant_id: str
    type: str  # ORIGINAL, PERSPECTIVE_CORRECTED, CURVATURE_CORRECTED, CYLINDRICAL_UNWRAPPED, GLARE_REDUCED, SHADOW_CORRECTED, ROTATED, CONTRAST_ENHANCED, CLAHE, SHARPENED, DENOISED, ADAPTIVE_THRESHOLD, UPSCALED, CHANNEL_OPTIMIZED
    source_variant: str = "original"
    quality_scores: Stage5VariantQuality = Field(default_factory=Stage5VariantQuality)
    transformation_chain: List[str] = Field(default_factory=list)
    coordinate_mapping_available: bool = True
    preview_base64: Optional[str] = None

class Stage5DifficultRegion(BaseModel):
    region_id: str
    bbox: List[float] = Field(default_factory=list)  # [x, y, w, h] in variant space
    original_bbox: List[float] = Field(default_factory=list)  # [x, y, w, h] in original image space
    polygon: Optional[List[List[float]]] = None  # Detailed polygon coordinates
    original_polygon: Optional[List[List[float]]] = None
    distortion_type: str = "UNKNOWN"
    recovery_technique_applied: Optional[str] = None
    status: str = "RECOVERED"  # RECOVERED, PARTIALLY_OCCLUDED, TEXT_OCCLUDED_BY_GLARE, OCR_UNCERTAIN
    confidence: float = 0.90

class Stage5OcrConsensusItem(BaseModel):
    consensus_id: str
    raw_text: str
    normalized_text: str
    consensus_confidence: float = 0.95
    agreement_count: int = 1
    total_variants_evaluated: int = 1
    competing_candidates: List[str] = Field(default_factory=list)
    processed_bbox: List[float] = Field(default_factory=list)
    original_bbox: List[float] = Field(default_factory=list)
    original_polygon: Optional[List[List[float]]] = None
    source_variants: List[str] = Field(default_factory=list)
    transformation_chain: List[str] = Field(default_factory=list)
    status: str = "CONFIRMED"  # CONFIRMED, OCR_UNCERTAIN, TEXT_OCCLUDED_BY_GLARE, PARTIALLY_OCCLUDED

class Stage5Response(BaseModel):
    scan_id: str
    recovery_status: str = "COMPLETED"  # COMPLETED, MINIMAL_PROCESSING, DEGRADED_FALLBACK
    distortions_detected: List[str] = Field(default_factory=list)
    variants: List[Stage5VariantInfo] = Field(default_factory=list)
    difficult_regions: List[Stage5DifficultRegion] = Field(default_factory=list)
    ocr_consensus: List[Stage5OcrConsensusItem] = Field(default_factory=list)
    uncertain_regions: List[Stage5OcrConsensusItem] = Field(default_factory=list)
    fallback_used: bool = False
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ----------------------------------------------------
# STAGE 6: UNIVERSAL PRODUCT-SPECIFIC ADAPTIVE SCHEMA MODELS
# ----------------------------------------------------

class Stage6CategoryCandidate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    confidence: float = 0.50
    evidence: List[str] = Field(default_factory=list)

class Stage6ProductProfile(BaseModel):
    category: str = "UNKNOWN"
    subcategory: Optional[str] = None
    category_confidence: float = 0.0
    category_status: str = "NEEDS_REVIEW"  # CONFIRMED, NEEDS_REVIEW, UNCERTAIN
    category_evidence: List[str] = Field(default_factory=list)
    category_candidates: List[Stage6CategoryCandidate] = Field(default_factory=list)

class Stage6AdaptiveField(BaseModel):
    field_name: str
    value: Optional[str] = None
    status: str = "NOT_VISIBLE"  # PRESENT, NOT_VISIBLE, NOT_APPLICABLE, UNKNOWN, NEEDS_REVIEW
    relevance: float = 0.0
    confidence: float = 0.0
    source_region_ids: List[str] = Field(default_factory=list)
    panel: Optional[str] = None
    evidence: Optional[str] = None
    unit: Optional[str] = None

class Stage6AdaptiveSchema(BaseModel):
    fields: List[Stage6AdaptiveField] = Field(default_factory=list)
    universal_core_fields: List[Stage6AdaptiveField] = Field(default_factory=list)
    category_specific_fields: List[Stage6AdaptiveField] = Field(default_factory=list)

class Stage6SingleProductProfile(BaseModel):
    product_id: str
    product_profile: Stage6ProductProfile
    adaptive_schema: Stage6AdaptiveSchema
    uncertain_fields: List[Stage6AdaptiveField] = Field(default_factory=list)
    not_visible_fields: List[Stage6AdaptiveField] = Field(default_factory=list)
    not_applicable_fields: List[Stage6AdaptiveField] = Field(default_factory=list)

class Stage6Response(BaseModel):
    scan_id: str
    status: str = "COMPLETED"  # COMPLETED, NEEDS_REVIEW, DEGRADED_FALLBACK
    products: List[Stage6SingleProductProfile] = Field(default_factory=list)
    imported_product_detected: bool = False
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==============================================================================
# STAGE 7: CROSS-PANEL INFORMATION MERGING & MULTI-IMAGE CONSOLIDATION MODELS
# ==============================================================================

class Stage7SourceImage(BaseModel):
    image_id: str
    panel: str = "UNKNOWN"  # FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, SIDE, PARTIAL, UNKNOWN
    scan_id: Optional[str] = None
    bbox: List[float] = Field(default_factory=list)

class Stage7FieldSource(BaseModel):
    image_id: str
    panel: str = "UNKNOWN"
    region_id: Optional[str] = None
    bbox: List[float] = Field(default_factory=list)
    confidence: float = 0.90
    raw_text: Optional[str] = None

class Stage7ConflictCandidate(BaseModel):
    value: str
    image_id: str
    panel: str = "UNKNOWN"
    confidence: float = 0.90
    raw_text: Optional[str] = None

class Stage7FieldConflict(BaseModel):
    field_name: str
    status: str = "CONFLICT"
    candidates: List[Stage7ConflictCandidate] = Field(default_factory=list)

class Stage7UnifiedField(BaseModel):
    field_name: str
    value: Optional[str] = None
    status: str = "CONFIRMED"  # CONFIRMED, CONFLICT, NEEDS_REVIEW, NOT_VISIBLE, NOT_APPLICABLE
    confidence: float = 0.0
    sources: List[Stage7FieldSource] = Field(default_factory=list)
    unit: Optional[str] = None
    evidence: Optional[str] = None
    candidates: List[Stage7ConflictCandidate] = Field(default_factory=list)

class Stage7CrossPanelLink(BaseModel):
    link_id: str
    entity_type: str  # MANUFACTURER_ADDRESS, PACKER_ADDRESS, IMPORTER_ADDRESS, BRAND_PRODUCT, etc.
    source_image_id: str
    target_image_id: str
    source_panel: str = "UNKNOWN"
    target_panel: str = "UNKNOWN"
    confidence: float = 0.90
    linked_value: str

class Stage7ProductMatchEvidence(BaseModel):
    image_a: str
    image_b: str
    same_product_confidence: float = 0.0
    status: str = "MATCHED"  # MATCHED, POSSIBLE_MATCH, NOT_MATCHED, NEEDS_REVIEW
    evidence: List[str] = Field(default_factory=list)

class Stage7PanelCompleteness(BaseModel):
    available_panels: List[str] = Field(default_factory=list)
    missing_panels: List[str] = Field(default_factory=list)

class Stage7EvidenceGraphNode(BaseModel):
    node_id: str
    node_type: str  # PRODUCT, PANEL, FIELD, ENTITY, REGION
    label: str
    image_id: Optional[str] = None
    panel: Optional[str] = None

class Stage7EvidenceGraphEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relation: str  # HAS_PANEL, HAS_FIELD, LINKED_TO, OWNS

class Stage7CrossPanelEvidenceGraph(BaseModel):
    nodes: List[Stage7EvidenceGraphNode] = Field(default_factory=list)
    edges: List[Stage7EvidenceGraphEdge] = Field(default_factory=list)

class Stage7UnifiedProduct(BaseModel):
    product_id: str = "product_001"
    source_images: List[Stage7SourceImage] = Field(default_factory=list)
    identity: Stage4ProductIdentity = Field(default_factory=Stage4ProductIdentity)
    category_profile: Stage6ProductProfile = Field(default_factory=Stage6ProductProfile)
    fields: List[Stage7UnifiedField] = Field(default_factory=list)
    conflicts: List[Stage7FieldConflict] = Field(default_factory=list)
    cross_panel_links: List[Stage7CrossPanelLink] = Field(default_factory=list)
    evidence_graph: Stage7CrossPanelEvidenceGraph = Field(default_factory=Stage7CrossPanelEvidenceGraph)
    panel_completeness: Stage7PanelCompleteness = Field(default_factory=Stage7PanelCompleteness)
    merge_confidence: float = 0.90
    status: str = "MERGED"  # MERGED, PARTIAL, NEEDS_REVIEW, UNMATCHED

class Stage7Session(BaseModel):
    session_id: str = "session_001"
    image_ids: List[str] = Field(default_factory=list)
    panel_ids: List[str] = Field(default_factory=list)
    product_ids: List[str] = Field(default_factory=list)
    product_matches: List[Stage7ProductMatchEvidence] = Field(default_factory=list)
    products: List[Stage7UnifiedProduct] = Field(default_factory=list)

class Stage7Response(BaseModel):
    session_id: str
    status: str = "COMPLETED"  # COMPLETED, NEEDS_REVIEW, PARTIAL
    products: List[Stage7UnifiedProduct] = Field(default_factory=list)
    session: Optional[Stage7Session] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==============================================================================
# STAGE 8: VERIFIED LEGAL METROLOGY RULE ENGINE MODELS
# ==============================================================================

class Stage8RuleDefinition(BaseModel):
    rule_id: str
    act_name: str = "The Legal Metrology Act, 2009"
    rules_name: str = "Legal Metrology (Packaged Commodities) Rules, 2011"
    rule_number: str
    sub_rule: Optional[str] = None
    clause: Optional[str] = None
    title: str
    requirement_text: str
    requirement_type: str = "DECLARATION"  # DECLARATION, PACK_SIZE, UNIT_SALE_PRICE, FSSAI, IMPORTER, CONSUMER_CARE
    applicable_product_categories: List[str] = Field(default_factory=lambda: ["ALL"])
    applicable_packaging_types: List[str] = Field(default_factory=lambda: ["ALL"])
    applicable_market_context: str = "RETAIL"  # RETAIL, WHOLESALE, INSTITUTIONAL, ECOMMERCE, ALL
    applicability_conditions: List[str] = Field(default_factory=list)
    exceptions: List[str] = Field(default_factory=list)
    exemptions: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    validation_conditions: List[str] = Field(default_factory=list)
    effective_from: Optional[str] = "2011-03-07"
    effective_until: Optional[str] = None
    jurisdiction: str = "INDIA"
    source_name: str = "Gazette of India"
    source_url: Optional[str] = None
    source_document: Optional[str] = None
    source_version: str = "2024.1"
    verification_status: str = "VERIFIED"  # VERIFIED, UNVERIFIED, SUPERSEDED, NEEDS_REVIEW
    notes: Optional[str] = None

class Stage8ApplicabilityResult(BaseModel):
    rule_id: str
    applicability_status: str = "APPLICABLE"  # APPLICABLE, NOT_APPLICABLE, UNKNOWN, NEEDS_REVIEW
    reason: str = "Applicable to product category"
    conditions_evaluated: List[str] = Field(default_factory=list)

class Stage8EvidenceItem(BaseModel):
    image_id: Optional[str] = None
    panel: Optional[str] = None
    region_id: Optional[str] = None
    bbox: List[float] = Field(default_factory=list)
    observed_text: Optional[str] = None
    normalized_value: Optional[str] = None
    semantic_field: Optional[str] = None
    confidence: float = 0.90

class Stage8RuleTrace(BaseModel):
    rule_id: str
    applicable: bool = True
    observed_field: Optional[str] = None
    observed_value: Optional[str] = None
    evidence: Optional[Stage8EvidenceItem] = None
    evaluation: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE, NOT_VISIBLE, UNKNOWN, NEEDS_REVIEW, CONFLICT
    confidence: float = 0.90
    rule_source: Optional[str] = None
    rule_version: Optional[str] = None
    trace_steps: List[str] = Field(default_factory=list)

class Stage8RuleEvaluation(BaseModel):
    rule_id: str
    rule_number: str
    requirement_title: str
    applicability_status: str = "APPLICABLE"  # APPLICABLE, NOT_APPLICABLE, UNKNOWN, NEEDS_REVIEW
    evaluation_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE, NOT_VISIBLE, UNKNOWN, NEEDS_REVIEW, CONFLICT
    confidence: float = 0.90
    evidence: List[Stage8EvidenceItem] = Field(default_factory=list)
    rule_source: Optional[str] = None
    rule_version: Optional[str] = None
    trace: Optional[Stage8RuleTrace] = None

class Stage8ProductEvaluation(BaseModel):
    product_id: str = "product_001"
    overall_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW, PARTIAL
    evaluations: List[Stage8RuleEvaluation] = Field(default_factory=list)
    needs_review_items: List[Stage8RuleEvaluation] = Field(default_factory=list)
    conflicts: List[Stage7FieldConflict] = Field(default_factory=list)
    rule_traces: List[Stage8RuleTrace] = Field(default_factory=list)

class Stage8Request(BaseModel):
    session_id: str = "session_001"
    product_id: Optional[str] = None
    unified_product: Optional[Stage7UnifiedProduct] = None
    rule_context: Dict[str, Any] = Field(default_factory=dict)

class Stage8Response(BaseModel):
    session_id: str
    rule_engine_version: str = "2024.1"
    status: str = "COMPLETED"  # COMPLETED, NEEDS_REVIEW, PARTIAL
    product_evaluations: List[Stage8ProductEvaluation] = Field(default_factory=list)
    overall_status: str = "COMPLIANT"
    needs_review_items: List[Stage8RuleEvaluation] = Field(default_factory=list)
    conflicts: List[Stage7FieldConflict] = Field(default_factory=list)
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================
# STAGE 9 DATA MODELS: VIOLATION & EVIDENCE ENGINE
# =======================================================

class Stage9EvidenceItem(BaseModel):
    image_id: Optional[str] = None
    product_id: Optional[str] = None
    panel: Optional[str] = None
    region_id: Optional[str] = None
    original_bbox: List[float] = Field(default_factory=list)
    observed_text: Optional[str] = None
    normalized_value: Optional[str] = None
    semantic_field: Optional[str] = None
    ocr_confidence: float = 0.90
    semantic_confidence: float = 0.90
    rule_evaluation_id: Optional[str] = None
    evidence_confidence: float = 0.90

class Stage9Violation(BaseModel):
    violation_id: str
    product_id: str
    scan_id: Optional[str] = None
    rule_id: str
    rule_number: str
    clause: Optional[str] = None
    requirement: str
    violation_type: str  # MISSING_REQUIRED_DECLARATION, INCORRECT_DECLARATION, INCONSISTENT_DECLARATION, INVALID_VALUE, FORMAT_NON_COMPLIANCE, QUANTITY_NON_COMPLIANCE, PRICE_DECLARATION_ISSUE, DATE_DECLARATION_ISSUE, ENTITY_INFORMATION_ISSUE, CONSUMER_INFORMATION_ISSUE, OTHER_VERIFIED_NON_COMPLIANCE
    violation_status: str = "CONFIRMED"  # CONFIRMED, NEEDS_REVIEW, RESOLVED, DISMISSED
    severity: str = "UNCLASSIFIED"  # LOW, MEDIUM, HIGH, CRITICAL, UNCLASSIFIED
    description: str
    observed_value: Optional[str] = None
    expected_condition: str
    evidence: List[Stage9EvidenceItem] = Field(default_factory=list)
    confidence: float = 0.90
    rule_source: Optional[str] = None
    rule_version: Optional[str] = None
    fingerprint: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    review_status: str = "NOT_REQUIRED"  # NOT_REQUIRED, PENDING_REVIEW, REVIEWED

class Stage9ReviewItem(BaseModel):
    review_id: str
    product_id: str
    reason: str  # INSUFFICIENT_EVIDENCE, CONFLICTING_DECLARATIONS, NOT_VISIBLE, UNKNOWN_STATUS, UNVERIFIED_RULE, AMBIGUOUS_SEMANTICS
    related_rule_id: Optional[str] = None
    related_rule_number: Optional[str] = None
    description: str
    evidence: List[Stage9EvidenceItem] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Stage9ViolationSummary(BaseModel):
    total_evaluations: int = 0
    confirmed_violations: int = 0
    needs_review_items: int = 0
    compliant_rules: int = 0
    not_applicable_rules: int = 0

class Stage9ProductViolationResult(BaseModel):
    product_id: str
    overall_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW
    violations: List[Stage9Violation] = Field(default_factory=list)
    review_items: List[Stage9ReviewItem] = Field(default_factory=list)
    summary: Stage9ViolationSummary = Field(default_factory=Stage9ViolationSummary)

class Stage9Request(BaseModel):
    session_id: str = "session_001"
    stage8_response: Optional[Stage8Response] = None
    product_evaluations: Optional[List[Stage8ProductEvaluation]] = None

class Stage9Response(BaseModel):
    session_id: str
    violation_engine_version: str = "2024.1"
    status: str = "COMPLETED"  # COMPLETED, NEEDS_REVIEW
    product_results: List[Stage9ProductViolationResult] = Field(default_factory=list)
    overall_status: str = "COMPLIANT"
    summary: Stage9ViolationSummary = Field(default_factory=Stage9ViolationSummary)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================
# STAGE 10 DATA MODELS: FINAL INTEGRATION & PIPELINE
# =======================================================

class Stage10StageProgress(BaseModel):
    stage_name: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, NEEDS_REVIEW, SKIPPED
    processing_time_ms: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Stage10ProcessingMetadata(BaseModel):
    pipeline_version: str = "2024.1"
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    processing_time_ms: float = 0.0
    stages_executed: List[Stage10StageProgress] = Field(default_factory=list)

class Stage10AuditEvent(BaseModel):
    event_id: str
    scan_id: str
    product_id: Optional[str] = None
    stage: str
    event_type: str
    status: str
    relevant_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Stage10FinalResult(BaseModel):
    scan_id: str
    session_id: str
    product_id: str
    product_identity: Optional[Stage4ProductIdentity] = None
    images: List[Dict[str, Any]] = Field(default_factory=list)
    panels: List[Dict[str, Any]] = Field(default_factory=list)
    extracted_information: List[Stage7UnifiedField] = Field(default_factory=list)
    rule_evaluations: List[Stage8RuleEvaluation] = Field(default_factory=list)
    violations: List[Stage9Violation] = Field(default_factory=list)
    review_items: List[Stage9ReviewItem] = Field(default_factory=list)
    conflicts: List[Stage7FieldConflict] = Field(default_factory=list)
    evidence: List[Stage9EvidenceItem] = Field(default_factory=list)
    overall_status: str = "COMPLIANT"  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW, PARTIAL, FAILED
    summary: Dict[str, int] = Field(default_factory=dict)
    processing: Stage10ProcessingMetadata

class Stage10ScanStatusResponse(BaseModel):
    scan_id: str
    session_id: str
    pipeline_state: str
    overall_status: str
    progress: List[Stage10StageProgress] = Field(default_factory=list)
    audit_events: List[Stage10AuditEvent] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class Stage10RunRequest(BaseModel):
    session_id: Optional[str] = None
    images: List[Dict[str, Any]] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)

class Stage10RunResponse(BaseModel):
    scan_id: str
    session_id: str
    pipeline_state: str
    overall_status: str
    final_results: List[Stage10FinalResult] = Field(default_factory=list)
    audit_trail: List[Stage10AuditEvent] = Field(default_factory=list)
    processing: Stage10ProcessingMetadata






