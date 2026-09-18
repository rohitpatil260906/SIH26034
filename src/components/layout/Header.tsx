import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useInspection } from '../../context/InspectionContext';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Search,
  Shield,
  ChevronDown,
  LogOut,
  Sliders,
  MapPin,
  Camera,
  Layers,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { RoleBadge } from '../ui/Badge';
import { OfficerRole } from '../../types';

interface HeaderProps {
  onToggleMobileMenu: () => void;
  onOpenArchitecture?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileMenu, onOpenArchitecture }) => {
  const { currentUser, logout, switchRole } = useAuth();
  const { inspections, currentInspection, startNewInspection } = useInspection();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [activeZone, setActiveZone] = useState('Delhi NCR - Central Zone');

  // Search auto-complete or quick navigate
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    navigate(`/inspections?search=${encodeURIComponent(searchQuery)}`);
  };

  const pendingReviewsCount = inspections.filter((i) => i.status === 'Under Review').length;
  const recentViolationsCount = inspections.filter((i) => i.status === 'Non-Compliant').length;

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200 shadow-2xs">
      {/* Top National Strip */}
      <div className="bg-[#0b1d30] text-white px-4 py-1 text-[11px] flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-2 text-[11px]">
          <span className="font-bold tracking-wider uppercase text-amber-300">GOVERNMENT OF INDIA</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300 hidden sm:inline">Ministry of Consumer Affairs, Food & Public Distribution</span>
          <span className="hidden md:inline text-slate-500">|</span>
          <span className="hidden md:inline text-slate-300">Legal Metrology Division</span>
        </div>
        <div className="flex items-center space-x-3 text-slate-300 text-[10px]">
          <span className="hidden lg:inline text-slate-400">Legal Metrology (Packaged Commodities) Rules, 2011</span>
          <span className="px-2 py-0.5 bg-emerald-950/90 text-emerald-300 border border-emerald-700/60 rounded font-mono font-medium flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
            SECURE ENFORCEMENT NODE
          </span>
        </div>
      </div>

      {/* Main Action Header */}
      <div className="px-4 py-2.5 flex items-center justify-between">
        {/* Mobile toggle & Brand Logo */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-1.5 rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            aria-label="Toggle Navigation"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* National Emblem & LM-COMPASS Branding */}
          <div
            onClick={() => navigate('/dashboard')}
            className="flex items-center space-x-2.5 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#0f2942] text-white flex items-center justify-center font-bold text-base shadow-xs border border-slate-700 group-hover:border-amber-400 transition">
              <Shield className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-slate-900 text-sm tracking-tight">LM-COMPASS</span>
                <span className="text-[11px] font-bold text-amber-800 bg-amber-100/90 px-1.5 py-0.2 rounded border border-amber-300 font-mono">
                  VidhiCheck
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-medium leading-none mt-0.5">
                Legal Metrology Compliance & Inspection System
              </p>
            </div>
          </div>

          {/* Jurisdiction Tag */}
          <div className="hidden xl:flex items-center space-x-1.5 ml-4 pl-4 border-l border-slate-200 text-xs text-slate-600">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium text-slate-700">Jurisdiction:</span>
            <select
              value={activeZone}
              onChange={(e) => setActiveZone(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded px-2 py-0.5 text-xs text-slate-800 font-medium focus:outline-none focus:ring-1 focus:ring-slate-400"
            >
              <option value="Delhi NCR - Central Zone">Delhi NCR - Central Zone</option>
              <option value="Maharashtra - Mumbai Zone I">Maharashtra - Mumbai Zone I</option>
              <option value="Karnataka - Bengaluru South">Karnataka - Bengaluru South</option>
              <option value="Tamil Nadu - Chennai North">Tamil Nadu - Chennai North</option>
              <option value="West Bengal - Kolkata Central">West Bengal - Kolkata Central</option>
            </select>
          </div>
        </div>

        {/* Center/Right Actions: Scan Product Button, System Architecture, Search & Profile */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Prominent Quick "Scan Product" Button */}
          <button
            onClick={() => {
              if (!currentInspection) {
                startNewInspection(undefined, 2);
              }
              navigate('/new-inspection?step=2&camera=open');
            }}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs shadow-xs border border-amber-600 transition cursor-pointer"
            title="Scan Product Label using Camera or Photo Upload"
          >
            <Camera className="w-4 h-4 text-slate-950" />
            <span className="hidden sm:inline">Scan Product</span>
            <span className="sm:hidden">Scan</span>
          </button>

          {/* Technical Architecture Trigger */}
          {onOpenArchitecture && (
            <button
              onClick={onOpenArchitecture}
              className="hidden md:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs border border-slate-300 transition"
              title="View 4-Stage Computer Vision & OCR Architecture"
            >
              <Layers className="w-3.5 h-3.5 text-[#0f2942]" />
              <span>Architecture</span>
            </button>
          )}

          {/* Global Search */}
          <form onSubmit={handleSearchSubmit} className="hidden lg:block relative w-56 xl:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search product, barcode, rule..."
              className="w-full bg-slate-50 border border-slate-300 rounded-md pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0f2942] focus:border-[#0f2942]"
            />
          </form>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowProfileMenu(false);
              }}
              className="relative p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {pendingReviewsCount + recentViolationsCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500 ring-2 ring-white"></span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg border border-slate-200 z-50 animate-in fade-in duration-100">
                <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">Enforcement Alerts</span>
                  <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">
                    {pendingReviewsCount + recentViolationsCount} New
                  </span>
                </div>
                <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
                  <div
                    className="p-3 hover:bg-slate-50 transition cursor-pointer"
                    onClick={() => {
                      navigate('/violations');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-red-600 shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-slate-900">Non-Compliance Flagged: Heritage Mustard Oil</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Missing "inclusive of all taxes" under Rule 6(1)(e).</p>
                        <span className="text-[10px] text-slate-400 mt-1 block">15 mins ago • Connaught Place</span>
                      </div>
                    </div>
                  </div>
                  <div
                    className="p-3 hover:bg-slate-50 transition cursor-pointer"
                    onClick={() => {
                      navigate('/inspections');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-amber-500 shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-slate-900">Lab Scrutiny Requested: Detergent Powder</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Packing date stamp illegible. Awaiting batch documents.</p>
                        <span className="text-[10px] text-slate-400 mt-1 block">4 hours ago • Indore Central</span>
                      </div>
                    </div>
                  </div>
                  <div
                    className="p-3 hover:bg-slate-50 transition cursor-pointer"
                    onClick={() => {
                      navigate('/inspections');
                      setShowNotifications(false);
                    }}
                  >
                    <div className="flex items-start space-x-2">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-emerald-600 shrink-0"></span>
                      <div>
                        <p className="text-xs font-semibold text-slate-900">Routine Audit Passed: Annapurna Basmati 5kg</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">All mandatory declarations verified conforming.</p>
                        <span className="text-[10px] text-slate-400 mt-1 block">Yesterday • Karol Bagh</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-2 border-t border-slate-100 bg-slate-50 text-center">
                  <button
                    onClick={() => {
                      navigate('/audit-log');
                      setShowNotifications(false);
                    }}
                    className="text-xs text-[#0f2942] font-semibold hover:underline"
                  >
                    View Complete Audit Trail
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Officer Profile & Role Selector */}
          <div className="relative">
            <button
              onClick={() => {
                setShowProfileMenu(!showProfileMenu);
                setShowNotifications(false);
              }}
              className="flex items-center space-x-2 p-1.5 pl-2 rounded-md hover:bg-slate-100 border border-slate-200 transition text-left"
            >
              <div className="w-7 h-7 rounded-full bg-[#0f2942] text-amber-300 flex items-center justify-center text-xs font-bold">
                {currentUser?.name.charAt(0) || 'O'}
              </div>
              <div className="hidden sm:block text-left pr-1">
                <p className="text-xs font-semibold text-slate-900 leading-tight truncate max-w-[130px]">
                  {currentUser?.name || 'Officer'}
                </p>
                <p className="text-[10px] text-slate-500 font-mono leading-none mt-0.5">
                  {currentUser?.badgeNumber || 'LM-DEL-2018'}
                </p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-md shadow-lg border border-slate-200 z-50 animate-in fade-in duration-100">
                <div className="p-3 border-b border-slate-100 bg-slate-50">
                  <p className="text-xs font-bold text-slate-900">{currentUser?.name}</p>
                  <p className="text-[11px] text-slate-600 font-mono mt-0.5">{currentUser?.badgeNumber}</p>
                  <p className="text-[11px] text-slate-500 mt-1">{currentUser?.department}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <RoleBadge role={currentUser?.role || 'OFFICER'} />
                    <span className="text-[10px] text-emerald-700 font-medium flex items-center">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-1"></span>
                      Active Session
                    </span>
                  </div>
                </div>

                {/* Quick Role Switcher for Demonstrations */}
                <div className="p-3 border-b border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    DEMO: Switch Officer Role
                  </span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {(['OFFICER', 'SENIOR_OFFICER', 'ADMIN', 'VIEWER'] as OfficerRole[]).map((r) => (
                      <button
                        key={r}
                        onClick={() => {
                          switchRole(r);
                          setShowProfileMenu(false);
                        }}
                        className={`text-[11px] px-2 py-1 rounded text-left border transition ${
                          currentUser?.role === r
                            ? 'bg-[#0f2942] text-white border-[#0f2942] font-semibold'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
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

                <div className="p-1">
                  <button
                    onClick={() => {
                      navigate('/settings');
                      setShowProfileMenu(false);
                    }}
                    className="w-full text-left px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100 rounded flex items-center space-x-2"
                  >
                    <Sliders className="w-3.5 h-3.5 text-slate-500" />
                    <span>Regulatory Preferences & Defaults</span>
                  </button>
                  <button
                    onClick={() => {
                      logout();
                      navigate('/login');
                    }}
                    className="w-full text-left px-3 py-1.5 text-xs text-red-700 hover:bg-red-50 rounded flex items-center space-x-2 mt-1"
                  >
                    <LogOut className="w-3.5 h-3.5 text-red-600" />
                    <span>Sign Out from Officer Session</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
