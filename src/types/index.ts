export type OfficerRole = 'ADMIN' | 'SENIOR_OFFICER' | 'OFFICER' | 'VIEWER';

export interface User {
  id: string;
  name: string;
  badgeNumber: string;
  role: OfficerRole;
  department: string;
  jurisdictionZone: string;
  email: string;
  phone: string;
  status: 'Active' | 'On Leave' | 'Suspended';
  lastActive: string;
  avatarUrl?: string;
}

export type InspectionStatus = 'Compliant' | 'Non-Compliant' | 'Under Review';
export type InspectionType = 'Market Surveillance' | 'Consumer Complaint' | 'Port of Entry Inward' | 'Routine Audit';
export type SurfaceType = 'Front (PDP)' | 'Back Panel' | 'Side Panel' | 'Top/Bottom' | 'Outer Carton';

export interface BoundingBox {
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  width: number; // percentage
  height: number; // percentage
  label: string;
}

export interface ExtractedDeclaration {
  id: string;
  declarationType: string;
  extractedValue: string;
  expectedRequirement: string;
  ruleReference: string;
  surface: SurfaceType;
  status: 'Found' | 'Missing' | 'Defective' | 'Under Review';
  confidence: 'High' | 'Medium' | 'Low';
  confidenceScore?: number; // e.g. 0.94 for technical inspector drawer
  officerStatus: 'Verified' | 'Edited' | 'Flagged' | 'Pending';
  correctionNotes?: string;
  boundingBox?: BoundingBox;
  sourcePdf?: string;
  sourcePdfPage?: number;
  amendmentCitation?: string;
  effectiveDate?: string;
}

export interface InspectionViolation {
  id: string;
  violationType: string;
  ruleReference: string;
  statutoryActClause: string;
  product: string;
  surface: SurfaceType;
  description: string;
  severity: 'High' | 'Medium' | 'Low';
  officerStatus: 'Needs Review' | 'Accepted' | 'Dismissed' | 'Re-inspection Required';
  evidenceImage: string;
  evidenceBoundingBox: BoundingBox;
  officerComments?: string;
  recommendedPenalty: string;
  reportedDate: string;
  sourcePdf?: string;
  sourcePdfPage?: number;
  amendmentCitation?: string;
  effectiveDate?: string;
  expectedRequirement?: string;
  detectedText?: string;
}

export interface InspectionImage {
  id: string;
  surface: SurfaceType;
  url: string;
  name: string;
  timestamp: string;
  qualityStatus: 'Good' | 'Fair' | 'Poor';
  dimensions: string;
  ocrExtracted: boolean;
}

export interface ExtractedLabelLine {
  lineNumber: number;
  text: string;
  confidence: number;
  matchedRule?: string;
  category?: string;
  status: 'Compliant' | 'Non-Compliant' | 'Under Review' | 'Informational';
  finding?: string;
  penalRef?: string;
}

export type ProductCategory =
  | 'Category A — Food & Food Products'
  | 'Category B — Beverages & Bottled Liquids'
  | 'Category C — Cosmetics & Personal Care'
  | 'Category D — Cleaning, Detergents & Household Care'
  | 'Category E — Pharmaceuticals, Medical Devices & Healthcare'
  | 'Category F — Electronics, Electrical Appliances & IT Goods'
  | 'Category G — Stationery, Paper, Office & School Supplies'
  | 'Category H — Toys, Baby Gear & Infant Products'
  | 'Category I — Textiles, Apparel, Footwear & Accessories'
  | 'Category J — Hardware, Construction, Paint & Tools'
  | 'Category K — Automotive Parts, Lubricants & Accessories'
  | 'Category L — Agricultural, Seeds, Fertilizers & Pesticides'
  | 'Category M — Pet Food & Animal Care Products'
  | 'Category N — Tobacco, Pan Masala & Related Commodities'
  | 'Category O — Industrial Raw Materials & Bulk Packaged Commodities'
  | 'Category P — Imported Commodities (Special Provisions)'
  | 'Category Q — E-Commerce / Outer Delivery Packages'
  | 'Category R — Unknown / Uncertain / Ambiguous Commodity';

export type SemanticRegionType =
  | 'DIRECTIONS'
  | 'INGREDIENTS'
  | 'POSSIBLE_INGREDIENTS'
  | 'WARNING'
  | 'MARKETER'
  | 'MARKETER_ADDRESS'
  | 'MANUFACTURER'
  | 'MANUFACTURER_ADDRESS'
  | 'PACKER'
  | 'PACKER_ADDRESS'
  | 'IMPORTER'
  | 'IMPORTER_ADDRESS'
  | 'POSTAL_PIN'
  | 'MRP'
  | 'NET_QUANTITY'
  | 'UNIT_SALE_PRICE'
  | 'CONSUMER_CARE'
  | 'CONSUMER_CARE_EMAIL'
  | 'CONSUMER_CARE_PHONE'
  | 'CONSUMER_CARE_ADDRESS'
  | 'COUNTRY_OF_ORIGIN'
  | 'DATE_MANUFACTURE'
  | 'DATE_EXPIRY'
  | 'DATE_BEST_BEFORE'
  | 'BATCH_LOT'
  | 'GENERIC_COMMODITY_NAME'
  | 'BRAND_IDENTITY'
  | 'BARCODE'
  | 'FSSAI_LICENSE'
  | 'NUTRITIONAL_INFO'
  | 'STORAGE_INSTRUCTIONS'
  | 'DISPOSAL_RECYCLING'
  | 'ECO_GREEN_DOT'
  | 'RED_BROWN_NON_VEG_DOT'
  | 'CERTIFICATION_MARK'
  | 'MARKETING_CLAIM'
  | 'GENERIC_ADDRESS'
  | 'OTHER_TEXT';

export interface MultiTierConfidence {
  image_quality_confidence: number;
  ocr_confidence: number;
  classification_confidence: number;
  extraction_confidence: number;
  rule_validation_confidence: number;
  overall_confidence: number;
}

export interface LmCompassFieldItem {
  field_name: string;
  display_name: string;
  status: 'FOUND' | 'MISSING' | 'AMBIGUOUS' | 'NOT_APPLICABLE' | 'CONFLICT';
  extracted_value?: string;
  surface?: string;
  bounding_box?: BoundingBox;
  confidence: number;
  statutory_basis?: string;
}

export interface LmCompassComplianceItem {
  rule_id: string;
  statutory_citation: string;
  requirement_title: string;
  status: 'COMPLIANT' | 'NON_COMPLIANT' | 'NEEDS_REVIEW' | 'NOT_APPLICABLE';
  evidence_field?: string;
  evidence_value?: string;
  evidence_surface?: string;
  evidence_bbox?: BoundingBox;
  evidence_text?: string;
  confidence: number;
  notes?: string;
}

export interface LmCompassViolationItem {
  rule_id: string;
  statutory_citation: string;
  violation_title: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  legal_reasoning: string;
  prescribed_requirement: string;
  detected_defect: string;
  exact_evidence_bbox: BoundingBox;
  exact_evidence_text: string;
  evidence_surface: string;
  penal_provision: string;
  statutory_fine: string;
  remedial_action: string;
}

export interface LmCompassNeedsReviewItem {
  rule_id: string;
  statutory_citation: string;
  review_title: string;
  reason: string;
  suggested_officer_action: string;
  evidence_surface?: string;
  detected_text?: string;
}

export interface LmCompassResult {
  product_understanding: {
    category_name: string;
    category_code: string;
    classification_status: string;
    detected_commodity?: string;
    is_imported: boolean;
    is_multipack: boolean;
    is_liquid: boolean;
    has_primary_display_panel: boolean;
    total_surfaces_analyzed: number;
    surfaces_detected: string[];
    confidence_score: number;
  };
  declared_fields: LmCompassFieldItem[];
  compliance_matrix: LmCompassComplianceItem[];
  violations: LmCompassViolationItem[];
  needs_review: LmCompassNeedsReviewItem[];
  duplicate_consistency: {
    net_quantity_consistency: string;
    mrp_consistency: string;
    notes?: string;
  };
  multi_tier_confidence: MultiTierConfidence;
  overall_status: 'COMPLIANT' | 'NON_COMPLIANT' | 'NEEDS_REVIEW';
  summary_rationale: string;
}

export type ProductTypeCategory =
  | 'Food'
  | 'Cosmetic/toiletry'
  | 'Household product'
  | 'Clothing/textile'
  | 'Electrical/electronic packaged commodity'
  | 'Liquid product'
  | 'Weight-based commodity'
  | 'Volume-based commodity'
  | 'Multipack'
  | 'Imported product'
  | 'Other packaged commodity'
  | 'NEEDS REVIEW';

export interface ProductClassification {
  productType: ProductTypeCategory;
  isImported: boolean;
  isMultipack: boolean;
  isLiquid: boolean;
  isPerishable: boolean;
  isScheduledCommodity: boolean;
  pdpAreaCm2?: number;
  confidence: number;
  reasoning: string;
}

export type DeclarationCheckStatus =
  | 'DETECTED'
  | 'NOT DETECTED'
  | 'UNREADABLE'
  | 'NEEDS REVIEW'
  | 'NOT APPLICABLE';

export interface FieldEvidence {
  field_name: string;
  label: string;
  value: string;
  confidence: number;
  source_text: string;
  image_id?: string;
  surface?: SurfaceType;
  bounding_box?: BoundingBox;
  status: DeclarationCheckStatus;
  rule_reference?: string;
  review_reason?: string;
  notes?: string;
  assignment_reasoning?: string;
  surrounding_context?: string[];
  semantic_class?: string;
  raw_ocr?: string;
  image_quality_confidence?: number;
  ocr_confidence?: number;
  classification_confidence?: number;
  extraction_confidence?: number;
}

export interface StructuredProductData {
  // 1-5: Product Identity
  brand?: string;
  brand_name?: string;
  product_name: string;
  generic_name?: string;
  commodity_name: string;
  product_variant?: string;
  category?: string;
  product_category?: string;
  category_code?: string;
  classification_status?: string;

  // 6-12: Responsible Entities
  manufacturer_name?: string;
  manufacturer_address?: string;
  manufacturer: {
    name: string;
    address: string;
    pin_code?: string;
  };
  packer_name?: string;
  packer_address?: string;
  packer: {
    name: string;
    address: string;
  };
  importer_name?: string;
  importer_address?: string;
  importer: {
    name: string;
    address: string;
  };
  marketer_name?: string;
  marketer_address?: string;
  marketer?: {
    name: string;
    address: string;
    pin_code?: string;
  };
  brand_owner_info?: string;

  // 13: Country of Origin
  country_of_origin: string;

  // 14-20: Quantity Information
  net_quantity: string;
  net_weight?: string;
  net_volume?: string;
  piece_count?: string;
  quantity_per_package?: string;
  total_multipack_quantity?: string;
  unit_of_measurement?: string;
  units?: string;

  // 21-23: Price Information
  mrp: string;
  unit_sale_price?: string;
  tax_inclusive_wording?: string;

  // 24-28: Dates & Temporal Traceability
  manufacturing_date: string;
  packing_date: string;
  import_date: string;
  best_before?: string;
  best_before_date?: string;
  use_by_expiry?: string;
  expiry_date?: string;
  expiry_or_best_before: string;

  // 29-31: Batch Identification
  batch_number: string;
  lot_number?: string;
  code_number?: string;

  // 32-35: Consumer Grievance Details
  consumer_care_phone?: string;
  consumer_care_email?: string;
  consumer_care_address?: string;
  consumer_care: {
    phone: string;
    email: string;
    address: string;
  };
  other_complaint_info?: string;

  // 36-37: Dimensions & Other Declarations
  package_dimensions?: string;
  other_declarations: string[];

  // Additional Semantic Text Preservations
  directions_text?: string;
  ingredients_text?: string;
  warnings_text?: string;
  postal_pin?: string;

  // Full raw unmapped text preserved verbatim
  other_text?: string;
  classification?: ProductClassification;
  evidence?: Record<string, FieldEvidence>;
}

export interface CanonicalField {
  field: string;
  label: string;
  value: string;
  confidence: number;
  source: string;
  status: 'Detected' | 'Not Detected' | 'Unreadable' | 'Missing' | 'Defective' | 'Needs Review' | 'Not Applicable' | string;
  bbox?: BoundingBox;
  imageNumber?: number;
  surface?: SurfaceType;
  raw_ocr_value?: string;
  confidence_level?: string;
  review_reason?: string;
  crop_base64?: string;
  assignment_reasoning?: string;
  surrounding_context?: string[];
  semantic_class?: string;
}

export interface ComplianceCheckItem {
  ruleId: string;
  ruleNo: string;
  subRule: string;
  requirement: string;
  detectedInfo: string;
  confidence: number;
  status: 'PASS' | 'FAIL' | 'NEEDS REVIEW' | 'NOT APPLICABLE' | 'UNREADABLE';
  isApplicable?: boolean;
  applicabilityReason?: string;
  evidenceSource?: string;
  evidenceBbox?: BoundingBox;
  evidenceImageId?: string;
  evidenceSurface?: SurfaceType;
  reason?: string;
  penalRef?: string;
  sourcePdf?: string;
  sourcePdfPage?: number;
  amendmentCitation?: string;
  effectiveDate?: string;
  originalText?: string;
}

export interface InspectionRecord {
  id: string;
  date: string;
  officerName: string;
  officerBadge: string;
  jurisdiction: string;
  location: string;
  inspectionType: InspectionType;
  productName: string;
  brand: string;
  category: string;
  manufacturer: string;
  packerImporter: string;
  barcode: string;
  batchNumber: string;
  status: InspectionStatus;
  images: InspectionImage[];
  declarations: ExtractedDeclaration[];
  violations: InspectionViolation[];
  extractedLines?: ExtractedLabelLine[];
  structuredData?: StructuredProductData;
  canonicalFields?: CanonicalField[];
  fieldEvidences?: FieldEvidence[];
  classification?: ProductClassification;
  otherText?: string;
  complianceChecks?: ComplianceCheckItem[];
  complianceScore?: number;
  complianceSummary?: {
    passed: number;
    failed: number;
    needsReview: number;
    notApplicable: number;
  };
  detectedRegions?: any[];
  measurementValidation?: any;
  labelmeAnnotation?: any;
  preprocessingVariants?: any[];
  externalVerification?: string;
  scanId?: string;
  imageQuality?: any;
  labelmeExportUrl?: string;
  officerNotes: string;
  finalDecision: 'Accepted' | 'Notice Issued' | 'Pending Hearing' | 'Exempt' | 'Draft';
  qrVerificationHash: string;
  statutoryReference: string;
  lmCompassResult?: LmCompassResult;
}

export interface ProductItem {
  id: string;
  name: string;
  brand: string;
  category: string;
  manufacturer: string;
  barcode: string;
  standardQuantity: string;
  lastInspectionDate: string;
  lastInspectionId: string;
  complianceStatus: InspectionStatus;
  totalAudits: number;
  totalViolations: number;
  marketRiskRating: 'Low' | 'Medium' | 'High';
}

export interface LegalRuleItem {
  id: string;
  ruleNo: string;
  subRule: string;
  title: string;
  requirement: string;
  applicableDeclaration: string;
  category: string;
  prescribedParameters: string;
  source: string;
  penalProvision: string;
  lastUpdated: string;
  officerGuidance: string;
  fontTable?: Array<{ area: string; minHeightNormal: string; minHeightBlowMoulded: string }>;
  sourcePdf?: string;
  sourcePdfPage?: number;
  amendmentCitation?: string;
  effectiveDate?: string;
  originalText?: string;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  user: string;
  role: string;
  action: string;
  module: string;
  recordId: string;
  status: 'Success' | 'Warning' | 'Override';
  details: string;
  ipAddress: string;
}
