import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useInspection } from '../../context/InspectionContext';
import { NavDropdown, DropdownItem } from './NavDropdown';
import {
  Home,
  Camera,
  FileText,
  History,
  Settings,
  Calendar,
  Bell,
  User,
  ChevronDown,
  LogOut,
  Sliders,
  MapPin,
  Sparkles,
  Layers,
  Upload,
  ClipboardList,
  AlertOctagon,
  Scale,
  Package,
  BookOpen,
  BarChart3,
  Users,
  ShieldCheck,
  Menu,
  X,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { JurisdictionModal } from '../jurisdiction/JurisdictionModal';
import { RoleBadge } from '../ui/Badge';
import { OfficerRole } from '../../types';

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  onOpenArchitecture?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenArchitecture }) => {
  const { currentUser, logout, switchRole } = useAuth();
  const {
    inspections,
    currentInspection,
    startNewInspection,
    setActiveStep,
    activeJurisdiction,
    setActiveJurisdiction,
    updateInspectionDetails
  } = useInspection();

  const navigate = useNavigate();
  const location = useLocation();

  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isJurisdictionModalOpen, setIsJurisdictionModalOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [openNavDropdown, setOpenNavDropdown] = useState<'scan' | 'reports' | 'history' | 'settings' | null>(null);

  const profileMenuRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLElement>(null);

  // Close nav dropdown when navigating to a new route
  useEffect(() => {
    setOpenNavDropdown(null);
  }, [location.pathname]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target as Node)) {
        setShowProfileMenu(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        setOpenNavDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Format today's date dynamically (e.g., "19 Sep 2026")
  const formattedToday = useMemo(() => {
    const date = new Date();
    const day = date.getDate();
    const month = date.toLocaleDateString('en-GB', { month: 'short' });
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  }, []);

  // Route active detection
  const currentPath = location.pathname;

  const isHomeActive = currentPath === '/' || currentPath === '/dashboard';
  const isScanActive = currentPath.startsWith('/new-inspection') || currentPath === '/scan';
  const isReportsActive = currentPath.startsWith('/reports') || currentPath === '/analytics' || currentPath === '/legal-notices';
  const isHistoryActive = currentPath === '/inspections' || currentPath === '/history' || currentPath === '/products' || currentPath === '/violations' || currentPath === '/audit-log';
  const isSettingsActive = currentPath === '/settings' || currentPath === '/users' || currentPath === '/rules';

  // Counts for alerts
  const pendingReviewsCount = inspections.filter((i) => i.status === 'Under Review').length;
  const violationsCount = inspections.filter((i) => i.status === 'Non-Compliant').length;
  const totalNotifications = Math.max(2, pendingReviewsCount + (violationsCount > 0 ? 1 : 0));

  // Dropdown Items
  const scanDropdownItems: DropdownItem[] = [
    {
      label: 'Scan Product',
      description: 'Camera or label photo OCR analysis',
      icon: Camera,
      onClick: () => {
        if (!currentInspection) startNewInspection(undefined, 2);
        navigate('/new-inspection?step=2&camera=open');
      },
      badge: 'LIVE'
    },
    {
      label: 'New Inspection',
      description: 'Start full 7-step statutory audit',
      icon: ClipboardList,
      onClick: () => {
        startNewInspection();
        navigate('/new-inspection');
      }
    },
    {
      label: 'Upload Label',
      description: 'Upload high-res package label',
      icon: Upload,
      onClick: () => {
        if (!currentInspection) startNewInspection(undefined, 2);
        navigate('/new-inspection?step=2');
      }
    },
    {
      label: 'Camera Scan',
      description: 'Live continuous barcode & text capture',
      icon: Sparkles,
      onClick: () => {
        if (!currentInspection) {
          startNewInspection(undefined, 2);
        } else {
          setActiveStep(2);
        }
        navigate('/new-inspection?step=2&camera=open');
      }
    }
  ];

  const reportsDropdownItems: DropdownItem[] = [
    {
      label: 'Official Reports',
      description: 'Statutory LM inspection reports & PDFs',
      icon: FileText,
      onClick: () => navigate('/reports')
    },
    {
      label: 'Inspection Reports',
      description: 'Detailed inspection dockets & dossiers',
      icon: ClipboardList,
      onClick: () => navigate('/inspections')
    },
    {
      label: 'Compliance Reports',
      description: 'Analytics, trends & rule breakdown',
      icon: BarChart3,
      onClick: () => navigate('/analytics')
    },
    {
      label: 'Statutory Notices (Sec 36)',
      description: 'Show Cause notice & compounding forms',
      icon: Scale,
      onClick: () => navigate('/legal-notices'),
      badge: 'SEC 36'
    }
  ];

  const historyDropdownItems: DropdownItem[] = [
    {
      label: 'Inspections Registry',
      description: 'All past inspection dockets',
      icon: ClipboardList,
      onClick: () => navigate('/inspections'),
      badge: `${inspections.length}`
    },
    {
      label: 'Products Repository',
      description: 'Catalog of verified commodity packages',
      icon: Package,
      onClick: () => navigate('/products')
    },
    {
      label: 'Violations Registry',
      description: 'Flagged non-compliant packages & evidence',
      icon: AlertOctagon,
      onClick: () => navigate('/violations'),
      badge: violationsCount > 0 ? `${violationsCount}` : undefined
    },
    {
      label: 'Audit Log & Trail',
      description: 'Tamper-evident legal audit log',
      icon: ShieldCheck,
      onClick: () => navigate('/audit-log')
    }
  ];

  const settingsDropdownItems: DropdownItem[] = [
    {
      label: 'System Settings',
      description: 'Jurisdiction, tolerances & preferences',
      icon: Settings,
      onClick: () => navigate('/settings')
    },
    {
      label: 'Rule Library',
      description: 'LMPC Rules 2011 & Legal Metrology Act',
      icon: BookOpen,
      onClick: () => navigate('/rules')
    },
    {
      label: 'User Management',
      description: 'Officer accounts & access privileges',
      icon: Users,
      onClick: () => navigate('/users')
    },
    ...(onOpenArchitecture ? [{
      label: 'System Architecture',
      description: '4-Stage CV & OCR pipeline breakdown',
      icon: Layers,
      onClick: onOpenArchitecture,
      badge: '4-STAGE'
    }] : [])
  ];

  const activeJurisdictionLabel = activeJurisdiction?.state
    ? `${activeJurisdiction.state}${activeJurisdiction.city ? ', ' + activeJurisdiction.city : ''}`
    : 'National Jurisdiction';

  return (
    <header className="sticky top-0 z-40 bg-[#FFFCF8] border-b border-[#E5E2DD] shadow-2xs">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* LEFT: VidhiCheck Branding */}
        <div
          onClick={() => {
            setOpenNavDropdown(null);
            navigate('/dashboard');
          }}
          className="flex items-center space-x-3 cursor-pointer select-none group"
        >
          {/* Replit-style Purple Logo (4 Square Blocks) */}
          <div className="w-9 h-9 shrink-0 flex items-center justify-center transition-transform group-hover:scale-105">
            <svg
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-8 h-8"
            >
              {/* Top-right block */}
              <rect x="17" y="3" width="11" height="11" rx="2.5" fill="#7C3AED" />
              {/* Center-right block */}
              <rect x="17" y="16" width="11" height="11" rx="2.5" fill="#7C3AED" />
              {/* Center-left block */}
              <rect x="4" y="10" width="11" height="11" rx="2.5" fill="#7C3AED" />
              {/* Bottom-left block */}
              <rect x="4" y="23" width="11" height="11" rx="2.5" fill="#7C3AED" />
            </svg>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[21px] font-bold text-[#1F2328] tracking-tight font-sans">
                VidhiCheck
              </span>
            </div>
            <p className="text-[11.5px] text-[#5F6368] font-normal leading-none mt-0.5 tracking-tight hidden sm:block">
              AI-Powered Packaged Commodity Compliance Checker
            </p>
          </div>
        </div>

        {/* CENTER: Horizontal 5 Main Nav Items (Desktop) */}
        <nav ref={navRef} className="hidden md:flex items-center space-x-1 lg:space-x-3 h-full">
          {/* 1. Home */}
          <button
            type="button"
            onClick={() => {
              setOpenNavDropdown(null);
              setShowProfileMenu(false);
              setShowNotifications(false);
              navigate('/dashboard');
            }}
            className={`group relative flex flex-col items-center justify-center px-4 py-2 text-xs font-medium h-full transition-all duration-150 cursor-pointer select-none ${
              isHomeActive
                ? 'text-[#6D28D9] font-semibold'
                : 'text-[#1F2328] hover:text-[#6D28D9]'
            }`}
          >
            <Home className={`w-5 h-5 transition-colors ${isHomeActive ? 'text-[#6D28D9]' : 'text-[#5F6368] group-hover:text-[#6D28D9]'}`} />
            <span className="tracking-tight text-[13px] mt-1">Home</span>
            {isHomeActive && (
              <span className="absolute bottom-0 left-2 right-2 h-[2.5px] bg-[#7C3AED] rounded-t-full" />
            )}
          </button>

          {/* 2. Scan & Analyze */}
          <NavDropdown
            label="Scan & Analyze"
            icon={Camera}
            items={scanDropdownItems}
            isOpen={openNavDropdown === 'scan'}
            onToggle={() => {
              setShowProfileMenu(false);
              setShowNotifications(false);
              setOpenNavDropdown((prev) => (prev === 'scan' ? null : 'scan'));
            }}
            onClose={() => setOpenNavDropdown(null)}
            isRouteActive={isScanActive}
          />

          {/* 3. Reports */}
          <NavDropdown
            label="Reports"
            icon={FileText}
            items={reportsDropdownItems}
            isOpen={openNavDropdown === 'reports'}
            onToggle={() => {
              setShowProfileMenu(false);
              setShowNotifications(false);
              setOpenNavDropdown((prev) => (prev === 'reports' ? null : 'reports'));
            }}
            onClose={() => setOpenNavDropdown(null)}
            isRouteActive={isReportsActive}
          />

          {/* 4. History */}
          <NavDropdown
            label="History"
            icon={History}
            items={historyDropdownItems}
            isOpen={openNavDropdown === 'history'}
            onToggle={() => {
              setShowProfileMenu(false);
              setShowNotifications(false);
              setOpenNavDropdown((prev) => (prev === 'history' ? null : 'history'));
            }}
            onClose={() => setOpenNavDropdown(null)}
            isRouteActive={isHistoryActive}
          />

          {/* 5. Settings */}
          <NavDropdown
            label="Settings"
            icon={Settings}
            items={settingsDropdownItems}
            isOpen={openNavDropdown === 'settings'}
            onToggle={() => {
              setShowProfileMenu(false);
              setShowNotifications(false);
              setOpenNavDropdown((prev) => (prev === 'settings' ? null : 'settings'));
            }}
            onClose={() => setOpenNavDropdown(null)}
            isRouteActive={isSettingsActive}
          />
        </nav>

        {/* RIGHT: Date, Notification Bell, Profile */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          
          {/* Dynamic Today's Date */}
          <div className="hidden lg:flex items-center space-x-1.5 text-xs text-[#5F6368] px-2.5 py-1.5 rounded-lg bg-[#FAF9F7] border border-[#E5E2DD]/80">
            <Calendar className="w-3.5 h-3.5 text-[#8A8F98]" />
            <span className="font-medium text-[#1F2328] tracking-tight">{formattedToday}</span>
          </div>

          {/* Notification Bell */}
          <div className="relative" ref={notificationsRef}>
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowProfileMenu(false);
              }}
              className="relative p-2 rounded-full text-[#5F6368] hover:text-[#1F2328] hover:bg-[#FAF9F7] transition cursor-pointer"
              title="Notifications"
              aria-label="Notifications"
            >
              <Bell className="w-4.5 h-4.5" />
              {totalNotifications > 0 && (
                <span className="absolute top-1 right-1 flex items-center justify-center w-4 h-4 rounded-full bg-[#7C3AED] text-white text-[10px] font-bold font-mono">
                  {totalNotifications}
                </span>
              )}
            </button>

            {/* Notification Dropdown Panel */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-[#E5E2DD] z-50 animate-in fade-in zoom-in-95 duration-100 overflow-hidden">
                <div className="px-4 py-3 border-b border-[#E5E2DD] bg-[#FFFCF8] flex items-center justify-between">
                  <span className="text-xs font-bold text-[#1F2328] tracking-tight">Compliance Notifications</span>
                  <span className="text-[10px] bg-[#F5F3FF] text-[#6D28D9] px-2 py-0.5 rounded-full font-mono font-semibold">
                    {totalNotifications} New
                  </span>
                </div>
                <div className="divide-y divide-[#F0EDE8] max-h-72 overflow-y-auto">
                  <div
                    className="p-3 hover:bg-[#FAF9F7] transition cursor-pointer"
                    onClick={() => {
                      navigate('/violations');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2.5">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-[#DC2626] shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-[#1F2328]">Non-Compliance Flagged: Mustard Oil</p>
                        <p className="text-[11px] text-[#5F6368] mt-0.5">Missing "inclusive of all taxes" under Rule 6(1)(e).</p>
                        <span className="text-[10px] text-[#8A8F98] mt-1 block">15 mins ago • Mumbai Central</span>
                      </div>
                    </div>
                  </div>
                  <div
                    className="p-3 hover:bg-[#FAF9F7] transition cursor-pointer"
                    onClick={() => {
                      navigate('/inspections');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2.5">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-[#D97706] shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-[#1F2328]">Lab Scrutiny Requested: Detergent Powder</p>
                        <p className="text-[11px] text-[#5F6368] mt-0.5">Packing date stamp illegible. Awaiting batch documents.</p>
                        <span className="text-[10px] text-[#8A8F98] mt-1 block">2 hours ago • Western Division</span>
                      </div>
                    </div>
                  </div>
                  <div
                    className="p-3 hover:bg-[#FAF9F7] transition cursor-pointer"
                    onClick={() => {
                      navigate('/reports');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2.5">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-[#16A34A] shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-[#1F2328]">Official Report Ready: Basmati Rice 5kg</p>
                        <p className="text-[11px] text-[#5F6368] mt-0.5">Mandatory declarations verified conforming. Ready to export.</p>
                        <span className="text-[10px] text-[#8A8F98] mt-1 block">Yesterday • Docket #INSP-2026-001</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-2.5 border-t border-[#E5E2DD] bg-[#FAF9F7] text-center">
                  <button
                    onClick={() => {
                      navigate('/audit-log');
                      setShowNotifications(false);
                    }}
                    className="text-xs text-[#6D28D9] font-semibold hover:underline cursor-pointer"
                  >
                    View All Activity Logs
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Profile Control: [User Icon] Rohit Patil ▼ */}
          <div className="relative" ref={profileMenuRef}>
            <button
              onClick={() => {
                setShowProfileMenu(!showProfileMenu);
                setShowNotifications(false);
              }}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-[#FAF9F7] hover:bg-[#F0EDE8] border border-[#E5E2DD] transition cursor-pointer"
              aria-label="User profile menu"
            >
              <div className="w-6 h-6 rounded-full bg-[#E5E2DD] text-[#5F6368] flex items-center justify-center text-xs">
                <User className="w-3.5 h-3.5" />
              </div>
              <span className="text-xs font-semibold text-[#1F2328] tracking-tight">
                {currentUser?.name || 'Rohit Patil'}
              </span>
              <ChevronDown className={`w-3.5 h-3.5 text-[#8A8F98] transition-transform ${showProfileMenu ? 'rotate-180' : ''}`} />
            </button>

            {/* Profile Dropdown */}
            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-[#E5E2DD] z-50 animate-in fade-in zoom-in-95 duration-100 overflow-hidden">
                <div className="p-4 border-b border-[#E5E2DD] bg-[#FFFCF8]">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-10 h-10 rounded-full bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE] flex items-center justify-center text-sm font-bold">
                      {currentUser?.name?.charAt(0) || 'R'}
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-sm font-bold text-[#1F2328] truncate">{currentUser?.name || 'Rohit Patil'}</p>
                      <p className="text-[11px] text-[#5F6368] font-mono">{currentUser?.badgeNumber || 'LM-MH-2022-0941'}</p>
                    </div>
                  </div>
                  <div className="mt-2.5 flex items-center justify-between">
                    <RoleBadge role={currentUser?.role || 'OFFICER'} />
                    <button
                      onClick={() => {
                        setShowProfileMenu(false);
                        setIsJurisdictionModalOpen(true);
                      }}
                      className="text-[11px] text-[#6D28D9] hover:underline flex items-center font-medium"
                    >
                      <MapPin className="w-3 h-3 mr-0.5" />
                      <span className="truncate max-w-[120px]">{activeJurisdictionLabel}</span>
                    </button>
                  </div>
                </div>

                {/* Role Switcher Demo */}
                <div className="p-3 border-b border-[#E5E2DD] bg-[#FAF9F7]">
                  <span className="text-[10px] font-bold text-[#8A8F98] uppercase tracking-wider block mb-2">
                    Demo Officer Roles
                  </span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {(['OFFICER', 'SENIOR_OFFICER', 'ADMIN', 'VIEWER'] as OfficerRole[]).map((r) => (
                      <button
                        key={r}
                        onClick={() => {
                          switchRole(r);
                          setShowProfileMenu(false);
                        }}
                        className={`text-[11px] px-2 py-1 rounded-md text-left border transition cursor-pointer ${
                          currentUser?.role === r
                            ? 'bg-[#7C3AED] text-white border-[#7C3AED] font-semibold'
                            : 'bg-white text-[#1F2328] border-[#E5E2DD] hover:bg-[#F5F3FF] hover:text-[#6D28D9]'
                        }`}
                      >
                        {r === 'OFFICER' && 'Inspector'}
                        {r === 'SENIOR_OFFICER' && 'Asst Controller'}
                        {r === 'ADMIN' && 'HQ Admin'}
                        {r === 'VIEWER' && 'Legal Auditor'}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Dropdown links */}
                <div className="p-1.5 space-y-0.5">
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setShowProfileMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs text-[#1F2328] hover:bg-[#F5F3FF] hover:text-[#6D28D9] rounded-lg flex items-center space-x-2 transition cursor-pointer"
                  >
                    <Sliders className="w-3.5 h-3.5 text-[#5F6368]" />
                    <span>Preferences & Settings</span>
                  </button>
                  <button
                    onClick={() => {
                      logout();
                      navigate('/login');
                      setShowProfileMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs text-[#DC2626] hover:bg-[#FEF2F2] rounded-lg flex items-center space-x-2 transition cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5 text-[#DC2626]" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Toggle */}
          <button
            onClick={() => setIsMobileNavOpen(!isMobileNavOpen)}
            className="md:hidden p-2 rounded-lg text-[#5F6368] hover:text-[#1F2328] hover:bg-[#FAF9F7] cursor-pointer"
            aria-label="Toggle Navigation Menu"
          >
            {isMobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {isMobileNavOpen && (
        <div className="md:hidden border-t border-[#E5E2DD] bg-[#FFFCF8] px-4 py-3 space-y-1 animate-in slide-in-from-top-2 duration-150">
          <button
            onClick={() => {
              navigate('/dashboard');
              setIsMobileNavOpen(false);
            }}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm rounded-lg ${
              isHomeActive ? 'bg-[#F5F3FF] text-[#6D28D9] font-semibold' : 'text-[#1F2328]'
            }`}
          >
            <Home className="w-4 h-4" />
            <span>Home</span>
          </button>
          <button
            onClick={() => {
              if (!currentInspection) startNewInspection(undefined, 2);
              navigate('/new-inspection?step=2');
              setIsMobileNavOpen(false);
            }}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm rounded-lg ${
              isScanActive ? 'bg-[#F5F3FF] text-[#6D28D9] font-semibold' : 'text-[#1F2328]'
            }`}
          >
            <Camera className="w-4 h-4" />
            <span>Scan & Analyze</span>
          </button>
          <button
            onClick={() => {
              navigate('/reports');
              setIsMobileNavOpen(false);
            }}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm rounded-lg ${
              isReportsActive ? 'bg-[#F5F3FF] text-[#6D28D9] font-semibold' : 'text-[#1F2328]'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Reports</span>
          </button>
          <button
            onClick={() => {
              navigate('/inspections');
              setIsMobileNavOpen(false);
            }}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm rounded-lg ${
              isHistoryActive ? 'bg-[#F5F3FF] text-[#6D28D9] font-semibold' : 'text-[#1F2328]'
            }`}
          >
            <History className="w-4 h-4" />
            <span>History</span>
          </button>
          <button
            onClick={() => {
              navigate('/settings');
              setIsMobileNavOpen(false);
            }}
            className={`w-full flex items-center space-x-2 px-3 py-2 text-sm rounded-lg ${
              isSettingsActive ? 'bg-[#F5F3FF] text-[#6D28D9] font-semibold' : 'text-[#1F2328]'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      )}

      {/* Jurisdiction Modal */}
      <JurisdictionModal
        isOpen={isJurisdictionModalOpen}
        onClose={() => setIsJurisdictionModalOpen(false)}
        currentJurisdiction={activeJurisdiction}
        onSave={(newJ) => {
          setActiveJurisdiction(newJ);
          if (currentInspection && currentInspection.finalDecision === 'Draft') {
            updateInspectionDetails({
              jurisdictionDetails: newJ
            });
          }
        }}
      />
    </header>
  );
};
