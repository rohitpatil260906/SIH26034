import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const getBreadcrumbTitle = (path: string) => {
    switch (path) {
      case 'dashboard': return 'Dashboard';
      case 'new-inspection': return 'Scan & Analyze';
      case 'scan': return 'Scan & Analyze';
      case 'inspections': return 'Inspections';
      case 'history': return 'History';
      case 'products': return 'Products';
      case 'violations': return 'Violations';
      case 'reports': return 'Reports';
      case 'rules': return 'Rule Library';
      case 'analytics': return 'Analytics';
      case 'audit-log': return 'Audit Log';
      case 'users': return 'User Management';
      case 'settings': return 'Settings';
      case 'legal-notices': return 'Statutory Notices';
      default: return path;
    }
  };

  // Don't show redundant breadcrumb on root dashboard
  if (pathnames.length === 0 || (pathnames.length === 1 && pathnames[0] === 'dashboard')) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-1.5 text-xs text-[#5F6368] mb-5 select-none" aria-label="Breadcrumb">
      <Link to="/dashboard" className="hover:text-[#6D28D9] flex items-center transition-colors">
        <Home className="w-3.5 h-3.5 mr-1 text-[#8A8F98]" />
        <span>Home</span>
      </Link>
      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3 h-3 text-[#8A8F98]" />
            {isLast ? (
              <span className="font-semibold text-[#1F2328] truncate max-w-[240px]" aria-current="page">
                {getBreadcrumbTitle(value)}
              </span>
            ) : (
              <Link to={to} className="hover:text-[#6D28D9] transition-colors truncate max-w-[160px]">
                {getBreadcrumbTitle(value)}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
