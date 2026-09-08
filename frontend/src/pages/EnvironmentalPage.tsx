import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Statistic,
  notification, Alert as AntAlert, Progress,
} from 'antd';
import {
  PlayCircleOutlined, ReloadOutlined, WarningOutlined, CheckCircleOutlined,
} from '@ant-design/icons';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartTooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts';
import dayjs from 'dayjs';
import type { EnvironmentalReading } from '../types';
import { environmentApi, demoApi } from '../services/api';

const { Title, Text } = Typography;

// DGMS statutory limits
const LIMITS = {
  CH4_WARNING: 0.5,
  CH4_DANGER: 1.0,
  CH4_CRITICAL: 1.25,
  CO_WARNING: 25,
  CO_DANGER: 50,
  O2_MIN: 19.5,
};

export const EnvironmentalPage: React.FC = () => {
  const [readings, setReadings] = useState<EnvironmentalReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await environmentApi.readings({ limit: 40 });
      setReadings(res.data.data ?? []);
    } catch { /* no data */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  const handleSimulateGasBreach = async () => {
    setSimulating(true);
    try {
      const res = await demoApi.simulateGasBreach();
      notification.error({
        message: '🚨 Gas Breach Detected!',
        description: `Methane: ${res.data.data?.breach_details?.ch4 ?? 1.35}% — Above DGMS critical limit (1.25%)`,
        duration: 6,
      });
      await fetchData();
    } catch {
      notification.error({ message: 'Error', description: 'Run demo seed first.' });
    } finally {
      setSimulating(false);
    }
  };

  // Build chart data
  const chartData = readings
    .slice()
    .reverse()
    .map((r, i) => ({
      idx: i + 1,
      CH4: r.methane_ch4_pct,
      CO: r.carbon_monoxide_co_ppm,
      O2: r.oxygen_o2_pct,
      breach: r.is_breach,
    }));

  const latestReading = readings[0];
  const breachCount = readings.filter((r) => r.is_breach).length;

  const tableCols = [
    { title: 'Sensor', dataIndex: 'sensor_code', key: 'sensor', render: (v: string) => <Text code style={{ fontSize: 11 }}>{v}</Text> },
    {
      title: 'CH₄ %', dataIndex: 'methane_ch4_pct', key: 'ch4',
      render: (v: number) => (
        <span style={{ color: v >= LIMITS.CH4_CRITICAL ? '#ef4444' : v >= LIMITS.CH4_DANGER ? '#f97316' : '#22c55e', fontWeight: 600 }}>
          {v?.toFixed(3)}%
        </span>
      ),
    },
    {
      title: 'CO ppm', dataIndex: 'carbon_monoxide_co_ppm', key: 'co',
      render: (v: number) => (
        <span style={{ color: v >= LIMITS.CO_DANGER ? '#ef4444' : v >= LIMITS.CO_WARNING ? '#f97316' : '#22c55e', fontWeight: 600 }}>
          {v?.toFixed(1)}
        </span>
      ),
    },
    {
      title: 'O₂ %', dataIndex: 'oxygen_o2_pct', key: 'o2',
      render: (v: number) => (
        <span style={{ color: v < LIMITS.O2_MIN ? '#ef4444' : '#22c55e', fontWeight: 600 }}>
          {v?.toFixed(1)}%
        </span>
      ),
    },
    { title: 'Temp °C', dataIndex: 'temperature_c', key: 'temp', render: (v: number) => `${v?.toFixed(1)}°C` },
    { title: 'Humidity', dataIndex: 'humidity_pct', key: 'hum', render: (v: number) => `${v?.toFixed(0)}%` },
    {
      title: 'Status', dataIndex: 'is_breach', key: 'breach',
      render: (v: boolean) => v
        ? <Tag color="red" icon={<WarningOutlined />}>BREACH</Tag>
        : <Tag color="success" icon={<CheckCircleOutlined />}>Normal</Tag>,
    },
    { title: 'Source', dataIndex: 'source', key: 'src', render: (v: string) => <Tag>{v}</Tag> },
    { title: 'Time', dataIndex: 'created_at', key: 'time', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Environmental Gas Telemetry</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            LoRa Underground Gas Sensor Network · DGMS Threshold Monitoring
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
            <Button
              danger
              type="primary"
              icon={<PlayCircleOutlined />}
              loading={simulating}
              onClick={handleSimulateGasBreach}
            >
              Simulate CH₄ Gas Breach
            </Button>
          </Space>
        </Col>
      </Row>

      {breachCount > 0 && (
        <AntAlert
          type="error"
          showIcon
          message={`${breachCount} gas threshold breach(es) detected in recent readings!`}
          style={{ marginBottom: 16, borderRadius: 8 }}
        />
      )}

      {/* Live sensor gauges */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" bordered style={{ borderRadius: 10, borderTop: `3px solid ${latestReading?.methane_ch4_pct >= LIMITS.CH4_CRITICAL ? '#ef4444' : '#22c55e'}` }}>
            <Statistic
              title="Methane (CH₄)"
              value={latestReading?.methane_ch4_pct?.toFixed(3) ?? '—'}
              suffix="% vol"
              valueStyle={{ color: latestReading?.methane_ch4_pct >= LIMITS.CH4_CRITICAL ? '#ef4444' : '#22c55e' }}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>DGMS Limit: 1.25%</Text>
            {latestReading && (
              <Progress
                percent={Math.min(100, (latestReading.methane_ch4_pct / 1.5) * 100)}
                strokeColor={latestReading.methane_ch4_pct >= LIMITS.CH4_CRITICAL ? '#ef4444' : '#22c55e'}
                showInfo={false}
                size="small"
                style={{ marginTop: 6 }}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" bordered style={{ borderRadius: 10, borderTop: `3px solid ${latestReading?.carbon_monoxide_co_ppm >= LIMITS.CO_DANGER ? '#ef4444' : '#22c55e'}` }}>
            <Statistic
              title="Carbon Monoxide (CO)"
              value={latestReading?.carbon_monoxide_co_ppm?.toFixed(1) ?? '—'}
              suffix="ppm"
              valueStyle={{ color: latestReading?.carbon_monoxide_co_ppm >= LIMITS.CO_DANGER ? '#ef4444' : '#22c55e' }}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>DGMS Limit: 50 ppm</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" bordered style={{ borderRadius: 10, borderTop: `3px solid ${latestReading?.oxygen_o2_pct < LIMITS.O2_MIN ? '#ef4444' : '#22c55e'}` }}>
            <Statistic
              title="Oxygen (O₂)"
              value={latestReading?.oxygen_o2_pct?.toFixed(1) ?? '—'}
              suffix="% vol"
              valueStyle={{ color: latestReading?.oxygen_o2_pct < LIMITS.O2_MIN ? '#ef4444' : '#22c55e' }}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>Min Required: 19.5%</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" bordered style={{ borderRadius: 10, borderTop: '3px solid #f97316' }}>
            <Statistic
              title="Total Breaches"
              value={breachCount}
              valueStyle={{ color: breachCount > 0 ? '#ef4444' : '#22c55e' }}
              suffix={`/ ${readings.length}`}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>From last {readings.length} readings</Text>
          </Card>
        </Col>
      </Row>

      {/* Gas trend charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={14}>
          <Card title="CH₄ Concentration Trend — DGMS Limit Reference Lines" bordered style={{ borderRadius: 10 }}>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="idx" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 1.6]} />
                <RechartTooltip />
                <ReferenceLine y={LIMITS.CH4_WARNING} stroke="#22c55e" strokeDasharray="4 4" label={{ value: 'Warning 0.5%', fontSize: 10, fill: '#22c55e' }} />
                <ReferenceLine y={LIMITS.CH4_DANGER} stroke="#f97316" strokeDasharray="4 4" label={{ value: 'Danger 1.0%', fontSize: 10, fill: '#f97316' }} />
                <ReferenceLine y={LIMITS.CH4_CRITICAL} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'Critical 1.25%', fontSize: 10, fill: '#ef4444' }} />
                <Line type="monotone" dataKey="CH4" stroke="#7c3aed" strokeWidth={2} dot={(props) => {
                  const { cx, cy, payload } = props;
                  return payload.breach
                    ? <circle key={`dot-${cx}-${cy}`} cx={cx} cy={cy} r={5} fill="#ef4444" />
                    : <circle key={`dot-${cx}-${cy}`} cx={cx} cy={cy} r={3} fill="#7c3aed" />;
                }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="DGMS Statutory Limits Reference" bordered style={{ borderRadius: 10 }}>
            {[
              { gas: 'CH₄ (Methane)', warning: '0.5%', danger: '1.0%', critical: '1.25% — EVACUATE', color: '#7c3aed' },
              { gas: 'CO (Carbon Monoxide)', warning: '25 ppm', danger: '50 ppm', critical: '100 ppm — Toxic', color: '#f97316' },
              { gas: 'O₂ (Oxygen)', warning: '19.5%', danger: '18%', critical: '<16% — Asphyxiation', color: '#0ea5e9' },
            ].map((item) => (
              <div key={item.gas} style={{ padding: '10px 0', borderBottom: '1px solid #f5f5f5' }}>
                <div style={{ fontWeight: 600, fontSize: 13, color: item.color }}>{item.gas}</div>
                <div style={{ display: 'flex', gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
                  <Tag color="success">⚠ {item.warning}</Tag>
                  <Tag color="warning">🔶 {item.danger}</Tag>
                  <Tag color="error">🚨 {item.critical}</Tag>
                </div>
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      {/* Full readings table */}
      <Card title="Gas Telemetry Readings (Latest 40)" bordered style={{ borderRadius: 10 }}>
        <Table
          dataSource={readings}
          columns={tableCols}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
          loading={loading}
          rowClassName={(r) => r.is_breach ? 'ant-table-row-danger' : ''}
          scroll={{ x: 900 }}
          locale={{ emptyText: 'No gas telemetry readings. Seed demo data first.' }}
        />
      </Card>

      <style>{`
        .ant-table-row-danger td { background: #fef2f2 !important; }
      `}</style>
    </div>
  );
};
