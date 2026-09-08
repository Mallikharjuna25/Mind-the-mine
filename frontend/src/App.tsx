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
import { ModuleStandbyPage } from './pages/ModuleStandbyPage';

const PROTECTED_ROUTES = [
  { path: '/', element: <DashboardPage /> },
  { path: '/dashboard', element: <DashboardPage /> },
  { path: '/digital-twin', element: <DigitalTwinPage /> },
  { path: '/cctv', element: <CCTVMonitoringPage /> },
  { path: '/equipment', element: <EquipmentOCRPage /> },
  { path: '/environmental', element: <EnvironmentalPage /> },
  { path: '/risk-engine', element: <RiskEnginePage /> },
  { path: '/workflows', element: <WorkflowsPage /> },
  { path: '/compliance', element: <CompliancePage /> },
  { path: '/module-2', element: <ModuleStandbyPage moduleNumber={2} /> },
  { path: '/module-3', element: <ModuleStandbyPage moduleNumber={3} /> },
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

  // When logged in:
  return (
    <Routes>
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/login" element={<Navigate to="/" replace />} />
      {PROTECTED_ROUTES.map((r) => (
        <Route
          key={r.path}
          path={r.path}
          element={<AppLayout>{r.element}</AppLayout>}
        />
      ))}
      <Route path="*" element={<Navigate to="/" replace />} />
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
