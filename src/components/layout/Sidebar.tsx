import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useInspection } from '../../context/InspectionContext';
import {
  LayoutDashboard,
  PlusCircle,
  ClipboardList,
  Package,
  AlertOctagon,
  FileText,
  BookOpen,
  BarChart3,
  Users,
  ShieldCheck,
  Settings,
  LogOut,
  Camera,
  Scale,
  Layers,
  Shield
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onCloseMobile: () => void;
  onOpenArchitecture?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onCloseMobile, onOpenArchitecture }) => {
  const { currentUser, logout } = useAuth();
  const { inspections } = useInspection();
  const navigate = useNavigate();

  const violationsCount = inspections.filter((i) => i.status === 'Non-Compliant').length;

  const navItems = [
    { label: 'Overview', to: '/dashboard', icon: LayoutDashboard },
    {
      label: 'Scan a Product',
      to: '/new-inspection?step=2&camera=open',
      icon: Camera,
      isHighlight: true,
      badge: 'LIVE',
      badgeColor: 'bg-amber-400/20 text-amber-300 border border-amber-400/40'
    },
    { label: 'New Inspection', to: '/new-inspection', icon: PlusCircle },
    { label: 'Inspections', to: '/inspections', icon: ClipboardList, badge: inspections.length },
    { label: 'Products', to: '/products', icon: Package },
    {
      label: 'Violations',
      to: '/violations',
      icon: AlertOctagon,
      badge: violationsCount,
      badgeColor: 'bg-red-950 text-red-300 border border-red-800'
    },
    {
      label: 'Legal Notices',
      to: '/legal-notices',
      icon: Scale,
      badge: 'SEC 36',
      badgeColor: 'bg-indigo-950 text-indigo-300 border border-indigo-800'
    },
    { label: 'Official Reports', to: '/reports', icon: FileText },
    { label: 'Rule Library', to: '/rules', icon: BookOpen },
    { label: 'Analytics', to: '/analytics', icon: BarChart3 },
    { label: 'Audit Log', to: '/audit-log', icon: ShieldCheck },
    { label: 'User Management', to: '/users', icon: Users },
    { label: 'Settings', to: '/settings', icon: Settings }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-950/70 lg:hidden backdrop-blur-2xs"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-[#0a1826] text-slate-300 flex flex-col border-r border-slate-800 transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand / Emblem */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-amber-300 text-sm shadow-xs">
              <Shield className="w-4 h-4 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center space-x-1">
                <h2 className="text-xs font-black text-white tracking-wide">LM-COMPASS</h2>
                <span className="text-[10px] text-amber-400 font-mono font-bold">VidhiCheck</span>
              </div>
              <p className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                Govt of India • PS 26034
              </p>
            </div>
          </div>
          <button
            onClick={onCloseMobile}
            className="lg:hidden p-1 text-slate-400 hover:text-white"
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-[#14324f] text-white font-bold shadow-xs border-l-2 border-amber-400'
                      : item.isHighlight
                      ? 'bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 hover:text-amber-200 border border-amber-500/30'
                      : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                  }`
                }
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`w-4 h-4 ${item.isHighlight ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                      item.badgeColor || 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}

          {/* System Architecture Button in Nav */}
          {onOpenArchitecture && (
            <button
              onClick={() => {
                onCloseMobile();
                onOpenArchitecture();
              }}
              className="w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium text-slate-300 hover:bg-slate-800/80 hover:text-white border border-slate-800 transition mt-2"
            >
              <div className="flex items-center space-x-2.5">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span>System Architecture</span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-semibold">
                4-STAGE
              </span>
            </button>
          )}
        </nav>

        {/* Legal Statutory Notice */}
        <div className="p-3 mx-3 mb-2 bg-slate-900/90 border border-slate-800 rounded-md text-[10px] text-slate-400 leading-tight space-y-1">
          <p className="font-semibold text-slate-200 flex items-center">
            <Scale className="w-3 h-3 text-amber-400 mr-1" />
            Statutory Notice
          </p>
          <p className="text-[10px] text-slate-400">
            LMPC Rules, 2011 & Sec 36/48 Enforcement. Panchnama required for final seizure.
          </p>
        </div>

        {/* Bottom Officer Profile Card */}
        <div className="p-3 border-t border-slate-800 bg-slate-950">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 text-amber-300 flex items-center justify-center text-xs font-bold shrink-0">
                {currentUser?.name.charAt(0) || 'O'}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-white truncate">{currentUser?.name || 'Officer'}</p>
                <p className="text-[10px] text-slate-400 font-mono truncate">
                  {currentUser?.role.replace('_', ' ') || 'OFFICER'}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                logout();
                navigate('/login');
              }}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
