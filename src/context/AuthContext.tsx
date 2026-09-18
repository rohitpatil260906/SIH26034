import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, OfficerRole } from '../types';
import { MOCK_USERS } from '../data/mockUsers';

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  login: (emailOrBadge: string, role?: OfficerRole) => boolean;
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

  const login = (emailOrBadge: string, rolePreference?: OfficerRole) => {
    let matched = MOCK_USERS.find(
      u => u.email.toLowerCase() === emailOrBadge.toLowerCase() ||
           u.badgeNumber.toLowerCase() === emailOrBadge.toLowerCase()
    );

    if (!matched && rolePreference) {
      matched = MOCK_USERS.find(u => u.role === rolePreference);
    }

    if (!matched) {
      // Fallback to primary officer
      matched = MOCK_USERS[0];
    }

    setCurrentUser(matched);
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
