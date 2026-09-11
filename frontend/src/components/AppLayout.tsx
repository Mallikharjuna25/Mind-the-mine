import React, { useState } from 'react';
import { Layout, Menu, Badge, Button, Avatar, Dropdown, Space, Tag, notification } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  GlobalOutlined,
  CameraOutlined,
  ToolOutlined,
  AreaChartOutlined,
  ThunderboltOutlined,
  AlertOutlined,
  FileProtectOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SafetyCertificateOutlined,
  HomeOutlined,
  CheckCircleFilled,
  FileDoneOutlined,
  AuditOutlined,
  InfoCircleOutlined,
  PhoneOutlined,
  DownOutlined,
  FileSearchOutlined,
  FireOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from './ThemeToggle';
import { demoApi } from '../services/api';
import logo from '../assets/logo.svg';

const { Header, Sider, Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [simulating, setSimulating] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();
  const { isDark } = useTheme();

  const runSimulation = async (type: 'violation' | 'ocr' | 'gas') => {
    if (!isAdmin) {
      notification.warning({
        message: 'Admin Privilege Required',
        description: 'Demo simulation triggers are restricted to Administrator accounts.',
      });
      return;
    }
    setSimulating(type);
    try {
      if (type === 'violation') await demoApi.simulateViolation();
      else if (type === 'ocr') await demoApi.simulateOcr();
      else await demoApi.simulateGasBreach();
      notification.success({
        message: 'Simulation Triggered',
        description: `Live ${type.toUpperCase()} simulation event has been successfully dispatched to the streaming engine.`,
      });
    } catch {
      notification.error({
        message: 'Simulation Failed',
        description: 'Unable to reach backend simulation endpoints.',
      });
    } finally {
      setSimulating(null);
    }
  };

  const isWorker = user?.role === 'WORKER';

  const userMenu: MenuProps['items'] = [
    {
      key: 'user-info',
      disabled: true,
      label: (
        <div style={{ padding: '4px 0' }}>
          <div style={{ fontWeight: 600, color: isDark ? '#ffffff' : '#18181b' }}>{user?.full_name || 'User'}</div>
          <div style={{ fontSize: 11, color: isDark ? 'rgba(255, 255, 255, 0.55)' : '#71717a' }}>{user?.email}</div>
          <div style={{ fontSize: 10, marginTop: 4 }}>
            <Tag color={isAdmin ? 'purple' : 'blue'} style={{ fontSize: 10 }}>{user?.role}</Tag>
          </div>
        </div>
      ),
    },
    { type: 'divider' },
    { key: 'landing', icon: <GlobalOutlined />, label: 'Platform Portal Home' },
    { key: 'about', icon: <InfoCircleOutlined />, label: 'About DGMS & Architecture' },
    { key: 'contact', icon: <PhoneOutlined />, label: 'Emergency & Helpdesk' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Sign Out', danger: true },
  ];

  // Role-specific sidebar navigation:
  // - Worker sees ONLY Worker Portal & Central Dashboard
  // - Admin sees all operational subsystems WITHOUT the worker portal pass bar
  const menuItems: MenuProps['items'] = isWorker
    ? [
        {
          key: 'worker_group',
          label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: 8 }}>
              <span>Worker Space</span>
              <Tag color="cyan" style={{ fontSize: 9, margin: 0, padding: '0 4px', lineHeight: '16px' }}>PORTAL</Tag>
            </div>
          ),
          type: 'group',
          children: [
            { key: '/worker-portal', icon: <UserOutlined style={{ color: '#059669' }} />, label: 'My Digital RFID Pass & Records' },
            { key: '/dashboard', icon: <DashboardOutlined style={{ color: '#2563eb' }} />, label: 'Mine Safety Dashboard' },
            { key: '/digital-twin', icon: <GlobalOutlined style={{ color: '#7c3aed' }} />, label: 'GIS Digital Twin' },
          ],
        },
      ]
    : [
        { key: '/', icon: <DashboardOutlined />, label: 'Central Executive Dashboard' },
        { key: '/digital-twin', icon: <GlobalOutlined />, label: 'GIS Digital Twin' },
        {
          key: 'module1_group',
          label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: 8 }}>
              <span>AI Safety & Surveillance</span>
              <Tag color="green" style={{ fontSize: 9, margin: 0, padding: '0 4px', lineHeight: '16px' }}>ACTIVE</Tag>
            </div>
          ),
          type: 'group',
          children: [
            { key: '/cctv', icon: <CameraOutlined style={{ color: '#16a34a' }} />, label: 'CCTV PPE Feeds' },
            { key: '/equipment', icon: <ToolOutlined style={{ color: '#ca8a04' }} />, label: 'Equipment & OCR Scan' },
            { key: '/environmental', icon: <AreaChartOutlined style={{ color: '#0284c7' }} />, label: 'Environmental Telemetry' },
            { key: '/risk-engine', icon: <ThunderboltOutlined style={{ color: '#ea580c' }} />, label: 'Predictive Risk Index' },
            { key: '/workflows', icon: <AlertOutlined style={{ color: '#dc2626' }} />, label: 'Automated SOP Workflow' },
            { key: '/compliance', icon: <FileProtectOutlined style={{ color: '#9333ea' }} />, label: 'DGMS Statutory Logs' },
          ],
        },
        {
          key: 'module2_group',
          label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: 8 }}>
              <span>Field Operations & Audits</span>
              <Tag color="blue" style={{ fontSize: 9, margin: 0, padding: '0 4px', lineHeight: '16px' }}>ACTIVE</Tag>
            </div>
          ),
          type: 'group',
          children: [
            { key: '/inspections', icon: <FileDoneOutlined style={{ color: '#2563eb' }} />, label: 'Statutory Checklists' },
            { key: '/field-hazards', icon: <AlertOutlined style={{ color: '#ea580c' }} />, label: 'Hazards & AI Voice' },
            { key: '/remediation', icon: <SafetyCertificateOutlined style={{ color: '#059669' }} />, label: 'CAPA Remediation' },
            { key: '/gis-map', icon: <GlobalOutlined style={{ color: '#3b82f6' }} />, label: 'GIS Spatial Mine Map' },
            { key: '/offline-sync', icon: <SyncOutlined style={{ color: '#7c3aed' }} />, label: 'Offline Sync Center' },
          ],
        },
        {
          key: 'module3_group',
          label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: 8 }}>
              <span>Workforce Governance</span>
              <Tag color="purple" style={{ fontSize: 9, margin: 0, padding: '0 4px', lineHeight: '16px' }}>ACTIVE</Tag>
            </div>
          ),
          type: 'group',
          children: [
            { key: '/contractors', icon: <HomeOutlined style={{ color: '#9333ea' }} />, label: 'Contractor Directory' },
            { key: '/workers', icon: <UserOutlined style={{ color: '#2563eb' }} />, label: 'Workers & RFID Pass' },
            { key: '/training', icon: <AuditOutlined style={{ color: '#16a34a' }} />, label: 'DGMS Safety Induction' },
            { key: '/governance', icon: <FileProtectOutlined style={{ color: '#dc2626' }} />, label: 'Grievances & Approvals' },
          ],
        },
      ];

  const simulationMenuItems: MenuProps['items'] = [
    {
      key: 'violation',
      icon: <AlertOutlined style={{ color: '#ea580c' }} />,
      label: 'Simulate PPE Breach (CCTV Feed)',
      disabled: simulating !== null,
      onClick: () => runSimulation('violation'),
    },
    {
      key: 'ocr',
      icon: <FileSearchOutlined style={{ color: '#2563eb' }} />,
      label: 'Simulate OCR Equipment Scan',
      disabled: simulating !== null,
      onClick: () => runSimulation('ocr'),
    },
    {
      key: 'gas',
      icon: <FireOutlined style={{ color: '#ef4444' }} />,
      label: 'Simulate CH₄ Gas Threshold Breach',
      danger: true,
      disabled: simulating !== null,
      onClick: () => runSimulation('gas'),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* SIDEBAR */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={268}
        style={{
          borderRight: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
          background: isDark ? '#050505' : '#ffffff',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        {/* Brand Header */}
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            padding: '0 18px',
            borderBottom: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
            gap: 10,
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          <img src={logo} alt="logo" style={{ width: 28, height: 28, flexShrink: 0 }} />
          {!collapsed && (
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: isDark ? '#ffffff' : '#18181b', lineHeight: 1.2 }}>
                AI MineGuard
              </div>
              <div style={{ fontSize: 10, color: isDark ? 'rgba(255, 255, 255, 0.55)' : '#71717a', fontWeight: 500 }}>
                {user?.role === 'WORKER' ? '👷 Worker Self-Service Portal' : (isAdmin ? '🛡️ Admin Authority Portal' : '👷 Safety Officer Portal')}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Menu */}
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ border: 'none', marginTop: 8 }}
        />
      </Sider>

      {/* MAIN LAYOUT */}
      <Layout style={{ marginLeft: collapsed ? 80 : 268, transition: 'margin 0.2s' }}>
        {/* HEADER */}
        <Header
          style={{
            background: isDark ? '#111111' : '#ffffff',
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
            position: 'sticky',
            top: 0,
            zIndex: 99,
            gap: 12,
            height: 64,
            whiteSpace: 'nowrap',
            flexWrap: 'nowrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ width: 36, height: 36 }}
            />

            {/* Top Navigation Switcher Buttons */}
            <Space size={6} wrap={false}>
              {isWorker ? (
                <>
                  <Button
                    size="small"
                    type={location.pathname === '/worker-portal' ? 'primary' : 'default'}
                    onClick={() => navigate('/worker-portal')}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      borderColor: '#059669',
                      color: location.pathname === '/worker-portal' ? '#fff' : '#059669',
                      background: location.pathname === '/worker-portal' ? '#059669' : undefined,
                    }}
                  >
                    👷 Worker Portal & Pass
                  </Button>
                  <Button
                    size="small"
                    type={['/', '/dashboard'].includes(location.pathname) ? 'primary' : 'default'}
                    onClick={() => navigate('/dashboard')}
                    style={{ fontSize: 11, fontWeight: 600 }}
                  >
                    Central Dashboard
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    size="small"
                    type={['/', '/dashboard', '/digital-twin'].includes(location.pathname) ? 'primary' : 'default'}
                    onClick={() => navigate('/dashboard')}
                    style={{ fontSize: 11, fontWeight: 600 }}
                  >
                    Central Dashboard
                  </Button>
                  <Button
                    size="small"
                    type={['/cctv', '/equipment', '/environmental', '/risk-engine', '/workflows', '/compliance'].includes(location.pathname) ? 'primary' : 'default'}
                    onClick={() => navigate('/cctv')}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      borderColor: '#16a34a',
                      color: ['/cctv', '/equipment', '/environmental', '/risk-engine', '/workflows', '/compliance'].includes(location.pathname) ? '#fff' : '#16a34a',
                      background: ['/cctv', '/equipment', '/environmental', '/risk-engine', '/workflows', '/compliance'].includes(location.pathname) ? '#16a34a' : undefined,
                    }}
                  >
                    AI Safety & Surveillance
                  </Button>
                  <Button
                    size="small"
                    type={['/inspections', '/field-hazards', '/remediation', '/gis-map', '/offline-sync'].includes(location.pathname) ? 'primary' : 'default'}
                    onClick={() => navigate('/inspections')}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      borderColor: '#2563eb',
                      color: ['/inspections', '/field-hazards', '/remediation', '/gis-map', '/offline-sync'].includes(location.pathname) ? '#fff' : '#2563eb',
                      background: ['/inspections', '/field-hazards', '/remediation', '/gis-map', '/offline-sync'].includes(location.pathname) ? '#2563eb' : undefined,
                    }}
                  >
                    Field Operations
                  </Button>
                  <Button
                    size="small"
                    type={['/contractors', '/workers', '/training', '/governance'].includes(location.pathname) ? 'primary' : 'default'}
                    onClick={() => navigate('/contractors')}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      borderColor: '#9333ea',
                      color: ['/contractors', '/workers', '/training', '/governance'].includes(location.pathname) ? '#fff' : '#9333ea',
                      background: ['/contractors', '/workers', '/training', '/governance'].includes(location.pathname) ? '#9333ea' : undefined,
                    }}
                  >
                    Workforce & Contractors
                  </Button>
                </>
              )}
            </Space>
          </div>

          {/* Center: Admin Simulation Dropdown OR User Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
            {isAdmin ? (
              <Space size={6} wrap={false}>
                <Dropdown menu={{ items: simulationMenuItems }} placement="bottom" arrow>
                  <Button
                    size="small"
                    icon={<ThunderboltOutlined style={{ color: simulating ? '#eab308' : '#3b82f6' }} />}
                    loading={simulating !== null}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      borderColor: isDark ? '#3f3f46' : '#d4d4d8',
                      background: isDark ? '#18181b' : '#f4f4f5',
                    }}
                  >
                    {simulating ? `Simulating ${simulating}...` : '⚡ Simulators'}{' '}
                    <DownOutlined style={{ fontSize: 9, marginLeft: 2 }} />
                  </Button>
                </Dropdown>
              </Space>
            ) : (
              <Space size={8} wrap={false}>
                <Tag color="green" icon={<CheckCircleFilled />} style={{ fontSize: 11, fontWeight: 500, margin: 0 }}>
                  Active Surveillance
                </Tag>
                <Tag color="blue" style={{ fontSize: 11, fontWeight: 500, margin: 0 }}>
                  Shift: General 08:00 - 16:00
                </Tag>
              </Space>
            )}
          </div>

          {/* Right: User Role Badge, Theme Toggle & Dropdown */}
          <Space size={12} style={{ flexShrink: 0 }}>
            <ThemeToggle size="middle" />

            {isAdmin ? (
              <Tag color="gold" style={{ fontWeight: 600, fontSize: 11, margin: 0, padding: '2px 8px' }}>
                👑 Admin Authority
              </Tag>
            ) : (
              <Tag color="blue" style={{ fontWeight: 600, fontSize: 11, margin: 0, padding: '2px 8px' }}>
                👷 Worker Access
              </Tag>
            )}

            <Badge count={2} size="small">
              <Button
                type="text"
                icon={<BellOutlined style={{ fontSize: 17 }} />}
                onClick={() => navigate('/workflows')}
              />
            </Badge>

            <Dropdown
              menu={{
                items: userMenu,
                onClick: ({ key }) => {
                  if (key === 'logout') logout();
                  if (key === 'landing') navigate('/landing');
                  if (key === 'about') navigate('/about');
                  if (key === 'contact') navigate('/contact');
                },
              }}
              placement="bottomRight"
            >
              <Avatar
                size={32}
                icon={<UserOutlined />}
                style={{
                  background: isAdmin ? (isDark ? '#27272a' : '#18181b') : '#0284c7',
                  cursor: 'pointer',
                  border: isDark ? '1px solid #3f3f46' : '1px solid #e4e4e7',
                }}
              />
            </Dropdown>
          </Space>
        </Header>

        {/* PAGE CONTENT */}
        <Content style={{ padding: 24, background: isDark ? '#050505' : '#fafafa', minHeight: 'calc(100vh - 64px)' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
