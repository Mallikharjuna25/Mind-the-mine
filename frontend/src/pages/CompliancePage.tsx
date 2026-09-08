import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Statistic, Select,
} from 'antd';
import { FileProtectOutlined, ReloadOutlined, PrinterOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Violation, EnvironmentalReading, EquipmentAsset } from '../types';
import { complianceApi, environmentApi, equipmentApi } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

export const CompliancePage: React.FC = () => {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [breaches, setBreaches] = useState<EnvironmentalReading[]>([]);
  const [overdueEquipment, setOverdueEquipment] = useState<EquipmentAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<string>('month');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [violRes, envRes, eqRes] = await Promise.all([
        complianceApi.violations({ limit: 50 }),
        environmentApi.breaches({ limit: 20 }),
        equipmentApi.expiryAlerts(),
      ]);
      setViolations(violRes.data.data ?? []);
      setBreaches(envRes.data.data ?? []);
      setOverdueEquipment(eqRes.data.data ?? []);
    } catch { /* no data */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  const handlePrint = () => window.print();

  const violationCols = [
    { title: '#', key: 'idx', render: (_: unknown, __: unknown, i: number) => i + 1 },
    { title: 'Violation Type', dataIndex: 'violation_type', key: 'vt', render: (v: string) => <Tag color="red">{v?.replace(/_/g, ' ')}</Tag> },
    { title: 'Severity', dataIndex: 'severity', key: 'sev', render: (v: string) => <Tag>{v}</Tag> },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={v === 'RESOLVED' ? 'success' : v === 'OPEN' ? 'error' : 'warning'}>{v}</Tag> },
    { title: 'Confidence', dataIndex: 'confidence_score', key: 'conf', render: (v: number) => `${((v ?? 0) * 100).toFixed(1)}%` },
    { title: 'Date', dataIndex: 'created_at', key: 'at', render: (v: string) => dayjs(v).format('DD MMM YY HH:mm') },
  ];

  const breachCols = [
    { title: 'Sensor', dataIndex: 'sensor_code', key: 'sensor' },
    { title: 'CH₄ %', dataIndex: 'methane_ch4_pct', key: 'ch4', render: (v: number) => <span style={{ color: '#ef4444', fontWeight: 700 }}>{v?.toFixed(3)}%</span> },
    { title: 'CO ppm', dataIndex: 'carbon_monoxide_co_ppm', key: 'co', render: (v: number) => v?.toFixed(1) },
    { title: 'O₂ %', dataIndex: 'oxygen_o2_pct', key: 'o2', render: (v: number) => v?.toFixed(1) },
    { title: 'Timestamp', dataIndex: 'created_at', key: 'at', render: (v: string) => dayjs(v).format('DD MMM YY HH:mm') },
  ];

  const equipmentCols = [
    { title: 'Asset', dataIndex: 'name', key: 'name', render: (v: string) => <Text style={{ fontWeight: 600 }}>{v}</Text> },
    { title: 'Code', dataIndex: 'asset_code', key: 'code', render: (v: string) => <Text code>{v}</Text> },
    { title: 'Category', dataIndex: 'category', key: 'cat', render: (v: string) => <Tag>{v}</Tag> },
    {
      title: 'Fitness Expiry', dataIndex: 'fitness_expiry_date', key: 'expiry',
      render: (v: string) => {
        const overdue = dayjs(v).isBefore(dayjs());
        return <span style={{ color: overdue ? '#ef4444' : '#f97316', fontWeight: 700 }}>
          {dayjs(v).format('DD MMM YY')} {overdue ? '⚠ OVERDUE' : ''}
        </span>;
      },
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Compliance & Statutory Reports</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            DGMS / MoEFCC Compliance Summary · Exportable Audit-Ready Reports
          </Text>
        </Col>
        <Col>
          <Space>
            <Select value={period} onChange={setPeriod} style={{ width: 140 }}>
              <Option value="week">Last 7 Days</Option>
              <Option value="month">Last 30 Days</Option>
              <Option value="quarter">Last 90 Days</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
            <Button icon={<PrinterOutlined />} onClick={handlePrint}>Export / Print</Button>
          </Space>
        </Col>
      </Row>

      {/* Summary KPIs */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card size="small" bordered style={{ borderRadius: 8, borderTop: '3px solid #ef4444' }}>
            <Statistic title="Total Violations" value={violations.length} valueStyle={{ color: '#ef4444' }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" bordered style={{ borderRadius: 8, borderTop: '3px solid #f97316' }}>
            <Statistic title="Gas Breaches" value={breaches.length} valueStyle={{ color: '#f97316' }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" bordered style={{ borderRadius: 8, borderTop: '3px solid #7c3aed' }}>
            <Statistic title="Equipment Non-Compliant" value={overdueEquipment.length} valueStyle={{ color: '#7c3aed' }} />
          </Card>
        </Col>
      </Row>

      {/* Section A: PPE & CCTV Violations */}
      <Card
        title={<Space><FileProtectOutlined />Section A — CCTV & PPE Statutory Violations</Space>}
        bordered
        style={{ borderRadius: 10, marginBottom: 16 }}
      >
        <Table
          dataSource={violations}
          columns={violationCols}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
          loading={loading}
          locale={{ emptyText: 'No violations recorded. Run CCTV simulation.' }}
        />
      </Card>

      {/* Section B: Gas Breaches */}
      <Card
        title={<Space>⚗ Section B — Environmental Gas Threshold Breaches</Space>}
        bordered
        style={{ borderRadius: 10, marginBottom: 16 }}
      >
        <Table
          dataSource={breaches}
          columns={breachCols}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 8 }}
          loading={loading}
          locale={{ emptyText: 'No gas breaches detected. Run gas breach simulation.' }}
        />
      </Card>

      {/* Section C: Equipment Non-Compliance */}
      <Card
        title={<Space>⚙ Section C — Equipment Certificate Non-Compliance</Space>}
        bordered
        style={{ borderRadius: 10 }}
      >
        <Table
          dataSource={overdueEquipment}
          columns={equipmentCols}
          rowKey="id"
          size="small"
          pagination={false}
          loading={loading}
          locale={{ emptyText: 'All equipment certificates are valid.' }}
        />
      </Card>

      {/* Print styles */}
      <style>{`
        @media print {
          .ant-layout-sider, .ant-layout-header, .ant-btn { display: none !important; }
          .ant-card { box-shadow: none !important; break-inside: avoid; }
        }
      `}</style>
    </div>
  );
};
