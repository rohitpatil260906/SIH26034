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
  icon = false,
  className = ''
}) => {
  const variantStyles = {
    default: 'bg-slate-100 text-slate-800 border-slate-300',
    neutral: 'bg-slate-50 text-slate-700 border-slate-200',
    success: 'bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold',
    warning: 'bg-amber-50 text-amber-800 border-amber-300 font-semibold',
    danger: 'bg-red-50 text-red-800 border-red-300 font-semibold',
    info: 'bg-sky-50 text-sky-800 border-sky-300'
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs rounded border transition-colors ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: InspectionStatus | string; className?: string }> = ({
  status,
  className = ''
}) => {
  switch (status) {
    case 'Compliant':
      return (
        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-300 ${className}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mr-1" />
          <span>COMPLIANT</span>
        </span>
      );
    case 'Non-Compliant':
      return (
        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-800 border border-red-300 ${className}`}>
          <XCircle className="w-3.5 h-3.5 text-red-600 mr-1" />
          <span>NON-COMPLIANT</span>
        </span>
      );
    case 'Under Review':
      return (
        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300 ${className}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 mr-1" />
          <span>UNDER REVIEW</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300 ${className}`}>
          <Clock className="w-3.5 h-3.5 text-slate-500 mr-1" />
          <span>{status}</span>
        </span>
      );
  }
};

export const SeverityBadge: React.FC<{ severity: 'High' | 'Medium' | 'Low' }> = ({ severity }) => {
  switch (severity) {
    case 'High':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-semibold bg-red-100 text-red-900 border border-red-300 rounded">
          HIGH SEVERITY
        </span>
      );
    case 'Medium':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300 rounded">
          MEDIUM
        </span>
      );
    case 'Low':
      return (
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-slate-100 text-slate-800 border border-slate-300 rounded">
          LOW
        </span>
      );
  }
};

export const RoleBadge: React.FC<{ role: string }> = ({ role }) => {
  return (
    <span className="inline-flex items-center space-x-1 px-2 py-0.5 text-xs font-semibold bg-slate-800 text-slate-100 rounded border border-slate-700">
      <Shield className="w-3 h-3 text-sky-400 mr-1" />
      <span>{role.replace('_', ' ')}</span>
    </span>
  );
};
