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
  Eye
} from 'lucide-react';

interface ImageEvidenceViewerProps {
  images: InspectionImage[];
  evidences: FieldEvidence[];
  selectedField?: string;
  onSelectField?: (fieldName: string) => void;
  className?: string;
}

export const ImageEvidenceViewer: React.FC<ImageEvidenceViewerProps> = ({
  images,
  evidences,
  selectedField,
  onSelectField,
  className = ''
}) => {
  const [activeImageIndex, setActiveImageIndex] = useState<number>(0);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showBoxes, setShowBoxes] = useState<boolean>(true);

  const activeImage = images[activeImageIndex] || images[0];

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.3, 3.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.3, 0.7));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const selectedEvidence = evidences.find((e) => e.field_name === selectedField);

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col ${className}`}>
      {/* Viewer Header */}
      <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Crosshair className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Image Evidence Overlay Viewer
          </span>
          {activeImage && (
            <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono border border-slate-700">
              {activeImage.surface} • {activeImage.name}
            </span>
          )}
        </div>

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

        {/* Zoom Controls */}
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

      {/* Footer Inspector for Selected Field Evidence */}
      {selectedEvidence && (
        <div className="p-3 bg-slate-950 border-t border-slate-800 text-xs text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 animate-fadeIn">
          <div className="space-y-0.5">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white">{selectedEvidence.label}</span>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${
                  selectedEvidence.status === 'DETECTED'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                    : selectedEvidence.status === 'NOT DETECTED'
                    ? 'bg-red-950 text-red-300 border border-red-700'
                    : 'bg-amber-950 text-amber-300 border border-amber-700'
                }`}
              >
                {selectedEvidence.status}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {Math.round(selectedEvidence.confidence * 100)}% Confidence
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono select-all">
              Value: <span className="text-emerald-300 font-semibold">{selectedEvidence.value}</span>
              {selectedEvidence.source_text && (
                <span className="ml-2 text-slate-500">| Source: "{selectedEvidence.source_text}"</span>
              )}
            </p>
          </div>

          {selectedEvidence.rule_reference && (
            <div className="text-[10px] font-mono bg-slate-900 border border-slate-800 px-2 py-1 rounded text-slate-400">
              Statutory Ref: <span className="text-white">{selectedEvidence.rule_reference}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
