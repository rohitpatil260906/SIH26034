import React from 'react';
import { Check, ChevronRight } from 'lucide-react';

interface StepperProps {
  steps: string[];
  activeStep: number;
  onStepClick?: (stepNumber: number) => void;
}

export const Stepper: React.FC<StepperProps> = ({ steps, activeStep, onStepClick }) => {
  return (
    <div className="w-full bg-white border border-[#E5E2DD] rounded-xl p-3.5 mb-6 shadow-2xs">
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
                  className={`flex items-center space-x-2.5 text-left w-full group ${
                    isUpcoming ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
                  }`}
                >
                  {/* Step circle */}
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all ${
                      isCompleted
                        ? 'bg-[#16A34A] text-white'
                        : isCurrent
                        ? 'bg-[#7C3AED] text-white ring-4 ring-[#7C3AED]/15'
                        : 'bg-[#FAF9F7] text-[#8A8F98] border border-[#E5E2DD]'
                    }`}
                  >
                    {isCompleted ? <Check className="w-3.5 h-3.5 stroke-[2.5]" /> : stepNumber}
                  </span>

                  {/* Step text */}
                  <div className="overflow-hidden">
                    <p
                      className={`text-[10px] font-semibold uppercase tracking-wider ${
                        isCurrent
                          ? 'text-[#6D28D9]'
                          : isCompleted
                          ? 'text-[#16A34A]'
                          : 'text-[#8A8F98]'
                      }`}
                    >
                      Step {stepNumber}
                    </p>
                    <p
                      className={`text-xs font-medium truncate ${
                        isCurrent
                          ? 'text-[#1F2328] font-bold'
                          : isCompleted
                          ? 'text-[#5F6368]'
                          : 'text-[#8A8F98]'
                      }`}
                    >
                      {stepName}
                    </p>
                  </div>
                </button>

                {index < steps.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-[#E5E2DD] hidden md:block shrink-0" />
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
};
