import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, Shield } from 'lucide-react';
import { InspectionStatus } from '../../types';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'neutral' | 'info';
  children: React.ReactNode;
  icon?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  children,
  className = ''
}) => {
  const variantStyles = {
    default: 'bg-[#F8F7F4] text-[#1F2328] border-[#E5E2DD]',
    neutral: 'bg-[#FAF9F7] text-[#5F6368] border-[#E5E2DD]',
    success: 'bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0] font-medium',
    warning: 'bg-[#FFFBEB] text-[#D97706] border-[#FDE68A] font-medium',
    danger: 'bg-[#FEF2F2] text-[#DC2626] border-[#FECACA] font-medium',
    info: 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]'
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs rounded-md border transition-colors ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: InspectionStatus | string; className?: string }> = ({
  status,
  className = ''
}) => {
  const norm = (status || '').toUpperCase().trim();
  if (norm === 'COMPLIANT' || norm === 'PASS') {
    return (
      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-[#F0FDF4] text-[#16A34A] border border-[#BBF7D0] ${className}`}>
        <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A] mr-1 shrink-0" />
        <span>PASS</span>
      </span>
    );
  }
  if (norm === 'NON-COMPLIANT' || norm === 'FAIL' || norm === 'VIOLATION') {
    return (
      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA] ${className}`}>
        <XCircle className="w-3.5 h-3.5 text-[#DC2626] mr-1 shrink-0" />
        <span>FAIL</span>
      </span>
    );
  }
  if (norm === 'WARNING' || norm === 'WARN') {
    return (
      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A] ${className}`}>
        <AlertTriangle className="w-3.5 h-3.5 text-[#D97706] mr-1 shrink-0" />
        <span>WARNING</span>
      </span>
    );
  }
  if (norm === 'UNDER REVIEW' || norm === 'NEEDS REVIEW' || norm === 'MANUAL VERIFICATION REQUIRED' || norm === 'MANUAL REVIEW') {
    return (
      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-[#FFFBEB] text-[#B45309] border border-[#FDE68A] ${className}`}>
        <AlertTriangle className="w-3.5 h-3.5 text-[#D97706] mr-1 shrink-0" />
        <span>MANUAL VERIFICATION REQUIRED</span>
      </span>
    );
  }
  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-[#FAF9F7] text-[#5F6368] border border-[#E5E2DD] ${className}`}>
      <Clock className="w-3.5 h-3.5 text-[#8A8F98] mr-1 shrink-0" />
      <span>{status}</span>
    </span>
  );
};

export const ComplianceStatusBadge = StatusBadge;

export const SeverityBadge: React.FC<{ severity: 'High' | 'Medium' | 'Low' }> = ({ severity }) => {
  switch (severity) {
    case 'High':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-semibold bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA] rounded-md">
          HIGH SEVERITY
        </span>
      );
    case 'Medium':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-semibold bg-[#FFFBEB] text-[#D97706] border border-[#FDE68A] rounded-md">
          MEDIUM
        </span>
      );
    case 'Low':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-[#FAF9F7] text-[#5F6368] border border-[#E5E2DD] rounded-md">
          LOW
        </span>
      );
  }
};

export const RoleBadge: React.FC<{ role: string }> = ({ role }) => {
  return (
    <span className="inline-flex items-center space-x-1 px-2 py-0.5 text-xs font-semibold bg-[#F5F3FF] text-[#6D28D9] rounded-md border border-[#DDD6FE]">
      <Shield className="w-3 h-3 text-[#6D28D9] mr-1" />
      <span>{role.replace('_', ' ')}</span>
    </span>
  );
};
