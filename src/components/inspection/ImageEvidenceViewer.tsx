import React, { useState } from 'react';
import { InspectionImage, FieldEvidence, BoundingBox } from '../../types';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Crosshair,
  Maximize2,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Eye,
  Download,
  Ruler,
  Cpu,
  FileCode,
  Tag
} from 'lucide-react';

interface ImageEvidenceViewerProps {
  images: InspectionImage[];
  evidences: FieldEvidence[];
  selectedField?: string;
  onSelectField?: (fieldName: string) => void;
  detectedRegions?: any[];
  measurementValidation?: any;
  labelmeUrl?: string;
  scanId?: string;
  className?: string;
}

export const ImageEvidenceViewer: React.FC<ImageEvidenceViewerProps> = ({
  images,
  evidences,
  selectedField,
  onSelectField,
  detectedRegions = [],
  measurementValidation,
  labelmeUrl,
  scanId,
  className = ''
}) => {
  const [activeImageIndex, setActiveImageIndex] = useState<number>(0);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showBoxes, setShowBoxes] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'boxes' | 'regions'>('boxes');

  const activeImage = images[activeImageIndex] || images[0];

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.3, 3.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.3, 0.7));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const selectedEvidence = evidences.find((e) => e.field_name === selectedField);
  const selectedRegion = detectedRegions.find(
    (r) => r.category === selectedField || r.region_id === selectedField
  );

  const handleDownloadLabelMe = () => {
    if (labelmeUrl) {
      window.open(labelmeUrl, '_blank');
    } else if (scanId) {
      window.open(`/api/scan/${encodeURIComponent(scanId)}/labelme`, '_blank');
    }
  };

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col ${className}`}>
      {/* Viewer Header */}
      <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Crosshair className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Image Evidence & Region Inspector
          </span>
          {activeImage && (
            <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono border border-slate-700">
              {activeImage.surface} • {activeImage.name}
            </span>
          )}
          {scanId && (
            <span className="text-[10px] bg-indigo-950/80 text-indigo-300 px-2 py-0.5 rounded font-mono border border-indigo-800">
              Docket: {scanId}
            </span>
          )}
        </div>

        {/* Controls & Export */}
        <div className="flex items-center space-x-2">
          {/* Surface Switcher if multiple images exist */}
          {images.length > 1 && (
            <div className="flex items-center space-x-1.5">
              {images.map((img, idx) => (
                <button
                  key={img.id || idx}
                  type="button"
                  onClick={() => {
                    setActiveImageIndex(idx);
                    handleReset();
                  }}
                  className={`text-[11px] px-2.5 py-1 rounded font-medium transition cursor-pointer ${
                    activeImageIndex === idx
                      ? 'bg-emerald-600 text-white shadow-xs'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {img.surface}
                </button>
              ))}
            </div>
          )}

          {/* LabelMe Export Button */}
          {(labelmeUrl || scanId) && (
            <button
              type="button"
              onClick={handleDownloadLabelMe}
              className="flex items-center space-x-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs rounded border border-emerald-500/30 transition cursor-pointer font-medium"
              title="Download LabelMe v5.2.1 JSON format annotation"
            >
              <FileCode className="w-3.5 h-3.5 text-emerald-400" />
              <span>LabelMe JSON</span>
            </button>
          )}

          {/* Zoom & Layer Controls */}
          <div className="flex items-center space-x-1">
            <button
              type="button"
              onClick={() => setShowBoxes(!showBoxes)}
              className={`p-1.5 rounded text-xs transition cursor-pointer ${
                showBoxes ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
              title="Toggle Bounding Boxes"
            >
              <Layers className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleZoomIn}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleZoomOut}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition cursor-pointer"
              title="Reset View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Optical Calibration & Measurement Status Banner */}
      {measurementValidation && (
        <div className="px-4 py-1.5 bg-slate-950/70 border-b border-slate-800/80 flex items-center justify-between text-[11px]">
          <div className="flex items-center space-x-2">
            <Ruler className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-300 font-medium">Optical Calibration:</span>
            {measurementValidation.reference_detected ? (
              <span className="text-emerald-400 font-mono">
                {measurementValidation.reference_type} Detected • Ratio: {measurementValidation.pixel_to_mm_ratio} px/mm • Est. Font: {measurementValidation.estimated_font_height_mm} mm
              </span>
            ) : (
              <span className="text-amber-400/90 font-mono">
                Measurement unavailable — requires calibrated reference
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-slate-400">Table 1 Minimum:</span>
            <span className="font-mono text-white">{measurementValidation.table1_required_height_mm || 2.0} mm</span>
            <span
              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                measurementValidation.table1_complies
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                  : 'bg-amber-950 text-amber-300 border border-amber-700'
              }`}
            >
              {measurementValidation.table1_complies ? 'COMPLIES' : 'NEEDS REVIEW'}
            </span>
          </div>
        </div>
      )}

      {/* Main Viewport */}
      <div className="relative flex-1 min-h-[360px] bg-black/90 flex items-center justify-center overflow-hidden p-4">
        {activeImage?.url ? (
          <div
            className="relative transition-transform duration-150 ease-out origin-center max-w-full max-h-[500px]"
            style={{ transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)` }}
          >
            <img
              src={activeImage.url}
              alt={activeImage.surface}
              className="max-h-[460px] w-auto object-contain rounded select-none shadow-2xl"
            />

            {/* Bounding Box Overlays */}
            {showBoxes &&
              evidences.map((ev, idx) => {
                if (!ev.bounding_box) return null;
                const isSelected = selectedField === ev.field_name;
                const isViolation = ev.status === 'NOT DETECTED';
                const isReview = ev.status === 'NEEDS REVIEW' || ev.status === 'UNREADABLE';

                return (
                  <div
                    key={idx}
                    onClick={() => onSelectField && onSelectField(ev.field_name)}
                    className={`absolute cursor-pointer border-2 transition-all group ${
                      isSelected
                        ? 'border-amber-400 bg-amber-400/25 ring-2 ring-amber-300 shadow-xl z-20 scale-[1.02]'
                        : isViolation
                        ? 'border-red-500 bg-red-500/20 hover:bg-red-500/35 z-10'
                        : isReview
                        ? 'border-amber-500 bg-amber-500/20 hover:bg-amber-500/35 z-10'
                        : 'border-emerald-400/90 bg-emerald-500/15 hover:bg-emerald-500/30'
                    }`}
                    style={{
                      left: `${ev.bounding_box.x}%`,
                      top: `${ev.bounding_box.y}%`,
                      width: `${ev.bounding_box.width}%`,
                      height: `${ev.bounding_box.height}%`
                    }}
                  >
                    {/* Bounding Box Tag */}
                    <div
                      className={`absolute -top-5 left-0 px-1.5 py-0.5 text-[9px] font-bold rounded whitespace-nowrap shadow-md flex items-center space-x-1 ${
                        isSelected
                          ? 'bg-amber-500 text-slate-950 font-black ring-1 ring-white'
                          : isViolation
                          ? 'bg-red-600 text-white'
                          : isReview
                          ? 'bg-amber-600 text-white'
                          : 'bg-emerald-700 text-white'
                      }`}
                    >
                      <span>{ev.label || ev.field_name}</span>
                      <span className="opacity-80">({Math.round(ev.confidence * 100)}%)</span>
                    </div>
                  </div>
                );
              })}
          </div>
        ) : (
          <div className="text-center text-slate-500 text-xs py-12 space-y-2">
            <Eye className="w-8 h-8 mx-auto text-slate-600" />
            <p>Attach packaging images to view real-time optical bounding box overlays.</p>
          </div>
        )}
      </div>

      {/* Detected Packaging Regions Carousel / Selector */}
      {detectedRegions.length > 0 && (
        <div className="px-3 py-2 bg-slate-950/80 border-t border-slate-800/80 flex items-center space-x-2 overflow-x-auto text-[11px]">
          <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] whitespace-nowrap flex items-center space-x-1">
            <Tag className="w-3 h-3 text-indigo-400" />
            <span>Detected Regions ({detectedRegions.length}):</span>
          </span>
          {detectedRegions.map((reg) => {
            const isSel = selectedField === reg.category || selectedField === reg.region_id;
            return (
              <button
                key={reg.region_id}
                type="button"
                onClick={() => onSelectField && onSelectField(reg.category)}
                className={`px-2 py-0.5 rounded font-mono text-[10px] whitespace-nowrap transition cursor-pointer border ${
                  isSel
                    ? 'bg-amber-500 text-slate-950 border-amber-400 font-bold'
                    : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
                }`}
              >
                {reg.category} ({Math.round(reg.detection_confidence * 100)}%)
              </button>
            );
          })}
        </div>
      )}

      {/* Footer Inspector for Selected Field Evidence / Region */}
      {(selectedEvidence || selectedRegion) && (
        <div className="p-3 bg-slate-950 border-t border-slate-800 text-xs text-slate-300 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 animate-fadeIn">
          {/* Left: Crop Thumbnail if available */}
          {selectedRegion?.cropped_image_base64 && (
            <div className="flex-shrink-0">
              <img
                src={selectedRegion.cropped_image_base64}
                alt="Region Crop"
                className="h-14 w-auto max-w-[120px] object-contain rounded border border-slate-700 bg-black/60 shadow-md"
              />
            </div>
          )}

          {/* Middle: Field Particulars & OCR Disagreement Analysis */}
          <div className="space-y-1 flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-white">
                {selectedEvidence?.label || selectedRegion?.category || selectedField}
              </span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${
                  (selectedEvidence?.status || selectedRegion?.status) === 'DETECTED'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    : (selectedEvidence?.status || selectedRegion?.status) === 'NOT DETECTED'
                    ? 'bg-red-950 text-red-300 border border-red-700'
                    : 'bg-amber-950 text-amber-300 border border-amber-700'
                }`}
              >
                {selectedEvidence?.status || selectedRegion?.status || 'DETECTED'}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {Math.round((selectedEvidence?.confidence || selectedRegion?.ocr_confidence || 0.95) * 100)}% Confidence
              </span>
              {selectedRegion?.method_used && (
                <span className="text-[10px] text-indigo-300 bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-800">
                  Engine: {selectedRegion.method_used}
                </span>
              )}
            </div>

            <p className="text-[11px] text-slate-300 font-mono select-all truncate">
              Value: <span className="text-emerald-300 font-semibold">{selectedEvidence?.value || selectedRegion?.selected_text || 'Detected'}</span>
              {selectedEvidence?.source_text && (
                <span className="ml-2 text-slate-500">| Source: "{selectedEvidence.source_text}"</span>
              )}
            </p>

            {/* Multi-Engine OCR Candidates Comparison if available */}
            {selectedRegion?.ocr_candidates && Object.keys(selectedRegion.ocr_candidates).length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                <span className="text-[10px] text-slate-500 font-medium">OCR Consensus:</span>
                {Object.entries(selectedRegion.ocr_candidates).map(([engine, txt]) => (
                  <span
                    key={engine}
                    className="text-[10px] bg-slate-900 border border-slate-700 px-1.5 py-0.5 rounded font-mono text-slate-300"
                  >
                    <span className="text-slate-500 uppercase">{engine}:</span> "{String(txt)}"
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Right: Statutory Reference */}
          {selectedEvidence?.rule_reference && (
            <div className="text-[10px] font-mono bg-slate-900 border border-slate-800 px-2.5 py-1.5 rounded text-slate-400 flex-shrink-0">
              Statutory Ref: <span className="text-white font-semibold">{selectedEvidence.rule_reference}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
