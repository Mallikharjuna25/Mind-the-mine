import React, { useEffect, useState, useRef } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Badge, Descriptions,
  Modal, Statistic, notification, Empty, Tooltip,
} from 'antd';
import {
  CameraOutlined, PlayCircleOutlined, ReloadOutlined, EyeOutlined, CheckCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import type { Camera, DetectionEvent, Violation } from '../types';
import { cctvApi, demoApi } from '../services/api';

const { Title, Text } = Typography;

const DETECTION_COLOR: Record<string, string> = {
  PPE_VIOLATION: 'red',
  RESTRICTED_ZONE: 'volcano',
  FIRE_SMOKE: 'magenta',
};

export const CCTVMonitoringPage: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [detections, setDetections] = useState<DetectionEvent[]>([]);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [camRes, detRes, violRes] = await Promise.all([
        cctvApi.cameras(),
        cctvApi.detections({ limit: 20 }),
        cctvApi.violations({ limit: 20 }),
      ]);
      setCameras(camRes.data.data ?? []);
      setDetections(detRes.data.data ?? []);
      setViolations(violRes.data.data ?? []);
    } catch { /* no data yet */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  // Animated fake CCTV canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frame = 0;
    const draw = () => {
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Scanline effect
      for (let y = 0; y < canvas.height; y += 4) {
        ctx.fillStyle = 'rgba(255,255,255,0.02)';
        ctx.fillRect(0, y, canvas.width, 1);
      }

      // Noise dots
      for (let i = 0; i < 60; i++) {
        ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.08})`;
        ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 1, 1);
      }

      // Simulated figure silhouette
      const x = 180 + Math.sin(frame / 40) * 30;
      ctx.fillStyle = '#334155';
      ctx.fillRect(x, 90, 18, 40);
      ctx.beginPath();
      ctx.arc(x + 9, 80, 12, 0, Math.PI * 2);
      ctx.fill();

      // PPE bounding box (red)
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 2]);
      ctx.strokeRect(x - 8, 65, 38, 72);
      ctx.setLineDash([]);
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 9px monospace';
      ctx.fillText('NO_HELMET 0.92', x - 8, 62);

      // Timestamp
      ctx.fillStyle = '#94a3b8';
      ctx.font = '9px monospace';
      ctx.fillText(`CAM-PIT-FACE-01  ${dayjs().format('HH:mm:ss')}`, 6, 14);
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(canvas.width - 14, 10, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#94a3b8';
      ctx.font = '9px monospace';
      ctx.fillText('●REC', canvas.width - 44, 14);

      frame++;
      animRef.current = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  const handleSimulateViolation = async () => {
    setSimulating(true);
    try {
      await demoApi.simulateViolation();
      notification.success({ message: 'PPE Violation Simulated', description: 'Detection ingested & promoted to violation.' });
      await fetchData();
    } catch {
      notification.error({ message: 'Error', description: 'Run /demo/seed first.' });
    } finally {
      setSimulating(false);
    }
  };

  const detectionCols = [
    { title: 'Type', dataIndex: 'detection_type', key: 'type', render: (v: string) => <Tag color={DETECTION_COLOR[v] ?? 'default'} style={{ fontSize: 11 }}>{v}</Tag> },
    { title: 'Class', dataIndex: 'raw_class_name', key: 'class', render: (v: string) => <Text code style={{ fontSize: 11 }}>{v}</Text> },
    {
      title: 'Conf', dataIndex: 'confidence_score', key: 'conf',
      render: (v: number) => <Tag color={v > 0.85 ? 'red' : v > 0.75 ? 'orange' : 'green'}>{(v * 100).toFixed(0)}%</Tag>,
    },
    { title: 'Promoted', dataIndex: 'is_promoted', key: 'promoted', render: (v: boolean) => v ? <CheckCircleOutlined style={{ color: '#ef4444' }} /> : '—' },
    { title: 'Time', dataIndex: 'created_at', key: 'time', render: (v: string) => dayjs(v).format('HH:mm:ss') },
  ];

  const violationCols = [
    { title: 'Violation', dataIndex: 'violation_type', key: 'vtype', render: (v: string) => <Tag color="red" style={{ fontSize: 11 }}>{v}</Tag> },
    {
      title: 'Severity', dataIndex: 'severity', key: 'sev',
      render: (v: string) => <Tag color={v === 'CRITICAL' ? 'volcano' : v === 'HIGH' ? 'red' : 'orange'}>{v}</Tag>,
    },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Badge status={v === 'OPEN' ? 'error' : 'processing'} text={v} /> },
    { title: 'Time', dataIndex: 'created_at', key: 'time', render: (v: string) => dayjs(v).format('HH:mm DD/MM') },
    {
      title: '', key: 'action',
      render: (_: unknown, r: Violation) => (
        <Tooltip title="View Details">
          <Button size="small" icon={<EyeOutlined />} onClick={() => setSelectedViolation(r)} />
        </Tooltip>
      ),
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>AI Vision — CCTV Monitoring</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Real-time PPE violation, zone intrusion & fire/smoke detection
          </Text>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Refresh</Button>
            <Button
              type="primary"
              danger
              icon={<PlayCircleOutlined />}
              loading={simulating}
              onClick={handleSimulateViolation}
            >
              Simulate PPE Violation
            </Button>
          </Space>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Live camera feed */}
        <Col xs={24} lg={10}>
          <Card title="Live Camera Feed — Pit Face East Highwall" bordered style={{ borderRadius: 10 }}>
            <canvas
              ref={canvasRef}
              width={400}
              height={280}
              style={{ width: '100%', borderRadius: 8, background: '#0a0a0a', display: 'block' }}
            />
            <Row gutter={8} style={{ marginTop: 12 }}>
              {cameras.map((cam) => (
                <Col key={cam.id} span={12}>
                  <Card
                    size="small"
                    style={{
                      borderRadius: 8,
                      borderColor: cam.status === 'ACTIVE' ? '#22c55e' : '#e4e4e7',
                    }}
                  >
                    <div style={{ fontSize: 11 }}>
                      <CameraOutlined style={{ marginRight: 4 }} />
                      <strong>{cam.camera_code}</strong>
                    </div>
                    <div style={{ fontSize: 11, color: '#737373', marginTop: 2 }}>{cam.name}</div>
                    <Badge
                      status={cam.status === 'ACTIVE' ? 'success' : 'default'}
                      text={cam.status}
                      style={{ fontSize: 11, marginTop: 4 }}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
            {cameras.length === 0 && <Empty description="Seed demo data to view cameras" style={{ margin: '20px 0' }} />}
          </Card>
        </Col>

        {/* Detection events */}
        <Col xs={24} lg={14}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Total Detections" value={detections.length} /></Card></Col>
            <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Promoted to Violations" value={detections.filter(d => d.is_promoted).length} valueStyle={{ color: '#ef4444' }} /></Card></Col>
            <Col xs={24} sm={8}><Card size="small" bordered style={{ borderRadius: 8 }}><Statistic title="Open Violations" value={violations.filter(v => v.status === 'OPEN').length} valueStyle={{ color: '#f97316' }} /></Card></Col>
          </Row>

          <Card title="Detection Events (Latest 20)" bordered style={{ borderRadius: 10, marginTop: 16 }}>
            <Table
              dataSource={detections}
              columns={detectionCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 8 }}
              locale={{ emptyText: 'No detections yet. Click Simulate PPE Violation.' }}
            />
          </Card>
        </Col>

        {/* Violations table */}
        <Col xs={24}>
          <Card title="Statutory Violations (Promoted Candidates)" bordered style={{ borderRadius: 10 }}>
            <Table
              dataSource={violations}
              columns={violationCols}
              rowKey="id"
              size="small"
              pagination={{ pageSize: 10 }}
              locale={{ emptyText: 'No violations recorded yet.' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Violation detail modal */}
      <Modal
        title="Violation Detail"
        open={!!selectedViolation}
        onCancel={() => setSelectedViolation(null)}
        footer={null}
        width={600}
      >
        {selectedViolation && (
          <Descriptions column={2} size="small" bordered>
            <Descriptions.Item label="Type">{selectedViolation.violation_type}</Descriptions.Item>
            <Descriptions.Item label="Severity">
              <Tag color="red">{selectedViolation.severity}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              <Badge status="error" text={selectedViolation.status} />
            </Descriptions.Item>
            <Descriptions.Item label="Confidence">
              {((selectedViolation.confidence_score ?? 0) * 100).toFixed(1)}%
            </Descriptions.Item>
            <Descriptions.Item label="Description" span={2}>
              {selectedViolation.description}
            </Descriptions.Item>
            <Descriptions.Item label="Recorded At" span={2}>
              {dayjs(selectedViolation.created_at).format('DD MMM YYYY HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};
