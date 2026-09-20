import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, OfficerRole, Jurisdiction } from '../types';
import { MOCK_USERS } from '../data/mockUsers';

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  login: (
    email: string,
    role?: OfficerRole,
    officerName?: string,
    jurisdiction?: Jurisdiction
  ) => boolean;
  signUp: (
    officerName: string,
    email: string,
    password: string,
    jurisdiction: Jurisdiction,
    role?: OfficerRole
  ) => boolean;
  logout: () => void;
  switchRole: (role: OfficerRole) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('lmcs_current_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error(e);
      }
    }
    // Default to Enforcement Officer for demo
    return MOCK_USERS[0];
  });

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('lmcs_current_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('lmcs_current_user');
    }
  }, [currentUser]);

  const login = (
    email: string,
    rolePreference?: OfficerRole,
    officerName?: string,
    jurisdiction?: Jurisdiction
  ) => {
    let matched = MOCK_USERS.find(
      u => u.email.toLowerCase() === (email || '').toLowerCase()
    );

    if (!matched && rolePreference) {
      matched = MOCK_USERS.find(u => u.role === rolePreference);
    }

    let userObj: User;
    if (!matched) {
      userObj = { ...MOCK_USERS[0] };
    } else {
      userObj = { ...matched };
    }

    if (officerName && officerName.trim()) {
      userObj.name = officerName.trim();
    }
    if (email && email.trim()) {
      userObj.email = email.trim();
    }
    if (jurisdiction && jurisdiction.state) {
      userObj.jurisdictionDetails = { ...jurisdiction };
      const parts = [
        jurisdiction.city,
        jurisdiction.state,
        jurisdiction.pinCode ? `PIN: ${jurisdiction.pinCode}` : ''
      ].filter(Boolean);
      userObj.jurisdictionZone = parts.join(', ');
      try {
        localStorage.setItem('lmcs_active_jurisdiction', JSON.stringify(jurisdiction));
      } catch (e) {
        console.error(e);
      }
    }

    setCurrentUser(userObj);
    return true;
  };

  const signUp = (
    officerName: string,
    email: string,
    _password: string,
    jurisdiction: Jurisdiction,
    rolePreference: OfficerRole = 'OFFICER'
  ) => {
    const stateCode = (jurisdiction?.state || 'MH').slice(0, 2).toUpperCase();
    const parts = [
      jurisdiction?.city,
      jurisdiction?.state,
      jurisdiction?.pinCode ? `PIN: ${jurisdiction.pinCode}` : ''
    ].filter(Boolean);
    const jurisdictionSummary = parts.join(', ') || 'India';

    const newUser: User = {
      id: `USR-${Date.now()}`,
      name: officerName.trim() || 'Enforcement Officer',
      badgeNumber: `LM-${stateCode}-2026-${Math.floor(1000 + Math.random() * 9000)}`,
      role: rolePreference,
      department: 'Legal Metrology Enforcement Wing',
      jurisdictionZone: jurisdictionSummary,
      jurisdictionDetails: jurisdiction ? { ...jurisdiction } : undefined,
      email: email.trim(),
      phone: '+91 98201 14000',
      status: 'Active',
      lastActive: 'Just now'
    };

    if (jurisdiction) {
      try {
        localStorage.setItem('lmcs_active_jurisdiction', JSON.stringify(jurisdiction));
      } catch (e) {
        console.error(e);
      }
    }

    setCurrentUser(newUser);
    return true;
  };

  const logout = () => {
    setCurrentUser(null);
  };

  const switchRole = (role: OfficerRole) => {
    const targetUser = MOCK_USERS.find(u => u.role === role);
    if (targetUser) {
      setCurrentUser(targetUser);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        login,
        signUp,
        logout,
        switchRole
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
