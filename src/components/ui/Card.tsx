import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: (e: React.MouseEvent<HTMLDivElement>) => void;
  orientation?: 'vertical' | 'horizontal' | string;
  isFocusable?: boolean;
  isFocused?: boolean;
  onFocusToggle?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  onClick,
  isFocusable = false,
  isFocused: controlledIsFocused,
  onFocusToggle
}) => {
  const [internalFocused, setInternalFocused] = React.useState(false);
  const isFocused = controlledIsFocused !== undefined ? controlledIsFocused : internalFocused;

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isFocusable) {
      if (onFocusToggle) {
        onFocusToggle();
      } else {
        setInternalFocused((prev) => !prev);
      }
    }
    if (onClick) {
      onClick(e);
    }
  };

  const focusStyles = isFocused
    ? 'scale-[1.02] sm:scale-[1.03] shadow-md shadow-[#7C3AED]/10 border-[#7C3AED] ring-2 ring-[#7C3AED]/25 z-10 relative'
    : '';

  const interactiveStyles = (onClick || isFocusable)
    ? 'cursor-pointer hover:border-[#D8D4CE] hover:shadow-xs'
    : '';

  return (
    <div
      onClick={onClick || isFocusable ? handleClick : undefined}
      className={`bg-white border border-[#E5E2DD] rounded-xl shadow-2xs transition-all duration-250 ease-out motion-reduce:transform-none ${interactiveStyles} ${focusStyles} ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, action, className = '' }) => {
  return (
    <div className={`px-5 py-4 border-b border-[#E5E2DD] flex items-center justify-between ${className}`}>
      <div>
        <h3 className="text-sm font-semibold text-[#1F2328] tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-[#5F6368] mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="ml-4">{action}</div>}
    </div>
  );
};

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = 'p-5'
}) => {
  return <div className={className}>{children}</div>;
};

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = 'px-5 py-3.5 bg-[#FAF9F7] border-t border-[#E5E2DD] rounded-b-xl'
}) => {
  return <div className={className}>{children}</div>;
};
