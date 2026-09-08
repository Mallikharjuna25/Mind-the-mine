import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp, Spin } from 'antd';
import { StyleProvider } from '@ant-design/cssinjs';
import useShadcnTheme from './theme/shadcnTheme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppLayout } from './components/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { CCTVMonitoringPage } from './pages/CCTVMonitoringPage';
import { EquipmentOCRPage } from './pages/EquipmentOCRPage';
import { EnvironmentalPage } from './pages/EnvironmentalPage';
import { RiskEnginePage } from './pages/RiskEnginePage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { CompliancePage } from './pages/CompliancePage';

const ROUTES = [
  { path: '/', element: <DashboardPage /> },
  { path: '/digital-twin', element: <DigitalTwinPage /> },
  { path: '/cctv', element: <CCTVMonitoringPage /> },
  { path: '/equipment', element: <EquipmentOCRPage /> },
  { path: '/environmental', element: <EnvironmentalPage /> },
  { path: '/risk-engine', element: <RiskEnginePage /> },
  { path: '/workflows', element: <WorkflowsPage /> },
  { path: '/compliance', element: <CompliancePage /> },
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

  if (!user) return <LoginPage />;

  return (
    <AppLayout>
      <Routes>
        {ROUTES.map((r) => <Route key={r.path} path={r.path} element={r.element} />)}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
};

const App: React.FC = () => {
  const configProps = useShadcnTheme();

  return (
    <BrowserRouter>
      <StyleProvider hashPriority="high">
        <ConfigProvider {...configProps}>
          <AntApp>
            <AuthProvider>
              <AppRoutes />
            </AuthProvider>
          </AntApp>
        </ConfigProvider>
      </StyleProvider>
    </BrowserRouter>
  );
};

export default App;
