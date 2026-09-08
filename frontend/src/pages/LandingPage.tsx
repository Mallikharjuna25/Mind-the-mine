import React from 'react';
import { Typography, Button, Card, Tag, Row, Col, Space, Divider, Alert } from 'antd';
import {
  SafetyCertificateOutlined,
  EyeOutlined,
  ToolOutlined,
  ThunderboltOutlined,
  AlertOutlined,
  UserOutlined,
  ArrowRightOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  FireOutlined,
  FileDoneOutlined,
  AuditOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from '../components/ThemeToggle';
import logo from '../assets/logo.svg';

const { Title, Paragraph, Text } = Typography;

export const LandingPage: React.FC = () => {
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
      {/* ── TOP STICKY NAVBAR ────────────────────────────────────────────── */}
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

        {/* Center navigation links */}
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <Button type="link" onClick={() => navigate('/')} style={{ color: isDark ? '#ffffff' : '#18181b', fontWeight: 600, padding: 0, fontSize: 14 }}>
            Home
          </Button>
          <Button type="link" onClick={() => navigate('/about')} style={{ color: isDark ? '#a1a1aa' : '#52525b', padding: 0, fontSize: 14 }}>
            About Platform
          </Button>
          <a href="#modules" style={{ color: isDark ? '#a1a1aa' : '#52525b', textDecoration: 'none', fontSize: 14, fontWeight: 500 }}>
            Modules
          </a>
          <a href="#roles" style={{ color: isDark ? '#a1a1aa' : '#52525b', textDecoration: 'none', fontSize: 14, fontWeight: 500 }}>
            Worker vs Admin
          </a>
          <Button type="link" onClick={() => navigate('/contact')} style={{ color: isDark ? '#a1a1aa' : '#52525b', padding: 0, fontSize: 14 }}>
            Contact & Support
          </Button>
          <Tag color="green" style={{ margin: 0, fontWeight: 600 }}>Module 1 Active</Tag>
        </div>

        {/* Right CTA + Theme Toggle */}
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
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            }}
          >
            <SafetyCertificateOutlined /> Admin Login
          </Button>
        </Space>
      </nav>

      {/* ── HERO SECTION ─────────────────────────────────────────────────── */}
      <section
        style={{
          padding: '80px 24px 60px',
          maxWidth: 1200,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
          <Tag
            color="default"
            style={{
              padding: '4px 12px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 600,
              background: isDark ? '#18181b' : '#f4f4f5',
              borderColor: isDark ? '#27272a' : '#e4e4e7',
              color: isDark ? 'rgba(255, 255, 255, 0.88)' : '#18181b',
            }}
          >
            🛡️ STATUTORY COAL MINE SAFETY & RISK INTELLIGENCE · CMR 2017
          </Tag>
        </div>

        <Title
          level={1}
          style={{
            fontSize: 'clamp(32px, 5vw, 56px)',
            fontWeight: 800,
            letterSpacing: -1.2,
            lineHeight: 1.15,
            maxWidth: 960,
            margin: '0 auto 20px',
            color: isDark ? '#ffffff' : '#09090b',
          }}
        >
          Autonomous AI Safety Governance & Compliance for Modern Mines
        </Title>

        <Paragraph
          style={{
            fontSize: 'clamp(16px, 2vw, 19px)',
            color: isDark ? '#a1a1aa' : '#71717a',
            maxWidth: 780,
            margin: '0 auto 36px',
            lineHeight: 1.6,
          }}
        >
          A unified, centralized intelligence platform orchestrating edge CCTV computer vision, continuous multi-gas sensor telemetry, automated DGMS statutory form compliance, and an explainable multi-factor dynamic risk engine.
        </Paragraph>

        {/* Action Buttons: Worker Login & Admin Login */}
        <Space size={16} wrap style={{ justifyContent: 'center', marginBottom: 48 }}>
          <Button
            type="primary"
            size="large"
            onClick={() => navigate('/login?role=worker')}
            style={{
              height: 52,
              padding: '0 32px',
              fontSize: 16,
              fontWeight: 600,
              background: '#0284c7',
              borderColor: '#0284c7',
              color: '#ffffff',
              borderRadius: 10,
              boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
            }}
          >
            <UserOutlined /> Worker Portal Login <ArrowRightOutlined />
          </Button>

          <Button
            size="large"
            onClick={() => navigate('/login?role=admin')}
            style={{
              height: 52,
              padding: '0 28px',
              fontSize: 16,
              fontWeight: 600,
              borderRadius: 10,
              background: isDark ? '#27272a' : '#18181b',
              borderColor: isDark ? '#3f3f46' : '#18181b',
              color: '#ffffff',
            }}
          >
            <SafetyCertificateOutlined /> Admin Portal Login
          </Button>

          <Button
            type="dashed"
            size="large"
            onClick={() => navigate('/about')}
            style={{
              height: 52,
              padding: '0 24px',
              fontSize: 15,
              fontWeight: 500,
              borderRadius: 10,
              borderColor: isDark ? '#3f3f46' : '#d4d4d8',
              color: isDark ? 'rgba(255, 255, 255, 0.88)' : 'inherit',
            }}
          >
            <InfoCircleOutlined /> About Platform
          </Button>
        </Space>

        {/* Live Metrics Strip */}
        <div
          style={{
            background: isDark ? '#111111' : '#ffffff',
            border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
            borderRadius: 16,
            padding: '24px 32px',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            maxWidth: 1060,
            margin: '0 auto',
          }}
        >
          <Row gutter={[24, 24]} align="middle">
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>99.4%</div>
              <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a', marginTop: 4 }}>YOLOv8 PPE Accuracy</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#16a34a' }}>&lt; 5s</div>
              <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a', marginTop: 4 }}>Statutory SLA Alert Trigger</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#2563eb' }}>100%</div>
              <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a', marginTop: 4 }}>DGMS CMR 2017 Aligned</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#d97706' }}>24/7</div>
              <div style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#71717a', marginTop: 4 }}>Continuous Gas Telemetry</div>
            </Col>
          </Row>
        </div>
      </section>

      {/* ── MODULE ARCHITECTURE SECTION ───────────────────────────────────── */}
      <section id="modules" style={{ padding: '60px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <Tag color="default" style={{ fontSize: 12, fontWeight: 600, padding: '2px 10px' }}>
            CENTRALIZED PLATFORM ARCHITECTURE
          </Tag>
          <Title level={2} style={{ marginTop: 12, marginBottom: 8, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>
            The 3 Mining Operations Modules
          </Title>
          <Paragraph type="secondary" style={{ fontSize: 16, maxWidth: 680, margin: '0 auto', color: isDark ? '#a1a1aa' : '#71717a' }}>
            Module 1 is fully active and working on this branch. Module 2 and Module 3 buttons are accessible in the UI on standby roadmap.
          </Paragraph>
        </div>

        <Row gutter={[24, 24]}>
          {/* MODULE 1 (ACTIVE & WORKING) */}
          <Col xs={24} lg={8}>
            <Card
              bordered
              style={{
                borderRadius: 16,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: isDark ? '2px solid #16a34a' : '2px solid #16a34a',
                background: isDark ? '#111111' : '#ffffff',
                boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
                position: 'relative',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Tag color="success" icon={<CheckCircleFilled />} style={{ fontWeight: 600, padding: '2px 8px' }}>
                  ACTIVE & WORKING
                </Tag>
                <Text code style={{ fontSize: 11 }}>BRANCH: malli</Text>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <SafetyCertificateOutlined style={{ fontSize: 26, color: '#16a34a' }} />
                <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Module 1: AI Compliance & Risk Engine</Title>
              </div>

              <Paragraph type="secondary" style={{ fontSize: 13, lineHeight: 1.6, color: isDark ? '#a1a1aa' : '#71717a' }}>
                Operational AI safety core: real-time YOLOv8 PPE detection, heavy equipment DGMS certificate OCR extraction, continuous underground toxic gas telemetry, explainable risk calculation ($R = w_v V + w_e E + w_p P + w_s S$), and SLA corrective escalations.
              </Paragraph>

              <Divider style={{ margin: '12px 0', borderColor: isDark ? '#27272a' : '#e4e4e7' }} />

              <Space direction="vertical" size={8} style={{ width: '100%', marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <EyeOutlined style={{ color: '#16a34a', marginTop: 3 }} />
                  <span><strong>AI CCTV Vision:</strong> Live worker helmet & vest compliance.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <ToolOutlined style={{ color: '#2563eb', marginTop: 3 }} />
                  <span><strong>Equipment OCR:</strong> DGMS machinery fitness verification.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <FireOutlined style={{ color: '#dc2626', marginTop: 3 }} />
                  <span><strong>Gas Telemetry:</strong> Multi-gas ($CH_4, CO, O_2$) breach alarms.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <ThunderboltOutlined style={{ color: '#d97706', marginTop: 3 }} />
                  <span><strong>Dynamic Risk Engine:</strong> Explainable composite risk formula.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <AlertOutlined style={{ color: '#9333ea', marginTop: 3 }} />
                  <span><strong>DGMS SLA Workflows:</strong> Statutory countdowns & escalation logs.</span>
                </div>
              </Space>

              <div style={{ marginTop: 'auto' }}>
                <Button
                  type="primary"
                  block
                  size="large"
                  onClick={() => navigate('/login?role=worker')}
                  style={{ background: '#16a34a', borderColor: '#16a34a', color: '#fff', fontWeight: 600 }}
                >
                  Launch Module 1 (Active) <ArrowRightOutlined />
                </Button>
              </div>
            </Card>
          </Col>

          {/* MODULE 2 (STANDBY) */}
          <Col xs={24} lg={8}>
            <Card
              bordered
              style={{
                borderRadius: 16,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
                background: isDark ? '#111111' : '#ffffff',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Tag color="blue" icon={<ClockCircleOutlined />} style={{ fontWeight: 600, padding: '2px 8px' }}>
                  PHASE 2 ROADMAP
                </Tag>
                <Tag color="default" style={{ fontSize: 11 }}>STANDBY</Tag>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <FileDoneOutlined style={{ fontSize: 26, color: '#2563eb' }} />
                <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Module 2: Field Operations & Inspection Management</Title>
              </div>

              <Paragraph type="secondary" style={{ fontSize: 13, lineHeight: 1.6, color: isDark ? '#a1a1aa' : '#71717a' }}>
                Comprehensive pit inspection framework including digital pre-shift overman sign-offs, heavy machinery roadworthiness inspections, geo-tagged hazard logging, and drone bench inspection uploads.
              </Paragraph>

              <Divider style={{ margin: '12px 0', borderColor: isDark ? '#27272a' : '#e4e4e7' }} />

              <Space direction="vertical" size={8} style={{ width: '100%', marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Digital Pit Pre-Shift Safety Walkaround Checklists.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Mobile Equipment Roadworthiness Pre-Operation Logs.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Geo-Tagged Danger Zones & Blast Clearance Buffers.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Drone Aerial Bench Highwall Stability Photo Logs.</span>
                </div>
              </Space>

              <div style={{ marginTop: 'auto' }}>
                <Alert
                  message="Navigation Button Active"
                  description="Module 2 button is present in the navigation bar. Features are on standby roadmap."
                  type="info"
                  showIcon
                  style={{ marginBottom: 12, fontSize: 12, padding: '8px 12px' }}
                />
                <Button
                  block
                  size="large"
                  onClick={() => navigate('/login?role=worker')}
                  style={{ borderColor: isDark ? '#27272a' : '#e4e4e7', color: isDark ? '#a1a1aa' : '#52525b', fontWeight: 500 }}
                >
                  View Module 2 Specs in Portal
                </Button>
              </div>
            </Card>
          </Col>

          {/* MODULE 3 (STANDBY) */}
          <Col xs={24} lg={8}>
            <Card
              bordered
              style={{
                borderRadius: 16,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
                background: isDark ? '#111111' : '#ffffff',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Tag color="purple" icon={<ClockCircleOutlined />} style={{ fontWeight: 600, padding: '2px 8px' }}>
                  PHASE 3 ROADMAP
                </Tag>
                <Tag color="default" style={{ fontSize: 11 }}>STANDBY</Tag>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <AuditOutlined style={{ fontSize: 26, color: '#9333ea' }} />
                <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Module 3: Contractor Governance Management</Title>
              </div>

              <Paragraph type="secondary" style={{ fontSize: 13, lineHeight: 1.6, color: isDark ? '#a1a1aa' : '#71717a' }}>
                End-to-end contractor workforce governance including biometric gate pass verification, statutory PF/ESI minimum wage escrow audits, safety training tracking, and agency blacklisting matrix.
              </Paragraph>

              <Divider style={{ margin: '12px 0', borderColor: isDark ? '#27272a' : '#e4e4e7' }} />

              <Space direction="vertical" size={8} style={{ width: '100%', marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Contractor Worker Biometric Identity Gate Access.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Statutory Wage, PF & ESI Escrow Compliance Audits.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Mandatory Vocational Safety Induction (VT) Records.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  <CheckCircleFilled style={{ color: '#71717a', marginTop: 3 }} />
                  <span>Contractor Agency Safety Rating & Blacklisting Matrix.</span>
                </div>
              </Space>

              <div style={{ marginTop: 'auto' }}>
                <Alert
                  message="Navigation Button Active"
                  description="Module 3 button is present in the navigation bar. Features are on standby roadmap."
                  type="info"
                  showIcon
                  style={{ marginBottom: 12, fontSize: 12, padding: '8px 12px' }}
                />
                <Button
                  block
                  size="large"
                  onClick={() => navigate('/login?role=worker')}
                  style={{ borderColor: isDark ? '#27272a' : '#e4e4e7', color: isDark ? '#a1a1aa' : '#52525b', fontWeight: 500 }}
                >
                  View Module 3 Specs in Portal
                </Button>
              </div>
            </Card>
          </Col>
        </Row>
      </section>

      {/* ── ROLE-BASED ACCESS GOVERNANCE SECTION (WORKER VS ADMIN) ────────── */}
      <section id="roles" style={{ padding: '60px 24px', background: isDark ? '#09090b' : '#f4f4f5' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <Tag color="default" style={{ fontSize: 12, fontWeight: 600, padding: '2px 10px' }}>
              WORKER VS ADMIN GOVERNANCE
            </Tag>
            <Title level={2} style={{ marginTop: 12, marginBottom: 8, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>
              Worker Features vs. Admin Authority
            </Title>
            <Paragraph type="secondary" style={{ fontSize: 16, color: isDark ? '#a1a1aa' : '#71717a' }}>
              Two distinct operational portals tailored for on-ground workforce safety and executive compliance governance.
            </Paragraph>
          </div>

          <Row gutter={[24, 24]}>
            {/* WORKER ROLE */}
            <Col xs={24} md={12}>
              <Card
                bordered
                style={{
                  borderRadius: 16,
                  height: '100%',
                  background: isDark ? '#111111' : '#ffffff',
                  border: isDark ? '1px solid #27272a' : '1px solid #d4d4d8',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      background: '#0284c7',
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <UserOutlined style={{ fontSize: 24, color: '#ffffff' }} />
                  </div>
                  <div>
                    <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Worker Portal</Title>
                    <Tag color="blue" style={{ fontSize: 11, marginTop: 2 }}>SAFETY_OFFICER / MINE_WORKER / OPERATOR</Tag>
                  </div>
                </div>

                <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  Tailored for on-ground mine workers, pit operators, overmen, and safety inspectors:
                </Paragraph>

                <Space direction="vertical" size={10} style={{ width: '100%', marginBottom: 24 }}>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#0284c7', marginTop: 2 }} />
                    <span><strong>Module 1 Active & Working:</strong> Live CCTV PPE detection feed, continuous gas sensor threshold alerts, and machinery fitness checks.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#0284c7', marginTop: 2 }} />
                    <span><strong>Shift Safety Checklist:</strong> Complete digital pre-shift checks and submit field safety notes directly from the pit.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#0284c7', marginTop: 2 }} />
                    <span><strong>Module 2 & 3 Visibility:</strong> Labeled buttons for Field Operations and Contractor Governance available on standby.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#0284c7', marginTop: 2 }} />
                    <span><strong>Safety Protected:</strong> Restricted from accidental mathematical weight recalibration and system simulation controls.</span>
                  </div>
                </Space>

                <Button
                  block
                  size="large"
                  onClick={() => navigate('/login?role=worker')}
                  style={{ borderColor: '#0284c7', color: '#0284c7', fontWeight: 600, background: isDark ? '#111111' : '#ffffff' }}
                >
                  Sign In as Worker / Safety Officer
                </Button>
              </Card>
            </Col>

            {/* ADMIN ROLE */}
            <Col xs={24} md={12}>
              <Card
                bordered
                style={{
                  borderRadius: 16,
                  height: '100%',
                  background: isDark ? '#111111' : '#ffffff',
                  border: isDark ? '1px solid #27272a' : '1px solid #d4d4d8',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      background: isDark ? '#27272a' : '#18181b',
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <SafetyCertificateOutlined style={{ fontSize: 24, color: '#ffffff' }} />
                  </div>
                  <div>
                    <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Admin Portal</Title>
                    <Tag color={isDark ? '#27272a' : '#18181b'} style={{ fontSize: 11, marginTop: 2 }}>SUPER_ADMIN / MINE_MANAGER</Tag>
                  </div>
                </div>

                <Paragraph style={{ fontSize: 13, color: isDark ? '#a1a1aa' : '#52525b' }}>
                  Designed for Directors General, Chief Inspectors, and Mine Managers with statutory decision-making authority:
                </Paragraph>

                <Space direction="vertical" size={10} style={{ width: '100%', marginBottom: 24 }}>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 2 }} />
                    <span><strong>Risk Engine Weights:</strong> Adjust $w_v, w_e, w_p, w_s$ multipliers and trigger automated score recomputations.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 2 }} />
                    <span><strong>Simulation & Drills:</strong> Execute live demo safety drill events (PPE breaches, gas leaks, OCR validation).</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 2 }} />
                    <span><strong>Statutory Violation Overrides:</strong> Legally verify, escalate, or dismiss flagged infractions with audit tracking.</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10, fontSize: 13 }}>
                    <CheckCircleFilled style={{ color: '#16a34a', marginTop: 2 }} />
                    <span><strong>System Data Seeding:</strong> Seed synthetic coal mine assets, zones, and equipment inventory.</span>
                  </div>
                </Space>

                <Button
                  type="primary"
                  block
                  size="large"
                  onClick={() => navigate('/login?role=admin')}
                  style={{ background: isDark ? '#27272a' : '#18181b', borderColor: isDark ? '#3f3f46' : '#18181b', color: '#fff', fontWeight: 600 }}
                >
                  Sign In as Administrator
                </Button>
              </Card>
            </Col>
          </Row>
        </div>
      </section>

      {/* ── STATUTORY STANDARDS & FOOTER ─────────────────────────────────── */}
      <section id="compliance" style={{ padding: '60px 24px', maxWidth: 1100, margin: '0 auto', textAlign: 'center' }}>
        <Title level={3} style={{ fontWeight: 700, marginBottom: 16, color: isDark ? '#ffffff' : '#18181b' }}>
          Statutory Regulatory Frameworks
        </Title>
        <Paragraph type="secondary" style={{ maxWidth: 700, margin: '0 auto 32px', fontSize: 15, color: isDark ? '#a1a1aa' : '#71717a' }}>
          Engineered to satisfy mandatory Indian mining safety regulations including the Coal Mines Regulations (CMR 2017), Mines Act 1952, and Director General of Mines Safety (DGMS) circulars.
        </Paragraph>

        <Space size={16} wrap style={{ justifyContent: 'center', marginBottom: 48 }}>
          <Tag style={{ padding: '6px 14px', fontSize: 13, borderRadius: 8 }}>CMR 2017 Regulation 166 (Ventilation & Gases)</Tag>
          <Tag style={{ padding: '6px 14px', fontSize: 13, borderRadius: 8 }}>CMR 2017 Regulation 184 (HEMM Safety & Speed)</Tag>
          <Tag style={{ padding: '6px 14px', fontSize: 13, borderRadius: 8 }}>Mines Act 1952 Section 22A (Emergency Powers)</Tag>
          <Tag style={{ padding: '6px 14px', fontSize: 13, borderRadius: 8 }}>DGMS Tech. Circular No. 6 (Automated Vision)</Tag>
        </Space>

        <div style={{ borderTop: isDark ? '1px solid #27272a' : '1px solid #e4e4e7', paddingTop: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src={logo} alt="logo" style={{ width: 24, height: 24 }} />
            <Text strong style={{ fontSize: 13, color: isDark ? '#ffffff' : '#18181b' }}>AI MineGuard · Smart India Hackathon 2026</Text>
          </div>
          <Space size={16}>
            <Button type="link" onClick={() => navigate('/about')} style={{ color: isDark ? '#a1a1aa' : '#71717a', padding: 0 }}>
              About
            </Button>
            <Button type="link" onClick={() => navigate('/contact')} style={{ color: isDark ? '#a1a1aa' : '#71717a', padding: 0 }}>
              Contact
            </Button>
          </Space>
          <Text type="secondary" style={{ fontSize: 12, color: isDark ? '#a1a1aa' : '#71717a' }}>
            Branch: <Text code>malli</Text> · Module 1 AI Compliance and Risk Engine
          </Text>
        </div>
      </section>
    </div>
  );
};
