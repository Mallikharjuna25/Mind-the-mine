import React from 'react';
import { Typography, Button, Card, Tag, Row, Col, Space, Divider } from 'antd';
import {
  SafetyCertificateOutlined,
  EyeOutlined,
  ToolOutlined,
  ThunderboltOutlined,
  AlertOutlined,
  UserOutlined,
  ArrowRightOutlined,
  FireOutlined,
  FileDoneOutlined,
  AuditOutlined,
  GlobalOutlined,
  IdcardOutlined,
  SyncOutlined,
  SafetyOutlined,
  TeamOutlined,
  DashboardOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { PublicNavbar } from '../components/PublicNavbar';
import logo from '../assets/logo.svg';

const { Title, Paragraph, Text } = Typography;

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();

  const cardBg = isDark ? '#111111' : '#ffffff';
  const borderColor = isDark ? '#27272a' : '#e4e4e7';
  const textColor = isDark ? 'rgba(255, 255, 255, 0.88)' : '#18181b';
  const secondaryTextColor = isDark ? '#a1a1aa' : '#71717a';

  return (
    <div
      style={{
        minHeight: '100vh',
        background: isDark ? '#050505' : '#fafafa',
        color: textColor,
        transition: 'background-color 0.2s ease, color 0.2s ease',
      }}
    >
      <PublicNavbar />

      {/* ── HERO SECTION ──────────────────────────────────────────── */}
      <section
        style={{
          padding: '72px 24px 48px',
          maxWidth: 1160,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
          <Tag
            color="default"
            style={{
              padding: '4px 14px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 600,
              background: isDark ? '#18181b' : '#f4f4f5',
              borderColor,
              color: textColor,
            }}
          >
            🛡️ ENTERPRISE MINING SAFETY & STATUTORY COMPLIANCE · CMR 2017
          </Tag>
        </div>

        <Title
          level={1}
          style={{
            fontSize: 'clamp(32px, 4.5vw, 54px)',
            fontWeight: 800,
            letterSpacing: -1.2,
            lineHeight: 1.18,
            maxWidth: 920,
            margin: '0 auto 20px',
            color: isDark ? '#ffffff' : '#09090b',
          }}
        >
          Autonomous Safety Intelligence & Workforce Governance for Modern Mining
        </Title>

        <Paragraph
          style={{
            fontSize: 'clamp(16px, 1.8vw, 18px)',
            color: secondaryTextColor,
            maxWidth: 780,
            margin: '0 auto 36px',
            lineHeight: 1.65,
          }}
        >
          AI MineGuard is a unified operational intelligence platform engineered for coal and metal mines.
          It combines edge computer vision, real-time subterranean gas telemetry, mobile-first field inspections,
          and digital workforce governance to eliminate hazards, protect workers, and automate DGMS compliance.
        </Paragraph>

        {/* Action Buttons */}
        <Space size={16} wrap style={{ justifyContent: 'center', marginBottom: 48 }}>
          <Button
            type="primary"
            size="large"
            onClick={() => navigate('/login?role=admin')}
            style={{
              height: 50,
              padding: '0 30px',
              fontSize: 15,
              fontWeight: 600,
              background: '#0284c7',
              borderColor: '#0284c7',
              color: '#ffffff',
              borderRadius: 8,
              boxShadow: '0 4px 14px rgba(2, 132, 199, 0.25)',
            }}
          >
            <SafetyCertificateOutlined /> Enter Operations Console <ArrowRightOutlined />
          </Button>

          <Button
            size="large"
            onClick={() => navigate('/login?role=worker')}
            style={{
              height: 50,
              padding: '0 28px',
              fontSize: 15,
              fontWeight: 600,
              borderRadius: 8,
              background: cardBg,
              borderColor,
              color: textColor,
            }}
          >
            <UserOutlined /> Worker Self-Service Portal
          </Button>
        </Space>

        {/* Live Metrics Strip */}
        <div
          style={{
            background: cardBg,
            border: `1px solid ${borderColor}`,
            borderRadius: 14,
            padding: '24px 32px',
            boxShadow: '0 8px 24px -4px rgba(0, 0, 0, 0.08)',
            maxWidth: 1040,
            margin: '0 auto',
          }}
        >
          <Row gutter={[24, 24]} align="middle">
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>99.4%</div>
              <div style={{ fontSize: 13, color: secondaryTextColor, marginTop: 4 }}>Vision AI PPE Accuracy</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#16a34a' }}>&lt; 5s</div>
              <div style={{ fontSize: 13, color: secondaryTextColor, marginTop: 4 }}>Statutory SLA Alert Speed</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#2563eb' }}>100%</div>
              <div style={{ fontSize: 13, color: secondaryTextColor, marginTop: 4 }}>DGMS CMR 2017 Aligned</div>
            </Col>
            <Col xs={12} sm={6}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#d97706' }}>24/7</div>
              <div style={{ fontSize: 13, color: secondaryTextColor, marginTop: 4 }}>Atmospheric Gas Telemetry</div>
            </Col>
          </Row>
        </div>
      </section>

      {/* ── OUR SOLUTION SECTION ──────────────────────────────────── */}
      <section
        id="solution"
        style={{
          padding: '64px 24px',
          maxWidth: 1160,
          margin: '0 auto',
          scrollMarginTop: 80,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 44 }}>
          <Tag color="blue" style={{ fontSize: 11, fontWeight: 600, padding: '2px 10px', textTransform: 'uppercase' }}>
            Unified Enterprise Solution
          </Tag>
          <Title level={2} style={{ marginTop: 12, marginBottom: 8, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>
            Our Solution
          </Title>
          <Paragraph style={{ fontSize: 15, maxWidth: 640, margin: '0 auto', color: secondaryTextColor }}>
            A single, comprehensive platform that replaces fragmented manual logs with automated, real-time safety governance.
          </Paragraph>
        </div>

        <Row gutter={[24, 24]}>
          {/* Solution Pillar 1 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: `1px solid ${borderColor}`,
                background: cardBg,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ background: 'rgba(22, 163, 74, 0.12)', padding: 10, borderRadius: 10 }}>
                  <SafetyCertificateOutlined style={{ fontSize: 24, color: '#16a34a' }} />
                </div>
                <div>
                  <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b', fontSize: 16 }}>
                    Surveillance & Risk Engine
                  </Title>
                  <Text type="secondary" style={{ fontSize: 11 }}>Continuous Site Sensing</Text>
                </div>
              </div>

              <Paragraph style={{ fontSize: 13, lineHeight: 1.6, color: secondaryTextColor }}>
                Automated continuous surveillance using edge computer vision and environmental IoT sensors to anticipate and mitigate hazards before accidents occur.
              </Paragraph>

              <Divider style={{ margin: '14px 0', borderColor }} />

              <Space direction="vertical" size={10} style={{ width: '100%' }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <EyeOutlined style={{ color: '#16a34a', marginTop: 2 }} />
                  <span><strong>AI CCTV Vision:</strong> Automated PPE verification & exclusion zone monitoring.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <ToolOutlined style={{ color: '#2563eb', marginTop: 2 }} />
                  <span><strong>Machinery Fitness:</strong> OCR verification of DGMS certificates & operator licenses.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <FireOutlined style={{ color: '#dc2626', marginTop: 2 }} />
                  <span><strong>Gas Telemetry:</strong> Real-time methane, carbon monoxide, and oxygen breach alarms.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <ThunderboltOutlined style={{ color: '#d97706', marginTop: 2 }} />
                  <span><strong>Dynamic Risk Matrix:</strong> Multi-factor mathematical risk index calculated per zone.</span>
                </div>
              </Space>
            </Card>
          </Col>

          {/* Solution Pillar 2 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: `1px solid ${borderColor}`,
                background: cardBg,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ background: 'rgba(37, 99, 235, 0.12)', padding: 10, borderRadius: 10 }}>
                  <FileDoneOutlined style={{ fontSize: 24, color: '#2563eb' }} />
                </div>
                <div>
                  <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b', fontSize: 16 }}>
                    Field Operations & Inspections
                  </Title>
                  <Text type="secondary" style={{ fontSize: 11 }}>Mobile-First Audit Workflow</Text>
                </div>
              </div>

              <Paragraph style={{ fontSize: 13, lineHeight: 1.6, color: secondaryTextColor }}>
                Empowers safety officers and pit inspectors with digitized workflows that operate seamlessly both online and in disconnected subterranean tunnels.
              </Paragraph>

              <Divider style={{ margin: '14px 0', borderColor }} />

              <Space direction="vertical" size={10} style={{ width: '100%' }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <FileDoneOutlined style={{ color: '#2563eb', marginTop: 2 }} />
                  <span><strong>Statutory Checklists:</strong> Standardized DGMS pre-shift and machinery audit forms.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <AlertOutlined style={{ color: '#ea580c', marginTop: 2 }} />
                  <span><strong>Voice Hazard Logging:</strong> AI converts spoken field notes into structured incident reports.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <SafetyOutlined style={{ color: '#059669', marginTop: 2 }} />
                  <span><strong>CAPA Remediation:</strong> Verifiable corrective actions backed by photo evidence.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <SyncOutlined style={{ color: '#7c3aed', marginTop: 2 }} />
                  <span><strong>Offline Sync Center:</strong> Subterranean mesh caching with automatic cloud sync.</span>
                </div>
              </Space>
            </Card>
          </Col>

          {/* Solution Pillar 3 */}
          <Col xs={24} md={8}>
            <Card
              bordered
              style={{
                borderRadius: 14,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: `1px solid ${borderColor}`,
                background: cardBg,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ background: 'rgba(147, 51, 234, 0.12)', padding: 10, borderRadius: 10 }}>
                  <TeamOutlined style={{ fontSize: 24, color: '#9333ea' }} />
                </div>
                <div>
                  <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b', fontSize: 16 }}>
                    Workforce & Contractor Governance
                  </Title>
                  <Text type="secondary" style={{ fontSize: 11 }}>Statutory Credentialing</Text>
                </div>
              </div>

              <Paragraph style={{ fontSize: 13, lineHeight: 1.6, color: secondaryTextColor }}>
                Maintains transparent, compliant governance over the entire mining workforce, contractor agencies, and heavy machinery operators.
              </Paragraph>

              <Divider style={{ margin: '14px 0', borderColor }} />

              <Space direction="vertical" size={10} style={{ width: '100%' }}>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <IdcardOutlined style={{ color: '#9333ea', marginTop: 2 }} />
                  <span><strong>Worker Pass & RFID:</strong> Biometric authentication & designated HEMM equipment rosters.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <AuditOutlined style={{ color: '#16a34a', marginTop: 2 }} />
                  <span><strong>DGMS Safety Induction:</strong> Tracking MVTR 1966 certifications & medical fitness.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <TeamOutlined style={{ color: '#2563eb', marginTop: 2 }} />
                  <span><strong>Contractor Vetting:</strong> Real-time KYC validation, insurance validity, & SLA tracking.</span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
                  <AlertOutlined style={{ color: '#dc2626', marginTop: 2 }} />
                  <span><strong>Grievance Resolution:</strong> Formal show-cause logs & dispute resolution workflows.</span>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </section>

      {/* ── THE USE OF THE WEBSITE SECTION ───────────────────────── */}
      <section
        id="platform-use"
        style={{
          padding: '64px 24px',
          maxWidth: 1160,
          margin: '0 auto',
          scrollMarginTop: 80,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 44 }}>
          <Tag color="purple" style={{ fontSize: 11, fontWeight: 600, padding: '2px 10px', textTransform: 'uppercase' }}>
            Role-Based Workflows
          </Tag>
          <Title level={2} style={{ marginTop: 12, marginBottom: 8, fontWeight: 800, color: isDark ? '#ffffff' : '#18181b' }}>
            The Use of the Website
          </Title>
          <Paragraph style={{ fontSize: 15, maxWidth: 680, margin: '0 auto', color: secondaryTextColor }}>
            How different stakeholders interact with AI MineGuard every shift to ensure zero preventable accidents and continuous statutory compliance.
          </Paragraph>
        </div>

        <Row gutter={[24, 24]}>
          {/* Persona 1: Mine Workers */}
          <Col xs={24} md={8}>
            <div
              style={{
                background: cardBg,
                border: `1px solid ${borderColor}`,
                borderRadius: 14,
                padding: '28px 24px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <UserOutlined style={{ fontSize: 22, color: '#10b981' }} />
                <Title level={4} style={{ margin: 0, fontSize: 17, color: isDark ? '#ffffff' : '#18181b' }}>
                  Mine Workers & Operators
                </Title>
              </div>
              <Paragraph style={{ fontSize: 13, color: secondaryTextColor, lineHeight: 1.6, flexGrow: 1 }}>
                Workers log in to access the <strong>Worker Portal & Digital Pass</strong>. Here, they view their shift schedule, confirm designated heavy machinery assignments, check medical exam fitness validity, and report safety hazards from the pit face.
              </Paragraph>
              <div style={{ background: isDark ? '#18181b' : '#f4f4f5', padding: '12px 16px', borderRadius: 8, marginTop: 16 }}>
                <Text style={{ fontSize: 12, fontWeight: 600 }}>Key Use Case:</Text>
                <div style={{ fontSize: 12, color: secondaryTextColor, marginTop: 4 }}>
                  • Access digital RFID mine entry pass<br />
                  • Check shift schedule & designated HEMM<br />
                  • Submit hazard alerts with voice notes
                </div>
              </div>
              <Button
                block
                style={{ marginTop: 20, fontWeight: 600 }}
                onClick={() => navigate('/login?role=worker')}
              >
                Go to Worker Portal →
              </Button>
            </div>
          </Col>

          {/* Persona 2: Field Safety Officers */}
          <Col xs={24} md={8}>
            <div
              style={{
                background: cardBg,
                border: `1px solid ${borderColor}`,
                borderRadius: 14,
                padding: '28px 24px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <SafetyCertificateOutlined style={{ fontSize: 22, color: '#2563eb' }} />
                <Title level={4} style={{ margin: 0, fontSize: 17, color: isDark ? '#ffffff' : '#18181b' }}>
                  Safety Officers & Inspectors
                </Title>
              </div>
              <Paragraph style={{ fontSize: 13, color: secondaryTextColor, lineHeight: 1.6, flexGrow: 1 }}>
                Safety officers use the site on tablets in the pit or control room. They execute mandatory pre-shift DGMS checklists, monitor live CCTV PPE detection feeds, receive gas breach warnings within 5 seconds, and verify CAPA remediation evidence.
              </Paragraph>
              <div style={{ background: isDark ? '#18181b' : '#f4f4f5', padding: '12px 16px', borderRadius: 8, marginTop: 16 }}>
                <Text style={{ fontSize: 12, fontWeight: 600 }}>Key Use Case:</Text>
                <div style={{ fontSize: 12, color: secondaryTextColor, marginTop: 4 }}>
                  • Conduct statutory pre-shift inspections<br />
                  • Review real-time gas threshold breaches<br />
                  • Verify CAPA before/after hazard closure
                </div>
              </div>
              <Button
                type="primary"
                block
                style={{ marginTop: 20, fontWeight: 600, background: '#2563eb', borderColor: '#2563eb' }}
                onClick={() => navigate('/login?role=admin')}
              >
                View Inspection Console →
              </Button>
            </div>
          </Col>

          {/* Persona 3: Mine Management */}
          <Col xs={24} md={8}>
            <div
              style={{
                background: cardBg,
                border: `1px solid ${borderColor}`,
                borderRadius: 14,
                padding: '28px 24px',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <DashboardOutlined style={{ fontSize: 22, color: '#9333ea' }} />
                <Title level={4} style={{ margin: 0, fontSize: 17, color: isDark ? '#ffffff' : '#18181b' }}>
                  Mine Managers & Leadership
                </Title>
              </div>
              <Paragraph style={{ fontSize: 13, color: secondaryTextColor, lineHeight: 1.6, flexGrow: 1 }}>
                Mine managers use the <strong>Central Executive Dashboard</strong> and <strong>GIS Digital Twin</strong> to observe site-wide safety posture, verify contractor KYC validity, monitor statutory SLA escalations, and generate official DGMS audit reports.
              </Paragraph>
              <div style={{ background: isDark ? '#18181b' : '#f4f4f5', padding: '12px 16px', borderRadius: 8, marginTop: 16 }}>
                <Text style={{ fontSize: 12, fontWeight: 600 }}>Key Use Case:</Text>
                <div style={{ fontSize: 12, color: secondaryTextColor, marginTop: 4 }}>
                  • Real-time GIS digital twin visualization<br />
                  • Multi-mine compliance index tracking<br />
                  • One-click statutory DGMS audit exports
                </div>
              </div>
              <Button
                type="primary"
                block
                style={{ marginTop: 20, fontWeight: 600, background: '#18181b', borderColor: '#18181b' }}
                onClick={() => navigate('/login?role=admin')}
              >
                Open Operations Console →
              </Button>
            </div>
          </Col>
        </Row>
      </section>

      {/* ── ARCHITECTURE HIGHLIGHT BANNER ─────────────────────────── */}
      <section style={{ padding: '20px 24px 72px', maxWidth: 1160, margin: '0 auto' }}>
        <div
          style={{
            background: isDark
              ? 'linear-gradient(135deg, #111827 0%, #18181b 100%)'
              : 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
            border: `1px solid ${isDark ? '#1f293d' : '#bae6fd'}`,
            borderRadius: 16,
            padding: '40px 32px',
            textAlign: 'center',
          }}
        >
          <GlobalOutlined style={{ fontSize: 36, color: '#0284c7', marginBottom: 16 }} />
          <Title level={3} style={{ margin: '0 0 12px', color: isDark ? '#ffffff' : '#0f172a', fontWeight: 700 }}>
            Standardizing Safety & Statutory Compliance Across Coal & Metal Mines
          </Title>
          <Paragraph
            style={{
              fontSize: 15,
              maxWidth: 720,
              margin: '0 auto 28px',
              color: isDark ? '#94a3b8' : '#334155',
              lineHeight: 1.6,
            }}
          >
            Built to align strictly with the Coal Mines Regulations (CMR 2017), Mines Vocational Training Rules (MVTR 1966), and DGMS Technical Circulars.
          </Paragraph>
          <Space size={16} wrap style={{ justifyContent: 'center' }}>
            <Button
              type="primary"
              size="large"
              onClick={() => navigate('/login?role=admin')}
              style={{
                height: 48,
                padding: '0 28px',
                fontWeight: 600,
                background: '#0284c7',
                borderColor: '#0284c7',
                borderRadius: 8,
              }}
            >
              Launch Operations Console
            </Button>
            <Button
              size="large"
              onClick={() => navigate('/about')}
              style={{
                height: 48,
                padding: '0 24px',
                fontWeight: 600,
                borderRadius: 8,
                background: cardBg,
                borderColor,
                color: textColor,
              }}
            >
              About the Architecture
            </Button>
          </Space>
        </div>
      </section>

      {/* ── FOOTER ────────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: `1px solid ${borderColor}`,
          padding: '36px 32px',
          background: isDark ? '#09090b' : '#f4f4f5',
          fontSize: 13,
          color: secondaryTextColor,
        }}
      >
        <div
          style={{
            maxWidth: 1160,
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 16,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src={logo} alt="Logo" style={{ width: 22, height: 22 }} />
            <span style={{ fontWeight: 600, color: textColor }}>AI MineGuard</span>
            <span>— Mining Safety & Operational Intelligence</span>
          </div>

          <Space size={20}>
            <Button type="link" size="small" onClick={() => navigate('/about')} style={{ color: secondaryTextColor, padding: 0 }}>
              About
            </Button>
            <Button type="link" size="small" onClick={() => navigate('/contact')} style={{ color: secondaryTextColor, padding: 0 }}>
              Safety Desk
            </Button>
            <Button type="link" size="small" onClick={() => navigate('/login?role=worker')} style={{ color: secondaryTextColor, padding: 0 }}>
              Worker Portal
            </Button>
            <Button type="link" size="small" onClick={() => navigate('/login?role=admin')} style={{ color: secondaryTextColor, padding: 0 }}>
              Admin Portal
            </Button>
          </Space>

          <div>
            DGMS CMR 2017 Statutory Compliance Engine · Enterprise Production Release
          </div>
        </div>
      </footer>
    </div>
  );
};
