import React from 'react';
import { Card, Typography, Tag, Button, Row, Col, Alert, Steps } from 'antd';
import {
  ArrowLeftOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  ThunderboltOutlined,
  SafetyCertificateOutlined,
  FileDoneOutlined,
  AuditOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';

const { Title, Paragraph, Text } = Typography;

interface ModuleStandbyPageProps {
  moduleNumber: 2 | 3;
}

export const ModuleStandbyPage: React.FC<ModuleStandbyPageProps> = ({ moduleNumber }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();

  const isModule2 = moduleNumber === 2;

  const title = isModule2
    ? 'Module 2 — Field Operations and Inspection Management'
    : 'Module 3 — Contractor Governance Management';

  const subtitle = isModule2
    ? 'Standardized digital pit checklists, pre-shift mobile equipment roadworthiness, and geo-tagged hazard logs.'
    : 'Contractor agency onboarding, worker biometric verification, statutory wage compliance, and safety induction tracking.';

  const features = isModule2
    ? [
        { title: 'Digital Pit Pre-Shift Checklists', desc: 'Overman digital sign-off on ventilation, roof/wall soundness, and electrical grounding before worker entry.' },
        { title: 'Mobile Equipment Pre-Operation Inspection', desc: 'Dumper, shovel, and drill operator walkaround checklists verifying brakes, lights, and steering systems.' },
        { title: 'Geo-Tagged Hazard & Danger Zone Tagging', desc: 'Field safety officers pinning geo-referenced danger areas and blast radius clearance buffers on the digital twin.' },
        { title: 'Drone Bench & Highwall Survey Logs', desc: 'Periodic aerial photographic inspection logs identifying overhangs, loose boulders, and haul road erosion.' },
      ]
    : [
        { title: 'Contractor Worker Biometric Identity & Gate Pass', desc: 'Fingerprint and facial biometric access control cross-referencing valid medical fitness and statutory training.' },
        { title: 'Statutory Wage & PF/ESI Compliance Audit', desc: 'Automated escrow verification ensuring contracted laborers receive mandated statutory minimum wages and social security.' },
        { title: 'Mandatory Safety Induction & Badge Tracking', desc: 'Digital tracking of Vocational Training (VT) center certifications, refresher safety drills, and badge validity.' },
        { title: 'Contractor Safety Rating & Blacklisting Matrix', desc: 'Dynamic penalty point scoring blacklisting agencies with repeated unverified PPE breaches or statutory non-compliance.' },
      ];

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <Tag color={isModule2 ? 'blue' : 'purple'} style={{ fontSize: 12, padding: '2px 8px', fontWeight: 600 }}>
              {isModule2 ? 'MODULE 2 · PHASE 2 ROADMAP' : 'MODULE 3 · PHASE 3 ROADMAP'}
            </Tag>
            <Tag color="default" style={{ fontSize: 12 }}>STANDBY MODE</Tag>
          </div>
          <Title level={2} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>{title}</Title>
          <Text type="secondary" style={{ fontSize: 14, color: isDark ? '#a1a1aa' : '#71717a' }}>{subtitle}</Text>
        </div>

        <Button
          type="primary"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
          style={{ background: isDark ? '#27272a' : '#18181b', borderColor: isDark ? '#3f3f46' : '#18181b', height: 40 }}
        >
          Return to Module 1 (Active)
        </Button>
      </div>

      {/* Notice Banner */}
      <Alert
        message="Module Status: Standby Roadmap"
        description="Per system specifications, only Module 1 (AI Compliance and Risk Engine) is actively operational. Buttons for Module 2 and Module 3 are provided for complete navigation and worker workflow visibility, but backend features are on standby."
        type="info"
        showIcon
        style={{ marginBottom: 24, borderRadius: 10 }}
      />

      {/* Module Lifecycle Stepper */}
      <Card
        bordered
        style={{
          borderRadius: 12,
          marginBottom: 24,
          background: isDark ? '#111111' : '#ffffff',
          borderColor: isDark ? '#27272a' : '#e4e4e7',
        }}
      >
        <Title level={5} style={{ marginBottom: 16, color: isDark ? '#ffffff' : '#18181b' }}>Platform Module Status Overview</Title>
        <Steps
          current={isModule2 ? 1 : 2}
          items={[
            {
              title: 'Module 1: AI Compliance and Risk Engine',
              description: 'ACTIVE & WORKING (CCTV Vision, OCR, Gas Telemetry, Risk Scoring, SLA Alerts)',
              icon: <CheckCircleFilled style={{ color: '#16a34a' }} />,
            },
            {
              title: 'Module 2: Field Operations & Inspection',
              description: 'SCHEDULED PHASE 2 (Digital Pit Checklists, Pre-Shift Inspections, Geo-Hazards)',
              icon: isModule2 ? <ThunderboltOutlined style={{ color: '#2563eb' }} /> : <ClockCircleOutlined />,
            },
            {
              title: 'Module 3: Contractor Governance',
              description: 'SCHEDULED PHASE 3 (Biometric Gates, Wage Compliance, Safety Training Badges)',
              icon: !isModule2 ? <ThunderboltOutlined style={{ color: '#9333ea' }} /> : <ClockCircleOutlined />,
            },
          ]}
        />
      </Card>

      {/* Planned Feature Specifications (Design Only) */}
      <Title level={4} style={{ marginBottom: 16, color: isDark ? '#ffffff' : '#18181b' }}>
        {isModule2 ? 'Planned Field Operations & Inspection Specifications' : 'Planned Contractor Governance Specifications'}
      </Title>
      <Row gutter={[16, 16]}>
        {features.map((f, i) => (
          <Col xs={24} sm={12} key={i}>
            <Card
              bordered
              hoverable={false}
              style={{
                borderRadius: 12,
                height: '100%',
                background: isDark ? '#111111' : '#ffffff',
                border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                {isModule2 ? (
                  <FileDoneOutlined style={{ fontSize: 20, color: '#2563eb' }} />
                ) : (
                  <AuditOutlined style={{ fontSize: 20, color: '#9333ea' }} />
                )}
                <Text strong style={{ fontSize: 15, color: isDark ? '#ffffff' : '#18181b' }}>{f.title}</Text>
              </div>
              <Paragraph type="secondary" style={{ fontSize: 13, margin: 0, lineHeight: 1.6, color: isDark ? '#a1a1aa' : '#71717a' }}>
                {f.desc}
              </Paragraph>
              <div style={{ marginTop: 14 }}>
                <Tag color="default" style={{ fontSize: 11 }}>Feature Standby</Tag>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Return to Module 1 Callout */}
      <Card
        bordered
        style={{
          marginTop: 24,
          borderRadius: 12,
          background: isDark ? '#111111' : '#fafafa',
          border: isDark ? '1px dashed #3f3f46' : '1px dashed #d4d4d8',
          textAlign: 'center',
          padding: '16px 0',
        }}
      >
        <SafetyCertificateOutlined style={{ fontSize: 36, color: isDark ? '#ffffff' : '#18181b', marginBottom: 12 }} />
        <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Need Active Safety Systems?</Title>
        <Paragraph type="secondary" style={{ maxWidth: 540, margin: '8px auto 16px', color: isDark ? '#a1a1aa' : '#71717a' }}>
          Module 1 is fully operational with live CCTV computer vision, continuous multi-gas telemetry, explainable risk calculations, and DGMS SLA corrective workflows.
        </Paragraph>
        <Button
          type="primary"
          size="large"
          onClick={() => navigate('/')}
          style={{ background: isDark ? '#27272a' : '#18181b', borderColor: isDark ? '#3f3f46' : '#18181b', color: '#fff' }}
        >
          Explore Module 1 Dashboard
        </Button>
      </Card>
    </div>
  );
};
