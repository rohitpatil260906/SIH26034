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

  const [editingItem, setEditingItem] = useState<{ id: string; name: string; value: string; note: string } | null>(null);
  const [flaggingItem, setFlaggingItem] = useState<{ id: string; name: string; note: string } | null>(null);

  if (!currentInspection) return null;

  const images = currentInspection.images || [];
  const primaryImg = images[0];
  const structuredData = currentInspection.structuredData;
  const rawDecs = currentInspection.declarations || [];

  // Build evidence map combining structured data, declarations, and canonical fields
  const evidenceMap = useMemo(() => {
    const map: Record<string, FieldEvidence> = {};

    STATUTORY_FIELDS.forEach(field => {
      const val = field.getValue(structuredData, rawDecs);
      const isDetected = Boolean(val && val.trim() !== '');

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

      // Check if existing declaration has specific bbox
      const matchingDec = rawDecs.find(d =>
        d.declarationType.toLowerCase().includes(field.key.replace(/_/g, ' ')) ||
        field.label.toLowerCase().includes(d.declarationType.toLowerCase())
      );
      if (matchingDec?.boundingBox) {
        bbox = { ...matchingDec.boundingBox, label: field.label };
      }

      let status: DeclarationCheckStatus = isDetected ? 'DETECTED' : field.defaultStatus;
      if (!isDetected && field.isMandatory) {
        status = 'NOT DETECTED';
      }

      map[field.key] = {
        field_name: field.key,
        label: field.label,
        value: isDetected ? val : 'Not Detected on Package',
        confidence: isDetected ? 0.98 : 0.0,
        source_text: isDetected ? val : '',
        image_id: primaryImg?.id || 'img-primary',
        surface: matchingDec?.surface || primaryImg?.surface || 'Front (PDP)',
        bounding_box: bbox,
        status: status,
        notes: matchingDec?.correctionNotes
      };
    });

    return map;
  }, [structuredData, rawDecs, primaryImg]);

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
                <thead className="bg-slate-100/80 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Statutory Field</th>
                    <th className="py-2.5 px-4">Detected Value on Packaging</th>
                    <th className="py-2.5 px-4">Legal Metrology Rule</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4">Surface</th>
                    <th className="py-2.5 px-4 text-center">Visual Evidence</th>
                    <th className="py-2.5 px-4 text-right">Officer Calibration</th>
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
                        {/* Field Name & Category */}
                        <td className="py-3 px-4">
                          <div className="space-y-0.5">
                            <span className="font-semibold text-slate-900 block flex items-center">
                              {field.label}
                              {field.isMandatory && (
                                <span className="ml-1.5 text-[9px] text-red-600 font-bold uppercase bg-red-50 border border-red-200 px-1 rounded">
                                  Mandatory
                                </span>
                              )}
                            </span>
                            <span className="text-[10px] text-slate-400 block font-mono">
                              {field.category}
                            </span>
                          </div>
                        </td>

                        {/* Value */}
                        <td className="py-3 px-4 max-w-xs">
                          <div className="space-y-1">
                            <span className={`font-mono text-xs block break-words ${
                              isMissing ? 'text-red-600 italic font-sans' : 'text-slate-900 font-semibold'
                            }`}>
                              {ev?.value || '—'}
                            </span>
                            {ev?.notes && (
                              <span className="inline-block text-[10px] text-amber-800 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
                                Note: {ev.notes}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Rule Ref */}
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-600 whitespace-nowrap">
                          {field.ruleRef}
                        </td>

                        {/* Status Badge */}
                        <td className="py-3 px-4 whitespace-nowrap">
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

                        {/* Surface */}
                        <td className="py-3 px-4 text-[11px] font-mono text-slate-600 whitespace-nowrap">
                          {ev?.surface || 'Front (PDP)'}
                        </td>

                        {/* View Bounding Box button */}
                        <td className="py-3 px-4 text-center whitespace-nowrap">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSelectField(field.key);
                            }}
                            className={`px-2 py-1 rounded text-[11px] font-semibold transition flex items-center justify-center space-x-1 mx-auto ${
                              isSelected
                                ? 'bg-amber-500 text-white shadow-xs'
                                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                            }`}
                            title="Highlight on Packaging Image"
                          >
                            <Eye className="w-3 h-3" />
                            <span>{isSelected ? 'Viewing' : 'Inspect'}</span>
                          </button>
                        </td>

                        {/* Officer Calibration Actions */}
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end space-x-1" onClick={(e) => e.stopPropagation()}>
                            <button
                              type="button"
                              onClick={() => handleOpenEdit(field)}
                              className="p-1 rounded text-slate-500 hover:text-[#0f2942] hover:bg-slate-100 transition"
                              title="Calibrate / Edit Reading"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenFlag(field)}
                              className="p-1 rounded text-slate-500 hover:text-red-600 hover:bg-red-50 transition"
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
