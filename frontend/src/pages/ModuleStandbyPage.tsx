import React from 'react';
import { Card, Typography, Tag, Button, Row, Col, Alert, Steps } from 'antd';
import {
  ArrowLeftOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  CarOutlined,
  CompassOutlined,
  ThunderboltOutlined,
  SafetyCertificateOutlined,
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
    ? 'Module 2 — AI Mine Production, Fleet Optimization & Dispatch'
    : 'Module 3 — Geotechnical, Structural & Eco-Restoration';

  const subtitle = isModule2
    ? 'Dynamic shovel-dumper allocation, cycle time optimization, and haul road safety analytics.'
    : 'Slope stability radar integration, subsidence forecasting, and progressive ecological restoration telemetry.';

  const features = isModule2
    ? [
        { title: 'Dynamic Dispatch Engine', desc: 'Real-time linear programming & genetic algorithms for optimal hauler routing between blast faces and crushers.' },
        { title: 'Cycle-Time Bottleneck Analysis', desc: 'GPS telematics tracking loading, hauling, dumping, and queuing durations to eliminate idle time.' },
        { title: 'Haul Road Speed & Proximity Compliance', desc: 'CV and telematics alerting drivers to overspeeding, steep gradients, and collision proximity zones.' },
        { title: 'Fuel & Carbon Footprint Optimization', desc: 'AI-assisted gear/speed advisory models minimizing diesel burn per ton of coal extracted.' },
      ]
    : [
        { title: 'Slope Stability & Bench Failure Radar', desc: 'Interferometric radar & micro-seismic sensor integration for pit wall displacement early warning.' },
        { title: 'Subsurface InSAR Subsidence Tracking', desc: 'Satellite InSAR interferometry detecting millimeter-level ground subsidence over underground workings.' },
        { title: 'Acid Mine Drainage (AMD) Detection', desc: 'pH, heavy metal, and sulfate runoff forecasting across mine sumps and sedimentation ponds.' },
        { title: 'Eco-Restoration Vegetation Index (NDVI)', desc: 'Multispectral drone imagery computing vegetation health indices over reclaimed overburden dumps.' },
      ];

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', paddingBottom: 40 }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <Tag color={isModule2 ? 'blue' : 'purple'} style={{ fontSize: 12, padding: '2px 8px', fontWeight: 600 }}>
              {isModule2 ? 'PHASE 2 ROADMAP' : 'PHASE 3 ROADMAP'}
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
        message="Architecture Specification Notice"
        description="Per system guidelines, only Module 1 (AI Statutory Safety & Compliance Engine) is actively implemented on this branch. Module 2 and Module 3 navigation buttons are included in the centralized platform for architectural review and future milestone integration."
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
        <Title level={5} style={{ marginBottom: 16, color: isDark ? '#ffffff' : '#18181b' }}>Centralized Platform Implementation Roadmap</Title>
        <Steps
          current={isModule2 ? 1 : 2}
          items={[
            {
              title: 'Module 1: AI Safety & Statutory Compliance',
              description: 'Active & Deployed (CCTV Vision, OCR, Gas Telemetry, Risk Engine, DGMS SLA)',
              icon: <CheckCircleFilled style={{ color: '#16a34a' }} />,
            },
            {
              title: 'Module 2: Fleet & Dispatch Optimization',
              description: 'Scheduled Phase 2 (Shovel-Dumper Dispatch, Fuel Analytics, Cycle Times)',
              icon: isModule2 ? <ThunderboltOutlined style={{ color: '#2563eb' }} /> : <ClockCircleOutlined />,
            },
            {
              title: 'Module 3: Geotechnical & Eco-Restoration',
              description: 'Scheduled Phase 3 (Slope Radar, Subsidence InSAR, Overburden NDVI)',
              icon: !isModule2 ? <ThunderboltOutlined style={{ color: '#9333ea' }} /> : <ClockCircleOutlined />,
            },
          ]}
        />
      </Card>

      {/* Planned Feature Specifications (Design Only) */}
      <Title level={4} style={{ marginBottom: 16, color: isDark ? '#ffffff' : '#18181b' }}>
        {isModule2 ? 'Planned Fleet & Dispatch Specifications' : 'Planned Geotechnical & Restoration Specifications'}
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
                  <CarOutlined style={{ fontSize: 20, color: '#2563eb' }} />
                ) : (
                  <CompassOutlined style={{ fontSize: 20, color: '#9333ea' }} />
                )}
                <Text strong style={{ fontSize: 15, color: isDark ? '#ffffff' : '#18181b' }}>{f.title}</Text>
              </div>
              <Paragraph type="secondary" style={{ fontSize: 13, margin: 0, lineHeight: 1.6, color: isDark ? '#a1a1aa' : '#71717a' }}>
                {f.desc}
              </Paragraph>
              <div style={{ marginTop: 14 }}>
                <Tag color="default" style={{ fontSize: 11 }}>Feature Reserved</Tag>
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
        <Title level={4} style={{ margin: 0, color: isDark ? '#ffffff' : '#18181b' }}>Looking for Active Operational Systems?</Title>
        <Paragraph type="secondary" style={{ maxWidth: 540, margin: '8px auto 16px', color: isDark ? '#a1a1aa' : '#71717a' }}>
          Module 1 is fully operational with live computer vision hazard detection, real-time gas telemetry, explainable risk scoring, and DGMS statutory escalation workflows.
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
