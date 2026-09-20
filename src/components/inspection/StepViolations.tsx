import React, { useState } from 'react';
import { useInspection } from '../../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { SeverityBadge } from '../ui/Badge';
import { Modal } from '../ui/Modal';
import { LabelGraphic } from './LabelGraphic';
import { InspectionViolation, BoundingBox } from '../../types';
import {
  AlertOctagon,
  CheckCircle,
  XCircle,
  MessageSquare,
  ZoomIn,
  ArrowRight,
  ArrowLeft,
  ShieldAlert,
  Gavel,
  FileCheck
} from 'lucide-react';

export const StepViolations: React.FC = () => {
  const {
    currentInspection,
    selectedSamplePackage,
    updateViolationStatus,
    setActiveStep
  } = useInspection();

  const [selectedViolation, setSelectedViolation] = useState<InspectionViolation | null>(
    currentInspection?.violations[0] || null
  );

  const [commentingItem, setCommentingItem] = useState<InspectionViolation | null>(null);
  const [officerComment, setOfficerComment] = useState<string>('');

  if (!currentInspection) return null;

  const sampleImage = selectedSamplePackage?.images[0];
  const svgMockType = sampleImage?.svgMock || 'front-mustard';

  // Find real custom photograph for the selected surface, or fallback to first image
  const customImageUrl =
    currentInspection.images.find(img => img.surface === selectedViolation?.surface && img.url)?.url ||
    currentInspection.images.find(img => img.url)?.url;

  const handleSaveComment = () => {
    if (!commentingItem) return;
    updateViolationStatus(commentingItem.id, commentingItem.officerStatus, officerComment);
    setCommentingItem(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-red-50 border border-red-200 rounded-md p-3.5 text-xs text-red-900">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-red-700 shrink-0" />
          <div>
            <span className="font-bold text-red-950">
              {currentInspection.violations.length} Potential Statutory Violation(s) Identified ({currentInspection.productName}):
            </span>
            <span className="ml-1 text-red-800">
              Inspect high-resolution photographic evidence below, cross-check clause references, and assign formal officer determination.
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Violations List (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader
              title={`Infraction Docket (${currentInspection.violations.length})`}
              subtitle="Select violation to view focused photographic evidence"
            />
            <CardContent className="p-3 space-y-3">
              {currentInspection.violations.length === 0 ? (
                <div className="text-center p-8 text-slate-500 text-xs space-y-2">
                  <CheckCircle className="w-8 h-8 text-emerald-600 mx-auto" />
                  <p className="font-semibold text-slate-800">Zero Violations Detected</p>
                  <p className="text-[11px] text-slate-500">
                    The scanned product conforms to all tested requirements under Legal Metrology Rules, 2011.
                  </p>
                </div>
              ) : (
                currentInspection.violations.map((vio, index) => {
                  const isSelected = selectedViolation?.id === vio.id;
                  const isAccepted = vio.officerStatus === 'Accepted';
                  const isDismissed = vio.officerStatus === 'Dismissed';

                  return (
                    <div
                      key={`${vio.id}-${index}`}
                      onClick={() => setSelectedViolation(vio)}
                      className={`p-3 rounded-md border cursor-pointer space-y-2 select-none transition-all duration-200 ease-out ${
                        isSelected
                          ? 'border-red-600 bg-red-50/20 ring-2 ring-red-600/40 scale-[1.02] shadow-md z-10'
                          : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[10px] font-mono text-slate-500 block">
                            {vio.id} • {vio.ruleReference}
                          </span>
                          <h4 className="text-xs font-bold text-slate-900 mt-0.5">
                            {vio.violationType}
                          </h4>
                        </div>
                        <SeverityBadge severity={vio.severity} />
                      </div>

                      <p className="text-[11px] text-slate-600 line-clamp-2">
                        {vio.description}
                      </p>

                      <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
                        <span>Panel: {vio.surface}</span>
                        <span className={`font-semibold ${
                          isAccepted ? 'text-red-700' : isDismissed ? 'text-slate-500 line-through' : 'text-amber-700'
                        }`}>
                          Status: {vio.officerStatus}
                        </span>
                      </div>

                      {/* Officer Decision Buttons */}
                      <div className="flex items-center space-x-2 pt-1">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateViolationStatus(vio.id, 'Accepted');
                          }}
                          className={`flex-1 py-1 text-[11px] rounded font-semibold border transition ${
                            isAccepted
                              ? 'bg-red-700 text-white border-red-700'
                              : 'bg-white text-slate-700 border-slate-300 hover:bg-red-50 hover:text-red-800'
                          }`}
                        >
                          Accept Infraction
                        </button>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateViolationStatus(vio.id, 'Dismissed');
                          }}
                          className={`flex-1 py-1 text-[11px] rounded font-medium border transition ${
                            isDismissed
                              ? 'bg-slate-700 text-white border-slate-700'
                              : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-100'
                          }`}
                        >
                          Dismiss
                        </button>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setCommentingItem(vio);
                            setOfficerComment(vio.officerComments || '');
                          }}
                          className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-100 border border-slate-200"
                          title="Add Officer Comment"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {vio.officerComments && (
                        <div className="text-[10px] bg-slate-50 p-1.5 rounded border border-slate-200 text-slate-700">
                          <span className="font-semibold text-slate-800">Officer Note:</span> {vio.officerComments}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: High-Res Zoomable Evidence Viewer (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          <Card className="flex-1 flex flex-col">
            <CardHeader
              title={
                selectedViolation
                  ? `Evidence Inspection: ${selectedViolation.violationType}`
                  : 'Commodity Evidence Viewer'
              }
              subtitle="Interactive optical inspection with bounding box annotation"
              action={
                selectedViolation && (
                  <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    Surface: {selectedViolation.surface}
                  </span>
                )
              }
            />
            <div className="p-3 flex-1 flex flex-col min-h-[420px]">
              <div className="flex-1 h-[420px]">
                <LabelGraphic
                  svgMockType={svgMockType}
                  customImageUrl={customImageUrl}
                  surface={selectedViolation?.surface || 'Front (PDP)'}
                  boundingBoxes={selectedViolation ? [selectedViolation.evidenceBoundingBox] : []}
                  highlightBox={selectedViolation?.evidenceBoundingBox}
                  showAnnotations={true}
                />
              </div>

              {selectedViolation && (
                <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-md text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">Recommended Statutory Proceeding:</span>
                    <span className="font-mono text-slate-600 text-[11px]">{selectedViolation.statutoryActClause}</span>
                  </div>
                  <p className="text-slate-700 text-[11px] leading-relaxed">
                    {selectedViolation.recommendedPenalty}
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Officer Comment Modal */}
      {commentingItem && (
        <Modal
          isOpen={true}
          onClose={() => setCommentingItem(null)}
          title={`Officer Annotation: ${commentingItem.violationType}`}
          subtitle="Add procedural notes regarding this potential Legal Metrology violation"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setCommentingItem(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleSaveComment}>
                Save Comment
              </Button>
            </>
          }
        >
          <div className="space-y-3 text-xs">
            <label className="block font-semibold text-slate-700">
              Officer Observations / Investigation Directives:
            </label>
            <textarea
              rows={4}
              value={officerComment}
              onChange={(e) => setOfficerComment(e.target.value)}
              placeholder="e.g. Master carton barcode inspected; discrepancy confirmed. Directing compounding notice under Section 36(1)."
              className="w-full bg-white border border-slate-300 rounded p-2 text-xs text-slate-900 focus:ring-1 focus:ring-[#0f2942] focus:outline-none"
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
          onClick={() => setActiveStep(5)}
        >
          Back to Rule Validation
        </Button>

        <Button
          type="button"
          variant="primary"
          size="md"
          rightIcon={<ArrowRight className="w-4 h-4" />}
          onClick={() => setActiveStep(7)}
        >
          Proceed to Officer Review &amp; Finalize
        </Button>
      </div>
    </div>
  );
};
