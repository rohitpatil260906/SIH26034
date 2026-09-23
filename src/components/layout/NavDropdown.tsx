import React, { useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

export interface DropdownItem {
  label: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  onClick: () => void;
  badge?: string;
}

interface NavDropdownProps {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  items: DropdownItem[];
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
  isRouteActive?: boolean;
}

export const NavDropdown: React.FC<NavDropdownProps> = ({
  label,
  icon: Icon,
  items,
  isOpen,
  onToggle,
  onClose,
  isRouteActive = false
}) => {
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside of this dropdown
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const isVisuallyActive = isOpen || isRouteActive;

  return (
    <div ref={dropdownRef} className="relative h-full flex items-center">
      <button
        type="button"
        onClick={onToggle}
        className={`group relative flex flex-col items-center justify-center px-4 py-2 text-xs font-medium transition-all duration-150 cursor-pointer select-none ${
          isVisuallyActive
            ? 'text-[#6D28D9] font-semibold'
            : 'text-[#1F2328] hover:text-[#6D28D9]'
        }`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <div className="flex items-center space-x-1">
          <Icon
            className={`w-5 h-5 transition-colors ${
              isVisuallyActive ? 'text-[#6D28D9]' : 'text-[#5F6368] group-hover:text-[#6D28D9]'
            }`}
          />
        </div>
        <div className="flex items-center space-x-1 mt-1">
          <span className="tracking-tight text-[13px]">{label}</span>
          <ChevronDown
            className={`w-3 h-3 transition-transform duration-200 ${
              isOpen
                ? 'rotate-180 text-[#6D28D9]'
                : isVisuallyActive
                ? 'text-[#6D28D9]'
                : 'text-[#8A8F98] group-hover:text-[#6D28D9]'
            }`}
          />
        </div>

        {/* Active Purple Underline */}
        {isVisuallyActive && (
          <span className="absolute bottom-0 left-2 right-2 h-[2.5px] bg-[#7C3AED] rounded-t-full" />
        )}
      </button>

      {/* Dropdown Menu (Opens strictly on click; does not close on mouse out) */}
      {isOpen && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1 w-64 bg-[#FFFFFF] rounded-xl shadow-xl border border-[#E5E2DD] py-2 z-50 animate-dropdown">
          <div className="px-3 py-1.5 border-b border-[#F0EDE8] mb-1">
            <span className="text-[10px] font-semibold text-[#8A8F98] uppercase tracking-wider">{label}</span>
          </div>
          {items.map((item, idx) => {
            const ItemIcon = item.icon;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  onClose();
                  item.onClick();
                }}
                className="w-full text-left px-3 py-2 text-xs flex items-center space-x-2.5 hover:bg-[#F5F3FF] transition-colors rounded-lg mx-auto max-w-[96%] cursor-pointer group select-none"
              >
                {ItemIcon && (
                  <div className="p-1.5 rounded-md bg-[#FAF9F7] group-hover:bg-[#F5F3FF] group-hover:text-[#6D28D9] text-[#5F6368] border border-[#E5E2DD]/60 transition-colors">
                    <ItemIcon className="w-3.5 h-3.5" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-[#1F2328] group-hover:text-[#6D28D9] truncate text-[12.5px]">
                      {item.label}
                    </span>
                    {item.badge && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE] font-mono font-medium">
                        {item.badge}
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <p className="text-[11px] text-[#8A8F98] truncate">{item.description}</p>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
