import React, { useState } from 'react';
import { Button, Form, Input, Card, Typography, Space, Divider, notification, Tag } from 'antd';
import { SafetyOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { demoApi } from '../services/api';

const { Title, Text, Paragraph } = Typography;

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const handleLogin = async (values: { email: string; password: string }) => {
    setLoading(true);
    await login(values.email, values.password);
    setLoading(false);
  };

  const handleSeedAndLogin = async () => {
    setSeeding(true);
    try {
      await demoApi.seed();
      notification.success({ message: 'Demo Data Seeded', description: 'Logging in as Safety Officer...' });
      await login('safety@mineguard.in', 'Safety@12345');
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
        background: '#fafafa',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}
    >
      <div style={{ width: '100%', maxWidth: 440 }}>
        {/* Logo & branding */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 56,
              height: 56,
              background: '#18181b',
              borderRadius: 14,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}
          >
            <SafetyOutlined style={{ fontSize: 28, color: '#fff' }} />
          </div>
          <Title level={3} style={{ margin: 0 }}>AI MineGuard</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Smart Governance & Compliance System · SIH 2026
          </Text>
          <br />
          <Tag color="default" style={{ marginTop: 8, fontSize: 11 }}>Module 1 — AI Compliance & Risk Engine</Tag>
        </div>

        <Card bordered style={{ borderRadius: 14, boxShadow: '0 4px 6px -1px rgba(0,0,0,0.08)' }}>
          <Form layout="vertical" onFinish={handleLogin} autoComplete="off">
            <Form.Item
              label="Email"
              name="email"
              rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}
            >
              <Input
                size="large"
                placeholder="safety@mineguard.in"
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
              style={{ height: 44 }}
            >
              Sign In
            </Button>
          </Form>

          <Divider style={{ fontSize: 12, color: '#a3a3a3' }}>DEMO QUICK ACCESS</Divider>

          <Paragraph style={{ fontSize: 12, textAlign: 'center', color: '#737373', marginBottom: 12 }}>
            No credentials? One click to seed demo mine data & login as Safety Officer.
          </Paragraph>

          <Button
            block
            size="large"
            loading={seeding}
            onClick={handleSeedAndLogin}
            style={{ height: 44, fontWeight: 600 }}
          >
            🚀 Seed Demo Data & Enter Dashboard
          </Button>

          <Divider style={{ margin: '16px 0 12px' }} />

          <div style={{ background: '#fafafa', borderRadius: 8, padding: 12 }}>
            <Text style={{ fontSize: 11, fontWeight: 600, display: 'block', marginBottom: 8 }}>Demo Credentials</Text>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              {[
                { role: 'Super Admin', email: 'admin@mineguard.in', pwd: 'Admin@12345' },
                { role: 'Mine Manager', email: 'manager@mineguard.in', pwd: 'Manager@12345' },
                { role: 'Safety Officer', email: 'safety@mineguard.in', pwd: 'Safety@12345' },
              ].map((u) => (
                <div
                  key={u.role}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: 11,
                    padding: '4px 0',
                    borderBottom: '1px solid #f0f0f0',
                    cursor: 'pointer',
                  }}
                  onClick={() => {
                    document.querySelector<HTMLInputElement>('input[type="email"]')!.value = u.email;
                  }}
                >
                  <Tag style={{ fontSize: 10 }}>{u.role}</Tag>
                  <Text type="secondary" style={{ fontSize: 11 }}>{u.email}</Text>
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
