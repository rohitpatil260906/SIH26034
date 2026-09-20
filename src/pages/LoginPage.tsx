import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useInspection } from '../context/InspectionContext';
import { Button } from '../components/ui/Button';
import {
  User,
  Mail,
  Lock,
  MapPin,
  Building2,
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2
} from 'lucide-react';
import { OfficerRole, Jurisdiction } from '../types';
import {
  INDIAN_STATES_AND_UTS,
  getDistrictsForState,
  validatePinCode,
  getSamplePinForDistrict
} from '../data/jurisdictionData';

type AuthMode = 'login' | 'signup';

export const LoginPage: React.FC = () => {
  const { login, signUp } = useAuth();
  const { setActiveJurisdiction } = useInspection();
  const navigate = useNavigate();

  // Mode: 'login' (default) or 'signup'
  const [authMode, setAuthMode] = useState<AuthMode>('login');

  // Form Fields
  const [officerName, setOfficerName] = useState('Rohit Patil');
  const [email, setEmail] = useState('rohit.patil@legalmetrology.gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const [confirmPassword, setConfirmPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Jurisdiction State (India is default)
  const [selectedState, setSelectedState] = useState('Maharashtra');
  const [selectedCity, setSelectedCity] = useState('Nashik');
  const [pinCode, setPinCode] = useState('422001');

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Available districts for the currently selected state
  const availableDistricts = useMemo(() => {
    if (!selectedState) return [];
    return getDistrictsForState(selectedState);
  }, [selectedState]);

  // Handle State Change
  const handleStateChange = (newState: string) => {
    setSelectedState(newState);
    const districts = getDistrictsForState(newState);
    const newDistrict = districts.length > 0 ? districts[0] : '';
    setSelectedCity(newDistrict);

    if (newDistrict) {
      const samplePin = getSamplePinForDistrict(newState, newDistrict);
      if (samplePin) setPinCode(samplePin);
    } else {
      setPinCode('');
    }

    // Clear state error if present
    if (errors.state) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.state;
        return next;
      });
    }
  };

  // Handle City Change
  const handleCityChange = (newCity: string) => {
    setSelectedCity(newCity);
    if (selectedState && newCity) {
      const samplePin = getSamplePinForDistrict(selectedState, newCity);
      if (samplePin) setPinCode(samplePin);
    }

    if (errors.city) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next.city;
        return next;
      });
    }
  };

  // Validate entire form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // 1. Email validation
    if (!email.trim()) {
      newErrors.email = authMode === 'login' ? 'Please enter your email.' : 'Please enter official email.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = authMode === 'login' ? 'Please enter a valid email address.' : 'Please enter a valid official email address.';
    }

    // 2. Password validation
    if (!password) {
      newErrors.password = 'Please enter your password.';
    } else if (authMode === 'signup' && password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    // Sign-up only fields validation
    if (authMode === 'signup') {
      // Officer Name validation
      if (!officerName.trim()) {
        newErrors.officerName = 'Please enter officer name.';
      }

      // Confirm Password (Sign-up only)
      if (!confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password.';
      } else if (password !== confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match.';
      }

      // State validation
      if (!selectedState) {
        newErrors.state = 'Please select your state.';
      }

      // City / District validation
      if (!selectedCity) {
        newErrors.city = 'Please select your city / district.';
      }

      // PIN Code validation
      const pinVal = validatePinCode(pinCode, selectedState, selectedCity);
      if (!pinVal.isValid) {
        newErrors.pinCode = pinVal.error || 'Please enter a valid PIN code.';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Form Submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);

    if (authMode === 'login') {
      login(email.trim(), 'OFFICER');
    } else {
      const jurisdictionPayload: Jurisdiction = {
        country: 'India',
        state: selectedState,
        city: selectedCity,
        pinCode: pinCode.trim()
      };

      // Update active jurisdiction in context & localStorage
      setActiveJurisdiction(jurisdictionPayload);
      signUp(officerName.trim(), email.trim(), password, jurisdictionPayload, 'OFFICER');
    }

    navigate('/dashboard');
  };

  // Quick Demo Account Execution
  const handleQuickDemoLogin = (
    role: OfficerRole,
    demoEmail: string,
    demoName: string,
    demoState: string,
    demoCity: string,
    demoPin: string
  ) => {
    setOfficerName(demoName);
    setEmail(demoEmail);
    setSelectedState(demoState);
    setSelectedCity(demoCity);
    setPinCode(demoPin);

    const jurisdictionPayload: Jurisdiction = {
      country: 'India',
      state: demoState,
      city: demoCity,
      pinCode: demoPin
    };

    setActiveJurisdiction(jurisdictionPayload);
    login(demoEmail, role, demoName, jurisdictionPayload);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F8F7F4] flex flex-col justify-between text-[#1F2328] font-sans antialiased">
      {/* Top Government Official Strip */}
      <header className="bg-[#FFFCF8] border-b border-[#E5E2DD] px-4 sm:px-8 py-2.5 text-xs flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <span className="font-bold text-[#1F2328] tracking-wider text-[11px] sm:text-xs">
            GOVERNMENT OF INDIA
          </span>
          <span className="text-[#8A8F98]">|</span>
          <span className="text-[#5F6368] hidden sm:inline text-xs">
            Ministry of Consumer Affairs, Food & Public Distribution
          </span>
          <span className="text-[#5F6368] sm:hidden text-[11px]">
            Legal Metrology
          </span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-[#5F6368]">
          <span className="w-2 h-2 rounded-full bg-[#16A34A] animate-pulse"></span>
          <span className="font-medium">National Enforcement Portal</span>
        </div>
      </header>

      {/* Main Authentication Centerpiece */}
      <main className="flex-1 flex items-center justify-center px-4 py-8 sm:py-12">
        <div className="w-full max-w-[480px] bg-white border border-[#E5E2DD] rounded-2xl shadow-sm overflow-hidden transition-all">
          {/* Header with National Emblem & VidhiCheck Branding */}
          <div className="pt-8 pb-6 px-6 sm:px-8 bg-[#FFFCF8] border-b border-[#E5E2DD] text-center space-y-4">
            {/* Government of India Emblem */}
            <div className="flex flex-col items-center justify-center space-y-1.5">
              <img
                src="/emblem-of-india.svg"
                alt="State Emblem of India"
                className="h-16 w-auto object-contain drop-shadow-xs"
              />
              <div className="space-y-0.5">
                <p className="text-[11px] font-bold tracking-widest text-[#1F2328] uppercase font-sans">
                  GOVERNMENT OF INDIA
                </p>
                <p className="text-xs font-semibold text-[#5F6368]">
                  Legal Metrology Department
                </p>
              </div>
            </div>

            {/* VidhiCheck Brand Presentation */}
            <div className="pt-2 border-t border-[#E5E2DD]/60 flex flex-col items-center">
              <div className="flex items-center justify-center gap-2">
                <div className="w-7 h-7 rounded-md bg-[#FFF1EA] border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F]">
                  <Building2 className="w-4 h-4 text-[#FF5A1F]" />
                </div>
                <h1 className="text-2xl font-extrabold text-[#1F2328] tracking-tight">
                  VidhiCheck
                </h1>
              </div>
              <p className="text-xs text-[#5F6368] mt-1 font-medium">
                AI-Powered Packaged Commodity Compliance Checker
              </p>
            </div>

            {/* Login / Sign Up Tab Toggle */}
            <div className="pt-2">
              <div
                role="tablist"
                aria-label="Authentication Mode"
                className="grid grid-cols-2 p-1 bg-[#F8F7F4] border border-[#E5E2DD] rounded-xl text-xs font-semibold"
              >
                <button
                  type="button"
                  role="tab"
                  id="tab-login"
                  aria-selected={authMode === 'login'}
                  aria-controls="auth-panel"
                  onClick={() => {
                    setAuthMode('login');
                    setErrors({});
                  }}
                  className={`py-2 px-3 rounded-lg transition-all duration-150 cursor-pointer ${
                    authMode === 'login'
                      ? 'bg-[#FF5A1F] text-white shadow-xs font-bold'
                      : 'text-[#5F6368] hover:text-[#1F2328]'
                  }`}
                >
                  Login
                </button>
                <button
                  type="button"
                  role="tab"
                  id="tab-signup"
                  aria-selected={authMode === 'signup'}
                  aria-controls="auth-panel"
                  onClick={() => {
                    setAuthMode('signup');
                    setErrors({});
                  }}
                  className={`py-2 px-3 rounded-lg transition-all duration-150 cursor-pointer ${
                    authMode === 'signup'
                      ? 'bg-[#FF5A1F] text-white shadow-xs font-bold'
                      : 'text-[#5F6368] hover:text-[#1F2328]'
                  }`}
                >
                  Sign Up
                </button>
              </div>
            </div>
          </div>

          {/* Form Panel */}
          <form
            id="auth-panel"
            role="tabpanel"
            aria-labelledby={authMode === 'login' ? 'tab-login' : 'tab-signup'}
            onSubmit={handleSubmit}
            noValidate
            className="p-6 sm:p-8 space-y-4"
          >
            {/* 1. Officer Name (Only in Sign Up) */}
            {authMode === 'signup' && (
              <div>
                <label
                  htmlFor="officerName"
                  className="block text-xs font-semibold text-[#1F2328] mb-1.5"
                >
                  Officer Name <span className="text-[#DC2626]">*</span>
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#8A8F98] absolute left-3 top-3 pointer-events-none" />
                  <input
                    id="officerName"
                    name="officerName"
                    type="text"
                    value={officerName}
                    onChange={(e) => {
                      setOfficerName(e.target.value);
                      if (errors.officerName) {
                        setErrors((prev) => {
                          const next = { ...prev };
                          delete next.officerName;
                          return next;
                        });
                      }
                    }}
                    placeholder="Enter officer name"
                    aria-invalid={!!errors.officerName}
                    aria-describedby={errors.officerName ? 'officerName-error' : undefined}
                    className={`w-full bg-[#FAF9F7] border rounded-lg pl-9 pr-3 py-2 text-xs text-[#1F2328] transition-colors focus:bg-white focus:outline-none ${
                      errors.officerName
                        ? 'border-[#DC2626] focus:border-[#DC2626]'
                        : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                    }`}
                    required
                  />
                </div>
                {errors.officerName && (
                  <p id="officerName-error" className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3 shrink-0" />
                    <span>{errors.officerName}</span>
                  </p>
                )}
              </div>
            )}

            {/* 2. Email / Official Email */}
            <div>
              <label
                htmlFor={authMode === 'login' ? 'email' : 'officialEmail'}
                className="block text-xs font-semibold text-[#1F2328] mb-1.5"
              >
                {authMode === 'login' ? 'Email' : 'Official Email'} <span className="text-[#DC2626]">*</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#8A8F98] absolute left-3 top-3 pointer-events-none" />
                <input
                  id={authMode === 'login' ? 'email' : 'officialEmail'}
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errors.email) {
                      setErrors((prev) => {
                        const next = { ...prev };
                        delete next.email;
                        return next;
                      });
                    }
                  }}
                  placeholder={authMode === 'login' ? 'Enter email' : 'Enter official email'}
                  aria-invalid={!!errors.email}
                  aria-describedby={errors.email ? 'email-error' : undefined}
                  className={`w-full bg-[#FAF9F7] border rounded-lg pl-9 pr-3 py-2 text-xs text-[#1F2328] transition-colors focus:bg-white focus:outline-none ${
                    errors.email
                      ? 'border-[#DC2626] focus:border-[#DC2626]'
                      : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                  }`}
                  required
                />
              </div>
              {errors.email && (
                <p id="email-error" className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3 shrink-0" />
                  <span>{errors.email}</span>
                </p>
              )}
            </div>

            {/* 3. Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="password"
                  className="block text-xs font-semibold text-[#1F2328]"
                >
                  Password <span className="text-[#DC2626]">*</span>
                </label>
                {authMode === 'login' && (
                  <button
                    type="button"
                    onClick={() =>
                      alert(
                        'Please contact the Central Legal Metrology Helpdesk at 1800-11-4000 or your Divisional Controller to reset credentials.'
                      )
                    }
                    className="text-[11px] text-[#FF5A1F] hover:underline cursor-pointer"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#8A8F98] absolute left-3 top-3 pointer-events-none" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errors.password) {
                      setErrors((prev) => {
                        const next = { ...prev };
                        delete next.password;
                        return next;
                      });
                    }
                  }}
                  placeholder={authMode === 'login' ? 'Enter password' : 'Create password (min 6 chars)'}
                  aria-invalid={!!errors.password}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                  className={`w-full bg-[#FAF9F7] border rounded-lg pl-9 pr-9 py-2 text-xs text-[#1F2328] transition-colors focus:bg-white focus:outline-none ${
                    errors.password
                      ? 'border-[#DC2626] focus:border-[#DC2626]'
                      : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                  }`}
                  required
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-[#8A8F98] hover:text-[#1F2328] cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p id="password-error" className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3 shrink-0" />
                  <span>{errors.password}</span>
                </p>
              )}

              {/* Create account link (Only on Login, placed below Password field) */}
              {authMode === 'login' && (
                <div className="flex items-center justify-end mt-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('signup');
                      setErrors({});
                    }}
                    className="text-[11px] text-[#FF5A1F] hover:underline cursor-pointer"
                  >
                    Create account
                  </button>
                </div>
              )}
            </div>

            {/* 4. Confirm Password (Only in Sign-Up) */}
            {authMode === 'signup' && (
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-xs font-semibold text-[#1F2328] mb-1.5"
                >
                  Confirm Password <span className="text-[#DC2626]">*</span>
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#8A8F98] absolute left-3 top-3 pointer-events-none" />
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      if (errors.confirmPassword) {
                        setErrors((prev) => {
                          const next = { ...prev };
                          delete next.confirmPassword;
                          return next;
                        });
                      }
                    }}
                    placeholder="Confirm password"
                    aria-invalid={!!errors.confirmPassword}
                    aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
                    className={`w-full bg-[#FAF9F7] border rounded-lg pl-9 pr-3 py-2 text-xs text-[#1F2328] transition-colors focus:bg-white focus:outline-none ${
                      errors.confirmPassword
                        ? 'border-[#DC2626] focus:border-[#DC2626]'
                        : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                    }`}
                    required
                  />
                </div>
                {errors.confirmPassword && (
                  <p id="confirmPassword-error" className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3 shrink-0" />
                    <span>{errors.confirmPassword}</span>
                  </p>
                )}
              </div>
            )}

            {/* ========================================================================= */}
            {/* 5. DEDICATED JURISDICTION SECTION (Sign Up Only) */}
            {/* ========================================================================= */}
            {authMode === 'signup' && (
              <div className="pt-2">
                <div className="bg-[#FAF9F7] border border-[#E5E2DD] rounded-xl p-3.5 space-y-3">
                  <div className="flex items-center justify-between pb-1 border-b border-[#E5E2DD]/80">
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-[#1F2328]">
                      <MapPin className="w-3.5 h-3.5 text-[#FF5A1F]" />
                      <span>Jurisdiction</span>
                    </div>
                    <span className="text-[10px] font-semibold text-[#5F6368] bg-white border border-[#E5E2DD] px-2 py-0.5 rounded-full">
                      Country: India
                    </span>
                  </div>

                  {/* State Dropdown */}
                  <div>
                    <label
                      htmlFor="stateSelect"
                      className="block text-[11px] font-semibold text-[#1F2328] mb-1"
                    >
                      State / Union Territory <span className="text-[#DC2626]">*</span>
                    </label>
                    <select
                      id="stateSelect"
                      name="state"
                      value={selectedState}
                      onChange={(e) => handleStateChange(e.target.value)}
                      className={`w-full bg-white border rounded-lg px-3 py-2 text-xs text-[#1F2328] cursor-pointer focus:outline-none ${
                        errors.state
                          ? 'border-[#DC2626] focus:border-[#DC2626]'
                          : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                      }`}
                    >
                      <option value="">Select State ▼</option>
                      {INDIAN_STATES_AND_UTS.map((s) => (
                        <option key={s.code} value={s.name}>
                          {s.name} ({s.type === 'Union Territory' ? 'UT' : 'State'})
                        </option>
                      ))}
                    </select>
                    {errors.state && (
                      <p className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 shrink-0" />
                        <span>{errors.state}</span>
                      </p>
                    )}
                  </div>

                  {/* Dependent City / District Dropdown */}
                  <div>
                    <label
                      htmlFor="citySelect"
                      className="block text-[11px] font-semibold text-[#1F2328] mb-1"
                    >
                      City / District <span className="text-[#DC2626]">*</span>
                    </label>
                    <select
                      id="citySelect"
                      name="city"
                      value={selectedCity}
                      disabled={!selectedState || availableDistricts.length === 0}
                      onChange={(e) => handleCityChange(e.target.value)}
                      className={`w-full bg-white border rounded-lg px-3 py-2 text-xs text-[#1F2328] cursor-pointer focus:outline-none disabled:bg-[#F0EDE8] disabled:cursor-not-allowed ${
                        errors.city
                          ? 'border-[#DC2626] focus:border-[#DC2626]'
                          : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                      }`}
                    >
                      <option value="">Select City / District ▼</option>
                      {availableDistricts.map((dist) => (
                        <option key={dist} value={dist}>
                          {dist}
                        </option>
                      ))}
                    </select>
                    {errors.city && (
                      <p className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 shrink-0" />
                        <span>{errors.city}</span>
                      </p>
                    )}
                  </div>

                  {/* PIN Code Field */}
                  <div>
                    <label
                      htmlFor="pinCode"
                      className="block text-[11px] font-semibold text-[#1F2328] mb-1"
                    >
                      PIN Code <span className="text-[#DC2626]">*</span>
                    </label>
                    <input
                      id="pinCode"
                      name="pinCode"
                      type="text"
                      maxLength={6}
                      value={pinCode}
                      onChange={(e) => {
                        const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                        setPinCode(val);
                        if (errors.pinCode) {
                          setErrors((prev) => {
                            const next = { ...prev };
                            delete next.pinCode;
                            return next;
                          });
                        }
                      }}
                      placeholder="Enter PIN Code (e.g. 422001)"
                      className={`w-full bg-white border rounded-lg px-3 py-2 text-xs text-[#1F2328] font-mono focus:outline-none ${
                        errors.pinCode
                          ? 'border-[#DC2626] focus:border-[#DC2626]'
                          : 'border-[#E5E2DD] focus:border-[#FF5A1F]'
                      }`}
                      required
                    />
                    {errors.pinCode && (
                      <p className="text-[11px] text-[#DC2626] mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 shrink-0" />
                        <span>{errors.pinCode}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isSubmitting}
              className="w-full mt-2"
            >
              {authMode === 'login' ? 'Log In' : 'Sign Up'}
            </Button>

            {/* ========================================================================= */}
            {/* INSTANT DEMO LOGINS SECTION */}
            {/* ========================================================================= */}
            <div className="pt-4 border-t border-[#E5E2DD]">
              <span className="text-[11px] font-bold text-[#5F6368] uppercase tracking-wider block mb-2 text-center">
                INSTANT DEMO LOGINS
              </span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() =>
                    handleQuickDemoLogin(
                      'OFFICER',
                      'rohit.patil@legalmetrology.gov.in',
                      'Rohit Patil',
                      'Maharashtra',
                      'Nashik',
                      '422001'
                    )
                  }
                  className="p-2.5 bg-[#FAF9F7] hover:bg-[#FFF1EA] border border-[#E5E2DD] hover:border-[#FF5A1F]/40 rounded-lg text-left transition cursor-pointer group"
                >
                  <p className="font-semibold text-xs text-[#1F2328] group-hover:text-[#FF5A1F]">
                    Demo Officer
                  </p>
                  <p className="text-[10px] text-[#5F6368] truncate mt-0.5">
                    Rohit Patil • Nashik
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    handleQuickDemoLogin(
                      'SENIOR_OFFICER',
                      'p.nambiar@legalmetrology.gov.in',
                      'Dr. Priya Nambiar',
                      'Maharashtra',
                      'Mumbai City',
                      '400001'
                    )
                  }
                  className="p-2.5 bg-[#FAF9F7] hover:bg-[#FFF1EA] border border-[#E5E2DD] hover:border-[#FF5A1F]/40 rounded-lg text-left transition cursor-pointer group"
                >
                  <p className="font-semibold text-xs text-[#1F2328] group-hover:text-[#FF5A1F]">
                    Demo Inspector
                  </p>
                  <p className="text-[10px] text-[#5F6368] truncate mt-0.5">
                    Dr. Priya Nambiar • Mumbai
                  </p>
                </button>
              </div>
            </div>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-xs text-[#5F6368] border-t border-[#E5E2DD]/60">
        © 2026 Legal Metrology Department • LegalMetro Compliance Scanner (LMCS)
      </footer>
    </div>
  );
};