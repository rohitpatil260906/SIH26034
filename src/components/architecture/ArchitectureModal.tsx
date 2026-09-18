import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import {
  Cpu,
  Layers,
  Database,
  FileCheck,
  Server,
  Code,
  Shield,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Activity
} from 'lucide-react';

interface ArchitectureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ArchitectureModal: React.FC<ArchitectureModalProps> = ({ isOpen, onClose }) => {
  const [activeStage, setActiveStage] = useState<'stage1' | 'stage2' | 'stage3' | 'stage4' | 'data'>('stage2');

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="LM-COMPASS (VidhiCheck) — Technical Architecture"
      subtitle="4-Stage Unified Computer Vision, Multilingual OCR & Deterministic Legal Metrology Compliance Pipeline"
      maxWidth="4xl"
      footer={
        <div className="flex items-center justify-between w-full">
          <span className="text-[11px] text-slate-500 font-mono">
            Architecture Version 2.4 • Smart India Hackathon PS 26034
          </span>
          <Button variant="primary" size="sm" onClick={onClose}>
            Close Pipeline Architecture
          </Button>
        </div>
      }
    >
      <div className="space-y-6 text-xs text-slate-800">
        {/* Top Stages Stepper Tabs */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 border-b border-slate-200 pb-3">
          <button
            onClick={() => setActiveStage('stage1')}
            className={`p-2.5 rounded-md text-left transition border ${
              activeStage === 'stage1'
                ? 'bg-[#0f2942] text-white border-[#0f2942] shadow-xs'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <span className="text-[9px] uppercase font-mono block opacity-80">Stage 1</span>
            <span className="font-bold text-xs block truncate">Unified Acquisition</span>
            <span className="text-[10px] block opacity-70 truncate">Web, Camera & NGINX</span>
          </button>

          <button
            onClick={() => setActiveStage('stage2')}
            className={`p-2.5 rounded-md text-left transition border ${
              activeStage === 'stage2'
                ? 'bg-[#0f2942] text-white border-[#0f2942] shadow-xs'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <span className="text-[9px] uppercase font-mono block opacity-80">Stage 2</span>
            <span className="font-bold text-xs block truncate">Computer Vision</span>
            <span className="text-[10px] block opacity-70 truncate">OpenCV, YOLOv8, scikit</span>
          </button>

          <button
            onClick={() => setActiveStage('stage3')}
            className={`p-2.5 rounded-md text-left transition border ${
              activeStage === 'stage3'
                ? 'bg-[#0f2942] text-white border-[#0f2942] shadow-xs'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <span className="text-[9px] uppercase font-mono block opacity-80">Stage 3</span>
            <span className="font-bold text-xs block truncate">OCR & Rules Engine</span>
            <span className="text-[10px] block opacity-70 truncate">PaddleOCR, spaCy, LMPC</span>
          </button>

          <button
            onClick={() => setActiveStage('stage4')}
            className={`p-2.5 rounded-md text-left transition border ${
              activeStage === 'stage4'
                ? 'bg-[#0f2942] text-white border-[#0f2942] shadow-xs'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <span className="text-[9px] uppercase font-mono block opacity-80">Stage 4</span>
            <span className="font-bold text-xs block truncate">Reporting & Output</span>
            <span className="text-[10px] block opacity-70 truncate">Legal Notices & Challan</span>
          </button>

          <button
            onClick={() => setActiveStage('data')}
            className={`p-2.5 rounded-md text-left transition border ${
              activeStage === 'data'
                ? 'bg-[#0f2942] text-white border-[#0f2942] shadow-xs'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <span className="text-[9px] uppercase font-mono block opacity-80">Data Layer</span>
            <span className="font-bold text-xs block truncate">Persistence & Queue</span>
            <span className="text-[10px] block opacity-70 truncate">PostgreSQL, Redis, Elastic</span>
          </button>
        </div>

        {/* Dynamic Detail Content per Stage */}
        {activeStage === 'stage1' && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-bold text-slate-900 flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600 mr-2"></span>
                STAGE 1: UNIFIED ACQUISITION BRANCH
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Manages multi-modal image ingestion from field enforcement officers, mobile handheld terminals, and retail web listings into a high-throughput secure gateway.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Web Portal (Inspector & Official)</span>
                <p className="text-[11px] text-slate-600">• React.js + TypeScript frontend</p>
                <p className="text-[11px] text-slate-600">• Tailwind CSS executive styling</p>
                <p className="text-[11px] text-slate-600">• Responsive UI (Desktop, Tablet, Mobile)</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Mobile Field Node</span>
                <p className="text-[11px] text-slate-600">• React Native / PWA WebRTC Camera</p>
                <p className="text-[11px] text-slate-600">• High-res optical label capture</p>
                <p className="text-[11px] text-slate-600">• Offline caching for rural mandis</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Data Ingestion Gateway (NGINX)</span>
                <p className="text-[11px] text-slate-600">• Request routing & reverse proxy</p>
                <p className="text-[11px] text-slate-600">• Rate limiting & 25MB payload parsing</p>
                <p className="text-[11px] text-slate-600">• TLS 1.3 encryption for evidence</p>
              </div>
            </div>
          </div>
        )}

        {activeStage === 'stage2' && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-bold text-slate-900 flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 mr-2"></span>
                STAGE 2: COMPUTER VISION BRANCH (ANALYSIS)
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Applies advanced computer vision for packaging segmentation, glare correction, Region of Interest (ROI) detection, and optical pixel-to-mm numeral font measurement.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-emerald-800 block">Image Preprocessing</span>
                <p className="text-[10px] font-mono text-slate-500">OpenCV • PIL / Pillow</p>
                <p className="text-[11px] text-slate-600">• Perspective deskew & rotation correction</p>
                <p className="text-[11px] text-slate-600">• Non-local means denoising on glossy pouches</p>
                <p className="text-[11px] text-slate-600">• Contrast stretching & illumination leveling</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-emerald-800 block">Object Detection & Segmentation</span>
                <p className="text-[10px] font-mono text-slate-500">PyTorch • YOLOv8 • LabelImg</p>
                <p className="text-[11px] text-slate-600">• Principal Display Panel (PDP) isolation</p>
                <p className="text-[11px] text-slate-600">• Bounding box coordinates generation</p>
                <p className="text-[11px] text-slate-600">• MRP stamp, barcode & FSSAI seal cropping</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-emerald-800 block">Measurement Validation</span>
                <p className="text-[10px] font-mono text-slate-500">NumPy • scikit-image</p>
                <p className="text-[11px] text-slate-600">• Optical dimension calibration (DPI matrix)</p>
                <p className="text-[11px] text-slate-600">• Pixel-to-mm conversion for font height</p>
                <p className="text-[11px] text-slate-600">• Rule 7 & 8 minimum numeral height test</p>
              </div>
            </div>
          </div>
        )}

        {activeStage === 'stage3' && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-bold text-slate-900 flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-600 mr-2"></span>
                STAGE 3: OCR & RULES ENGINE BRANCH (TEXT & LOGIC)
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Extracts multilingual text across Indian regional scripts, normalizes syntax, verifies manufacturer credentials against the GST Portal, and assesses rules deterministically.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-amber-900 block">Multilingual OCR Engine</span>
                <p className="text-[10px] font-mono text-slate-500">Tesseract • EasyOCR • PaddleOCR</p>
                <p className="text-[11px] text-slate-600">• English + 10 Regional Indian Languages</p>
                <p className="text-[11px] text-slate-600">• High accuracy character extraction</p>
                <p className="text-[11px] text-slate-600">• Confidence scoring matrix per declaration</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-amber-900 block">Text Post-Processing</span>
                <p className="text-[10px] font-mono text-slate-500">NLTK • spaCy NLP</p>
                <p className="text-[11px] text-slate-600">• Domain spell correction for packaging</p>
                <p className="text-[11px] text-slate-600">• Regex token extraction for dates & prices</p>
                <p className="text-[11px] text-slate-600">• Mandatory phrase matching ("incl. of taxes")</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-amber-900 block">Deterministic Rules Engine</span>
                <p className="text-[10px] font-mono text-slate-500">Python Rule Engine • JSON Logic</p>
                <p className="text-[11px] text-slate-600">• Legal Metrology Rules, 2011 clauses</p>
                <p className="text-[11px] text-slate-600">• PASS / FAIL / WARN outputs</p>
                <p className="text-[11px] text-slate-600">• External GST Portal API verification</p>
              </div>
            </div>
          </div>
        )}

        {activeStage === 'stage4' && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-bold text-slate-900 flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-red-600 mr-2"></span>
                STAGE 4: REPORTING & COMPLIANCE BRANCH (OUTPUT)
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Transforms technical findings into official legal documentation, Section 36 statutory notices, compounding challans, and centralized audit logging.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Compliance Reporting</span>
                <p className="text-[10px] font-mono text-slate-500">ReportLab • Puppeteer • python-docx</p>
                <p className="text-[11px] text-slate-600">• Government format inspection reports</p>
                <p className="text-[11px] text-slate-600">• Digital QR hash verification code</p>
                <p className="text-[11px] text-slate-600">• Print-ready standard A4 portrait styling</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Legal Notice Generator</span>
                <p className="text-[10px] font-mono text-slate-500">Statutory Notice Templates</p>
                <p className="text-[11px] text-slate-600">• Auto-fill case particulars & evidence</p>
                <p className="text-[11px] text-slate-600">• Section 36 compounding demand</p>
                <p className="text-[11px] text-slate-600">• Issue & dispatch to manufacturer</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-slate-900 block">Audit & Compliance Logging</span>
                <p className="text-[10px] font-mono text-slate-500">Elasticsearch • Splunk</p>
                <p className="text-[11px] text-slate-600">• Centralized immutable audit trails</p>
                <p className="text-[11px] text-slate-600">• Real-time officer alert monitoring</p>
                <p className="text-[11px] text-slate-600">• Indian Evidence Act compliance</p>
              </div>
            </div>
          </div>
        )}

        {activeStage === 'data' && (
          <div className="space-y-4 animate-in fade-in duration-150">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
              <h4 className="text-sm font-bold text-slate-900 flex items-center">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-600 mr-2"></span>
                DATA LAYER & CROSS-CUTTING INFRASTRUCTURE
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                High-availability relational storage, full-text commodity search indexing, in-memory caching, and containerized deployment.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-purple-900 block">Database (PostgreSQL)</span>
                <p className="text-[11px] text-slate-600">• Users, Roles, Credentials (RBAC)</p>
                <p className="text-[11px] text-slate-600">• Inspection dockets & evidence paths</p>
                <p className="text-[11px] text-slate-600">• Legal rule versions & amendment history</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-purple-900 block">Search & Index (Elasticsearch)</span>
                <p className="text-[11px] text-slate-600">• Rapid GTIN / Barcode lookups</p>
                <p className="text-[11px] text-slate-600">• Manufacturer non-compliance records</p>
                <p className="text-[11px] text-slate-600">• Fuzzy matching on commodity names</p>
              </div>

              <div className="p-3 border border-slate-200 rounded-md bg-white space-y-1">
                <span className="font-bold text-purple-900 block">Cache & Queue (Redis)</span>
                <p className="text-[11px] text-slate-600">• Inspection session caching</p>
                <p className="text-[11px] text-slate-600">• Celery / background OCR job queue</p>
                <p className="text-[11px] text-slate-600">• Real-time dashboard KPI cache</p>
              </div>
            </div>
          </div>
        )}

        {/* Cross-cutting Tools Bar */}
        <div className="p-3 bg-slate-900 text-slate-300 rounded-lg flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span className="text-white font-bold">CROSS-CUTTING STACK:</span>
            <span>Docker • Kubernetes • Prometheus • Grafana • OAuth2/OIDC • NIC Cloud</span>
          </div>
          <span className="text-emerald-400 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block mr-1"></span>
            All 4 Branches Connected
          </span>
        </div>
      </div>
    </Modal>
  );
};
