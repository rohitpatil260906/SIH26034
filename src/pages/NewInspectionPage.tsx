import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInspection } from '../context/InspectionContext';
import { Stepper } from '../components/inspection/Stepper';
import { StepDetails } from '../components/inspection/StepDetails';
import { StepCapture } from '../components/inspection/StepCapture';
import { StepAnalysis } from '../components/inspection/StepAnalysis';
import { StepDeclarations } from '../components/inspection/StepDeclarations';
import { StepValidation } from '../components/inspection/StepValidation';
import { StepViolations } from '../components/inspection/StepViolations';
import { StepReview } from '../components/inspection/StepReview';

export const NewInspectionPage: React.FC = () => {
  const { currentInspection, activeStep, setActiveStep, startNewInspection } = useInspection();
  const [searchParams, setSearchParams] = useSearchParams();
  const isInitializedRef = React.useRef<boolean>(false);

  // Read initial target step and camera trigger once on mount / initial setup
  useEffect(() => {
    if (isInitializedRef.current) return;
    isInitializedRef.current = true;

    const stepParam = searchParams.get('step');
    const cameraParam = searchParams.get('camera') || searchParams.get('openCamera');
    const targetStep = stepParam ? parseInt(stepParam, 10) : (cameraParam === 'open' || cameraParam === 'true' ? 2 : 1);
    const validStep = targetStep >= 1 && targetStep <= 7 ? targetStep : 1;

    if (!currentInspection) {
      startNewInspection(undefined, validStep);
    } else if (validStep !== activeStep) {
      setActiveStep(validStep);
    }
  }, []);

  // Synchronize URL search params with activeStep without reverting user actions
  useEffect(() => {
    const currentStepParam = searchParams.get('step');
    const hasCamera = searchParams.get('camera') || searchParams.get('openCamera');
    const stepStr = activeStep.toString();

    if (currentStepParam !== stepStr || (activeStep !== 2 && hasCamera)) {
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set('step', stepStr);
      if (activeStep !== 2) {
        nextParams.delete('camera');
        nextParams.delete('openCamera');
      }
      setSearchParams(nextParams, { replace: true });
    }
  }, [activeStep, searchParams, setSearchParams]);

  const stepNames = [
    'Details',
    'Capture',
    'Analysis',
    'Declarations',
    'Validation',
    'Violations',
    'Review'
  ];

  const renderActiveStep = () => {
    switch (activeStep) {
      case 1:
        return <StepDetails />;
      case 2:
        return <StepCapture />;
      case 3:
        return <StepAnalysis />;
      case 4:
        return <StepDeclarations />;
      case 5:
        return <StepValidation />;
      case 6:
        return <StepViolations />;
      case 7:
        return <StepReview />;
      default:
        return <StepDetails />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="border-b border-slate-200 pb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">New Packaged Commodity Inspection</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Step {activeStep} of 7: {stepNames[activeStep - 1]} • Legal Metrology (Packaged Commodities) Rules, 2011
          </p>
        </div>
        {currentInspection && (
          <div className="text-xs text-slate-600 bg-white border border-slate-200 px-3 py-1 rounded font-mono">
            Docket: <strong className="text-slate-900">{currentInspection.id}</strong>
          </div>
        )}
      </div>

      {/* Stepper Navigation */}
      <Stepper
        steps={stepNames}
        activeStep={activeStep}
        onStepClick={(step) => setActiveStep(step)}
      />

      {/* Dynamic Active Step Content */}
      <div className="pb-8">
        {renderActiveStep()}
      </div>
    </div>
  );
};
