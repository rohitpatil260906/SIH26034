import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  maxWidth = 'lg'
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '4xl': 'max-w-4xl'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#1F2328]/50 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        className={`w-full ${widthClasses[maxWidth]} bg-white rounded-xl shadow-xl border border-[#E5E2DD] overflow-hidden flex flex-col max-h-[90vh]`}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#E5E2DD] flex items-center justify-between bg-[#FFFCF8]">
          <div>
            <h3 className="text-base font-semibold text-[#1F2328]">{title}</h3>
            {subtitle && <p className="text-xs text-[#5F6368] mt-0.5">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#8A8F98] hover:text-[#6D28D9] hover:bg-[#F5F3FF] transition cursor-pointer"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto flex-1 bg-white">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="px-5 py-3.5 border-t border-[#E5E2DD] bg-[#FAF9F7] flex items-center justify-end space-x-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
