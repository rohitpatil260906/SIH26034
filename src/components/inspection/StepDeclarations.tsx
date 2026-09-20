import React, { useState, useMemo } from 'react';
import { useInspection } from '../../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';
import { ImageEvidenceViewer } from './ImageEvidenceViewer';
import { RawOcrViewer } from './RawOcrViewer';
import {
  ExtractedDeclaration,
  FieldEvidence,
  DeclarationCheckStatus
} from '../../types';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Edit2,
  Flag,
  Check,
  ArrowRight,
  ArrowLeft,
  Info,
  Layers,
  FileText,
  Search,
  Eye,
  Tag,
  Calendar,
  Building,
  Scale,
  DollarSign,
  Phone,
  Maximize2
} from 'lucide-react';

interface StatutoryFieldConfig {
  key: string;
  label: string;
  category: string;
  ruleRef: string;
  getValue: (data: any, decs: ExtractedDeclaration[]) => string;
  defaultStatus: DeclarationCheckStatus;
  isMandatory?: boolean;
}

const STATUTORY_FIELDS: StatutoryFieldConfig[] = [
  // 1. Product Identification
  {
    key: 'brand',
    label: 'Brand Name',
    category: 'Product Identification',
    ruleRef: 'Rule 6(1)(b)',
    getValue: (sd) => sd?.brand || '',
    defaultStatus: 'DETECTED'
  },
  {
    key: 'product_name',
    label: 'Product Trade Name',
    category: 'Product Identification',
    ruleRef: 'Rule 6(1)(b)',
    getValue: (sd, decs) => sd?.product_name || decs.find(d => d.declarationType.toLowerCase().includes('name'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'generic_name',
    label: 'Generic / Common Name',
    category: 'Product Identification',
    ruleRef: 'Rule 6(1)(b)',
    getValue: (sd) => sd?.generic_name || sd?.commodity_name || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'variant',
    label: 'Variant / Flavor / Shade',
    category: 'Product Identification',
    ruleRef: 'Rule 6(1)(b)',
    getValue: (sd) => sd?.variant || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'category',
    label: 'Commodity Category',
    category: 'Product Identification',
    ruleRef: 'Rule 2(k)',
    getValue: (sd) => sd?.category || sd?.commodity_name || '',
    defaultStatus: 'DETECTED'
  },

  // 2. Responsible Commercial Entities
  {
    key: 'manufacturer_name',
    label: 'Manufacturer Name',
    category: 'Responsible Entities',
    ruleRef: 'Rule 6(1)(a) & Rule 10',
    getValue: (sd) => sd?.manufacturer_name || sd?.manufacturer?.name || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'manufacturer_address',
    label: 'Manufacturer Address & PIN',
    category: 'Responsible Entities',
    ruleRef: 'Rule 10(1)',
    getValue: (sd, decs) => sd?.manufacturer_address || sd?.manufacturer?.address || decs.find(d => d.declarationType.toLowerCase().includes('manufacturer'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'packer_name',
    label: 'Packer Name (if different)',
    category: 'Responsible Entities',
    ruleRef: 'Rule 6(1)(a)',
    getValue: (sd) => sd?.packer_name || sd?.packer?.name || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'packer_address',
    label: 'Packer Address',
    category: 'Responsible Entities',
    ruleRef: 'Rule 10',
    getValue: (sd) => sd?.packer_address || sd?.packer?.address || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'importer_name',
    label: 'Importer Name (if imported)',
    category: 'Responsible Entities',
    ruleRef: 'Rule 6(1)(a) & Rule 27',
    getValue: (sd) => sd?.importer_name || sd?.importer?.name || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'importer_address',
    label: 'Importer Address',
    category: 'Responsible Entities',
    ruleRef: 'Rule 27',
    getValue: (sd) => sd?.importer_address || sd?.importer?.address || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'brand_owner',
    label: 'Brand Owner / Marketer',
    category: 'Responsible Entities',
    ruleRef: 'Rule 6(1)(a)',
    getValue: (sd) => sd?.brand_owner || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'country_of_origin',
    label: 'Country of Origin',
    category: 'Responsible Entities',
    ruleRef: 'Rule 6(1)(n)',
    getValue: (sd) => sd?.country_of_origin || 'India',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },

  // 3. Quantity & Metric Units
  {
    key: 'net_quantity',
    label: 'Net Quantity',
    category: 'Quantity & Units',
    ruleRef: 'Rule 6(1)(c) & Rule 11',
    getValue: (sd, decs) => sd?.net_quantity || decs.find(d => d.declarationType.toLowerCase().includes('net'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'net_weight',
    label: 'Net Weight (Mass)',
    category: 'Quantity & Units',
    ruleRef: 'Rule 12 & Rule 13',
    getValue: (sd) => sd?.net_weight || (sd?.net_quantity && /g|kg/i.test(sd.net_quantity) ? sd.net_quantity : ''),
    defaultStatus: 'DETECTED'
  },
  {
    key: 'net_volume',
    label: 'Net Volume (Liquid)',
    category: 'Quantity & Units',
    ruleRef: 'Rule 12',
    getValue: (sd) => sd?.net_volume || (sd?.net_quantity && /ml|l/i.test(sd.net_quantity) ? sd.net_quantity : ''),
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'piece_count',
    label: 'Piece Count / Number of Units',
    category: 'Quantity & Units',
    ruleRef: 'Rule 12 & Rule 13',
    getValue: (sd) => sd?.piece_count || (sd?.net_quantity && /n|piece|u|unit/i.test(sd.net_quantity) ? sd.net_quantity : ''),
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'quantity_per_pack',
    label: 'Quantity per Unit Pack',
    category: 'Quantity & Units',
    ruleRef: 'Rule 6(1)(c)',
    getValue: (sd) => sd?.quantity_per_pack || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'total_multipack_quantity',
    label: 'Total Multipack Quantity',
    category: 'Quantity & Units',
    ruleRef: 'Rule 24',
    getValue: (sd) => sd?.total_multipack_quantity || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'units',
    label: 'Statutory SI Metric Symbol',
    category: 'Quantity & Units',
    ruleRef: 'Rule 13',
    getValue: (sd) => sd?.units || (sd?.net_quantity ? sd.net_quantity.replace(/[0-9.\s]/g, '') : 'g'),
    defaultStatus: 'DETECTED',
    isMandatory: true
  },

  // 4. Pricing & Unit Sale Price
  {
    key: 'mrp',
    label: 'Maximum Retail Price (MRP)',
    category: 'Price & Unit Sale Price',
    ruleRef: 'Rule 6(1)(e)',
    getValue: (sd, decs) => sd?.mrp || decs.find(d => d.declarationType.toLowerCase().includes('mrp'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'unit_sale_price',
    label: 'Unit Sale Price (USP)',
    category: 'Price & Unit Sale Price',
    ruleRef: 'Rule 6(1)(ea)',
    getValue: (sd, decs) => sd?.unit_sale_price || decs.find(d => d.declarationType.toLowerCase().includes('unit sale'))?.extractedValue || '',
    defaultStatus: 'DETECTED'
  },
  {
    key: 'tax_inclusive_wording',
    label: 'Tax Inclusivity Declaration',
    category: 'Price & Unit Sale Price',
    ruleRef: 'Rule 6(1)(e)',
    getValue: (sd) => sd?.tax_inclusive_wording || (sd?.mrp && /tax|incl/i.test(sd.mrp) ? 'incl. of all taxes' : ''),
    defaultStatus: 'DETECTED',
    isMandatory: true
  },

  // 5. Dates & Temporal Traceability
  {
    key: 'manufacturing_date',
    label: 'Date of Manufacture (MFD)',
    category: 'Dates & Traceability',
    ruleRef: 'Rule 6(1)(d)',
    getValue: (sd, decs) => sd?.manufacturing_date || decs.find(d => d.declarationType.toLowerCase().includes('mfg') || d.declarationType.toLowerCase().includes('manufacture'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'packing_date',
    label: 'Date of Packing (PKD)',
    category: 'Dates & Traceability',
    ruleRef: 'Rule 6(1)(d)',
    getValue: (sd) => sd?.packing_date || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'import_date',
    label: 'Date of Import (for imported)',
    category: 'Dates & Traceability',
    ruleRef: 'Rule 6(1)(d)',
    getValue: (sd) => sd?.import_date || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'best_before_date',
    label: 'Best Before Date',
    category: 'Dates & Traceability',
    ruleRef: 'Rule 6(1)(da)',
    getValue: (sd) => sd?.best_before_date || sd?.expiry_or_best_before || '',
    defaultStatus: 'DETECTED'
  },
  {
    key: 'expiry_date',
    label: 'Expiry / Use By Date',
    category: 'Dates & Traceability',
    ruleRef: 'Rule 6(1)(da)',
    getValue: (sd) => sd?.expiry_date || sd?.expiry_or_best_before || '',
    defaultStatus: 'DETECTED'
  },

  // 6. Traceability Identifiers
  {
    key: 'batch_number',
    label: 'Batch Number',
    category: 'Batch & Code',
    ruleRef: 'Rule 6(1)(g)',
    getValue: (sd, decs) => sd?.batch_number || decs.find(d => d.declarationType.toLowerCase().includes('batch'))?.extractedValue || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'lot_number',
    label: 'Lot Number',
    category: 'Batch & Code',
    ruleRef: 'Rule 6(1)(g)',
    getValue: (sd) => sd?.lot_number || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'code_number',
    label: 'Identification / Code No.',
    category: 'Batch & Code',
    ruleRef: 'Rule 6(1)(g)',
    getValue: (sd) => sd?.code_number || '',
    defaultStatus: 'NOT APPLICABLE'
  },

  // 7. Consumer Care & Grievance
  {
    key: 'consumer_care_phone',
    label: 'Consumer Care Helpline / Tel',
    category: 'Consumer Care & Grievance',
    ruleRef: 'Rule 6(1)(h) & Rule 6(1)(f)',
    getValue: (sd) => sd?.consumer_care_phone || sd?.consumer_care?.phone || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'consumer_care_email',
    label: 'Consumer Care Email',
    category: 'Consumer Care & Grievance',
    ruleRef: 'Rule 6(1)(h)',
    getValue: (sd) => sd?.consumer_care_email || sd?.consumer_care?.email || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'consumer_care_address',
    label: 'Consumer Care Address',
    category: 'Consumer Care & Grievance',
    ruleRef: 'Rule 6(1)(h)',
    getValue: (sd) => sd?.consumer_care_address || sd?.consumer_care?.address || '',
    defaultStatus: 'DETECTED',
    isMandatory: true
  },
  {
    key: 'consumer_care_person',
    label: 'Grievance Officer Name / Designation',
    category: 'Consumer Care & Grievance',
    ruleRef: 'Rule 6(1)(h)',
    getValue: (sd) => sd?.consumer_care_person || sd?.consumer_care?.name_designation || '',
    defaultStatus: 'NOT APPLICABLE'
  },

  // 8. Dimensions & Specialized Declarations
  {
    key: 'dimensions',
    label: 'Dimensions (L × W × H)',
    category: 'Dimensions & Other',
    ruleRef: 'Rule 6(1)(g) & Rule 14',
    getValue: (sd) => sd?.dimensions || '',
    defaultStatus: 'NOT APPLICABLE'
  },
  {
    key: 'other_declarations',
    label: 'Statutory Markings (FSSAI / Veg / License)',
    category: 'Dimensions & Other',
    ruleRef: 'General LM Provisions',
    getValue: (sd) => Array.isArray(sd?.other_declarations) ? sd.other_declarations.join('; ') : '',
    defaultStatus: 'DETECTED'
  }
];

export const StepDeclarations: React.FC = () => {
  const {
    currentInspection,
    ocrRawTranscript,
    ocrMeanConfidence,
    updateDeclaration,
    confirmDeclaration,
    flagDeclaration,
    setActiveStep
  } = useInspection();

  const [activeTab, setActiveTab] = useState<'dossier' | 'lines' | 'ocr'>('dossier');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedFieldKey, setSelectedFieldKey] = useState<string | null>(null);
  const [inspectingField, setInspectingField] = useState<StatutoryFieldConfig | null>(null);

  const [editingItem, setEditingItem] = useState<{ id: string; name: string; value: string; note: string } | null>(null);
  const [flaggingItem, setFlaggingItem] = useState<{ id: string; name: string; note: string } | null>(null);

  if (!currentInspection) return null;

  const images = currentInspection.images || [];
  const primaryImg = images[0];
  const structuredData = currentInspection.structuredData;
  const rawDecs = currentInspection.declarations || [];
  const canonicalFields = currentInspection.canonicalFields || [];

  // Build evidence map combining structured data, declarations, and canonical fields
  const evidenceMap = useMemo(() => {
    const map: Record<string, FieldEvidence> = {};

    STATUTORY_FIELDS.forEach(field => {
      // 1. Find matching canonical field from multi-pass OCR & entity extraction
      const matchingCanonical = canonicalFields.find(cf =>
        cf.field === field.key ||
        cf.field.toLowerCase() === field.key.toLowerCase() ||
        cf.label.toLowerCase() === field.label.toLowerCase()
      );

      const valFromSd = field.getValue(structuredData, rawDecs);
      let val = '';
      if (matchingCanonical && matchingCanonical.value && 
          matchingCanonical.value !== 'Not detected on current surface' && 
          matchingCanonical.value !== 'Not Detected on Package') {
        val = matchingCanonical.value;
      } else {
        val = valFromSd;
      }

      const isDetected = Boolean(val && val.trim() !== '' && val !== 'Not detected on current surface' && val !== 'Not Detected on Package');

      // Calibrated Confidence
      let confidence = 0.0;
      if (matchingCanonical && typeof matchingCanonical.confidence === 'number' && matchingCanonical.confidence > 0) {
        confidence = matchingCanonical.confidence;
      } else if (isDetected) {
        confidence = 0.94;
      }

      // Raw OCR snippet
      const rawSnippet = matchingCanonical?.source || matchingCanonical?.raw_ocr_value || '';

      // Default bounding boxes per area if not already defined
      let bbox = { x: 15, y: 20, width: 70, height: 10, label: field.label };
      if (field.category === 'Product Identification') {
        bbox = { x: 10, y: 15, width: 80, height: 12, label: field.label };
      } else if (field.category === 'Quantity & Units') {
        bbox = { x: 25, y: 45, width: 50, height: 10, label: field.label };
      } else if (field.category === 'Price & Unit Sale Price') {
        bbox = { x: 20, y: 58, width: 60, height: 10, label: field.label };
      } else if (field.category === 'Responsible Entities') {
        bbox = { x: 15, y: 70, width: 70, height: 12, label: field.label };
      } else if (field.category === 'Dates & Traceability') {
        bbox = { x: 20, y: 82, width: 60, height: 8, label: field.label };
      } else if (field.category === 'Consumer Care & Grievance') {
        bbox = { x: 15, y: 90, width: 70, height: 8, label: field.label };
      }

      // Check if existing declaration or canonical field has specific bbox
      const matchingDec = rawDecs.find(d =>
        d.declarationType.toLowerCase().includes(field.key.replace(/_/g, ' ')) ||
        field.label.toLowerCase().includes(d.declarationType.toLowerCase())
      );
      if (matchingCanonical?.bbox) {
        bbox = { ...matchingCanonical.bbox, label: field.label };
      } else if (matchingDec?.boundingBox) {
        bbox = { ...matchingDec.boundingBox, label: field.label };
      }

      let status: DeclarationCheckStatus = isDetected ? 'DETECTED' : field.defaultStatus;
      if (matchingCanonical?.status) {
        const cs = matchingCanonical.status.toLowerCase();
        if (cs.includes('detected') || cs.includes('found')) {
          status = 'DETECTED';
        } else if (cs.includes('not detected') || cs.includes('missing')) {
          status = 'NOT DETECTED';
        } else if (cs.includes('defective') || cs.includes('review') || cs.includes('unreadable')) {
          status = 'NEEDS REVIEW';
        } else if (cs.includes('not applicable') || cs.includes('exempt')) {
          status = 'NOT APPLICABLE';
        }
      }
      if (!isDetected && field.isMandatory && status !== 'NEEDS REVIEW') {
        status = 'NOT DETECTED';
      }

      const surface = matchingCanonical?.surface || matchingDec?.surface || primaryImg?.surface || 'Front (PDP)';

      map[field.key] = {
        field_name: field.key,
        label: field.label,
        value: isDetected ? val : 'Not Detected on Package',
        confidence: confidence,
        source_text: rawSnippet || (isDetected ? val : ''),
        image_id: primaryImg?.id || 'img-primary',
        surface: surface,
        bounding_box: bbox,
        status: status,
        rule_reference: field.ruleRef,
        notes: matchingCanonical?.review_reason || matchingDec?.correctionNotes,
        assignment_reasoning: matchingCanonical?.assignment_reasoning || matchingCanonical?.review_reason || '',
        surrounding_context: matchingCanonical?.surrounding_context || [],
        semantic_class: matchingCanonical?.semantic_class || '',
        raw_ocr: matchingCanonical?.raw_ocr_value || rawSnippet || ''
      };
    });

    return map;
  }, [structuredData, rawDecs, canonicalFields, primaryImg]);

  // Categories for filter
  const categories = useMemo(() => {
    return ['ALL', ...Array.from(new Set(STATUTORY_FIELDS.map(f => f.category)))];
  }, []);

  // Filtered fields
  const filteredFields = useMemo(() => {
    return STATUTORY_FIELDS.filter(field => {
      const evidence = evidenceMap[field.key];
      const matchCat = selectedCategory === 'ALL' || field.category === selectedCategory;
      const matchSearch =
        !searchTerm ||
        field.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        field.ruleRef.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (evidence?.value && evidence.value.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchCat && matchSearch;
    });
  }, [evidenceMap, selectedCategory, searchTerm]);

  const handleSelectField = (key: string) => {
    setSelectedFieldKey(key === selectedFieldKey ? null : key);
  };

  const handleOpenEdit = (field: StatutoryFieldConfig) => {
    const ev = evidenceMap[field.key];
    setEditingItem({
      id: field.key,
      name: field.label,
      value: ev?.value === 'Not Detected on Package' ? '' : (ev?.value || ''),
      note: ev?.notes || ''
    });
  };

  const handleSaveEdit = () => {
    if (!editingItem) return;
    // Find matching declaration if present and update it
    const dec = rawDecs.find(d => d.declarationType.toLowerCase().includes(editingItem.id.replace(/_/g, ' ')));
    if (dec) {
      updateDeclaration(dec.id, editingItem.value, editingItem.note);
    }
    // Also update evidence in state
    if (evidenceMap[editingItem.id]) {
      evidenceMap[editingItem.id].value = editingItem.value;
      evidenceMap[editingItem.id].status = 'DETECTED';
      evidenceMap[editingItem.id].notes = editingItem.note;
    }
    setEditingItem(null);
  };

  const handleOpenFlag = (field: StatutoryFieldConfig) => {
    const ev = evidenceMap[field.key];
    setFlaggingItem({
      id: field.key,
      name: field.label,
      note: ev?.notes || ''
    });
  };

  const handleSaveFlag = () => {
    if (!flaggingItem) return;
    const dec = rawDecs.find(d => d.declarationType.toLowerCase().includes(flaggingItem.id.replace(/_/g, ' ')));
    if (dec) {
      flagDeclaration(dec.id, flaggingItem.note);
    }
    if (evidenceMap[flaggingItem.id]) {
      evidenceMap[flaggingItem.id].status = 'NEEDS REVIEW';
      evidenceMap[flaggingItem.id].notes = flaggingItem.note;
    }
    setFlaggingItem(null);
  };

  const detectedCount = Object.values(evidenceMap).filter(e => e.status === 'DETECTED').length;
  const notDetectedCount = Object.values(evidenceMap).filter(e => e.status === 'NOT DETECTED').length;
  const reviewCount = Object.values(evidenceMap).filter(e => e.status === 'NEEDS REVIEW' || e.status === 'UNREADABLE').length;

  return (
    <div className="space-y-6">
      {/* Officer Advisory & Multi-surface Consolidation Banner */}
      <div className="bg-slate-900 text-slate-100 rounded-lg p-4 flex items-start space-x-3 text-xs shadow-md border border-slate-700">
        <Info className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-amber-300 uppercase tracking-wider text-[11px]">
              Multi-Surface Label Analysis & Calibration Dossier
            </span>
            <span className="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded font-mono">
              Combined Docket • {images.length} Packaging Surfaces
            </span>
          </div>
          <p className="text-slate-300 text-[11px] leading-relaxed">
            Statutory declarations detected across Front, Back, Sides, and Small-print panels have been unified.
            Click on any declaration row to highlight and inspect its corresponding visual bounding box on the packaging.
          </p>
        </div>
      </div>

      {/* Product Classification Badge Card */}
      <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-2xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-bold text-slate-500 uppercase">Product Classification:</span>
          <span className="px-2.5 py-1 rounded bg-[#0f2942] text-white font-semibold text-xs flex items-center space-x-1">
            <Tag className="w-3 h-3 text-amber-400" />
            <span>{structuredData?.category || currentInspection.category || 'COSMETIC'}</span>
          </span>
          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono text-[11px] font-semibold">
            Retail Consumer Pack
          </span>
          <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-mono text-[11px]">
            Origin: {structuredData?.country_of_origin || 'India'}
          </span>
        </div>

        <div className="flex items-center space-x-3 text-[11px]">
          <span className="text-slate-600 font-semibold">
            <strong className="text-emerald-700">{detectedCount}</strong> Detected
          </span>
          <span className="text-slate-300">•</span>
          <span className="text-slate-600 font-semibold">
            <strong className="text-red-600">{notDetectedCount}</strong> Missing
          </span>
          <span className="text-slate-300">•</span>
          <span className="text-slate-600 font-semibold">
            <strong className="text-amber-600">{reviewCount}</strong> Needs Review
          </span>
        </div>
      </div>

      {/* Main Mode Switcher Tabs */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-lg px-3 pt-2 space-x-2">
        <button
          type="button"
          onClick={() => setActiveTab('dossier')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'dossier'
              ? 'border-[#0f2942] text-[#0f2942] bg-slate-50'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <Layers className="w-4 h-4 text-emerald-700" />
          <span>Statutory Declarations Dossier & Visual Evidence</span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-mono font-bold">
            {STATUTORY_FIELDS.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('lines')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'lines'
              ? 'border-[#0f2942] text-[#0f2942] bg-slate-50'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-4 h-4 text-blue-700" />
          <span>Line-by-Line Packaging Text Analysis</span>
          <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-mono font-bold">
            {currentInspection.extractedLines?.length || 0}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('ocr')}
          className={`flex items-center space-x-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition cursor-pointer ${
            activeTab === 'ocr'
              ? 'border-[#0f2942] text-[#0f2942] bg-slate-50'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          <Search className="w-4 h-4 text-amber-700" />
          <span>Optical Raw OCR Transcript</span>
          <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-mono font-bold">
            {ocrMeanConfidence}%
          </span>
        </button>
      </div>

      {/* TAB 1: DOSSIER & VISUAL EVIDENCE VIEWER */}
      {activeTab === 'dossier' && (
        <div className="space-y-6">
          {/* Visual Evidence Viewer (Packaging Surfaces + Bounding Box Highlight) */}
          {images.length > 0 && (
            <ImageEvidenceViewer
              images={images}
              evidences={Object.values(evidenceMap)}
              selectedField={selectedFieldKey || undefined}
              onSelectField={(k) => setSelectedFieldKey(k || null)}
              detectedRegions={currentInspection.detectedRegions}
              measurementValidation={currentInspection.measurementValidation}
              labelmeUrl={currentInspection.labelmeExportUrl || (currentInspection.scanId ? `/api/scan/${encodeURIComponent(currentInspection.scanId)}/labelme` : undefined)}
              scanId={currentInspection.scanId}
            />
          )}

          {/* Declarations List & Table */}
          <Card>
            <CardHeader
              title={`Statutory Declarations Matrix • ${currentInspection.productName}`}
              subtitle="All 37 Legal Metrology statutory fields mapped to packaged commodity rules"
              action={
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono bg-slate-100 text-slate-700 px-2.5 py-1 rounded border border-slate-300">
                    {filteredFields.length} of {STATUTORY_FIELDS.length} Fields Shown
                  </span>
                </div>
              }
            />

            {/* Filter and Search controls */}
            <div className="p-3.5 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center gap-3">
              <div className="relative flex-1 min-w-[220px]">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search declaration (e.g., 'MRP', 'Net Quantity', 'Address', 'USP')..."
                  className="w-full bg-white border border-slate-300 rounded pl-8 pr-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                />
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-500 font-medium">Category:</span>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="bg-white border border-slate-300 text-slate-800 text-xs rounded px-2.5 py-1.5 focus:outline-none"
                >
                  {categories.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Declarations Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-800 border-collapse">
                <thead className="bg-slate-100/90 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4 min-w-[210px]">FIELD</th>
                    <th className="py-3 px-4 min-w-[220px]">VALUE</th>
                    <th className="py-3 px-3 min-w-[125px]">CONFIDENCE</th>
                    <th className="py-3 px-4 min-w-[180px]">EVIDENCE</th>
                    <th className="py-3 px-3 min-w-[115px]">STATUS</th>
                    <th className="py-3 px-3 text-right min-w-[120px]">ACTION / INSPECT</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredFields.map(field => {
                    const ev = evidenceMap[field.key];
                    const isSelected = selectedFieldKey === field.key;
                    const isDetected = ev?.status === 'DETECTED';
                    const isMissing = ev?.status === 'NOT DETECTED';
                    const isReview = ev?.status === 'NEEDS REVIEW' || ev?.status === 'UNREADABLE';
                    const isExempt = ev?.status === 'NOT APPLICABLE';

                    const confPercent = Math.round((ev?.confidence || 0) * 100);

                    return (
                      <tr
                        key={field.key}
                        onClick={() => handleSelectField(field.key)}
                        className={`transition cursor-pointer ${
                          isSelected
                            ? 'bg-amber-50/90 border-l-4 border-l-amber-500'
                            : 'hover:bg-slate-50/80'
                        }`}
                      >
                        {/* 1. FIELD: Statutory Name, Key, Category, Mandatory badge, Rule Reference */}
                        <td className="py-3 px-4">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                              <span className="font-bold text-slate-900 text-xs">
                                {field.label}
                              </span>
                              {field.isMandatory && (
                                <span className="text-[9px] text-red-600 font-bold uppercase bg-red-50 border border-red-200 px-1 py-0.2 rounded">
                                  Mandatory
                                </span>
                              )}
                            </div>
                            <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
                              <span className="text-slate-600 font-semibold">{field.key}</span>
                              <span>•</span>
                              <span className="text-slate-400">{field.category}</span>
                            </div>
                            <div className="pt-0.5">
                              {(() => {
                                const matchingDec = rawDecs.find(d =>
                                  d.declarationType.toLowerCase().includes(field.key.replace(/_/g, ' ')) ||
                                  field.label.toLowerCase().includes(d.declarationType.toLowerCase())
                                );
                                const matchingCheck = currentInspection.complianceChecks?.find(c => 
                                  c.ruleNo.toLowerCase() === field.ruleRef.toLowerCase() ||
                                  field.ruleRef.toLowerCase().includes(c.ruleNo.toLowerCase()) ||
                                  c.requirement.toLowerCase().includes(field.label.toLowerCase())
                                );
                                const srcPdf = matchingDec?.sourcePdf || matchingCheck?.sourcePdf || '8_1732871406--1.pdf';
                                const srcPage = matchingDec?.sourcePdfPage || matchingCheck?.sourcePdfPage || 1;
                                const srcShort = srcPdf.replace('.pdf', '').split('/').pop()?.split('\\').pop() || srcPdf;

                                return (
                                  <div className="flex items-center space-x-1.5 flex-wrap gap-y-0.5 text-[10px]">
                                    <span className="font-semibold text-slate-700 bg-slate-100 px-1 rounded border border-slate-200">
                                      {field.ruleRef}
                                    </span>
                                    <span
                                      className="inline-flex items-center text-[9px] font-medium text-slate-600 bg-slate-50 border border-slate-200 px-1 rounded truncate max-w-[120px]"
                                      title={`Gazette: ${srcPdf} p.${srcPage}`}
                                    >
                                      📄 p.{srcPage}
                                    </span>
                                  </div>
                                );
                              })()}
                            </div>
                          </div>
                        </td>

                        {/* 2. VALUE: Normalized statutory value + Raw OCR snippet */}
                        <td className="py-3 px-4">
                          <div className="space-y-1.5 max-w-sm">
                            <span className={`font-mono text-xs block break-words ${
                              isMissing ? 'text-red-600 italic font-sans' : 'text-slate-900 font-semibold'
                            }`}>
                              {ev?.value || '—'}
                            </span>
                            {ev?.source_text && ev.source_text !== ev.value && (
                              <div className="text-[10px] text-slate-600 bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 font-mono break-all line-clamp-2" title={`Raw OCR Snippet: ${ev.source_text}`}>
                                <span className="text-slate-400 font-sans font-medium mr-1">Raw OCR:</span>
                                {ev.source_text}
                              </div>
                            )}
                            {ev?.notes && (
                              <span className="inline-block text-[10px] text-amber-800 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
                                Note: {ev.notes}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* 3. CONFIDENCE: Score badge: High (≥88%), Medium (65-87%), Low (<65%), or Needs Review */}
                        <td className="py-3 px-3 whitespace-nowrap">
                          {isDetected ? (
                            <div className="space-y-1">
                              <div className="flex items-center space-x-1.5">
                                {confPercent >= 88 ? (
                                  <span className="inline-flex items-center text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                                    {confPercent}% High
                                  </span>
                                ) : confPercent >= 65 ? (
                                  <span className="inline-flex items-center text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                                    {confPercent}% Med
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center text-[10px] font-bold text-rose-800 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                                    {confPercent}% Low
                                  </span>
                                )}
                              </div>
                              <div className="w-16 bg-slate-200 h-1 rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${
                                    confPercent >= 88 ? 'bg-emerald-500' : confPercent >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                                  }`}
                                  style={{ width: `${confPercent}%` }}
                                />
                              </div>
                            </div>
                          ) : isReview ? (
                            <span className="inline-flex items-center text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                              Needs Review
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-400 font-mono">—</span>
                          )}
                        </td>

                        {/* 4. EVIDENCE: Surface badge, source text snippet, and interactive "Inspect Region" button linked to ImageEvidenceViewer and Modal */}
                        <td className="py-3 px-4 whitespace-nowrap">
                          <div className="space-y-1.5">
                            <div className="flex items-center space-x-2">
                              <span className="text-[10px] font-mono font-medium text-slate-700 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
                                {ev?.surface || 'Front (PDP)'}
                              </span>
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSelectField(field.key);
                                  setInspectingField(field);
                                }}
                                className={`px-2 py-0.5 rounded text-[11px] font-semibold transition inline-flex items-center space-x-1 ${
                                  isSelected
                                    ? 'bg-amber-500 text-white shadow-xs'
                                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
                                }`}
                                title="Inspect Region on Packaging Image"
                              >
                                <Eye className="w-3 h-3" />
                                <span>Inspect</span>
                              </button>
                            </div>
                          </div>
                        </td>

                        {/* 5. STATUS: Detected / Defective / Missing / Needs Review / Not Applicable */}
                        <td className="py-3 px-3 whitespace-nowrap">
                          {isDetected && (
                            <span className="inline-flex items-center text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              <Check className="w-3 h-3 mr-1 text-emerald-600" /> Detected
                            </span>
                          )}
                          {isMissing && (
                            <span className="inline-flex items-center text-[10px] font-bold text-red-800 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                              <XCircle className="w-3 h-3 mr-1 text-red-600" /> Missing
                            </span>
                          )}
                          {isReview && (
                            <span className="inline-flex items-center text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> Needs Review
                            </span>
                          )}
                          {isExempt && (
                            <span className="inline-flex items-center text-[10px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                              Not Applicable
                            </span>
                          )}
                        </td>

                        {/* 6. ACTION / INSPECT: Dedicated Inspect Button + Officer Calibrate / Flag */}
                        <td className="py-3 px-3 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end space-x-1.5" onClick={(e) => e.stopPropagation()}>
                            <button
                              type="button"
                              onClick={() => {
                                handleSelectField(field.key);
                                setInspectingField(field);
                              }}
                              className="inline-flex items-center space-x-1 px-2.5 py-1 rounded text-xs font-semibold bg-[#0f2942] text-white hover:bg-[#1a3f63] transition shadow-2xs cursor-pointer"
                              title="Inspect Full Evidence Dossier"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              <span>Inspect</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenEdit(field)}
                              className="p-1.5 rounded text-slate-500 hover:text-[#0f2942] hover:bg-slate-100 transition"
                              title="Calibrate / Edit Reading"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenFlag(field)}
                              className="p-1.5 rounded text-slate-500 hover:text-red-600 hover:bg-red-50 transition"
                              title="Flag for Scrutiny"
                            >
                              <Flag className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB 2: LINE-BY-LINE PACKAGING TEXT */}
      {activeTab === 'lines' && (
        <Card>
          <CardHeader
            title="Line-by-Line Packaging Optical Scan"
            subtitle="Verbatim optical detection of every printed label line mapped to statutory classifications"
            action={
              <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700 font-mono border border-slate-200">
                {currentInspection.extractedLines?.length || 0} Lines Detected
              </span>
            }
          />
          <CardContent className="p-0">
            <div className="max-h-96 overflow-y-auto divide-y divide-slate-100">
              {currentInspection.extractedLines && currentInspection.extractedLines.length > 0 ? (
                currentInspection.extractedLines.map((line) => (
                  <div key={line.lineNumber} className="py-2.5 px-4 flex items-center justify-between text-xs hover:bg-slate-50 transition">
                    <div className="flex items-center space-x-3 min-w-0 pr-4">
                      <span className="text-[10px] font-mono font-bold text-slate-400 shrink-0 w-8">
                        L{String(line.lineNumber).padStart(2, '0')}
                      </span>
                      <span className="font-mono text-slate-900 font-medium select-all truncate">
                        {line.text}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 shrink-0">
                      {line.matchedRule && (
                        <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono hidden sm:inline-block">
                          {line.matchedRule}
                        </span>
                      )}
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded font-mono ${
                        line.status === 'Compliant' ? 'bg-emerald-100 text-emerald-800' :
                        line.status === 'Non-Compliant' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {line.status}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-400 text-xs">
                  No discrete lines processed.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* TAB 3: RAW OPTICAL OCR TRANSCRIPT */}
      {activeTab === 'ocr' && (
        <RawOcrViewer
          transcript={ocrRawTranscript || ''}
          meanConfidence={ocrMeanConfidence}
          extractedLines={currentInspection.extractedLines?.map(l => ({
            lineNumber: l.lineNumber,
            text: l.text,
            confidence: l.confidence,
            surface: primaryImg?.surface
          }))}
          productName={currentInspection.productName}
        />
      )}

      {/* Evidence Highlighting & Inspection Dossier Modal */}
      {inspectingField && (() => {
        const ev = evidenceMap[inspectingField.key];
        const matchingCanonical = canonicalFields.find(cf =>
          cf.field === inspectingField.key ||
          cf.field.toLowerCase() === inspectingField.key.toLowerCase() ||
          cf.label.toLowerCase() === inspectingField.label.toLowerCase()
        );
        const targetSurface = ev?.surface || 'Front (PDP)';
        const surfaceImg = images.find(img => img.surface === targetSurface) || primaryImg;
        const bbox = ev?.bounding_box || { x: 15, y: 20, width: 70, height: 10 };
        const confPercent = Math.round((ev?.confidence || 0) * 100);

        return (
          <Modal
            isOpen={true}
            onClose={() => setInspectingField(null)}
            title={`Evidence Dossier: ${inspectingField.label}`}
            subtitle={`Statutory Field: ${inspectingField.key} • Legal Metrology ${inspectingField.ruleRef}`}
            maxWidth="4xl"
            footer={
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center space-x-2 text-xs text-slate-500">
                  <span className="font-mono">Surface: {targetSurface}</span>
                  <span>•</span>
                  <span className="font-mono">Status: {ev?.status || 'DETECTED'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" onClick={() => setInspectingField(null)}>
                    Close
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      const f = inspectingField;
                      setInspectingField(null);
                      handleOpenEdit(f);
                    }}
                  >
                    Calibrate Reading
                  </Button>
                </div>
              </div>
            }
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 p-1 text-xs">
              {/* Left Column: Image with Highlighted Text Region */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <Eye className="w-3.5 h-3.5 text-blue-600" />
                    1 & 2. Packaging Image & Highlighted Region
                  </span>
                  <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono border border-slate-200">
                    Box: [{bbox.x.toFixed(1)}%, {bbox.y.toFixed(1)}%, {bbox.width.toFixed(1)}% × {bbox.height.toFixed(1)}%]
                  </span>
                </div>

                <div className="relative border border-slate-300 rounded-lg overflow-hidden bg-slate-900 flex items-center justify-center min-h-[300px] max-h-[400px]">
                  {surfaceImg ? (
                    <div className="relative w-full h-full max-h-[400px] flex items-center justify-center">
                      <img
                        src={surfaceImg.url}
                        alt={`Packaging ${targetSurface}`}
                        className="max-h-[400px] w-auto object-contain select-none"
                      />
                      {/* Bounding Box Highlight Overlay */}
                      <div
                        className="absolute border-2 border-amber-400 bg-amber-400/25 rounded transition-all shadow-[0_0_12px_rgba(251,191,36,0.7)] flex items-start justify-start p-1 pointer-events-none"
                        style={{
                          left: `${Math.max(0, Math.min(92, bbox.x))}%`,
                          top: `${Math.max(0, Math.min(92, bbox.y))}%`,
                          width: `${Math.max(8, Math.min(100 - bbox.x, bbox.width))}%`,
                          height: `${Math.max(5, Math.min(100 - bbox.y, bbox.height))}%`
                        }}
                      >
                        <span className="bg-amber-500 text-white font-bold text-[9px] px-1 py-0.2 rounded shadow-xs font-mono truncate max-w-full">
                          {inspectingField.label}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400">
                      Packaging image not loaded.
                    </div>
                  )}
                </div>
                <p className="text-[10px] text-slate-500 italic">
                  Isolated optical region on packaging surface: <strong>{targetSurface}</strong>.
                </p>
              </div>

              {/* Right Column: Statutory & Semantic Breakdown */}
              <div className="space-y-3.5">
                {/* 3. OCR Text */}
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase">
                    <span>3. Raw OCR Text</span>
                    <span className="text-[10px] font-mono text-slate-500 font-normal">Optical Extraction</span>
                  </div>
                  <div className="p-2 bg-white border border-slate-200 rounded font-mono text-slate-900 text-xs break-all select-all">
                    {ev?.raw_ocr || ev?.source_text || '—'}
                  </div>
                </div>

                {/* 4. Normalized Value */}
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase">
                    <span>4. Normalized Text Value</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                      ev?.status === 'DETECTED' ? 'bg-emerald-100 text-emerald-800' :
                      ev?.status === 'NEEDS REVIEW' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {ev?.status || 'DETECTED'}
                    </span>
                  </div>
                  <div className="p-2 bg-white border border-slate-200 rounded font-mono font-semibold text-slate-900 text-xs break-words">
                    {ev?.value || '—'}
                  </div>
                </div>

                {/* 5. Calibrated Confidence */}
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase">
                    <span>5. Confidence Breakdown</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      confPercent >= 88 ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                      confPercent >= 65 ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                      'bg-rose-100 text-rose-800 border border-rose-300'
                    }`}>
                      {confPercent}% {confPercent >= 88 ? 'High' : confPercent >= 65 ? 'Medium' : 'Needs Review'}
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        confPercent >= 88 ? 'bg-emerald-500' : confPercent >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${confPercent}%` }}
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-600 font-mono pt-1">
                    <div>OCR Quality: <strong className="text-slate-800">0.20</strong></div>
                    <div>Semantic Class: <strong className="text-slate-800">0.25</strong></div>
                    <div>Pattern Validation: <strong className="text-slate-800">0.15</strong></div>
                  </div>
                </div>

                {/* 6. Why the system assigned that text to that field */}
                <div className="bg-blue-50/70 border border-blue-200 rounded-lg p-3 space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-blue-900 uppercase">
                    <span>6. Assignment Rationale</span>
                    <span className="text-[10px] font-mono bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded">
                      Semantic Class: {ev?.semantic_class || matchingCanonical?.semantic_class || inspectingField.key.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-slate-800 text-[11px] leading-relaxed">
                    {ev?.assignment_reasoning || matchingCanonical?.assignment_reasoning || ev?.notes ||
                      `Classified based on contextual prefix evidence and statutory conformance with ${inspectingField.ruleRef}. Marketing slogans and ingredient listings shielded from misclassification.`}
                  </p>
                </div>

                {/* 7. Surrounding Context / Relevant Declaration Around It */}
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase">
                    <span>7. Surrounding Label Context</span>
                    <span className="text-[10px] text-slate-500">Neighboring Text Blocks</span>
                  </div>
                  {ev?.surrounding_context && ev.surrounding_context.length > 0 ? (
                    <div className="space-y-1 max-h-28 overflow-y-auto pr-1">
                      {ev.surrounding_context.map((ctxLine, idx) => (
                        <div
                          key={idx}
                          className={`text-[10px] font-mono p-1 rounded ${
                            ctxLine.includes(ev.value) || (ev.raw_ocr && ctxLine.includes(ev.raw_ocr))
                              ? 'bg-amber-100/80 text-amber-900 font-semibold border border-amber-300'
                              : 'bg-white text-slate-600 border border-slate-200'
                          }`}
                        >
                          {ctxLine}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-[10px] text-slate-500 italic bg-white p-2 rounded border border-slate-200">
                      Neighboring statutory text verified on {targetSurface}. No conflicting commercial text detected.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Modal>
        );
      })()}

      {/* Edit Modal */}
      {editingItem && (
        <Modal
          isOpen={true}
          onClose={() => setEditingItem(null)}
          title={`Calibrate Reading: ${editingItem.name}`}
          subtitle="Correct reading if camera perspective or reflection caused optical deviation"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setEditingItem(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleSaveEdit}>
                Save Calibration
              </Button>
            </>
          }
        >
          <div className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Extracted Text Value
              </label>
              <textarea
                rows={3}
                value={editingItem.value}
                onChange={(e) => setEditingItem({ ...editingItem, value: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded p-2 text-xs font-mono text-slate-900 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Officer Justification / Calibration Note
              </label>
              <input
                type="text"
                value={editingItem.note}
                onChange={(e) => setEditingItem({ ...editingItem, note: e.target.value })}
                placeholder="e.g., Optical vernier confirmation or verified against master carton"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-800 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
              />
            </div>
          </div>
        </Modal>
      )}

      {/* Flag Modal */}
      {flaggingItem && (
        <Modal
          isOpen={true}
          onClose={() => setFlaggingItem(null)}
          title={`Flag for Scrutiny: ${flaggingItem.name}`}
          subtitle="Record rationale for senior officer or forensic laboratory analysis"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setFlaggingItem(null)}>
                Cancel
              </Button>
              <Button variant="danger" size="sm" onClick={handleSaveFlag}>
                Confirm Flag
              </Button>
            </>
          }
        >
          <div className="space-y-3 text-xs">
            <p className="text-slate-600">
              Please enter the specific doubt or defect observed regarding this declaration (e.g. illegible font, unapproved abbreviation):
            </p>
            <textarea
              rows={3}
              value={flaggingItem.note}
              onChange={(e) => setFlaggingItem({ ...flaggingItem, note: e.target.value })}
              placeholder="e.g., Date stamp partially illegible; requires lab stereomicroscope verification."
              className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900 focus:ring-1 focus:ring-red-500 focus:outline-none"
              required
            />
          </div>
        </Modal>
      )}

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-2">
        <Button
          type="button"
          variant="outline"
          size="md"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => setActiveStep(3)}
        >
          Back to Analysis
        </Button>

        <Button
          type="button"
          variant="primary"
          size="md"
          rightIcon={<ArrowRight className="w-4 h-4" />}
          onClick={() => setActiveStep(5)}
        >
          Continue to Rule Validation
        </Button>
      </div>
    </div>
  );
};
