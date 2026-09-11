import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Modal,
  Statistic, notification, Empty, Progress, Alert,
} from 'antd';
import {
  ToolOutlined, ReloadOutlined, FileSearchOutlined, QrcodeOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import type { EquipmentAsset, EquipmentDocument } from '../types';
import { useTheme } from '../contexts/ThemeContext';
import { equipmentApi, demoApi } from '../services/api';

const { Title, Text } = Typography;

const CONDITION_COLOR: Record<string, string> = {
  OPERATIONAL: 'success', UNDER_MAINTENANCE: 'warning', OUT_OF_SERVICE: 'error', DECOMMISSIONED: 'default',
};

const CATEGORY_ICON: Record<string, string> = {
  DUMPER: '🚛', EXCAVATOR: '🚧', DRILL: '⛏️', DOZER: '🚜', LOADER: '🏗️',
};

export const EquipmentOCRPage: React.FC = () => {
  const { isDark } = useTheme();
  const [assets, setAssets] = useState<EquipmentAsset[]>([]);
  const [expiryAlerts, setExpiryAlerts] = useState<EquipmentAsset[]>([]);
  const [documents, setDocuments] = useState<EquipmentDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<EquipmentAsset | null>(null);
  const [docModalOpen, setDocModalOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [assetRes, expiryRes] = await Promise.all([
        equipmentApi.assets({ limit: 50 }),
        equipmentApi.expiryAlerts(),
      ]);
      setAssets(assetRes.data.data ?? []);
      setExpiryAlerts(expiryRes.data.data ?? []);
    } catch { /* no data yet */ }
    setLoading(false);
  };

  const handleViewDocuments = async (asset: EquipmentAsset) => {
    setSelectedAsset(asset);
    setDocModalOpen(true);
    try {
      const res = await equipmentApi.documents(asset.id);
      setDocuments(res.data.data ?? []);
    } catch {
      setDocuments([]);
    }
  };

  const handleSimulateOcr = async () => {
    setScanning(true);
    try {
      const res = await demoApi.simulateOcr();
      notification.success({
        message: 'OCR Pipeline Complete',
        description: `DGMS certificate processed. Confidence: ${((res.data.data?.ocr_confidence ?? 0) * 100).toFixed(1)}%`,
      });
      await fetchData();
    } catch {
      notification.error({ message: 'OCR Scan Error', description: 'Ensure demo seed is run first.' });
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const assetCols = [
    {
      title: 'Asset', key: 'asset',
      render: (_: unknown, r: EquipmentAsset) => (
        <div>
          <div style={{ fontWeight: 600, fontSize: 13 }}>
            {CATEGORY_ICON[r.category] ?? '⚙️'} {r.name}
          </div>
          <Text type="secondary" style={{ fontSize: 11 }}>{r.asset_code} · {r.make_model}</Text>
        </div>
      ),
    },
    {
      title: 'Category', dataIndex: 'category', key: 'cat',
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: 'Condition', dataIndex: 'working_condition', key: 'cond',
      render: (v: string) => <Tag color={CONDITION_COLOR[v] ?? 'default'}>{v}</Tag>,
    },
    {
      title: 'Fitness Expiry', dataIndex: 'fitness_expiry_date', key: 'expiry',
      render: (v: string) => {
        const daysLeft = dayjs(v).diff(dayjs(), 'day');
        const color = daysLeft < 0 ? 'red' : daysLeft < 15 ? 'orange' : daysLeft < 30 ? 'gold' : 'green';
        return (
          <span>
            <span style={{ color, fontWeight: 600 }}>{dayjs(v).format('DD MMM YY')}</span>
            <br />
            <Text type="secondary" style={{ fontSize: 11 }}>
              {daysLeft < 0 ? `${Math.abs(daysLeft)}d overdue` : `${daysLeft}d left`}
            </Text>
          </span>
        );
      },
    },
    {
      title: '', key: 'actions',
      render: (_: unknown, r: EquipmentAsset) => (
        <Space size={4}>
          <Button size="small" icon={<FileSearchOutlined />} onClick={() => handleViewDocuments(r)}>Docs</Button>
        </Space>
      ),
    },
  ];

  const docCols = [
    { title: 'Document Type', dataIndex: 'document_type', key: 'dtype', render: (v: string) => <Tag>{v.replace(/_/g, ' ')}</Tag> },
    {
      title: 'OCR Confidence',
      dataIndex: 'ocr_confidence',
      key: 'conf',
      render: (v: number) => (
        <Progress percent={Math.round((v ?? 0) * 100)} size="small" status={v > 0.8 ? 'success' : 'exception'} style={{ width: 120 }} />
      ),
    },
    {
      title: 'Validity', dataIndex: 'valid_until', key: 'valid',
      render: (v: string) => v ? dayjs(v).format('DD MMM YY') : '—',
    },
    {
      title: 'Status', dataIndex: 'verification_status', key: 'status',
      render: (v: string) => <Tag color={v === 'VERIFIED' ? 'success' : 'warning'}>{v}</Tag>,
    },
    { title: 'Uploaded', dataIndex: 'created_at', key: 'at', render: (v: string) => dayjs(v).format('DD/MM HH:mm') },
  ];

  const overdueCount = expiryAlerts.filter((a) => dayjs(a.fitness_expiry_date).isBefore(dayjs())).length;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>Equipment Registry & Statutory OCR Scanner</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            HEMM asset tracking, QR codes & DGMS fitness certificate digitization
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
            <Button
              type="primary"
              icon={<FileSearchOutlined />}
              loading={scanning}
              onClick={handleSimulateOcr}
            >
              Run OCR Scan (Synthetic DGMS Certificate)
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Expiry alert banners */}
      {overdueCount > 0 && (
        <Alert
          type="error"
          showIcon
          message={`${overdueCount} equipment asset(s) have overdue DGMS fitness certificates!`}
          style={{ marginBottom: 16, borderRadius: 8 }}
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Total Assets" value={assets.length} prefix={<ToolOutlined />} /></Card></Col>
        <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Overdue Certificates" value={overdueCount} valueStyle={{ color: '#ef4444' }} /></Card></Col>
        <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Expiring <30 Days" value={expiryAlerts.length - overdueCount} valueStyle={{ color: '#f97316' }} /></Card></Col>
      </Row>

      <Card title="Equipment Asset Registry" bordered style={{ borderRadius: 10 }}>
        <Table
          dataSource={assets}
          columns={assetCols}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
          loading={loading}
          locale={{ emptyText: <Empty description="Seed demo data to view equipment assets." /> }}
        />
      </Card>

      {/* OCR Process Visual */}
      <Card
        title={<Space><FileSearchOutlined />OCR Document Pipeline</Space>}
        bordered
        style={{ borderRadius: 10, marginTop: 16 }}
      >
        <Row gutter={[16, 16]} align="middle">
          {[
            { step: '1', icon: '📄', label: 'Document Upload / Synthetic Generation', desc: 'DGMS fitness cert, calibration record, insurance doc' },
            { step: '2', icon: '🔍', label: 'Tesseract OCR Extraction', desc: 'Multi-region text parsing with confidence scoring' },
            { step: '3', icon: '🧠', label: 'Regex + NLP Parser', desc: 'Certificate number, issue/expiry date, asset code, status' },
            { step: '4', icon: '📅', label: 'Asset Registry Update', desc: 'fitness_expiry_date auto-updated, calendar alerts triggered' },
          ].map((s) => (
            <Col xs={24} sm={12} md={6} key={s.step}>
              <Card
                size="small"
                style={{ borderRadius: 8, textAlign: 'center', borderTop: isDark ? '3px solid #3b82f6' : '3px solid #2563eb' }}
              >
                <div style={{ fontSize: 24 }}>{s.icon}</div>
                <div style={{ fontSize: 11, fontWeight: 700, marginTop: 4, color: isDark ? '#60a5fa' : '#2563eb' }}>Step {s.step}</div>
                <div style={{ fontSize: 12, fontWeight: 600, marginTop: 2 }}>{s.label}</div>
                <div style={{ fontSize: 11, marginTop: 4 }}><Text type="secondary">{s.desc}</Text></div>
              </Card>
            </Col>
          ))}
        </Row>
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Button
            type="primary"
            icon={<QrcodeOutlined />}
            loading={scanning}
            onClick={handleSimulateOcr}
            size="large"
          >
            Generate & Scan Synthetic DGMS Certificate
          </Button>
        </div>
      </Card>

      {/* Document modal */}
      <Modal
        title={`Documents — ${selectedAsset?.name ?? ''}`}
        open={docModalOpen}
        onCancel={() => { setDocModalOpen(false); setSelectedAsset(null); }}
        footer={null}
        width={750}
      >
        <Table
          dataSource={documents}
          columns={docCols}
          rowKey="id"
          size="small"
          pagination={false}
          locale={{ emptyText: 'No documents uploaded yet. Run OCR Scan to create one.' }}
        />
      </Modal>
    </div>
  );
};
