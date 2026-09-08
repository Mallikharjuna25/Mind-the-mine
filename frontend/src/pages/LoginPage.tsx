import React, { useState, useEffect } from 'react';
import { Button, Form, Input, Card, Typography, Space, Divider, notification, Tag, Segmented, Alert } from 'antd';
import {
  SafetyOutlined,
  SafetyCertificateOutlined,
  UserOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from '../components/ThemeToggle';
import { demoApi } from '../services/api';
import logo from '../assets/logo.svg';

const { Title, Text, Paragraph } = Typography;

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form] = Form.useForm();

  const [portalType, setPortalType] = useState<'admin' | 'user'>('admin');
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const { isDark } = useTheme();

  // Parse query params to auto-switch tab if specified
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const roleParam = params.get('role');
    if (roleParam === 'user') {
      setPortalType('user');
      form.setFieldsValue({
        email: 'safety@mineguard.in',
        password: 'Safety@12345',
      });
    } else {
      setPortalType('admin');
      form.setFieldsValue({
        email: 'admin@mineguard.in',
        password: 'Admin@12345',
      });
    }
  }, [location.search, form]);

  const handlePortalSwitch = (val: string | number) => {
    const nextType = val as 'admin' | 'user';
    setPortalType(nextType);
    if (nextType === 'admin') {
      form.setFieldsValue({
        email: 'admin@mineguard.in',
        password: 'Admin@12345',
      });
    } else {
      form.setFieldsValue({
        email: 'safety@mineguard.in',
        password: 'Safety@12345',
      });
    }
  };

  const handleLogin = async (values: { email: string; password: string }) => {
    setLoading(true);
    const success = await login(values.email, values.password);
    setLoading(false);
    if (success) {
      navigate('/');
    }
  };

  const handleSeedAndLogin = async (asRole: 'admin' | 'user') => {
    setSeeding(true);
    try {
      await demoApi.seed();
      notification.success({
        message: 'Demo Data Initialized',
        description: `Synthetic mine data ready. Logging in as ${asRole === 'admin' ? 'Super Admin' : 'Safety Officer'}...`,
      });
      const creds = asRole === 'admin'
        ? { email: 'admin@mineguard.in', pwd: 'Admin@12345' }
        : { email: 'safety@mineguard.in', pwd: 'Safety@12345' };

      const success = await login(creds.email, creds.pwd);
      if (success) navigate('/');
    } catch {
      notification.error({ message: 'Seed Failed', description: 'Ensure the backend is running on port 8000.' });
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: isDark ? '#050505' : '#fafafa',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px 16px',
        transition: 'background-color 0.2s ease',
      }}
    >
      {/* Top action row: Back to landing link + Theme Toggle */}
      <div style={{ width: '100%', maxWidth: 460, marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          type="link"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
          style={{ padding: 0, color: isDark ? '#a1a1aa' : '#71717a', fontSize: 13 }}
        >
          Back to Overview / Landing Page
        </Button>
        <ThemeToggle size="small" />
      </div>

      <div style={{ width: '100%', maxWidth: 460 }}>
        {/* Header Branding */}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div
            style={{
              width: 52,
              height: 52,
              background: '#18181b',
              borderRadius: 14,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 12,
            }}
          >
            <img src={logo} alt="logo" style={{ width: 28, height: 28 }} />
          </div>
          <Title level={3} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>AI MineGuard Portal</Title>
          <Text type="secondary" style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a' }}>
            Statutory Safety & Compliance · Smart India Hackathon 2026
          </Text>
        </div>

        {/* Role Selector Segmented */}
        <div style={{ marginBottom: 16 }}>
          <Segmented
            block
            size="large"
            value={portalType}
            onChange={handlePortalSwitch}
            options={[
              {
                label: (
                  <div style={{ padding: '6px 0', fontWeight: 600 }}>
                    <SafetyCertificateOutlined style={{ marginRight: 6 }} />
                    Admin Login
                  </div>
                ),
                value: 'admin',
              },
              {
                label: (
                  <div style={{ padding: '6px 0', fontWeight: 600 }}>
                    <UserOutlined style={{ marginRight: 6 }} />
                    User / Officer Login
                  </div>
                ),
                value: 'user',
              },
            ]}
          />
        </div>

        {/* Role Permission Guidance Notice */}
        <Alert
          message={
            portalType === 'admin'
              ? '👑 Administrator Privileges'
              : '👷 Authorized Safety Officer / User Privileges'
          }
          description={
            portalType === 'admin'
              ? 'Enables risk engine dynamic weight tuning, demo simulation controls, statutory violation overrides, and managerial SLA recomputations.'
              : 'Enables live CCTV hazard monitoring, equipment fitness inspection, continuous gas telemetry review, and on-ground SLA corrective action submissions.'
          }
          type={portalType === 'admin' ? 'info' : 'success'}
          showIcon
          icon={portalType === 'admin' ? <SafetyCertificateOutlined /> : <SafetyOutlined />}
          style={{ marginBottom: 16, borderRadius: 10, fontSize: 12 }}
        />

        <Card
          bordered
          style={{
            borderRadius: 14,
            boxShadow: isDark ? '0 4px 20px rgba(0,0,0,0.5)' : '0 4px 12px rgba(0,0,0,0.06)',
            background: isDark ? '#111111' : '#fff',
            borderColor: isDark ? '#27272a' : '#e4e4e7',
          }}
        >
          <Form form={form} layout="vertical" onFinish={handleLogin} autoComplete="off">
            <Form.Item
              label="Authorized Email"
              name="email"
              rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}
            >
              <Input
                size="large"
                placeholder={portalType === 'admin' ? 'admin@mineguard.in' : 'safety@mineguard.in'}
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Enter password' }]}
            >
              <Input.Password
                size="large"
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </Form.Item>

            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loading}
              style={{
                height: 44,
                fontWeight: 600,
                background: portalType === 'admin' ? '#18181b' : '#0284c7',
                borderColor: portalType === 'admin' ? '#18181b' : '#0284c7',
              }}
            >
              Sign In to {portalType === 'admin' ? 'Admin Dashboard' : 'Safety Portal'}
            </Button>
          </Form>

          <Divider style={{ fontSize: 12, color: '#a3a3a3', margin: '20px 0 16px' }}>
            DEMO INSTANT ACCESS
          </Divider>

          <Paragraph style={{ fontSize: 12, textAlign: 'center', color: '#71717a', marginBottom: 12 }}>
            One-click initialization with synthetic Kusmunda Coal Mine test assets:
          </Paragraph>

          <Button
            block
            size="large"
            loading={seeding}
            onClick={() => handleSeedAndLogin(portalType)}
            style={{ height: 42, fontWeight: 600 }}
          >
            🚀 Seed & Login as {portalType === 'admin' ? 'Super Admin' : 'Safety Officer'}
          </Button>

          <Divider style={{ margin: '16px 0 12px' }} />

          {/* Quick Credential Pre-fill Helpers */}
          <div style={{ background: isDark ? '#18181b' : '#fafafa', borderRadius: 8, padding: 12, border: isDark ? '1px solid #27272a' : '1px solid #f0f0f0' }}>
            <Text style={{ fontSize: 11, fontWeight: 600, display: 'block', marginBottom: 8, color: isDark ? '#a1a1aa' : '#52525b' }}>
              Quick Credentials (Click to prefill)
            </Text>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              {[
                { role: 'Super Admin', email: 'admin@mineguard.in', pwd: 'Admin@12345', type: 'admin' },
                { role: 'Mine Manager', email: 'manager@mineguard.in', pwd: 'Manager@12345', type: 'admin' },
                { role: 'Safety Officer', email: 'safety@mineguard.in', pwd: 'Safety@12345', type: 'user' },
              ].map((u) => (
                <div
                  key={u.role}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: 11,
                    padding: '6px 8px',
                    borderRadius: 6,
                    background: form.getFieldValue('email') === u.email ? (isDark ? '#27272a' : '#e4e4e7') : 'transparent',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onClick={() => {
                    setPortalType(u.type as 'admin' | 'user');
                    form.setFieldsValue({ email: u.email, password: u.pwd });
                  }}
                >
                  <Space size={6}>
                    <Tag color={u.type === 'admin' ? 'default' : 'blue'} style={{ fontSize: 10 }}>
                      {u.role}
                    </Tag>
                    <Text style={{ fontSize: 11 }}>{u.email}</Text>
                  </Space>
                  <Text code style={{ fontSize: 10 }}>{u.pwd}</Text>
                </div>
              ))}
            </Space>
          </div>
        </Card>
      </div>
    </div>
  );
};
