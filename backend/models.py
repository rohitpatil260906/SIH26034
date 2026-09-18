from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class BoundingBox(BaseModel):
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

class ImageQualityMetrics(BaseModel):
    resolution_megapixels: float
    blur_laplacian_variance: float
    is_blurred: bool
    mean_brightness: float
    contrast_std_dev: float
    text_visibility: str
    overall_quality_score: int
    advisory: Optional[str] = None

class ExtractedLine(BaseModel):
    line_index: int
    text: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    is_uncertain: bool = False
    surface: str = "Front (PDP)"

class CanonicalField(BaseModel):
    field_name: str
    statutory_name: str
    extracted_value: str
    confidence: float
    status: str  # 'Found', 'Defective', 'Missing', 'Under Review'
    bbox: Optional[BoundingBox] = None
    rule_reference: str
    penal_provision: Optional[str] = None
    is_uncertain: bool = False
    detected_on_surface: str = "Front (PDP)"

class AddressInfo(BaseModel):
    name: str = ""
    full_address: str = ""
    pin_code: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    has_valid_pin: bool = False

class NetQuantityInfo(BaseModel):
    raw_text: str = ""
    value: float = 0.0
    unit: str = ""
    unit_type: str = "weight"  # weight, volume, length, count
    font_height_mm: float = 3.0
    complies_standard_units: bool = True
    prohibited_unit_detected: Optional[str] = None

class MrpInfo(BaseModel):
    raw_text: str = ""
    currency: str = "INR"
    amount: float = 0.0
    tax_inclusive_statement_present: bool = True
    complies_tax_phrase: bool = True

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

class ProductClassification(BaseModel):
    product_type: str = "Other packaged commodity"
    is_imported: bool = False
    is_multipack: bool = False
    is_liquid: bool = False
    is_perishable: bool = False
    is_scheduled_commodity: bool = False
    pdp_area_cm2: float = 120.0
    confidence: float = 0.95
    reasoning: str = ""

class FieldEvidence(BaseModel):
    field_name: str
    label: str
    value: str
    confidence: float = 0.98
    source_text: str = ""
    image_id: Optional[str] = None
    surface: str = "Front (PDP)"
    bounding_box: Optional[BoundingBox] = None
    status: str = "DETECTED"  # 'DETECTED', 'NOT DETECTED', 'UNREADABLE', 'NEEDS REVIEW', 'NOT APPLICABLE'
    rule_reference: Optional[str] = None
    review_reason: Optional[str] = None
    notes: Optional[str] = None

class StructuredProductData(BaseModel):
    product_name: str = ""
    commodity_name: str = ""
    brand: Optional[str] = None
    generic_name: Optional[str] = None
    variant: Optional[str] = None
    manufacturer: AddressInfo = Field(default_factory=AddressInfo)
    packer: Optional[AddressInfo] = None
    importer: Optional[AddressInfo] = None
    net_quantity: NetQuantityInfo = Field(default_factory=NetQuantityInfo)
    mrp: MrpInfo = Field(default_factory=MrpInfo)
    unit_sale_price: Optional[UnitSalePriceInfo] = None
    mfd: DateInfo = Field(default_factory=DateInfo)
    expiry: Optional[DateInfo] = None
    batch: str = ""
    consumer_care: ConsumerCareInfo = Field(default_factory=ConsumerCareInfo)
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
    status: str  # 'PASS', 'FAIL', 'NEEDS REVIEW', 'NOT APPLICABLE', 'UNREADABLE'
    detected_declaration: str
    statutory_requirement: str
    font_size_or_unit_check: str
    section_penalty: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    surface: str = "Front (PDP)"
    is_applicable: bool = True
    applicability_reason: Optional[str] = None

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
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
