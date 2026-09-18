import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed rounded border';

  const sizeStyles = {
    sm: 'px-2.5 py-1 text-xs space-x-1.5 shadow-xs',
    md: 'px-3.5 py-1.5 text-sm space-x-2 shadow-xs',
    lg: 'px-4 py-2 text-base space-x-2.5 shadow-sm'
  };

  const variantStyles = {
    primary: 'bg-[#0f2942] hover:bg-[#163a5f] text-white border-[#0f2942] focus:ring-slate-400',
    secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300 focus:ring-slate-300',
    outline: 'bg-white hover:bg-slate-50 text-slate-700 border-slate-300 hover:border-slate-400 focus:ring-slate-300',
    danger: 'bg-red-700 hover:bg-red-800 text-white border-red-700 focus:ring-red-400',
    success: 'bg-emerald-700 hover:bg-emerald-800 text-white border-emerald-700 focus:ring-emerald-400',
    ghost: 'bg-transparent hover:bg-slate-100 text-slate-700 border-transparent shadow-none focus:ring-slate-200'
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
      ) : leftIcon ? (
        <span className="mr-1.5 inline-flex items-center">{leftIcon}</span>
      ) : null}
      <span>{children}</span>
      {!isLoading && rightIcon && (
        <span className="ml-1.5 inline-flex items-center">{rightIcon}</span>
      )}
    </button>
  );
};
