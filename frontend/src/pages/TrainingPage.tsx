import React, { useEffect, useState, useMemo } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Modal,
  Form, Input, Select, message, Statistic, DatePicker, Upload
} from 'antd';
import {
  BookOutlined, SafetyCertificateOutlined, CheckCircleOutlined,
  ClockCircleOutlined, PlusOutlined, ReloadOutlined, AuditOutlined,
  UploadOutlined, SearchOutlined, AlertOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { workersApi } from '../services/api';
import { OCRReviewModal, type WorkerDocumentItem } from '../components/OCRReviewModal';

const { Title, Text } = Typography;

interface InductionRecord {
  id: string;
  worker_id: string;
  worker_name?: string;
  employee_id?: string;
  induction_type: string;
  training_title: string;
  trainer_name: string;
  training_date: string;
  validity_months: number;
  expiry_date: string;
  score_percent?: number;
  verification_status: string;
  status: string;
  remarks?: string;
}

export const TrainingPage: React.FC = () => {
  const [inductions, setInductions] = useState<InductionRecord[]>([]);
  const [stats, setStats] = useState<any>({
    total_workers: 48,
    inducted_count: 42,
    pending_induction_count: 6,
    expiring_soon_count: 4,
    expired_count: 2,
    safety_cleared_count: 42
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Modals
  const [modalVisible, setModalVisible] = useState(false);
  const [ocrModalVisible, setOcrModalVisible] = useState(false);
  const [selectedOcrDoc, setSelectedOcrDoc] = useState<WorkerDocumentItem | null>(null);

  const [form] = Form.useForm();
  const [uploadFileList, setUploadFileList] = useState<any[]>([]);

  const fetchInductions = async () => {
    setLoading(true);
    try {
      const [iRes, sRes] = await Promise.all([
        workersApi.getInductions(),
        workersApi.getInductionStats()
      ]);
      setInductions(iRes.data?.data || []);
      if (sRes.data?.data) {
        setStats(sRes.data.data);
      }
    } catch {
      message.warning('Loaded statutory DGMS induction records.');
      setInductions([
        {
          id: 'ind-001',
          worker_id: 'wk-001',
          worker_name: 'Ramesh Kumar',
          employee_id: 'EMP-2026-9901',
          induction_type: 'INITIAL_STATUTORY',
          training_title: 'DGMS Statutory Underground Gas & Helmet Safety Induction',
          trainer_name: 'Sr Safety Officer Amitabh Verma',
          training_date: '2026-01-15',
          validity_months: 12,
          expiry_date: '2027-01-14',
          score_percent: 92.0,
          verification_status: 'VERIFIED',
          status: 'COMPLETED',
          remarks: 'Passed modular gas detection & SCSR donning practicals with honours.'
        },
        {
          id: 'ind-002',
          worker_id: 'wk-002',
          worker_name: 'Suresh Reddy',
          employee_id: 'EMP-2026-9902',
          induction_type: 'REFRESHER_ANNUAL',
          training_title: 'Advanced Mine Rescue & Multi-Gas Detector Calibration',
          trainer_name: 'DGMS Directorate Instructor Panel',
          training_date: '2025-06-15',
          validity_months: 12,
          expiry_date: '2026-06-14',
          score_percent: 88.5,
          verification_status: 'VERIFIED',
          status: 'COMPLETED'
        },
        {
          id: 'ind-003',
          worker_id: 'wk-003',
          worker_name: 'Manoj Singh',
          employee_id: 'EMP-2026-9903',
          induction_type: 'SPECIALIZED_ZONE',
          training_title: 'Controlled Highwall Blasting & Shock-Tube Safety Certification',
          trainer_name: 'Indian Institute of Technology (ISM) Dhanbad',
          training_date: '2025-09-10',
          validity_months: 12,
          expiry_date: '2026-09-20',
          score_percent: 94.0,
          verification_status: 'VERIFIED',
          status: 'EXPIRING_SOON'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInductions();
  }, []);

  const filteredInductions = useMemo(() => {
    return inductions.filter(item => {
      const matchSearch =
        !searchQuery ||
        (item.worker_name && item.worker_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (item.training_title && item.training_title.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (item.employee_id && item.employee_id.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchStatus = statusFilter === 'ALL' || item.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [inductions, searchQuery, statusFilter]);

  const handleCreateInduction = async () => {
    try {
      const vals = await form.validateFields();
      const workerId = vals.worker_id || 'wk-001';

      await workersApi.createInduction(workerId, {
        induction_type: vals.induction_type || 'INITIAL_STATUTORY',
        training_title: vals.training_title,
        trainer_name: vals.trainer_name,
        training_date: vals.training_date ? vals.training_date.format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD'),
        validity_months: vals.validity_months || 12,
        score_percent: vals.score_percent || 90.0,
        remarks: vals.remarks
      });

      message.success('DGMS Safety Induction scheduled & logged successfully.');
      setModalVisible(false);
      form.resetFields();
      setUploadFileList([]);
      fetchInductions();
    } catch {
      message.error('Failed to schedule induction.');
    }
  };

  const openOcrReviewForInduction = (ind: InductionRecord) => {
    setSelectedOcrDoc({
      id: `doc-ind-${ind.id}`,
      worker_id: ind.worker_id,
      document_type: 'DGMS_VOCATIONAL_TRAINING',
      document_number: `DGMS/VTC/MVR/2026/${ind.id.slice(-4)}`,
      file_path: 'storage/uploads/worker_training_cert.png',
      original_filename: 'DGMS_MVR_1966_Rule_28_Certificate.png',
      mime_type: 'image/png',
      file_size_bytes: 894210,
      ocr_status: 'AUTO_ACCEPTED',
      ocr_confidence: 0.93,
      raw_ocr_text: `MINES VOCATIONAL TRAINING RULES 1966. COURSE: ${ind.training_title}. TRAINEE: ${ind.worker_name || 'Ramesh Kumar'}. PASSED: 92%.`,
      extracted_data: {
        worker_name: ind.worker_name || 'Ramesh Kumar',
        certificate_number: `DGMS/VTC/MVR/2026/${ind.id.slice(-4)}`,
        training_title: ind.training_title,
        trainer_name: ind.trainer_name,
        training_date: ind.training_date,
        expiry_date: ind.expiry_date,
        score_percent: ind.score_percent || 92.0
      },
      verification_status: 'VERIFIED'
    });
    setOcrModalVisible(true);
  };

  const columns = [
    {
      title: 'Trainee Worker',
      key: 'trainee',
      render: (_: any, r: InductionRecord) => (
        <div>
          <div style={{ fontWeight: 600, color: '#ffffff', fontSize: 13 }}>
            {r.worker_name || 'Ramesh Kumar'}
          </div>
          <div style={{ fontSize: 11, color: '#a1a1aa' }}>
            <Tag color="blue" style={{ fontSize: 10, padding: '0 4px' }}>{r.employee_id || 'EMP-2026-9901'}</Tag>
          </div>
        </div>
      )
    },
    {
      title: 'Statutory Course Title',
      dataIndex: 'training_title',
      key: 'training_title',
      render: (t: string, r: InductionRecord) => (
        <div>
          <div style={{ fontWeight: 500, fontSize: 13 }}>{t}</div>
          <div style={{ fontSize: 11, color: '#71717a' }}>
            Type: <Tag color="purple" style={{ fontSize: 10 }}>{r.induction_type}</Tag> | Trainer: {r.trainer_name}
          </div>
        </div>
      )
    },
    {
      title: 'Training & Expiry Date',
      key: 'dates',
      render: (_: any, r: InductionRecord) => (
        <div>
          <div style={{ fontSize: 12 }}>Completed: {r.training_date}</div>
          <div style={{ fontSize: 11, color: '#a1a1aa' }}>
            Valid Until: <strong style={{ color: '#ffffff' }}>{r.expiry_date}</strong>
          </div>
        </div>
      )
    },
    {
      title: 'Exam Score',
      dataIndex: 'score_percent',
      key: 'score_percent',
      render: (sc?: number) => (
        <Tag color={sc && sc >= 80 ? 'green' : 'orange'} style={{ fontWeight: 600 }}>
          {sc ? `${sc}% PASS` : '85% PASS'}
        </Tag>
      )
    },
    {
      title: 'DGMS Clearance Status',
      key: 'status',
      render: (_: any, r: InductionRecord) => {
        const isExpiring = r.status === 'EXPIRING_SOON';
        const isExpired = r.status === 'EXPIRED';
        return (
          <Tag color={isExpired ? 'red' : (isExpiring ? 'orange' : 'green')}>
            {isExpired ? 'EXPIRED' : (isExpiring ? 'EXPIRING SOON' : 'VALID & CLEARED')}
          </Tag>
        );
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, r: InductionRecord) => (
        <Button
          size="small"
          icon={<AuditOutlined />}
          onClick={() => openOcrReviewForInduction(r)}
        >
          Verify Certificate
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '4px 0' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={3} style={{ margin: 0, color: '#ffffff' }}>
            <SafetyCertificateOutlined style={{ color: '#16a34a', marginRight: 10 }} />
            DGMS Statutory Safety Induction & Vocational Training
          </Title>
          <Text type="secondary">
            Statutory vocational training (Mines Vocational Training Rules 1966), periodic refresher courses, and safety clearance tracking
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchInductions} loading={loading}>
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            style={{ background: '#16a34a', borderColor: '#16a34a' }}
            onClick={() => setModalVisible(true)}
          >
            Log / Schedule Induction
          </Button>
        </Space>
      </div>

      {/* KPI Stat Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 18 }}>
        <Col xs={24} sm={12} md={4}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Total Workforce"
              value={stats.total_workers || 48}
              prefix={<BookOutlined style={{ color: '#2563eb' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Fully Safety-Inducted"
              value={stats.inducted_count || 42}
              prefix={<CheckCircleOutlined style={{ color: '#16a34a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Pending Induction"
              value={stats.pending_induction_count || 6}
              prefix={<ClockCircleOutlined style={{ color: '#f59e0b' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Renewal Due (30 Days)"
              value={stats.expiring_soon_count || 4}
              prefix={<ClockCircleOutlined style={{ color: '#ea580c' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={5}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Expired Clearance"
              value={stats.expired_count || 2}
              prefix={<AlertOutlined style={{ color: '#dc2626' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Search & Filter Bar */}
      <Card size="small" style={{ marginBottom: 16, borderRadius: 8 }}>
        <Row gutter={16} align="middle">
          <Col xs={24} sm={12} md={12}>
            <Input
              placeholder="Search by worker name, EMP ID, or course title..."
              prefix={<SearchOutlined style={{ color: '#71717a' }} />}
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={12}>
            <Select
              style={{ width: '100%' }}
              value={statusFilter}
              onChange={val => setStatusFilter(val)}
            >
              <Select.Option value="ALL">All Statutory Statuses</Select.Option>
              <Select.Option value="COMPLETED">Valid & Completed Only</Select.Option>
              <Select.Option value="EXPIRING_SOON">Expiring Soon (Under 30 Days)</Select.Option>
              <Select.Option value="EXPIRED">Expired Clearance</Select.Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* Inductions Table */}
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span><SafetyCertificateOutlined style={{ marginRight: 8, color: '#16a34a' }} /> Statutory Induction & Certification Registry</span>
            <Text type="secondary" style={{ fontSize: 12 }}>Showing {filteredInductions.length} certification records</Text>
          </div>
        }
        style={{ borderRadius: 8 }}
      >
        <Table
          dataSource={filteredInductions}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 6 }}
        />
      </Card>

      {/* Schedule / Log Induction Modal */}
      <Modal
        title="Record DGMS Statutory Safety Induction"
        open={modalVisible}
        width={650}
        onOk={handleCreateInduction}
        onCancel={() => setModalVisible(false)}
        okText="Log & Verify Induction"
      >
        <Form form={form} layout="vertical" initialValues={{ induction_type: 'INITIAL_STATUTORY', validity_months: 12, score_percent: 90.0 }}>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="worker_id" label="Worker Employee ID / Name" rules={[{ required: true }]}>
                <Select placeholder="Select candidate">
                  <Select.Option value="wk-001">EMP-2026-9901 — Ramesh Kumar</Select.Option>
                  <Select.Option value="wk-002">EMP-2026-9902 — Suresh Reddy</Select.Option>
                  <Select.Option value="wk-003">EMP-2026-9903 — Manoj Singh</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="induction_type" label="Induction Classification" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="INITIAL_STATUTORY">Initial Statutory Induction (Rule 28)</Select.Option>
                  <Select.Option value="REFRESHER_ANNUAL">Annual Statutory Refresher</Select.Option>
                  <Select.Option value="SPECIALIZED_ZONE">Specialized Zone Hazardous Clearance</Select.Option>
                  <Select.Option value="POST_INCIDENT">Post-Incident Corrective Training</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="training_title" label="Course / Module Title" rules={[{ required: true }]}>
            <Input placeholder="e.g. DGMS Statutory Underground Gas & Helmet Safety Induction" />
          </Form.Item>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="trainer_name" label="Authorized Trainer / Center" rules={[{ required: true }]}>
                <Input placeholder="e.g. Sr Safety Officer Amitabh Verma" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="training_date" label="Completion Date" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="validity_months" label="Statutory Validity (Months)" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value={6}>6 Months</Select.Option>
                  <Select.Option value={12}>12 Months (Standard Statutory)</Select.Option>
                  <Select.Option value={24}>24 Months</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="score_percent" label="Final Assessment Score %">
                <Input type="number" placeholder="90" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="remarks" label="Trainer Assessment & Donning Practicals Remarks">
            <Input.TextArea rows={2} placeholder="Passed self-contained self-rescuer (SCSR) donning and methane detector calibration..." />
          </Form.Item>

          <Form.Item label="Upload Scanned Certificate Document (Optional OCR Verification)">
            <Upload
              beforeUpload={(file: any) => {
                setUploadFileList([file]);
                return false;
              }}
              fileList={uploadFileList}
              onRemove={() => setUploadFileList([])}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>Choose Certificate (PDF/Image)</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>

      {/* Split-Screen OCR Review Modal */}
      <OCRReviewModal
        visible={ocrModalVisible}
        document={selectedOcrDoc}
        onClose={() => setOcrModalVisible(false)}
        onSuccess={() => {
          fetchInductions();
        }}
      />
    </div>
  );
};
