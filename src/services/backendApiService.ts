/**
 * LM-COMPASS (VidhiCheck) Backend API Client Service
 * Connects frontend directly to the Stage 2 (CV), Stage 3 (OCR & Rules),
 * Data Layer, and Stage 4 (Reports & Evaluation) backend endpoints.
 */

export interface QualityMetricsApiResponse {
  resolution_megapixels: number;
  width: number;
  height: number;
  blur_laplacian_variance: number;
  is_blurred: boolean;
  noise_variance: number;
  is_noisy: boolean;
  mean_brightness: number;
  contrast_std_dev: number;
  glare_percentage: number;
  is_glare_detected: boolean;
  rotation_angle_deg: number;
  perspective_distortion_detected: boolean;
  skew_angle_deg: number;
  background_interference_score: number;
  text_visibility: string;
  overall_quality_score: number;
  advisory?: string | null;
}

export interface PreprocessingVariantApiResponse {
  variant_id: string;
  name: string;
  description: string;
  base64_image?: string;
  width: number;
  height: number;
  processing_time_ms: number;
}

export interface BackendRegionItem {
  region_id: string;
  category: string;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
    label?: string;
    pixel_coords?: [number, number, number, number];
  };
  detection_confidence: number;
  ocr_confidence: number;
  cropped_image_base64?: string;
  ocr_candidates?: Record<string, string>;
  selected_text?: string;
  method_used?: string;
  status: string;
}

export interface MeasurementValidationApiResponse {
  reference_detected: boolean;
  reference_type?: string | null;
  pixel_to_mm_ratio?: number | null;
  estimated_font_height_mm?: number | null;
  table1_required_height_mm: number;
  table1_complies: boolean;
  status_message: string;
}

export interface LabelMeAnnotationResponse {
  version: string;
  flags: Record<string, any>;
  shapes: Array<{
    label: string;
    points: [[number, number], [number, number]];
    shape_type: string;
    detection_confidence?: number;
    ocr_confidence?: number;
  }>;
  imagePath: string;
  imageHeight: number;
  imageWidth: number;
}

export interface ScanProcessApiResponse {
  scan_id: string;
  product_info: any;
  canonical_fields: Array<{
    field_name: string;
    statutory_name: string;
    extracted_value: string;
    confidence: number;
    status: string;
    bbox?: { x: number; y: number; width: number; height: number; label?: string };
    rule_reference: string;
    penal_provision?: string | null;
    is_uncertain?: boolean;
    detected_on_surface: string;
    raw_ocr_value?: string;
    confidence_level?: string;
    review_reason?: string;
    evidence_crop_base64?: string;
  }>;
  compliance_checks: Array<{
    rule_no: string;
    rule_title: string;
    sub_rule: string;
    status: 'PASS' | 'FAIL' | 'WARN' | 'NEEDS REVIEW' | 'NOT APPLICABLE' | 'NOT DETECTED';
    detected_declaration: string;
    statutory_requirement: string;
    font_size_or_unit_check: string;
    section_penalty?: string | null;
    bounding_box?: { x: number; y: number; width: number; height: number; label?: string };
    surface: string;
    is_applicable: boolean;
    source_pdf?: string;
    source_pdf_page?: number;
    amendment_citation?: string;
    effective_date?: string;
    original_text?: string;
  }>;
  compliance_score: number;
  overall_status: 'COMPLIANT' | 'NON_COMPLIANT' | 'NEEDS_REVIEW';
  extracted_lines: Array<{
    line_index: number;
    text: string;
    confidence: number;
    bbox?: { x: number; y: number; width: number; height: number };
    is_uncertain?: boolean;
    surface: string;
  }>;
  surfaces_processed: string[];
  image_quality?: QualityMetricsApiResponse;
  preprocessing_variants: PreprocessingVariantApiResponse[];
  detected_regions: BackendRegionItem[];
  measurement_validation?: MeasurementValidationApiResponse;
  labelme_annotation?: LabelMeAnnotationResponse;
  external_verification: string;
  timestamp: string;
}

export interface BenchmarkMetricItem {
  metric_name: string;
  category: string;
  measured_accuracy: number;
  target_threshold: number;
  status: string;
  sample_count: number;
  notes: string;
}

export interface BenchmarkResponse {
  benchmark_id: string;
  timestamp: string;
  total_test_samples: number;
  test_categories: string[];
  metrics: BenchmarkMetricItem[];
  overall_system_reliability: number;
  false_positive_rate: number;
  false_negative_rate: number;
  disagreement_resolution_rate: number;
}

export interface SystemStatusResponse {
  status: string;
  version: string;
  yolo_model_loaded: boolean;
  yolo_backend: string;
  tesseract_available: boolean;
  easyocr_available: boolean;
  paddleocr_available: boolean;
  opencv_version: string;
  database_backend: string;
  database_connected: boolean;
  redis_cache_backend: string;
  redis_connected: boolean;
  elasticsearch_backend: string;
  elasticsearch_connected: boolean;
  external_government_api: string;
}

/**
 * Checks image quality against the 12 automated metrics
 */
export async function checkImageQualityApi(imageBase64: string): Promise<QualityMetricsApiResponse | null> {
  try {
    const res = await fetch('/api/scan/quality', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: imageBase64 })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('Quality API error:', err);
    return null;
  }
}

/**
 * Generates the 13 preprocessing variants
 */
export async function getPreprocessingVariantsApi(imageBase64: string): Promise<PreprocessingVariantApiResponse[]> {
  try {
    const res = await fetch('/api/scan/variants', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: imageBase64 })
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.warn('Variants API error:', err);
    return [];
  }
}

/**
 * Executes dynamic region detection and LabelMe generation
 */
export async function detectPackagingRegionsApi(imageBase64: string): Promise<{
  regions: BackendRegionItem[];
  labelme: LabelMeAnnotationResponse;
  measurement: MeasurementValidationApiResponse;
} | null> {
  try {
    const res = await fetch('/api/scan/detect-regions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: imageBase64 })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('Region detection API error:', err);
    return null;
  }
}

/**
 * Executes the complete 4-stage pipeline on single or multi-surface images
 */
export async function processScanApi(
  images: Array<{ data: string; surface: string; file_name?: string; text_lines?: string[] }>,
  options?: any
): Promise<ScanProcessApiResponse> {
  const res = await fetch('/api/scan/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ images, options })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errData.detail || `Pipeline execution failed: HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Retrieves evaluation benchmark metrics
 */
export async function getEvaluationBenchmarkApi(): Promise<BenchmarkResponse | null> {
  try {
    const res = await fetch('/api/evaluation/benchmark');
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('Benchmark API error:', err);
    return null;
  }
}

/**
 * Retrieves system diagnostic status
 */
export async function getSystemStatusApi(): Promise<SystemStatusResponse | null> {
  try {
    const res = await fetch('/api/system/status');
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('System status API error:', err);
    return null;
  }
}

export function getPdfReportUrl(scanId: string): string {
  return `/api/reports/${encodeURIComponent(scanId)}/pdf`;
}

export function getDocxReportUrl(scanId: string): string {
  return `/api/reports/${encodeURIComponent(scanId)}/docx`;
}

export function getLabelMeJsonUrl(scanId: string): string {
  return `/api/scan/${encodeURIComponent(scanId)}/labelme`;
}
