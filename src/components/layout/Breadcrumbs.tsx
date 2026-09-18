import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(x => x);

  const getBreadcrumbTitle = (path: string) => {
    switch (path) {
      case 'dashboard': return 'Operational Overview';
      case 'new-inspection': return 'New Inspection';
      case 'inspections': return 'Inspections Registry';
      case 'products': return 'Product Repository';
      case 'violations': return 'Violations & Evidence';
      case 'reports': return 'Official Reports';
      case 'rules': return 'Rule Library';
      case 'analytics': return 'Enforcement Analytics';
      case 'audit-log': return 'Audit Trail & Logs';
      case 'users': return 'User Management';
      case 'settings': return 'System Settings';
      default: return path;
    }
  };

  return (
    <nav className="flex items-center space-x-1.5 text-xs text-slate-500 mb-3" aria-label="Breadcrumb">
      <Link to="/dashboard" className="hover:text-slate-900 flex items-center transition">
        <Home className="w-3.5 h-3.5 mr-1 text-slate-400" />
        <span>Home</span>
      </Link>
      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
            {isLast ? (
              <span className="font-semibold text-slate-900 truncate max-w-[200px]" aria-current="page">
                {getBreadcrumbTitle(value)}
              </span>
            ) : (
              <Link to={to} className="hover:text-slate-900 transition truncate max-w-[150px]">
                {getBreadcrumbTitle(value)}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
