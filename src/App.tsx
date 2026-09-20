import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { InspectionProvider } from './context/InspectionContext';
import { AppShell } from './components/layout/AppShell';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionHistoryPage } from './pages/InspectionHistoryPage';
import { InspectionDetailPage } from './pages/InspectionDetailPage';
import { ProductRepositoryPage } from './pages/ProductRepositoryPage';
import { ViolationsRegistryPage } from './pages/ViolationsRegistryPage';
import { LegalNoticePage } from './pages/LegalNoticePage';
import { RuleLibraryPage } from './pages/RuleLibraryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { UserManagementPage } from './pages/UserManagementPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { SettingsPage } from './pages/SettingsPage';

// Protected route guard
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <InspectionProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Route */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Application Routes inside AppShell */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppShell />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="scan" element={<NewInspectionPage />} />
              <Route path="new-inspection" element={<NewInspectionPage />} />
              <Route path="inspections" element={<InspectionHistoryPage />} />
              <Route path="history" element={<InspectionHistoryPage />} />
              <Route path="reports" element={<InspectionHistoryPage />} />
              <Route path="reports/:id" element={<InspectionDetailPage />} />
              <Route path="products" element={<ProductRepositoryPage />} />
              <Route path="violations" element={<ViolationsRegistryPage />} />
              <Route path="legal-notices" element={<LegalNoticePage />} />
              <Route path="rules" element={<RuleLibraryPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="users" element={<UserManagementPage />} />
              <Route path="audit-log" element={<AuditLogPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </InspectionProvider>
    </AuthProvider>
  );
};

export default App;
