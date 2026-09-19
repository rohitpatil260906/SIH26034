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



