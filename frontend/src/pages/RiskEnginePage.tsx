import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Statistic,
  Slider, Divider, Progress, notification, Empty, Alert,
} from 'antd';
import { ThunderboltOutlined, ReloadOutlined, BugOutlined, LockOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
} from 'recharts';
import dayjs from 'dayjs';
import type { RiskScore, Anomaly } from '../types';
import { riskApi, mineApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const RISK_COLOR: Record<string, string> = {
  LOW: '#22c55e', MEDIUM: '#f97316', HIGH: '#ef4444', CRITICAL: '#7f1d1d',
};


export const RiskEnginePage: React.FC = () => {
  const [riskScores, setRiskScores] = useState<RiskScore[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [mines, setMines] = useState<{ id: string; name: string }[]>([]);
  const [recomputing, setRecomputing] = useState(false);
  const [loading, setLoading] = useState(true);

  // Interactive weight sliders (default values from config)
  const [weights, setWeights] = useState({ wv: 40, we: 25, wp: 15, ws: 20 });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [riskRes, anomalyRes, mineRes] = await Promise.all([
        riskApi.scores({ limit: 20 }),
        riskApi.anomalies({ limit: 20 }),
        mineApi.list(),
      ]);
      setRiskScores(riskRes.data.data ?? []);
      setAnomalies(anomalyRes.data.data ?? []);
      setMines(mineRes.data.data ?? []);
    } catch { /* no data */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  const { isAdmin } = useAuth();

  const handleRecompute = async () => {
    if (!isAdmin) {
      notification.warning({
        message: 'Admin Privilege Required',
        description: 'Recomputing statutory risk scores across mine zones requires Administrator authority.',
      });
      return;
    }
    if (!mines[0]) return;
    setRecomputing(true);
    try {
      await riskApi.recompute(mines[0].id);
      notification.success({ message: 'Risk Recomputed', description: 'All zone risk scores updated successfully.' });
      await fetchData();
    } catch {
      notification.error({ message: 'Error', description: 'Seed demo data first.' });
    } finally {
      setRecomputing(false);
    }
  };

  // Radar chart data from latest risk scores
  const radarData = riskScores.slice(0, 5).map((r, i) => ({
    zone: `Zone ${i + 1}`,
    Violations: Math.round(r.violation_component * 100),
    Environment: Math.round(r.environment_component * 100),
    Production: Math.round(r.production_component * 100),
    Equipment: Math.round(r.equipment_component * 100),
  }));

  const barData = riskScores.map((r) => ({
    zone: r.zone_id?.slice(0, 8) ?? `Z${riskScores.indexOf(r) + 1}`,
    score: Math.round(r.composite_score * 100),
    fill: RISK_COLOR[r.risk_level ?? 'LOW'],
  }));

  // Computed demo score using slider weights
  const demoScore = (
    (weights.wv * 0.65 + weights.we * 0.4 + weights.wp * 0.25 + weights.ws * 0.5) / 100
  ).toFixed(3);
  const demoLevel = parseFloat(demoScore) > 0.75 ? 'CRITICAL' : parseFloat(demoScore) > 0.5 ? 'HIGH' : parseFloat(demoScore) > 0.25 ? 'MEDIUM' : 'LOW';

  const riskCols = [
    { title: 'Zone', dataIndex: 'zone_id', key: 'zone', render: (v: string) => <Text code style={{ fontSize: 11 }}>{v?.slice(0, 8)}</Text> },
    {
      title: 'Composite R', dataIndex: 'composite_score', key: 'composite',
      sorter: (a: RiskScore, b: RiskScore) => b.composite_score - a.composite_score,
      render: (v: number) => (
        <Space>
          <Progress percent={Math.round(v * 100)} size="small" strokeColor={RISK_COLOR[v > 0.75 ? 'CRITICAL' : v > 0.5 ? 'HIGH' : v > 0.25 ? 'MEDIUM' : 'LOW']} showInfo={false} style={{ width: 80 }} />
          <span style={{ fontWeight: 600, color: RISK_COLOR[v > 0.75 ? 'CRITICAL' : v > 0.5 ? 'HIGH' : v > 0.25 ? 'MEDIUM' : 'LOW'] }}>
            {(v * 100).toFixed(1)}%
          </span>
        </Space>
      ),
    },
    {
      title: 'Level', dataIndex: 'risk_level', key: 'level',
      render: (v: string) => <Tag color={RISK_COLOR[v]} style={{ color: '#fff' }}>{v}</Tag>,
    },
    { title: 'Violations (V)', dataIndex: 'violation_component', key: 'v', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { title: 'Env (E)', dataIndex: 'environment_component', key: 'e', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { title: 'Prod (P)', dataIndex: 'production_component', key: 'p', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { title: 'Equipment (S)', dataIndex: 'equipment_component', key: 's', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { title: 'Updated', dataIndex: 'computed_at', key: 'at', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
  ];

  const anomalyCols = [
    { title: 'Type', dataIndex: 'anomaly_type', key: 'type', render: (v: string) => <Tag>{v}</Tag> },
    {
      title: 'Severity', dataIndex: 'severity', key: 'sev',
      render: (v: string) => <Tag color={RISK_COLOR[v === 'CRITICAL' ? 'CRITICAL' : v === 'HIGH' ? 'HIGH' : 'MEDIUM']}>{v}</Tag>,
    },
    { title: 'Description', dataIndex: 'description', key: 'desc', render: (v: string) => <Text style={{ fontSize: 12 }}>{v}</Text> },
    { title: 'Detected', dataIndex: 'detected_at', key: 'at', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
    {
      title: 'Ack', dataIndex: 'is_acknowledged', key: 'ack',
      render: (v: boolean) => v ? <Tag color="success">Acknowledged</Tag> : <Tag color="error">Pending</Tag>,
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Explainable Risk Scoring Engine</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Composite Risk Formula: R = w<sub>v</sub>·V + w<sub>e</sub>·E + w<sub>p</sub>·P + w<sub>s</sub>·S
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
            <Button
              type="primary"
              icon={isAdmin ? <ThunderboltOutlined /> : <LockOutlined />}
              loading={recomputing}
              onClick={handleRecompute}
              disabled={!isAdmin}
              title={isAdmin ? 'Recompute All Zone Scores' : 'Admin privilege required to recompute scores'}
              style={isAdmin ? {} : { opacity: 0.6 }}
            >
              Recompute All Zone Scores {!isAdmin && '(Admin Only)'}
            </Button>
          </Space>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Interactive formula calculator */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space><ThunderboltOutlined />Interactive Risk Calculator</Space>
                {isAdmin ? (
                  <Tag color="#18181b" icon={<SafetyCertificateOutlined />}>Admin Editable</Tag>
                ) : (
                  <Tag color="default" icon={<LockOutlined />}>Read Only (Officer)</Tag>
                )}
              </div>
            }
            bordered
            style={{ borderRadius: 10 }}
          >
            {!isAdmin && (
              <Alert
                message="Statutory Weight Controls Locked"
                description="Logged in as Safety Officer / User. You are viewing active DGMS statutory risk parameters in read-only mode. Administrator authority is required to modify weights."
                type="info"
                showIcon
                style={{ marginBottom: 14, fontSize: 12, borderRadius: 8 }}
              />
            )}

            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, fontFamily: 'monospace' }}>
              R = ({weights.wv}%·V) + ({weights.we}%·E) + ({weights.wp}%·P) + ({weights.ws}%·S)
            </div>

            {[
              { key: 'wv', label: 'w_v — Violations Weight', color: '#ef4444' },
              { key: 'we', label: 'w_e — Environment Weight', color: '#f97316' },
              { key: 'wp', label: 'w_p — Production Weight', color: '#0ea5e9' },
              { key: 'ws', label: 'w_s — Equipment Safety Weight', color: '#7c3aed' },
            ].map((item) => (
              <div key={item.key} style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <Text style={{ fontSize: 12, fontWeight: 600, color: item.color }}>{item.label}</Text>
                  <Text style={{ fontSize: 12 }}>{weights[item.key as keyof typeof weights]}%</Text>
                </div>
                <Slider
                  min={0}
                  max={100}
                  disabled={!isAdmin}
                  value={weights[item.key as keyof typeof weights]}
                  onChange={(v) => setWeights((prev) => ({ ...prev, [item.key]: v }))}
                  trackStyle={{ backgroundColor: item.color }}
                  handleStyle={{ borderColor: item.color }}
                />
              </div>
            ))}

            <Divider />
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 12, color: '#737373', marginBottom: 8 }}>
                Computed Score (using sample component values)
              </div>
              <Statistic
                value={(parseFloat(demoScore) * 100).toFixed(1)}
                suffix="%"
                valueStyle={{ color: RISK_COLOR[demoLevel], fontSize: 32 }}
              />
              <Tag
                color={RISK_COLOR[demoLevel]}
                style={{ color: '#fff', fontSize: 14, padding: '4px 16px', marginTop: 8 }}
              >
                {demoLevel}
              </Tag>
            </div>
          </Card>
        </Col>

        {/* Charts */}
        <Col xs={24} lg={14}>
          <Card title="Zone Risk Score Comparison" bordered style={{ borderRadius: 10, marginBottom: 16 }}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData} margin={{ left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="zone" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip formatter={(v: unknown) => [`${v}%`, 'Risk Score']} />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {barData.map((entry, idx) => (
                    <rect key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {barData.length === 0 && <Empty description="Seed demo data to view charts" style={{ paddingTop: 20 }} />}
          </Card>

          {radarData.length > 0 && (
            <Card title="Risk Factor Component Radar" bordered style={{ borderRadius: 10 }}>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="zone" tick={{ fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
                  <Radar name="Violations" dataKey="Violations" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
                  <Radar name="Environment" dataKey="Environment" stroke="#f97316" fill="#f97316" fillOpacity={0.2} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                </RadarChart>
              </ResponsiveContainer>
            </Card>
          )}
        </Col>

        {/* Zone risk table */}
        <Col xs={24}>
          <Card title="Zone Risk Score Ledger" bordered style={{ borderRadius: 10 }}>
            <Table
              dataSource={riskScores}
              columns={riskCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 8 }}
              loading={loading}
              scroll={{ x: 900 }}
              locale={{ emptyText: 'No risk scores. Seed demo data and click Recompute.' }}
            />
          </Card>
        </Col>

        {/* Anomaly table */}
        <Col xs={24}>
          <Card
            title={<Space><BugOutlined />Anomaly Detection Log (Isolation Forest)</Space>}
            bordered
            style={{ borderRadius: 10 }}
          >
            <Table
              dataSource={anomalies}
              columns={anomalyCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 8 }}
              loading={loading}
              locale={{ emptyText: 'No anomalies detected yet.' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
