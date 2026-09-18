import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Shield, Lock, User, CheckCircle2, AlertCircle } from 'lucide-react';
import { OfficerRole } from '../types';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('r.sharma@legalmetrology.gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const [rememberMe, setRememberMe] = useState(true);
  const [selectedRole, setSelectedRole] = useState<OfficerRole>('OFFICER');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(username, selectedRole);
    navigate('/dashboard');
  };

  const handleQuickDemoLogin = (role: OfficerRole, email: string) => {
    login(email, role);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between text-slate-900 font-sans">
      {/* Top Official Banner */}
      <div className="bg-[#0f2942] text-white px-4 py-2 text-xs flex items-center justify-between shadow-xs">
        <div className="flex items-center space-x-2">
          <span className="font-bold tracking-wide">GOVERNMENT OF INDIA</span>
          <span className="text-slate-400">|</span>
          <span className="text-slate-300">Ministry of Consumer Affairs, Food & Public Distribution</span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Official Enforcement Network (NIC Node)</span>
        </div>
      </div>

      {/* Main Form Center */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white border border-slate-300 rounded-md shadow-md overflow-hidden">
          {/* Header */}
          <div className="p-6 bg-slate-50 border-b border-slate-200 text-center space-y-2">
            <div className="w-14 h-14 rounded bg-[#0f2942] text-white flex items-center justify-center mx-auto shadow-sm">
              <Shield className="w-8 h-8 text-amber-300" />
            </div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight mt-1">
              LegalMetro Compliance Scanner
            </h2>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              LMCS • Packaged Commodity Inspection & Compliance System
            </p>
            <p className="text-[11px] text-slate-500">
              For Authorized Legal Metrology Officers & Enforcement Teams
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official Email / Officer Badge Number
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. r.sharma@legalmetrology.gov.in"
                  className="w-full bg-white border border-slate-300 rounded pl-9 pr-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942] focus:border-[#0f2942]"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700">
                  Secure Password
                </label>
                <a href="#forgot" onClick={(e) => { e.preventDefault(); alert('Please contact the Central Legal Metrology Controller Helpdesk at 1800-11-4000 to reset your nodal credentials.'); }} className="text-[11px] text-[#0f2942] hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded pl-9 pr-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-[#0f2942] focus:border-[#0f2942]"
                  required
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-600 pt-1">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded text-[#0f2942] focus:ring-[#0f2942] border-slate-300"
                />
                <span>Remember this terminal</span>
              </label>
              <span className="text-[11px] text-slate-500 font-mono">TLS 1.3 256-Bit</span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full mt-2"
            >
              Sign In to Enforcement Portal
            </Button>

            {/* Quick Demo Access Bar */}
            <div className="pt-4 border-t border-slate-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2 text-center">
                Instant Demo Logins (Smart India Hackathon)
              </span>
              <div className="grid grid-cols-2 gap-1.5 text-xs">
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('OFFICER', 'r.sharma@legalmetrology.gov.in')}
                  className="p-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded text-left"
                >
                  <p className="font-semibold text-[11px] text-slate-800">Field Inspector</p>
                  <p className="text-[10px] text-slate-500">Rajesh K. Sharma</p>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('SENIOR_OFFICER', 'p.nambiar@legalmetrology.gov.in')}
                  className="p-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded text-left"
                >
                  <p className="font-semibold text-[11px] text-slate-800">Asst. Controller</p>
                  <p className="text-[10px] text-slate-500">Dr. Priya Nambiar</p>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('ADMIN', 'v.rawat.controller@legalmetrology.gov.in')}
                  className="p-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded text-left"
                >
                  <p className="font-semibold text-[11px] text-slate-800">Zonal Admin</p>
                  <p className="text-[10px] text-slate-500">V. S. Rawat</p>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoLogin('VIEWER', 'a.deshmukh@legalmetrology.gov.in')}
                  className="p-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded text-left"
                >
                  <p className="font-semibold text-[11px] text-slate-800">Legal Auditor</p>
                  <p className="text-[10px] text-slate-500">Ananya Deshmukh</p>
                </button>
              </div>
            </div>
          </form>

          {/* Secure Access Indicator */}
          <div className="p-3 bg-slate-50 border-t border-slate-200 text-center text-[11px] text-slate-500 flex items-center justify-center space-x-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Authorized access only under Section 15 of Legal Metrology Act, 2009.</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="p-3 text-center text-[11px] text-slate-500 border-t border-slate-200 bg-white">
        © 2026 Legal Metrology Department • LegalMetro Compliance Scanner (LMCS) • Smart India Hackathon PS 26034
      </footer>
    </div>
  );
};
