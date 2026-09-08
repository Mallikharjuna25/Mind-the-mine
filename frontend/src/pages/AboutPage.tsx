import React from 'react';
import { Typography, Card, Row, Col, Tag, Button, Space } from 'antd';
import {
  SafetyCertificateOutlined,
  UserOutlined,
  ArrowRightOutlined,
  CheckCircleFilled,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from '../components/ThemeToggle';
import logo from '../assets/logo.svg';

const { Title, Paragraph } = Typography;

export const AboutPage: React.FC = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();

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
          <Button type="link" onClick={() => navigate('/about')} style={{ color: isDark ? '#ffffff' : '#18181b', fontWeight: 600, padding: 0, fontSize: 14 }}>
            About Platform
          </Button>
          <Button type="link" onClick={() => navigate('/contact')} style={{ color: isDark ? '#a1a1aa' : '#52525b', padding: 0, fontSize: 14 }}>
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

      {/* ── HERO BANNER ───────────────────────────────────────────────────── */}
      <div style={{ padding: '60px 24px 40px', maxWidth: 1000, margin: '0 auto', textAlign: 'center' }}>
        <Tag color="default" style={{ padding: '4px 12px', fontSize: 12, fontWeight: 600, marginBottom: 16 }}>
          MISSION & ARCHITECTURE
        </Tag>
        <Title level={1} style={{ fontSize: 'clamp(28px, 4vw, 44px)', fontWeight: 800, margin: '0 0 16px', color: isDark ? '#ffffff' : '#18181b' }}>
          About AI MineGuard Platform
        </Title>
        <Paragraph style={{ fontSize: 16, color: isDark ? '#a1a1aa' : '#71717a', maxWidth: 760, margin: '0 auto 32px', lineHeight: 1.7 }}>
          AI MineGuard is an autonomous intelligence, statutory safety, and workforce compliance platform developed for modern opencast and underground coal mines under the Smart India Hackathon (SIH 2026) framework.
        </Paragraph>
      </div>

      {/* ── CONTENT SECTIONS ──────────────────────────────────────────────── */}
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
        {/* Core Vision Card */}
        <Card
          bordered
          style={{
            borderRadius: 16,
            background: isDark ? '#111111' : '#ffffff',
            borderColor: isDark ? '#27272a' : '#e4e4e7',
            marginBottom: 32,
            boxShadow: '0 4px 20px rgba(0,0,0,0.04)',
          }}
        >
          <Row gutter={[32, 24]} align="middle">
            <Col xs={24} md={14}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <SafetyCertificateOutlined style={{ fontSize: 28, color: '#16a34a' }} />
                <Title level={3} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>
                  Zero-Harm Mining Vision
                </Title>
              </div>
              <Paragraph style={{ color: isDark ? '#a1a1aa' : '#52525b', fontSize: 14, lineHeight: 1.7 }}>
                The Indian coal mining sector operates under stringent regulations set by the Directorate General of Mines Safety (DGMS) and Coal Mines Regulations (CMR 2017). Human oversights during pre-shift inspections, delayed response to toxic gas spikes, and lack of continuous PPE monitoring remain primary causes of preventable pit accidents.
              </Paragraph>
              <Paragraph style={{ color: isDark ? '#a1a1aa' : '#52525b', fontSize: 14, lineHeight: 1.7, margin: 0 }}>
                AI MineGuard unifies real-time computer vision, IoT environmental sensors, machinery OCR fitness logs, and multi-factor mathematical risk scoring into a centralized, explainable command dashboard accessible by both field workers and executive administrators.
              </Paragraph>
            </Col>
            <Col xs={24} md={10}>
              <div
                style={{
                  background: isDark ? '#18181b' : '#f4f4f5',
                  borderRadius: 12,
                  padding: 24,
                  border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
                }}
              >
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12, color: isDark ? '#ffffff' : '#18181b' }}>
                  Key Project Objectives
                </div>
                <Space direction="vertical" size={10} style={{ width: '100%', fontSize: 13 }}>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 3 }} />
                    <span>Real-time YOLOv8 PPE detection with sub-second alert triggers.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 3 }} />
                    <span>Continuous multi-gas telemetry ($CH_4, CO, O_2$) with automated statutory alarms.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 3 }} />
                    <span>Explainable multi-factor dynamic risk formula: $R = w_v V + w_e E + w_p P + w_s S$.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 3 }} />
                    <span>Enforced DGMS SLA countdowns with managerial escalation audit trails.</span>
                  </div>
                </Space>
              </div>
            </Col>
          </Row>
        </Card>

        {/* The 3-Module Breakdown */}
        <Title level={3} style={{ marginBottom: 20, color: isDark ? '#ffffff' : '#18181b' }}>
          Three-Module Centralized Architecture
        </Title>
        <Row gutter={[20, 20]}>
          {/* Module 1 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                background: isDark ? '#111111' : '#ffffff',
                border: isDark ? '2px solid #16a34a' : '2px solid #16a34a',
              }}
            >
              <Tag color="success" style={{ fontWeight: 600, marginBottom: 12 }}>
                ACTIVE ON THIS DEPLOYMENT
              </Tag>
              <Title level={4} style={{ margin: '0 0 8px', color: isDark ? '#ffffff' : '#18181b' }}>
                Module 1: AI Compliance and Risk Engine
              </Title>
              <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b', lineHeight: 1.6 }}>
                Fully functional edge surveillance engine covering AI CCTV PPE compliance, heavy equipment DGMS certificate OCR extraction, continuous gas telemetry alarms, explainable risk calculations, and SLA corrective workflows.
              </Paragraph>
            </Card>
          </Col>

          {/* Module 2 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                background: isDark ? '#111111' : '#ffffff',
                borderColor: isDark ? '#27272a' : '#e4e4e7',
              }}
            >
              <Tag color="blue" style={{ fontWeight: 600, marginBottom: 12 }}>
                PHASE 2 ROADMAP (STANDBY)
              </Tag>
              <Title level={4} style={{ margin: '0 0 8px', color: isDark ? '#ffffff' : '#18181b' }}>
                Module 2: Field Operations & Inspection Management
              </Title>
              <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b', lineHeight: 1.6 }}>
                Standardized digital pit inspection checklists, pre-shift mobile equipment roadworthiness verifications, geo-tagged blast zone clearance logging, and drone bench inspection uploads.
              </Paragraph>
            </Card>
          </Col>

          {/* Module 3 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                background: isDark ? '#111111' : '#ffffff',
                borderColor: isDark ? '#27272a' : '#e4e4e7',
              }}
            >
              <Tag color="purple" style={{ fontWeight: 600, marginBottom: 12 }}>
                PHASE 3 ROADMAP (STANDBY)
              </Tag>
              <Title level={4} style={{ margin: '0 0 8px', color: isDark ? '#ffffff' : '#18181b' }}>
                Module 3: Contractor Governance Management
              </Title>
              <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b', lineHeight: 1.6 }}>
                Comprehensive contractor firm onboarding, biometric worker identity verification, statutory PF/ESI wage compliance audits, mandatory safety induction tracking, and agency blacklisting matrix.
              </Paragraph>
            </Card>
          </Col>
        </Row>

        {/* CTA Bar */}
        <Card
          bordered
          style={{
            marginTop: 40,
            borderRadius: 16,
            background: isDark ? '#18181b' : '#18181b',
            borderColor: isDark ? '#27272a' : '#18181b',
            color: '#ffffff',
            textAlign: 'center',
            padding: '24px 16px',
          }}
        >
          <Title level={3} style={{ color: '#ffffff', margin: '0 0 8px' }}>
            Ready to Explore the Platform?
          </Title>
          <Paragraph style={{ color: 'rgba(255, 255, 255, 0.7)', maxWidth: 540, margin: '0 auto 24px' }}>
            Log in as a Worker to view on-ground active safety tasks and telemetry, or as an Administrator for complete governance authority.
          </Paragraph>
          <Space size={16} wrap>
            <Button
              size="large"
              onClick={() => navigate('/login?role=worker')}
              style={{ fontWeight: 600, background: '#ffffff', color: '#18181b', borderColor: '#ffffff', height: 44, padding: '0 24px' }}
            >
              <UserOutlined /> Access Worker Portal
            </Button>
            <Button
              type="primary"
              size="large"
              onClick={() => navigate('/login?role=admin')}
              style={{ fontWeight: 600, background: '#2563eb', borderColor: '#2563eb', height: 44, padding: '0 24px' }}
            >
              <SafetyCertificateOutlined /> Launch Admin Portal <ArrowRightOutlined />
            </Button>
          </Space>
        </Card>
      </div>
    </div>
  );
};
