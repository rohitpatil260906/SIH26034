import React, { useState } from 'react';
import { useInspection } from '../../context/InspectionContext';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import {
  CheckCircle2,
  Circle,
  Loader2,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ArrowLeft,
  ScanLine,
  SlidersHorizontal,
  FileText,
  Sparkles,
  AlertTriangle
} from 'lucide-react';

export const StepAnalysis: React.FC = () => {
  const {
    currentInspection,
    isAnalyzing,
    analysisProgress,
    analysisStage,
    ocrRawTranscript,
    ocrMeanConfidence,
    runAnalysisWorkflow,
    setActiveStep
  } = useInspection();

  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  const hasRunAnalysis = currentInspection?.declarations && currentInspection.declarations.length > 0;
  const attachedPhotoCount = currentInspection?.images.filter(img => img.url).length || 0;

  // Auto-initiate optical analysis workflow when entering analysis step if not yet executed
  React.useEffect(() => {
    if (currentInspection && currentInspection.images.length > 0 && !hasRunAnalysis && !isAnalyzing) {
      runAnalysisWorkflow();
    }
  }, []);

  if (!currentInspection) return null;

  const analysisStages = [
    { title: '1. Image Quality Assessment', description: 'Evaluating resolution, Laplacian blur variance, exposure, contrast, and text visibility' },
    { title: '2. Multi-Pass Image Enhancement', description: 'Applying 3x3 Laplacian sharpening, contrast normalization, and Sauvola adaptive binarization' },
    { title: '3. Text Region Detection', description: 'Spatial bounding box detection across product label and packaging panels' },
    { title: '4. Multi-Pass OCR Execution', description: 'Optical character recognition across enhanced, grayscale, and binarized image passes' },
    { title: '5. Structured Information Extraction', description: 'Converting OCR into canonical JSON schema (MRP, Net Qty, MFD, Manufacturer, Consumer Care)' },
    { title: '6. Multi-Image Surface Synthesis', description: 'Combining Front (PDP) and Back panel declarations into unified product record' },
    { title: '7. Statutory Rule Matching & Validation', description: 'Checking packaging declarations against all 34 Legal Metrology (Packaged Commodities) Rules' },
    { title: '8. Compliance Report Generation', description: 'Compiling evidence links, bounding boxes, violations, and official Panchnama docket' }
  ];

  const getStageStatus = (index: number) => {
    const threshold = (index + 1) * 12.5;
    if (analysisProgress >= threshold) return 'completed';
    if (isAnalyzing && analysisProgress >= index * 12.5) return 'running';
    return 'pending';
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader
          title="Automated Optical Label Inspection & Declaration Extraction"
          subtitle="Legal Metrology (Packaged Commodities) Rules, 2011 • In-Browser Optical Character Recognition"
        />
        <CardContent className="space-y-6">
          {/* Main Trigger / Progress Banner */}
          {!hasRunAnalysis && !isAnalyzing ? (
            <div className="bg-[#FAF9F7] border border-[#E5E2DD] rounded-xl p-6 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-[#F5F3FF] text-[#6D28D9] flex items-center justify-center mx-auto">
                <ScanLine className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-900">
                Ready to Process {currentInspection.images.length} Captured Surface Images
                {attachedPhotoCount > 0 && ` (${attachedPhotoCount} Real Camera Photographs)`}
              </h4>
              <p className="text-xs text-slate-600 max-w-lg mx-auto">
                The optical character recognition engine will read all words, numbers, and symbols directly from the product label, extract mandatory declarations, and check compliance under Rule 6.
              </p>
              <div className="pt-2">
                <Button
                  type="button"
                  variant="primary"
                  size="md"
                  onClick={runAnalysisWorkflow}
                  leftIcon={<ScanLine className="w-4 h-4" />}
                >
                  Analyze Product Labels Now
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Progress Bar */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                  <span>{isAnalyzing ? 'Analysis Pipeline in Progress...' : 'Inspection Pipeline Complete'}</span>
                  <span className="font-mono text-[#7C3AED]">{analysisProgress}%</span>
                </div>
                <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#7C3AED] transition-all duration-300 ease-out"
                    style={{ width: `${analysisProgress}%` }}
                  />
                </div>
                <p className="text-[11px] text-slate-500 italic">
                  {analysisStage}
                </p>
              </div>

              {/* Real-time OCR Product Confirmation Pill */}
              {hasRunAnalysis && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3.5 flex items-start space-x-3 text-xs text-emerald-900">
                  <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-emerald-950">Successfully Analyzed Label:</span>
                      <span className="font-semibold text-emerald-800 bg-white px-2 py-0.5 rounded border border-emerald-300">
                        {currentInspection.productName}
                      </span>
                    </div>
                    <p className="text-[11px] text-emerald-800 leading-relaxed">
                      Optical character recognition extracted <strong>{currentInspection.declarations.length} statutory declarations</strong>. Evaluated <strong>{currentInspection.violations.length} potential rule infractions</strong>.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Sequential Stages List */}
          <div className="border border-slate-200 rounded-md divide-y divide-slate-200 bg-white overflow-hidden">
            {analysisStages.map((stage, idx) => {
              const status = getStageStatus(idx);
              return (
                <div
                  key={stage.title}
                  className={`p-3.5 flex items-center justify-between transition-colors ${
                    status === 'running'
                      ? 'bg-slate-50'
                      : status === 'completed'
                      ? 'bg-white'
                      : 'bg-slate-50/50 opacity-60'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {status === 'completed' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
                    ) : status === 'running' ? (
                      <Loader2 className="w-4 h-4 text-[#7C3AED] animate-spin shrink-0" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-300 shrink-0" />
                    )}
                    <div>
                      <p className="text-xs font-semibold text-slate-900">{stage.title}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{stage.description}</p>
                    </div>
                  </div>

                  <div className="text-right shrink-0 ml-4">
                    {status === 'completed' && (
                      <span className="text-[11px] font-medium text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        Processed
                      </span>
                    )}
                    {status === 'running' && (
                      <span className="text-[11px] font-medium text-[#0f2942] bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                        Reading...
                      </span>
                    )}
                    {status === 'pending' && (
                      <span className="text-[10px] text-slate-400 font-mono">Queued</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Line-by-Line Optical Label Inspector & Rule Compliance Evaluation */}
          {hasRunAnalysis && currentInspection.extractedLines && currentInspection.extractedLines.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-2.5">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-[#0f2942]" />
                    <span>Line-by-Line Optical Text &amp; Legal Metrology Rule Audit</span>
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Every recognized line on the product label evaluated against the Legal Metrology (Packaged Commodities) Rules, 2011
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-[11px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                    Total: {currentInspection.extractedLines.length} Lines
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold border border-emerald-300">
                    Compliant: {currentInspection.extractedLines.filter(l => l.status === 'Compliant').length}
                  </span>
                  {currentInspection.extractedLines.filter(l => l.status === 'Non-Compliant').length > 0 && (
                    <span className="px-2 py-0.5 rounded bg-red-100 text-red-800 font-semibold border border-red-300">
                      Violations: {currentInspection.extractedLines.filter(l => l.status === 'Non-Compliant').length}
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {currentInspection.extractedLines.map((line) => {
                  const isCompliant = line.status === 'Compliant';
                  const isViolation = line.status === 'Non-Compliant';
                  const isReview = line.status === 'Under Review';

                  return (
                    <div
                      key={`line-${line.lineNumber}`}
                      className={`p-3 rounded-lg border text-xs transition-colors ${
                        isViolation
                          ? 'bg-red-50/60 border-red-300 text-red-950'
                          : isCompliant
                          ? 'bg-emerald-50/40 border-emerald-200 text-slate-900'
                          : isReview
                          ? 'bg-amber-50/50 border-amber-300 text-amber-950'
                          : 'bg-slate-50 border-slate-200 text-slate-800'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 mb-1.5">
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] font-mono font-bold bg-[#0f2942] text-white px-1.5 py-0.5 rounded">
                            Line #{line.lineNumber}
                          </span>
                          <span className="font-semibold text-slate-900 text-xs font-mono bg-white px-2 py-0.5 rounded border border-slate-200">
                            "{line.text}"
                          </span>
                        </div>

                        <div className="flex items-center space-x-1.5 shrink-0">
                          {isCompliant && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                              <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                              PASS
                            </span>
                          )}
                          {isViolation && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-300">
                              <AlertTriangle className="w-3 h-3 mr-1 text-red-600" />
                              VIOLATION
                            </span>
                          )}
                          {isReview && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                              <Circle className="w-3 h-3 mr-1 text-amber-600" />
                              UNDER REVIEW
                            </span>
                          )}
                          {!isCompliant && !isViolation && !isReview && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-200 text-slate-700">
                              INFO
                            </span>
                          )}
                          <span className="text-[10px] font-mono text-slate-500">
                            {line.confidence}% Conf.
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 text-[11px] mt-1 text-slate-600">
                        {line.matchedRule && (
                          <span className="font-semibold text-[#0f2942] bg-white px-1.5 py-0.5 rounded border border-slate-200">
                            {line.matchedRule}
                          </span>
                        )}
                        {line.finding && (
                          <span className={isViolation ? 'text-red-700 font-medium' : isCompliant ? 'text-emerald-700' : 'text-slate-600'}>
                            {line.finding}
                          </span>
                        )}
                        {line.penalRef && (
                          <span className="text-red-800 font-mono text-[10px] bg-red-100 px-1.5 py-0.5 rounded border border-red-300">
                            Penal clause: {line.penalRef}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Expandable Technical Details Drawer */}
          <div className="border border-slate-200 rounded-md overflow-hidden bg-slate-50">
            <button
              type="button"
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="w-full px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 flex items-center justify-between transition cursor-pointer"
            >
              <div className="flex items-center space-x-2">
                <SlidersHorizontal className="w-4 h-4 text-slate-500" />
                <span>Technical Inspection Parameters &amp; Optical Metrics</span>
              </div>
              {showTechnicalDetails ? (
                <ChevronUp className="w-4 h-4 text-slate-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-500" />
              )}
            </button>

            {showTechnicalDetails && (
              <div className="p-4 border-t border-slate-200 bg-white text-xs space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block uppercase font-mono">Preprocessing &amp; Deblurring</span>
                    <span className="text-sm font-bold text-slate-900 mt-0.5 block">3×3 Laplacian Sharpening</span>
                    <span className="text-[10px] text-emerald-700">Contrast Stretched Grayscale &amp; Inversion</span>
                  </div>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block uppercase font-mono">Optical OCR Engine</span>
                    <span className="text-sm font-bold text-slate-900 mt-0.5 block">Tesseract.js WebAssembly ({ocrMeanConfidence}%)</span>
                    <span className="text-[10px] text-slate-600">Multi-Pass Sparse &amp; PDP Scanning</span>
                  </div>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded">
                    <span className="text-[10px] text-slate-500 block uppercase font-mono">Statutory Rule Mapping</span>
                    <span className="text-sm font-bold text-slate-900 mt-0.5 block">Rules 1–34 Compendium</span>
                    <span className="text-[10px] text-slate-600">PCR 2011 &amp; 2022 Amendments</span>
                  </div>
                </div>

                {ocrRawTranscript && (
                  <div className="p-3 bg-slate-900 text-slate-200 rounded font-mono text-[11px] space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-[10px] border-b border-slate-700 pb-1">
                      <span className="flex items-center space-x-1">
                        <FileText className="w-3 h-3 text-amber-400" />
                        <span>Verbatim Optical OCR Output:</span>
                      </span>
                      <span>{ocrRawTranscript.length} characters</span>
                    </div>
                    <pre className="whitespace-pre-wrap max-h-32 overflow-y-auto leading-relaxed text-slate-300">
                      {ocrRawTranscript}
                    </pre>
                  </div>
                )}

                <p className="text-[11px] text-slate-500 leading-normal">
                  All character coordinate arrays and bounding vectors are timestamped and cryptographically hashed in the audit repository to ensure evidential integrity under the Indian Evidence Act.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-2">
        <Button
          type="button"
          variant="outline"
          size="md"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => setActiveStep(2)}
        >
          Back to Capture
        </Button>

        <div className="flex items-center space-x-3">
          {hasRunAnalysis && !isAnalyzing && (
            <Button
              type="button"
              variant="outline"
              size="md"
              leftIcon={<ScanLine className="w-4 h-4" />}
              onClick={runAnalysisWorkflow}
            >
              Re-run Analysis
            </Button>
          )}

          <Button
            type="button"
            variant="primary"
            size="md"
            rightIcon={<ArrowRight className="w-4 h-4" />}
            disabled={!hasRunAnalysis || isAnalyzing}
            onClick={() => setActiveStep(4)}
          >
            View Extracted Declarations
          </Button>
        </div>
      </div>
    </div>
  );
};
