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
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-150 active:scale-[0.98] motion-reduce:transform-none focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100 rounded-lg border cursor-pointer select-none';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs space-x-1.5 shadow-2xs',
    md: 'px-4 py-2 text-sm space-x-2 shadow-2xs',
    lg: 'px-5 py-2.5 text-base space-x-2.5 shadow-xs'
  };

  const variantStyles = {
    primary: 'bg-[#7C3AED] hover:bg-[#6D28D9] active:bg-[#5B21B6] text-white border-transparent focus:ring-[#7C3AED]/30 shadow-xs',
    secondary: 'bg-white hover:bg-[#FAF9F7] active:bg-[#F0EDE8] text-[#1F2328] border-[#E5E2DD] hover:border-[#D8D4CE] focus:ring-[#7C3AED]/20',
    outline: 'bg-transparent hover:bg-[#F5F3FF] text-[#6D28D9] border-[#7C3AED]/70 hover:border-[#7C3AED] focus:ring-[#7C3AED]/20',
    danger: 'bg-[#DC2626] hover:bg-[#B91C1C] text-white border-[#DC2626] focus:ring-red-400',
    success: 'bg-[#16A34A] hover:bg-[#15803D] text-white border-[#16A34A] focus:ring-emerald-400',
    ghost: 'bg-transparent hover:bg-[#F5F3FF] text-[#1F2328] hover:text-[#6D28D9] border-transparent shadow-none focus:ring-[#7C3AED]/20'
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
