import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Timeline,
  Statistic, notification, Modal, Form, Input, DatePicker, Badge,
} from 'antd';
import {
  AlertOutlined, CheckCircleOutlined, ReloadOutlined, ClockCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Alert, CorrectiveAction } from '../types';
import { workflowApi } from '../services/api';

const { Title, Text } = Typography;

const SLA_LEVELS: Record<number, { label: string; color: string; minutes: number }> = {
  1: { label: 'L1 — Safety Officer', color: '#22c55e', minutes: 15 },
  2: { label: 'L2 — Mine Manager', color: '#f97316', minutes: 60 },
  3: { label: 'L3 — Director Technical', color: '#ef4444', minutes: 240 },
};

const SEV_COLOR: Record<string, string> = {
  INFO: 'blue', WARNING: 'orange', HIGH: 'red', CRITICAL: 'volcano', EMERGENCY: 'magenta',
};

export const WorkflowsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [caList, setCaList] = useState<CorrectiveAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [acknowledging, setAcknowledging] = useState<string | null>(null);
  const [caModalOpen, setCaModalOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [alertRes, caRes] = await Promise.all([
        workflowApi.alerts({ limit: 30 }),
        workflowApi.correctiveActions({ limit: 30 }),
      ]);
      setAlerts(alertRes.data.data ?? []);
      setCaList(caRes.data.data ?? []);
    } catch { /* no data */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  const handleAcknowledge = async (alertId: string) => {
    setAcknowledging(alertId);
    try {
      await workflowApi.acknowledge(alertId);
      notification.success({ message: 'Alert Acknowledged', description: 'SLA clock paused.' });
      await fetchData();
    } catch {
      notification.error({ message: 'Error', description: 'Could not acknowledge alert.' });
    } finally {
      setAcknowledging(null);
    }
  };

  const handleCreateCA = async (values: Record<string, unknown>) => {
    try {
      await workflowApi.createCA({ ...values, alert_id: selectedAlert?.id });
      notification.success({ message: 'Corrective Action Created' });
      form.resetFields();
      setCaModalOpen(false);
      setSelectedAlert(null);
      await fetchData();
    } catch {
      notification.error({ message: 'Error creating corrective action' });
    }
  };

  const openAlerts = alerts.filter((a) => a.status === 'OPEN');
  const criticalAlerts = alerts.filter((a) => a.severity === 'CRITICAL' || a.severity === 'EMERGENCY');
  const openCA = caList.filter((c) => c.status !== 'CLOSED' && c.status !== 'RESOLVED');

  const getSlaStatus = (alert: Alert) => {
    if (!alert.sla_deadline) return null;
    const mins = dayjs(alert.sla_deadline).diff(dayjs(), 'minute');
    if (alert.status !== 'OPEN') return <Tag color="success"><CheckCircleOutlined /> Resolved</Tag>;
    if (mins < 0) return <Tag color="error"><ClockCircleOutlined /> Overdue {Math.abs(mins)}m</Tag>;
    return <Tag color={mins < 15 ? 'warning' : 'processing'}><ClockCircleOutlined /> {mins}m left</Tag>;
  };

  const alertCols = [
    { title: 'Alert', key: 'info', render: (_: unknown, r: Alert) => (
      <div>
        <div style={{ fontWeight: 600, fontSize: 13 }}>{r.title}</div>
        <Text type="secondary" style={{ fontSize: 11 }}>{r.message?.slice(0, 80)}</Text>
      </div>
    )},
    { title: 'Severity', dataIndex: 'severity', key: 'sev', render: (v: string) => <Tag color={SEV_COLOR[v]}>{v}</Tag> },
    { title: 'SLA', dataIndex: 'sla_level', key: 'sla', render: (v: number) => <Tag color={SLA_LEVELS[v]?.color}>{SLA_LEVELS[v]?.label}</Tag> },
    { title: 'Deadline', key: 'deadline', render: (_: unknown, r: Alert) => getSlaStatus(r) },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Badge status={v === 'OPEN' ? 'error' : 'success'} text={v} /> },
    { title: 'Created', dataIndex: 'created_at', key: 'at', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
    { title: '', key: 'actions', render: (_: unknown, r: Alert) => (
      <Space size={4}>
        {r.status === 'OPEN' && (
          <Button
            size="small"
            type="primary"
            icon={<CheckCircleOutlined />}
            loading={acknowledging === r.id}
            onClick={() => handleAcknowledge(r.id)}
          >
            Ack
          </Button>
        )}
        <Button
          size="small"
          icon={<AlertOutlined />}
          onClick={() => { setSelectedAlert(r); setCaModalOpen(true); }}
        >
          + CAPA
        </Button>
      </Space>
    )},
  ];

  const caCols = [
    { title: 'Title', dataIndex: 'title', key: 'title', render: (v: string) => <Text style={{ fontSize: 13 }}>{v}</Text> },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => {
      const colors: Record<string, string> = { OPEN: 'red', IN_PROGRESS: 'blue', PENDING_VERIFICATION: 'orange', RESOLVED: 'success', CLOSED: 'default' };
      return <Tag color={colors[v] ?? 'default'}>{v?.replace(/_/g, ' ')}</Tag>;
    }},
    { title: 'Assigned To', dataIndex: 'assigned_to', key: 'assigned', render: (v: string) => v ?? '—' },
    { title: 'Due', dataIndex: 'due_date', key: 'due', render: (v: string) => v ? dayjs(v).format('DD MMM YY') : '—' },
    { title: 'Created', dataIndex: 'created_at', key: 'at', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Alerts, SLA Escalations & Corrective Actions</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            3-Tier SLA Escalation: 15m → 60m → 240m · CAPA lifecycle tracking
          </Text>
        </Col>
        <Col>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
        </Col>
      </Row>

      {/* KPI row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={6}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Open Alerts" value={openAlerts.length} valueStyle={{ color: '#ef4444' }} /></Card></Col>
        <Col xs={24} sm={6}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Critical / Emergency" value={criticalAlerts.length} valueStyle={{ color: '#7c3aed' }} /></Card></Col>
        <Col xs={24} sm={6}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Open CAPAs" value={openCA.length} valueStyle={{ color: '#f97316' }} /></Card></Col>
        <Col xs={24} sm={6}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Total Alerts" value={alerts.length} /></Card></Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* SLA tier reference */}
        <Col xs={24} lg={7}>
          <Card title="SLA Escalation Tiers" bordered style={{ borderRadius: 10 }}>
            <Timeline
              items={Object.entries(SLA_LEVELS).map(([level, info]) => ({
                color: info.color,
                children: (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>Level {level}</div>
                    <div style={{ fontSize: 12, color: '#525252' }}>{info.label}</div>
                    <Tag color={info.color} style={{ marginTop: 4, fontSize: 11 }}>
                      Response within {info.minutes}m
                    </Tag>
                  </div>
                ),
              }))}
            />
          </Card>
        </Col>

        {/* Alerts table */}
        <Col xs={24} lg={17}>
          <Card
            title={<Space><AlertOutlined />Active Alerts & SLA Status</Space>}
            bordered
            style={{ borderRadius: 10 }}
          >
            <Table
              dataSource={alerts}
              columns={alertCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 8 }}
              loading={loading}
              scroll={{ x: 900 }}
              locale={{ emptyText: 'No alerts. Run demo simulations to generate alerts.' }}
              rowClassName={(r) => r.severity === 'EMERGENCY' ? 'ant-table-row-danger' : ''}
            />
          </Card>
        </Col>

        {/* CAPA table */}
        <Col xs={24}>
          <Card title="Corrective & Preventive Actions (CAPA)" bordered style={{ borderRadius: 10 }}>
            <Table
              dataSource={caList}
              columns={caCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 8 }}
              loading={loading}
              locale={{ emptyText: 'No corrective actions. Click "+ CAPA" on an alert to create one.' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Create CAPA modal */}
      <Modal
        title={`New Corrective Action${selectedAlert ? ` — ${selectedAlert.title}` : ''}`}
        open={caModalOpen}
        onCancel={() => { setCaModalOpen(false); setSelectedAlert(null); form.resetFields(); }}
        onOk={() => form.submit()}
        okText="Create Action"
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateCA} style={{ marginTop: 16 }}>
          <Form.Item name="title" label="Action Title" rules={[{ required: true }]}>
            <Input placeholder="e.g., Provide hardhat to all workers in Zone PIT-01" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} placeholder="Detailed steps to rectify the violation or breach..." />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="assigned_to" label="Assign To">
                <Input placeholder="Officer name / designation" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="due_date" label="Due Date">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="mine_id" label="Mine" initialValue={selectedAlert?.mine_id}>
            <Input disabled />
          </Form.Item>
        </Form>
      </Modal>

      <style>{`
        .ant-table-row-danger td { background: #fff5f5 !important; }
      `}</style>
    </div>
  );
};
