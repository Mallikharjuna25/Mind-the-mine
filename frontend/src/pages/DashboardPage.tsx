import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Statistic, Table, Tag, Progress, Timeline, Typography, Button, Spin, Space,
} from 'antd';
import {
  AlertOutlined, SafetyOutlined, ThunderboltOutlined, CameraOutlined, ReloadOutlined, RiseOutlined,
} from '@ant-design/icons';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import dayjs from 'dayjs';
import type { Alert, RiskScore, EnvironmentalReading } from '../types';
import { riskApi, workflowApi, environmentApi, cctvApi, demoApi } from '../services/api';

const { Title, Text } = Typography;

const RISK_COLOR: Record<string, string> = {
  LOW: '#22c55e', MEDIUM: '#f97316', HIGH: '#ef4444', CRITICAL: '#7f1d1d',
};

const SEV_COLOR: Record<string, string> = {
  INFO: 'blue', WARNING: 'orange', HIGH: 'red', CRITICAL: 'volcano', EMERGENCY: 'magenta',
};

export const DashboardPage: React.FC = () => {
  const [riskScores, setRiskScores] = useState<RiskScore[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [readings, setReadings] = useState<EnvironmentalReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [violationCount, setViolationCount] = useState(0);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [riskRes, alertRes, envRes, cctvRes] = await Promise.all([
        riskApi.scores(),
        workflowApi.alerts({ limit: 10 }),
        environmentApi.readings({ limit: 20 }),
        cctvApi.violations({ limit: 1 }),
      ]);
      setRiskScores(riskRes.data.data ?? []);
      setAlerts(alertRes.data.data ?? []);
      setReadings(envRes.data.data ?? []);
      setViolationCount(cctvRes.data.data?.total ?? (cctvRes.data.data ?? []).length);
    } catch { /* backend may not be seeded yet */ }
    setLoading(false);
  };

  useEffect(() => { fetchAll(); }, []);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await demoApi.seed();
      await fetchAll();
    } finally { setSeeding(false); }
  };

  // Build 24-hour gas trend data from readings
  const gasTrend = readings
    .slice()
    .reverse()
    .map((r, i) => ({
      t: i,
      CH4: r.methane_ch4_pct ?? 0,
      CO: (r.carbon_monoxide_co_ppm ?? 0) / 10,
      O2: r.oxygen_o2_pct ?? 0,
    }));

  const criticalAlerts = alerts.filter(
    (a) => a.severity === 'CRITICAL' || a.severity === 'EMERGENCY',
  );

  const avgRisk = riskScores.length
    ? riskScores.reduce((s, r) => s + r.composite_score, 0) / riskScores.length
    : 0;

  const activeBreaches = readings.filter((r) => r.is_breach).length;

  const riskTableCols = [
    { title: 'Zone', dataIndex: 'zone_id', key: 'zone_id', render: (v: string) => <Text code style={{ fontSize: 11 }}>{v?.slice(0, 8)}</Text> },
    {
      title: 'Score', dataIndex: 'composite_score', key: 'score',
      render: (v: number) => (
        <Progress
          percent={Math.round(v * 100)}
          size="small"
          strokeColor={RISK_COLOR[v > 0.75 ? 'CRITICAL' : v > 0.5 ? 'HIGH' : v > 0.25 ? 'MEDIUM' : 'LOW']}
          showInfo={false}
          style={{ width: 100 }}
        />
      ),
    },
    {
      title: 'Level', dataIndex: 'risk_level', key: 'risk_level',
      render: (v: string) => <Tag color={RISK_COLOR[v]} style={{ color: '#fff' }}>{v}</Tag>,
    },
    {
      title: 'Updated', dataIndex: 'computed_at', key: 'computed_at',
      render: (v: string) => dayjs(v).format('HH:mm DD/MM'),
    },
  ];

  return (
    <div>
      {/* Header row */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 20 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Executive Command Dashboard</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Kusmunda Mega Opencast Project · SECL · Live View
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchAll} loading={loading}>Refresh</Button>
            <Button type="primary" loading={seeding} onClick={handleSeed}>
              Seed Demo Data
            </Button>
          </Space>
        </Col>
      </Row>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
      ) : (
        <>
          {/* KPI Cards */}
          <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
            <Col xs={24} sm={12} md={6}>
              <Card bordered style={{ borderRadius: 10 }}>
                <Statistic
                  title="Avg Zone Risk Score"
                  value={(avgRisk * 100).toFixed(1)}
                  suffix="%"
                  prefix={<ThunderboltOutlined style={{ color: avgRisk > 0.5 ? '#ef4444' : '#22c55e' }} />}
                  valueStyle={{ color: avgRisk > 0.5 ? '#ef4444' : '#22c55e' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card bordered style={{ borderRadius: 10 }}>
                <Statistic
                  title="Active Alerts"
                  value={alerts.length}
                  prefix={<AlertOutlined style={{ color: '#f97316' }} />}
                  valueStyle={{ color: '#f97316' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card bordered style={{ borderRadius: 10 }}>
                <Statistic
                  title="Gas Breaches (Latest)"
                  value={activeBreaches}
                  prefix={<SafetyOutlined style={{ color: activeBreaches > 0 ? '#ef4444' : '#22c55e' }} />}
                  valueStyle={{ color: activeBreaches > 0 ? '#ef4444' : '#22c55e' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card bordered style={{ borderRadius: 10 }}>
                <Statistic
                  title="CCTV Violations"
                  value={violationCount}
                  prefix={<CameraOutlined style={{ color: '#7c3aed' }} />}
                  valueStyle={{ color: '#7c3aed' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Charts & tables */}
          <Row gutter={[16, 16]}>
            {/* Gas trend chart */}
            <Col xs={24} lg={14}>
              <Card title="Gas Telemetry Trend (Latest 20 Readings)" bordered style={{ borderRadius: 10 }}>
                <ResponsiveContainer width="100%" height={260}>
                  <AreaChart data={gasTrend} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="ch4Grad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="coGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="t" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Area type="monotone" dataKey="CH4" name="CH₄ %" stroke="#ef4444" fill="url(#ch4Grad)" strokeWidth={2} dot={false} />
                    <Area type="monotone" dataKey="CO" name="CO ÷10 ppm" stroke="#f97316" fill="url(#coGrad)" strokeWidth={2} dot={false} />
                    <Area type="monotone" dataKey="O2" name="O₂ %" stroke="#22c55e" fill="none" strokeWidth={2} strokeDasharray="4 4" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </Col>

            {/* Alert feed */}
            <Col xs={24} lg={10}>
              <Card
                title={
                  <Space>
                    <AlertOutlined />
                    Active SLA Alerts
                    {criticalAlerts.length > 0 && (
                      <Tag color="red">{criticalAlerts.length} Critical</Tag>
                    )}
                  </Space>
                }
                bordered
                style={{ borderRadius: 10, maxHeight: 340, overflowY: 'auto' }}
              >
                {alerts.length === 0 ? (
                  <Text type="secondary">No active alerts. Seed demo data to populate.</Text>
                ) : (
                  <Timeline
                    items={alerts.slice(0, 8).map((a) => ({
                      color: SEV_COLOR[a.severity] === 'red' ? 'red' : a.severity === 'EMERGENCY' ? '#7c3aed' : 'orange',
                      children: (
                        <div>
                          <Space size={4}>
                            <Tag color={SEV_COLOR[a.severity]} style={{ fontSize: 10 }}>{a.severity}</Tag>
                            <Text style={{ fontSize: 12, fontWeight: 600 }}>{a.title}</Text>
                          </Space>
                          <div style={{ fontSize: 11, color: '#737373', marginTop: 2 }}>
                            {dayjs(a.created_at).format('HH:mm DD/MM')} · SLA L{a.sla_level}
                          </div>
                        </div>
                      ),
                    }))}
                  />
                )}
              </Card>
            </Col>

            {/* Zone risk table */}
            <Col xs={24}>
              <Card
                title={
                  <Space>
                    <ThunderboltOutlined />
                    Zone Risk Scores
                    <RiseOutlined style={{ color: '#ef4444' }} />
                  </Space>
                }
                bordered
                style={{ borderRadius: 10 }}
                extra={
                  <Tag color="default" style={{ fontSize: 11 }}>
                    R = w_v·V + w_e·E + w_p·P + w_s·S
                  </Tag>
                }
              >
                <Table
                  dataSource={riskScores}
                  columns={riskTableCols}
                  rowKey="id"
                  size="small"
                  pagination={false}
                  locale={{ emptyText: 'Seed demo data to view risk scores' }}
                />
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
};
