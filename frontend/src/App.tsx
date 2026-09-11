import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp, Spin } from 'antd';
import { StyleProvider } from '@ant-design/cssinjs';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppLayout } from './components/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { AboutPage } from './pages/AboutPage';
import { ContactPage } from './pages/ContactPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { CCTVMonitoringPage } from './pages/CCTVMonitoringPage';
import { EquipmentOCRPage } from './pages/EquipmentOCRPage';
import { EnvironmentalPage } from './pages/EnvironmentalPage';
import { RiskEnginePage } from './pages/RiskEnginePage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { CompliancePage } from './pages/CompliancePage';

// Field Operations & Inspections
import { FieldInspectionsPage } from './pages/FieldInspectionsPage';
import { FieldHazardsPage } from './pages/FieldHazardsPage';
import { RemediationPage } from './pages/RemediationPage';
import { GISMapPage } from './pages/GISMapPage';
import { OfflineSyncPage } from './pages/OfflineSyncPage';

// Contractor & Worker Governance
import { ContractorsPage } from './pages/ContractorsPage';
import { WorkersPage } from './pages/WorkersPage';
import { TrainingPage } from './pages/TrainingPage';
import { GovernancePage } from './pages/GovernancePage';
import { WorkerPortalPage } from './pages/WorkerPortalPage';

const PROTECTED_ROUTES = [
  // Central Overview & Portal
  { path: '/', element: <DashboardPage /> },
  { path: '/dashboard', element: <DashboardPage /> },
  { path: '/worker-portal', element: <WorkerPortalPage /> },
  { path: '/digital-twin', element: <DigitalTwinPage /> },

  // AI Safety & Environmental Surveillance
  { path: '/cctv', element: <CCTVMonitoringPage /> },
  { path: '/equipment', element: <EquipmentOCRPage /> },
  { path: '/environmental', element: <EnvironmentalPage /> },
  { path: '/risk-engine', element: <RiskEnginePage /> },
  { path: '/workflows', element: <WorkflowsPage /> },
  { path: '/compliance', element: <CompliancePage /> },

  // Field Operations & Inspection Management
  { path: '/inspections', element: <FieldInspectionsPage /> },
  { path: '/field-hazards', element: <FieldHazardsPage /> },
  { path: '/remediation', element: <RemediationPage /> },
  { path: '/gis-map', element: <GISMapPage /> },
  { path: '/offline-sync', element: <OfflineSyncPage /> },

  // Contractor & Worker Compliance Governance
  { path: '/contractors', element: <ContractorsPage /> },
  { path: '/workers', element: <WorkersPage /> },
  { path: '/training', element: <TrainingPage /> },
  { path: '/governance', element: <GovernancePage /> },
];

const AppRoutes: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip="Loading AI MineGuard..." />
      </div>
    );
  }

  // When not logged in:
  if (!user) {
    return (
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  const isWorker = user.role === 'WORKER';

  // Role-specific routing:
  // Workers only have access to Worker Portal and Central Dashboard
  if (isWorker) {
    return (
      <Routes>
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/login" element={<Navigate to="/worker-portal" replace />} />
        <Route path="/" element={<AppLayout><WorkerPortalPage /></AppLayout>} />
        <Route path="/worker-portal" element={<AppLayout><WorkerPortalPage /></AppLayout>} />
        <Route path="/dashboard" element={<AppLayout><DashboardPage /></AppLayout>} />
        <Route path="*" element={<Navigate to="/worker-portal" replace />} />
      </Routes>
    );
  }

  // Admin routing: full access to operational and governance suites
  return (
    <Routes>
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      {PROTECTED_ROUTES.map((r) => (
        <Route
          key={r.path}
          path={r.path}
          element={<AppLayout>{r.element}</AppLayout>}
        />
      ))}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

const ConfiguredApp: React.FC = () => {
  const { configProps } = useTheme();

  return (
    <ConfigProvider {...configProps}>
      <AntApp>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </AntApp>
    </ConfigProvider>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <StyleProvider hashPriority="high">
        <ThemeProvider>
          <ConfiguredApp />
        </ThemeProvider>
      </StyleProvider>
    </BrowserRouter>
  );
};

export default App;
