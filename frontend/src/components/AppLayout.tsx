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
  PlayCircleOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { demoApi } from '../services/api';
import logo from '../assets/logo.svg';

const { Header, Sider, Content } = Layout;

const menuItems: MenuProps['items'] = [
  { key: '/', icon: <DashboardOutlined />, label: 'Executive Dashboard' },
  { key: '/digital-twin', icon: <GlobalOutlined />, label: 'GIS Digital Twin' },
  {
    key: 'module1',
    label: 'Module 1 — AI Compliance',
    type: 'group',
    children: [
      { key: '/cctv', icon: <CameraOutlined />, label: 'CCTV Monitoring' },
      { key: '/equipment', icon: <ToolOutlined />, label: 'Equipment & OCR' },
      { key: '/environmental', icon: <AreaChartOutlined />, label: 'Gas Telemetry' },
      { key: '/risk-engine', icon: <ThunderboltOutlined />, label: 'Risk Engine' },
      { key: '/workflows', icon: <AlertOutlined />, label: 'Alerts & SLA' },
      { key: '/compliance', icon: <FileProtectOutlined />, label: 'Compliance Reports' },
    ],
  },
];

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [simulating, setSimulating] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const runSimulation = async (type: 'violation' | 'ocr' | 'gas') => {
    setSimulating(type);
    try {
      if (type === 'violation') await demoApi.simulateViolation();
      else if (type === 'ocr') await demoApi.simulateOcr();
      else await demoApi.simulateGasBreach();
      notification.success({
        message: 'Simulation Triggered',
        description: `${type === 'violation' ? 'CCTV PPE violation' : type === 'ocr' ? 'DGMS certificate OCR' : 'Methane gas breach'} simulated successfully.`,
        placement: 'topRight',
      });
    } catch {
      notification.error({ message: 'Simulation Error', description: 'Backend not reachable.' });
    } finally {
      setSimulating(null);
    }
  };

  const userMenu: MenuProps['items'] = [
    {
      key: 'role',
      label: (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 600 }}>{user?.full_name}</span>
          <span style={{ color: '#737373', fontSize: 12 }}>{user?.designation}</span>
        </Space>
      ),
      disabled: true,
    },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', danger: true },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* SIDEBAR */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={240}
        style={{
          borderRight: '1px solid #f0f0f0',
          background: '#fff',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        {/* Logo */}
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            padding: collapsed ? '0 20px' : '0 20px',
            borderBottom: '1px solid #f0f0f0',
            gap: 10,
            overflow: 'hidden',
            whiteSpace: 'nowrap',
          }}
        >
          <img src={logo} alt="logo" style={{ width: 28, height: 28, flexShrink: 0 }} />
          {!collapsed && (
            <div>
              <div style={{ fontWeight: 700, fontSize: 13, color: '#18181b', lineHeight: 1.3 }}>
                AI MineGuard
              </div>
              <div style={{ fontSize: 10, color: '#737373' }}>SIH 2026 · Module 1</div>
            </div>
          )}
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ border: 'none', marginTop: 8 }}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin 0.2s' }}>
        {/* HEADER */}
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
            position: 'sticky',
            top: 0,
            zIndex: 99,
            gap: 12,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ width: 40, height: 40 }}
          />

          {/* Live simulation toolbar */}
          <Space size={8} wrap style={{ flex: 1 }}>
            <Tag
              color="default"
              style={{ fontWeight: 600, fontSize: 11, letterSpacing: 0.5 }}
            >
              DEMO CONTROLS
            </Tag>
            <Button
              size="small"
              icon={<PlayCircleOutlined />}
              loading={simulating === 'violation'}
              onClick={() => runSimulation('violation')}
            >
              PPE Violation
            </Button>
            <Button
              size="small"
              icon={<PlayCircleOutlined />}
              loading={simulating === 'ocr'}
              onClick={() => runSimulation('ocr')}
            >
              OCR Scan
            </Button>
            <Button
              size="small"
              danger
              icon={<PlayCircleOutlined />}
              loading={simulating === 'gas'}
              onClick={() => runSimulation('gas')}
            >
              Gas Breach
            </Button>
          </Space>

          <Space size={16}>
            <Badge count={3} size="small">
              <Button type="text" icon={<BellOutlined style={{ fontSize: 18 }} />} />
            </Badge>
            <Dropdown
              menu={{
                items: userMenu,
                onClick: ({ key }) => key === 'logout' && logout(),
              }}
              placement="bottomRight"
            >
              <Avatar
                size={32}
                icon={<UserOutlined />}
                style={{ background: '#18181b', cursor: 'pointer' }}
              />
            </Dropdown>
          </Space>
        </Header>

        {/* PAGE CONTENT */}
        <Content style={{ padding: 24, background: '#fafafa', minHeight: 'calc(100vh - 64px)' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
