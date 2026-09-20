import React, { useState, useMemo, useEffect, useRef } from 'react';
import {
  INDIAN_STATES_AND_UTS,
  getDistrictsForState,
  validatePinCode,
  getSamplePinForDistrict,
  PinValidationResult
} from '../../data/jurisdictionData';
import { Jurisdiction } from '../../types';
import { MapPin, Search, Check, AlertCircle, ChevronDown, Building2, Globe } from 'lucide-react';

export interface JurisdictionSelectorProps {
  value: Jurisdiction;
  onChange: (value: Jurisdiction) => void;
  layout?: 'grid' | 'stack' | 'compact';
  showTitle?: boolean;
  title?: string;
  subtitle?: string;
  disabled?: boolean;
  onValidationChange?: (isValid: boolean, errorText?: string) => void;
  showErrors?: boolean;
}

export const JurisdictionSelector: React.FC<JurisdictionSelectorProps> = ({
  value,
  onChange,
  layout = 'grid',
  showTitle = true,
  title = 'Jurisdiction',
  subtitle = 'Statutory territorial jurisdiction under Legal Metrology Rules, 2011',
  disabled = false,
  onValidationChange,
  showErrors = true
}) => {
  const [districtSearch, setDistrictSearch] = useState('');
  const [isDistrictDropdownOpen, setIsDistrictDropdownOpen] = useState(false);
  const districtDropdownRef = useRef<HTMLDivElement>(null);
  const districtSearchInputRef = useRef<HTMLInputElement>(null);
  const pinInputRef = useRef<HTMLInputElement>(null);

  const country = value.country || 'India';
  const state = value.state || '';
  const city = value.city || '';
  const pinCode = value.pinCode || '';

  // Cascading enabled states
  const isCountrySelected = Boolean(country && country.trim().length > 0);
  const isStateEnabled = !disabled && isCountrySelected;
  const isCityEnabled = !disabled && isStateEnabled && Boolean(state);
  const isPinEnabled = !disabled && isCityEnabled && Boolean(city);

  // Available districts for the selected state
  const availableDistricts = useMemo(() => {
    if (!state) return [];
    return getDistrictsForState(state);
  }, [state]);

  // Filtered districts according to search
  const filteredDistricts = useMemo(() => {
    if (!districtSearch.trim()) return availableDistricts;
    const query = districtSearch.toLowerCase();
    return availableDistricts.filter(d => d.toLowerCase().includes(query));
  }, [availableDistricts, districtSearch]);

  // PIN validation result
  const pinValidation: PinValidationResult = useMemo(() => {
    if (!pinCode) {
      return { isValid: false, error: 'Please enter a valid 6-digit PIN code.' };
    }
    return validatePinCode(pinCode, state, city);
  }, [pinCode, state, city]);

  // Close district dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        districtDropdownRef.current &&
        !districtDropdownRef.current.contains(event.target as Node)
      ) {
        setIsDistrictDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Report validation up to parent
  useEffect(() => {
    if (!onValidationChange) return;

    if (!isCountrySelected) {
      onValidationChange(false, 'Country must be selected.');
      return;
    }
    if (!state) {
      onValidationChange(false, 'Please select a State/Union Territory.');
      return;
    }
    if (!city) {
      onValidationChange(false, 'Please select a City/District.');
      return;
    }
    if (!pinCode || pinCode.length !== 6) {
      onValidationChange(false, 'PIN Code must contain exactly 6 digits.');
      return;
    }
    if (!pinValidation.isValid) {
      onValidationChange(false, pinValidation.error || 'PIN Code does not match the selected location.');
      return;
    }

    onValidationChange(true, undefined);
  }, [country, state, city, pinCode, pinValidation, isCountrySelected, onValidationChange]);

  // Handlers for cascading state updates
  const handleCountryChange = (newCountry: string) => {
    onChange({
      country: newCountry,
      state: '',
      city: '',
      pinCode: ''
    });
    setDistrictSearch('');
    setIsDistrictDropdownOpen(false);
  };

  const handleStateChange = (newState: string) => {
    onChange({
      country: country || 'India',
      state: newState,
      city: '',
      pinCode: ''
    });
    setDistrictSearch('');
    setIsDistrictDropdownOpen(false);
  };

  const handleCitySelect = (newCity: string) => {
    onChange({
      country: country || 'India',
      state,
      city: newCity,
      pinCode: '' // Reset PIN Code when City/District changes
    });
    setIsDistrictDropdownOpen(false);
    setDistrictSearch('');

    // Focus PIN input for immediate fast entry
    setTimeout(() => {
      pinInputRef.current?.focus();
    }, 50);
  };

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Only numbers accepted, max 6 digits
    const rawVal = e.target.value;
    const digitsOnly = rawVal.replace(/\D/g, '').slice(0, 6);
    onChange({
      country: country || 'India',
      state,
      city,
      pinCode: digitsOnly
    });
  };

  const samplePin = city ? getSamplePinForDistrict(state, city) : '';

  const handleApplySamplePin = () => {
    if (samplePin) {
      onChange({
        country: country || 'India',
        state,
        city,
        pinCode: samplePin
      });
    }
  };

  const isFormValid = isCountrySelected && Boolean(state) && Boolean(city) && pinValidation.isValid;

  return (
    <div className="space-y-4">
      {showTitle && (
        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-md bg-[#F5F3FF] text-[#6D28D9] border border-[#DDD6FE] flex items-center justify-center font-bold">
              <MapPin className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">{title}</h3>
              {subtitle && <p className="text-[11px] text-slate-500">{subtitle}</p>}
            </div>
          </div>
          {isFormValid && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300">
              <Check className="w-3 h-3 mr-1 text-emerald-600" />
              Jurisdiction Validated
            </span>
          )}
        </div>
      )}

      {/* Grid of 4 Cascading Fields */}
      <div
        className={
          layout === 'grid'
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3'
            : layout === 'compact'
            ? 'grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs'
            : 'space-y-3'
        }
      >
        {/* 1. COUNTRY */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
            <span>Country</span>
            <span className="text-[10px] text-slate-400 font-normal">Default: India</span>
          </label>
          <div className="relative">
            <select
              value={country}
              disabled={disabled}
              onChange={(e) => handleCountryChange(e.target.value)}
              className="w-full appearance-none bg-white border border-slate-300 rounded px-3 py-1.5 text-xs text-slate-900 font-medium focus:outline-none focus:ring-1 focus:ring-[#0f2942] disabled:bg-slate-100 disabled:text-slate-400 cursor-pointer"
            >
              <option value="India">India</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
              <ChevronDown className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>

        {/* 2. STATE / UNION TERRITORY */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
            <span>State / Union Territory</span>
            <span className="text-[10px] text-slate-400 font-normal">28 States • 8 UTs</span>
          </label>
          <div className="relative">
            <select
              value={state}
              disabled={!isStateEnabled}
              onChange={(e) => handleStateChange(e.target.value)}
              className={`w-full appearance-none rounded px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-[#0f2942] cursor-pointer ${
                !isStateEnabled
                  ? 'bg-slate-100 border border-slate-200 text-slate-400 cursor-not-allowed'
                  : !state && showErrors
                  ? 'bg-amber-50/50 border border-amber-300 text-slate-800'
                  : 'bg-white border border-slate-300 text-slate-900'
              }`}
            >
              <option value="">Select State / UT ▼</option>
              <optgroup label="States (28)">
                {INDIAN_STATES_AND_UTS.filter(s => s.type === 'State').map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Union Territories (8)">
                {INDIAN_STATES_AND_UTS.filter(s => s.type === 'Union Territory').map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </optgroup>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
              <ChevronDown className="w-3.5 h-3.5" />
            </div>
          </div>
          {isStateEnabled && !state && showErrors && (
            <p className="text-[10px] text-amber-700 mt-1 flex items-center">
              <AlertCircle className="w-3 h-3 mr-1 shrink-0" />
              Please select a State/Union Territory.
            </p>
          )}
        </div>

        {/* 3. CITY / DISTRICT (Searchable Dropdown) */}
        <div ref={districtDropdownRef} className="relative">
          <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
            <span>City / District</span>
            {availableDistricts.length > 0 && (
              <span className="text-[10px] text-slate-400 font-normal">
                {availableDistricts.length} districts
              </span>
            )}
          </label>

          <button
            type="button"
            disabled={!isCityEnabled}
            onClick={() => {
              if (isCityEnabled) {
                setIsDistrictDropdownOpen(!isDistrictDropdownOpen);
                setTimeout(() => districtSearchInputRef.current?.focus(), 50);
              }
            }}
            className={`w-full flex items-center justify-between rounded px-3 py-1.5 text-xs text-left font-medium focus:outline-none focus:ring-1 focus:ring-[#0f2942] ${
              !isCityEnabled
                ? 'bg-slate-100 border border-slate-200 text-slate-400 cursor-not-allowed'
                : !city && showErrors
                ? 'bg-amber-50/50 border border-amber-300 text-slate-700 cursor-pointer'
                : 'bg-white border border-slate-300 text-slate-900 cursor-pointer'
            }`}
          >
            <span className={city ? 'font-semibold text-slate-900' : 'text-slate-500'}>
              {city || (state ? 'Select City / District ▼' : 'Select State first')}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0 ml-1" />
          </button>

          {/* Searchable Dropdown Menu */}
          {isDistrictDropdownOpen && isCityEnabled && (
            <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-300 rounded-md shadow-lg z-50 p-2 space-y-1.5 min-w-[220px]">
              {/* Search Bar */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2 top-2.5" />
                <input
                  ref={districtSearchInputRef}
                  type="text"
                  placeholder="Type to filter district..."
                  value={districtSearch}
                  onChange={(e) => setDistrictSearch(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded pl-7 pr-2 py-1 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-[#0f2942]"
                />
              </div>

              {/* District Options List */}
              <div className="max-h-48 overflow-y-auto divide-y divide-slate-100 text-xs">
                {filteredDistricts.length === 0 ? (
                  <div className="p-3 text-center text-slate-400 text-xs">
                    No district found matching "{districtSearch}"
                  </div>
                ) : (
                  filteredDistricts.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => handleCitySelect(d)}
                      className={`w-full text-left px-2.5 py-1.5 rounded transition flex items-center justify-between text-xs cursor-pointer ${
                        d.toLowerCase() === city.toLowerCase()
                          ? 'bg-[#7C3AED] text-white font-semibold'
                          : 'hover:bg-slate-100 text-slate-800'
                      }`}
                    >
                      <span>{d}</span>
                      {d.toLowerCase() === city.toLowerCase() && (
                        <Check className="w-3.5 h-3.5 text-amber-300 ml-1 shrink-0" />
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {isCityEnabled && !city && showErrors && (
            <p className="text-[10px] text-amber-700 mt-1 flex items-center">
              <AlertCircle className="w-3 h-3 mr-1 shrink-0" />
              Please select a City/District.
            </p>
          )}
        </div>

        {/* 4. PIN CODE */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center justify-between">
            <span>PIN Code</span>
            <span className="text-[10px] text-slate-400 font-normal">6-digit Indian PIN</span>
          </label>
          <div className="relative">
            <input
              ref={pinInputRef}
              type="text"
              inputMode="numeric"
              maxLength={6}
              disabled={!isPinEnabled}
              value={pinCode}
              onChange={handlePinChange}
              placeholder={isPinEnabled ? 'Enter 6-digit PIN' : 'Select City first'}
              className={`w-full rounded px-3 py-1.5 text-xs font-mono font-medium focus:outline-none focus:ring-1 ${
                !isPinEnabled
                  ? 'bg-slate-100 border border-slate-200 text-slate-400 cursor-not-allowed'
                  : pinCode.length === 6 && pinValidation.isValid
                  ? 'bg-emerald-50/40 border border-emerald-500 text-emerald-950 focus:ring-emerald-600'
                  : pinCode.length > 0 && !pinValidation.isValid && showErrors
                  ? 'bg-red-50/50 border border-red-400 text-red-950 focus:ring-red-500'
                  : 'bg-white border border-slate-300 text-slate-900 focus:border-[#7C3AED]'
              }`}
            />
            {pinCode.length === 6 && pinValidation.isValid && (
              <Check className="w-3.5 h-3.5 text-emerald-600 absolute right-2.5 top-2.5" />
            )}
          </div>

          {/* Validation Feedback Messages */}
          {isPinEnabled && showErrors && (
            <div>
              {pinCode.length > 0 && !pinValidation.isValid ? (
                <p className="text-[10px] text-red-700 mt-1 flex items-center font-medium">
                  <AlertCircle className="w-3 h-3 mr-1 shrink-0 text-red-600" />
                  {pinValidation.error}
                </p>
              ) : pinCode.length === 0 ? (
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[10px] text-slate-400">Must be 6 digits.</span>
                  {samplePin && (
                    <button
                      type="button"
                      onClick={handleApplySamplePin}
                      className="text-[10px] text-[#6D28D9] hover:underline font-medium cursor-pointer"
                    >
                      Fill sample: {samplePin}
                    </button>
                  )}
                </div>
              ) : pinValidation.warning ? (
                <p className="text-[10px] text-amber-700 mt-1">
                  {pinValidation.warning}
                </p>
              ) : null}
            </div>
          )}
        </div>
      </div>

      {/* Summary readout badge when fully selected */}
      {isFormValid && (
        <div className="bg-slate-50 border border-slate-200 rounded p-2 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-1">
          <div className="flex items-center space-x-1.5 text-slate-700">
            <Building2 className="w-3.5 h-3.5 text-[#6D28D9]" />
            <span className="font-semibold text-slate-900">Active Jurisdiction:</span>
            <span>
              {country} • {state} • {city} (PIN: <strong className="font-mono text-slate-900">{pinCode}</strong>)
            </span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono">
            Territorial Rule Alignment: Statutory Confirmed
          </div>
        </div>
      )}
    </div>
  );
};
