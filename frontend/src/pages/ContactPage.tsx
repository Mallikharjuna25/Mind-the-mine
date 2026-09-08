import React, { useState } from 'react';
import { Typography, Card, Row, Col, Tag, Button, Space, Form, Input, notification } from 'antd';
import {
  SafetyCertificateOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from '../components/ThemeToggle';
import logo from '../assets/logo.svg';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

export const ContactPage: React.FC = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    setTimeout(() => {
      notification.success({
        message: 'Message Dispatched',
        description: 'Your safety inquiry has been logged with the Kusmunda Area Control Room.',
      });
      form.resetFields();
      setSubmitting(false);
    }, 600);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: isDark ? '#050505' : '#fafafa',
        color: isDark ? 'rgba(255, 255, 255, 0.88)' : '#18181b',
        fontFamily: 'inherit',
        transition: 'background-color 0.2s ease, color 0.2s ease',
      }}
    >
      {/* ── TOP NAVBAR ────────────────────────────────────────────────────── */}
      <nav
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          background: isDark ? 'rgba(17, 17, 17, 0.92)' : 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(10px)',
          borderBottom: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
          padding: '0 32px',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => navigate('/')}>
          <img src={logo} alt="AI MineGuard Logo" style={{ width: 32, height: 32 }} />
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: -0.3, lineHeight: 1.2, color: isDark ? '#ffffff' : '#18181b' }}>
              AI MineGuard
            </div>
            <div style={{ fontSize: 10, color: isDark ? 'rgba(255, 255, 255, 0.55)' : '#71717a', fontWeight: 500 }}>
              Smart India Hackathon 2026
            </div>
          </div>
        </div>

        {/* Center links */}
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <Button type="link" onClick={() => navigate('/')} style={{ color: isDark ? '#a1a1aa' : '#52525b', padding: 0, fontSize: 14 }}>
            Home
          </Button>
          <Button type="link" onClick={() => navigate('/about')} style={{ color: isDark ? '#a1a1aa' : '#52525b', padding: 0, fontSize: 14 }}>
            About Platform
          </Button>
          <Button type="link" onClick={() => navigate('/contact')} style={{ color: isDark ? '#ffffff' : '#18181b', fontWeight: 600, padding: 0, fontSize: 14 }}>
            Contact & Support
          </Button>
          <Tag color="green" style={{ margin: 0, fontWeight: 600 }}>Module 1 Active</Tag>
        </div>

        {/* Right CTA */}
        <Space size={12}>
          <ThemeToggle size="middle" />
          <Button
            onClick={() => navigate('/login?role=worker')}
            style={{
              fontWeight: 500,
              borderColor: isDark ? '#27272a' : '#e4e4e7',
              background: isDark ? '#111111' : '#ffffff',
              color: isDark ? '#ffffff' : '#18181b',
            }}
          >
            <UserOutlined /> Worker Login
          </Button>
          <Button
            type="primary"
            onClick={() => navigate('/login?role=admin')}
            style={{
              background: isDark ? '#27272a' : '#18181b',
              borderColor: isDark ? '#3f3f46' : '#18181b',
              color: '#ffffff',
              fontWeight: 500,
            }}
          >
            <SafetyCertificateOutlined /> Admin Login
          </Button>
        </Space>
      </nav>

      {/* ── HEADER BANNER ─────────────────────────────────────────────────── */}
      <div style={{ padding: '60px 24px 30px', maxWidth: 1000, margin: '0 auto', textAlign: 'center' }}>
        <Tag color="default" style={{ padding: '4px 12px', fontSize: 12, fontWeight: 600, marginBottom: 16 }}>
          24/7 SUPPORT & STATUTORY DESK
        </Tag>
        <Title level={1} style={{ fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 800, margin: '0 0 16px', color: isDark ? '#ffffff' : '#18181b' }}>
          Contact & Safety Operations Center
        </Title>
        <Paragraph style={{ fontSize: 16, color: isDark ? '#a1a1aa' : '#71717a', maxWidth: 640, margin: '0 auto 32px' }}>
          Connect directly with the Kusmunda Mega Opencast Central Control Room, technical support team, or DGMS statutory reporting cell.
        </Paragraph>
      </div>

      {/* ── MAIN CONTENT ─────────────────────────────────────────────────── */}
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
        <Row gutter={[32, 32]}>
          {/* Contact Details Column */}
          <Col xs={24} md={10}>
            <Card
              bordered
              style={{
                borderRadius: 16,
                background: isDark ? '#111111' : '#ffffff',
                borderColor: isDark ? '#27272a' : '#e4e4e7',
                marginBottom: 24,
              }}
            >
              <Title level={4} style={{ color: isDark ? '#ffffff' : '#18181b', marginBottom: 20 }}>
                Operations HQ
              </Title>

              <Space direction="vertical" size={20} style={{ width: '100%' }}>
                <div style={{ display: 'flex', gap: 14 }}>
                  <EnvironmentOutlined style={{ fontSize: 20, color: '#16a34a', marginTop: 3 }} />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, color: isDark ? '#ffffff' : '#18181b' }}>Mine Location</div>
                    <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b', marginTop: 2 }}>
                      Kusmunda Area, SECL<br />
                      Post: Kusmunda Colliery, Korba<br />
                      Chhattisgarh — 495454, India
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 14 }}>
                  <PhoneOutlined style={{ fontSize: 20, color: '#dc2626', marginTop: 3 }} />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, color: isDark ? '#ffffff' : '#18181b' }}>Emergency Safety Hotline</div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: '#dc2626', marginTop: 2 }}>
                      1800-MINE-911 (Toll Free)
                    </div>
                    <div style={{ fontSize: 12, color: isDark ? '#a1a1aa' : '#71717a' }}>24/7 Monitored Gas & Pit Alarm Line</div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 14 }}>
                  <MailOutlined style={{ fontSize: 20, color: '#2563eb', marginTop: 3 }} />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, color: isDark ? '#ffffff' : '#18181b' }}>Statutory Desk Email</div>
                    <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b', marginTop: 2 }}>
                      safety@mineguard.in<br />
                      admin@mineguard.in
                    </div>
                  </div>
                </div>
              </Space>
            </Card>

            <Card
              bordered
              style={{
                borderRadius: 16,
                background: isDark ? '#111111' : '#ffffff',
                borderColor: isDark ? '#27272a' : '#e4e4e7',
              }}
            >
              <Title level={5} style={{ color: isDark ? '#ffffff' : '#18181b', marginBottom: 12 }}>
                DGMS Regulatory Inspection Cell
              </Title>
              <Paragraph style={{ fontSize: 12, color: isDark ? '#a1a1aa' : '#71717a', lineHeight: 1.6, margin: 0 }}>
                Directorate General of Mines Safety (DGMS), Bilaspur Region.<br />
                All statutory safety violations promoted via Module 1 are archived with encrypted audit trails per CMR 2017 standards.
              </Paragraph>
            </Card>
          </Col>

          {/* Inquiry Form Column */}
          <Col xs={24} md={14}>
            <Card
              bordered
              style={{
                borderRadius: 16,
                background: isDark ? '#111111' : '#ffffff',
                borderColor: isDark ? '#27272a' : '#e4e4e7',
                boxShadow: '0 4px 20px rgba(0,0,0,0.04)',
              }}
            >
              <Title level={3} style={{ color: isDark ? '#ffffff' : '#18181b', marginBottom: 6 }}>
                Submit Field Inquiry or Hazard Observation
              </Title>
              <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a', marginBottom: 24 }}>
                Report an on-ground condition, request system technical assistance, or notify the Safety Officer desk.
              </Paragraph>

              <Form form={form} layout="vertical" onFinish={handleSubmit}>
                <Row gutter={16}>
                  <Col xs={24} sm={12}>
                    <Form.Item label="Your Name" name="name" rules={[{ required: true, message: 'Please enter your name' }]}>
                      <Input size="large" placeholder="Rajesh Kumar" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Form.Item label="Employee / Badge ID" name="badgeId" rules={[{ required: true, message: 'Please enter badge ID' }]}>
                      <Input size="large" placeholder="SECL-KUS-4821" />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item label="Contact Email / Phone" name="contact" rules={[{ required: true, message: 'Please enter contact info' }]}>
                  <Input size="large" placeholder="operator@kusmunda.secl.in" />
                </Form.Item>

                <Form.Item label="Observation / Message Details" name="message" rules={[{ required: true, message: 'Please enter details' }]}>
                  <TextArea rows={4} placeholder="Describe pit observation, sensor query, or system support request..." />
                </Form.Item>

                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  block
                  loading={submitting}
                  icon={<SendOutlined />}
                  style={{
                    height: 46,
                    fontWeight: 600,
                    background: isDark ? '#27272a' : '#18181b',
                    borderColor: isDark ? '#3f3f46' : '#18181b',
                    color: '#ffffff',
                  }}
                >
                  Send Message to Safety Desk
                </Button>
              </Form>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};
