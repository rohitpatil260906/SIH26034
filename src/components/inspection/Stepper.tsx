import React from 'react';
import { Check, ChevronRight } from 'lucide-react';

interface StepperProps {
  steps: string[];
  activeStep: number;
  onStepClick?: (stepNumber: number) => void;
}

export const Stepper: React.FC<StepperProps> = ({ steps, activeStep, onStepClick }) => {
  return (
    <div className="w-full bg-white border border-slate-200 rounded-md p-3 mb-6 shadow-2xs">
      <nav aria-label="Progress">
        <ol className="flex items-center justify-between space-x-2 md:space-x-4 overflow-x-auto pb-1">
          {steps.map((stepName, index) => {
            const stepNumber = index + 1;
            const isCompleted = stepNumber < activeStep;
            const isCurrent = stepNumber === activeStep;
            const isUpcoming = stepNumber > activeStep;

            return (
              <li
                key={stepName}
                className="flex items-center space-x-2 flex-1 min-w-[120px]"
              >
                <button
                  type="button"
                  disabled={isUpcoming}
                  onClick={() => onStepClick && onStepClick(stepNumber)}
                  className={`flex items-center space-x-2 text-left w-full group ${
                    isUpcoming ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                  }`}
                >
                  {/* Step circle */}
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-colors ${
                      isCompleted
                        ? 'bg-emerald-700 text-white'
                        : isCurrent
                        ? 'bg-[#0f2942] text-white ring-2 ring-[#0f2942]/20'
                        : 'bg-slate-100 text-slate-500 border border-slate-300'
                    }`}
                  >
                    {isCompleted ? <Check className="w-3.5 h-3.5" /> : stepNumber}
                  </span>

                  {/* Step text */}
                  <div className="overflow-hidden">
                    <p
                      className={`text-[10px] font-semibold uppercase tracking-wider ${
                        isCurrent
                          ? 'text-[#0f2942]'
                          : isCompleted
                          ? 'text-emerald-800'
                          : 'text-slate-400'
                      }`}
                    >
                      Step {stepNumber}
                    </p>
                    <p
                      className={`text-xs font-medium truncate ${
                        isCurrent
                          ? 'text-slate-900 font-bold'
                          : isCompleted
                          ? 'text-slate-700'
                          : 'text-slate-400'
                      }`}
                    >
                      {stepName}
                    </p>
                  </div>
                </button>

                {index < steps.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-slate-300 hidden md:block shrink-0" />
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
};
