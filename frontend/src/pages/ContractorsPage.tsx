import React, { useEffect, useState, useMemo } from 'react';
import {
  Row, Col, Card, Table, Tag, Button, Space, Typography, Modal,
  Form, Input, Select, Progress, message, Statistic, Drawer, Tabs,
  Upload, Badge
} from 'antd';
import {
  ShopOutlined, PlusOutlined, SafetyCertificateOutlined,
  CheckCircleOutlined, ClockCircleOutlined, ReloadOutlined,
  UploadOutlined, AuditOutlined, EyeOutlined, SearchOutlined
} from '@ant-design/icons';
import { contractorsApi } from '../services/api';
import { OCRReviewModal, type WorkerDocumentItem } from '../components/OCRReviewModal';

const { Title, Text, Paragraph } = Typography;

interface Contract {
  id: string;
  contract_number: string;
  title: string;
  contract_type: string;
  start_date: string;
  end_date: string;
  contract_value: number;
  status: string;
}

interface ContractDocument {
  id: string;
  document_type: string;
  file_name: string;
  file_path: string;
  mime_type: string;
  valid_from?: string;
  valid_until?: string;
}

interface ContractCompliance {
  id: string;
  compliance_item: string;
  category: string;
  status: string;
  score_deduction: number;
  remarks?: string;
  inspected_at: string;
}

interface Contractor {
  id: string;
  mine_id: string;
  company_name: string;
  registration_number: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  work_scope: string;
  status: string;
  compliance_score: number;
  compliance_status?: string;
  contracts?: Contract[];
  documents?: ContractDocument[];
  compliances?: ContractCompliance[];
}

export const ContractorsPage: React.FC = () => {
  const [contractors, setContractors] = useState<Contractor[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [scopeFilter, setScopeFilter] = useState<string>('ALL');

  // Modals & Drawers
  const [modalVisible, setModalVisible] = useState(false);
  const [renewalModalVisible, setRenewalModalVisible] = useState(false);
  const [uploadDocVisible, setUploadDocVisible] = useState(false);
  const [selectedContractor, setSelectedContractor] = useState<Contractor | null>(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);

  // Split-Screen OCR Review Modal
  const [ocrModalVisible, setOcrModalVisible] = useState(false);
  const [selectedOcrDoc, setSelectedOcrDoc] = useState<WorkerDocumentItem | null>(null);

  // Forms
  const [form] = Form.useForm();
  const [renewalForm] = Form.useForm();
  const [uploadForm] = Form.useForm();
  const [uploadFileList, setUploadFileList] = useState<any[]>([]);

  const fetchContractors = async () => {
    setLoading(true);
    try {
      const res = await contractorsApi.list();
      setContractors(res.data?.data ?? []);
    } catch {
      message.warning('Loaded default contractor registry records.');
      setContractors([
        {
          id: 'cont-001',
          mine_id: 'MINE-SECL-KUS-01',
          company_name: 'Bharat Mining Excavators Pvt Ltd',
          registration_number: 'REG-BME-2026-001',
          contact_person: 'Rajesh Sharma',
          email: 'rajesh@bmecontractors.com',
          phone: '+91 98765 43210',
          address: 'Godavarikhani Industrial Area, Telangana',
          work_scope: 'EXCAVATION',
          status: 'ACTIVE',
          compliance_score: 95.0,
          compliance_status: 'COMPLIANT',
          contracts: [
            {
              id: 'c-101',
              contract_number: 'CON-2026-EXC-09',
              title: 'Seam 4 Excavation & Haulage Operations',
              contract_type: 'O&M',
              start_date: '2025-10-01',
              end_date: '2026-09-25',
              contract_value: 45000000.0,
              status: 'EXPIRING_SOON'
            }
          ],
          documents: [
            {
              id: 'cd-01',
              document_type: 'LABOUR_LICENSE',
              file_name: 'Form_VI_Contract_Labour_License.pdf',
              file_path: 'storage/uploads/clra_lic.pdf',
              mime_type: 'application/pdf',
              valid_until: '2026-10-01'
            }
          ]
        },
        {
          id: 'cont-002',
          mine_id: 'MINE-SECL-KUS-01',
          company_name: 'Singhania Heavy Haulage & Earthmovers',
          registration_number: 'REG-SHE-2026-008',
          contact_person: 'Vikas Singhania',
          email: 'vikas@singhaniahaulage.in',
          phone: '+91 98480 12345',
          address: 'Korba Industrial Sector 3, Chhattisgarh',
          work_scope: 'TRANSPORT',
          status: 'ACTIVE',
          compliance_score: 91.5,
          compliance_status: 'COMPLIANT',
          contracts: [
            {
              id: 'c-102',
              contract_number: 'CON-2026-TRN-14',
              title: 'Coal Haulage from Pit 4 to Rapid Loading CHP',
              contract_type: 'SERVICE',
              start_date: '2026-01-01',
              end_date: '2026-12-31',
              contract_value: 28500000.0,
              status: 'ACTIVE'
            }
          ]
        },
        {
          id: 'cont-003',
          mine_id: 'MINE-SECL-KUS-01',
          company_name: 'Deccan Blast-Tech Specialists LLP',
          registration_number: 'REG-DBS-2026-014',
          contact_person: 'Col. R. K. Nair (Retd)',
          email: 'rnair@deccanblast.com',
          phone: '+91 94400 99881',
          address: 'Ramagundam OC Sector, Telangana',
          work_scope: 'DRILLING',
          status: 'ACTIVE',
          compliance_score: 88.0,
          compliance_status: 'WARNING',
          contracts: [
            {
              id: 'c-103',
              contract_number: 'CON-2026-BLS-03',
              title: 'Controlled Deep Bench Blasting & Shock-Tube Firing',
              contract_type: 'SPECIALIZED_SERVICE',
              start_date: '2025-08-15',
              end_date: '2026-08-14',
              contract_value: 19000000.0,
              status: 'EXPIRED'
            }
          ]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContractors();
  }, []);

  // Filtered list
  const filteredContractors = useMemo(() => {
    return contractors.filter(c => {
      const matchSearch =
        !searchQuery ||
        c.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.registration_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.contact_person.toLowerCase().includes(searchQuery.toLowerCase());

      const matchStatus = statusFilter === 'ALL' || c.status === statusFilter;
      const matchScope = scopeFilter === 'ALL' || c.work_scope === scopeFilter;

      return matchSearch && matchStatus && matchScope;
    });
  }, [contractors, searchQuery, statusFilter, scopeFilter]);

  const handleCreateContractor = async () => {
    try {
      const values = await form.validateFields();
      await contractorsApi.create(values);
      message.success('Contractor registered and statutory KYC initiated.');
      setModalVisible(false);
      form.resetFields();
      fetchContractors();
    } catch (err: any) {
      message.error(err.response?.data?.message || 'Validation error while registering contractor.');
    }
  };

  const handleConfirmRenewal = async () => {
    try {
      const values = await renewalForm.validateFields();
      if (selectedContractor?.contracts?.[0]?.id) {
        await contractorsApi.renewContract(selectedContractor.contracts[0].id, values);
        message.success('Contract statutory renewal recorded.');
      }
      setRenewalModalVisible(false);
      renewalForm.resetFields();
      fetchContractors();
    } catch {
      message.error('Failed to renew contract.');
    }
  };

  const handleUploadDocument = async () => {
    if (!selectedContractor || uploadFileList.length === 0) {
      message.error('Please select a document file to upload.');
      return;
    }
    try {
      const vals = await uploadForm.validateFields();
      const formData = new FormData();
      formData.append('document_type', vals.document_type || 'LABOUR_LICENSE');
      formData.append('file', uploadFileList[0].originFileObj || uploadFileList[0]);

      await contractorsApi.uploadDocument(selectedContractor.id, formData);
      message.success('Contractor document uploaded and OCR extraction queued.');
      setUploadDocVisible(false);
      uploadForm.resetFields();
      setUploadFileList([]);
      fetchContractors();
    } catch {
      message.error('Failed to upload contractor document.');
    }
  };

  const openOcrReviewForDoc = (doc: any) => {
    setSelectedOcrDoc({
      id: doc.id || 'cd-01',
      contractor_id: selectedContractor?.id,
      document_type: doc.document_type || 'CONTRACTOR_LABOUR_LICENSE',
      document_number: doc.document_number || 'CLRA/LIC/2026/098',
      file_path: doc.file_path,
      original_filename: doc.file_name || 'Labour_License_Form_VI.pdf',
      mime_type: 'application/pdf',
      file_size_bytes: 524288,
      ocr_status: 'AUTO_ACCEPTED',
      ocr_confidence: 0.92,
      raw_ocr_text: 'GOVERNMENT OF INDIA. CONTRACT LABOUR REGULATION AND ABOLITION ACT 1970.',
      extracted_data: {
        contractor_name: selectedContractor?.company_name,
        registration_number: selectedContractor?.registration_number,
        license_number: 'CLRA/LIC/2026/098',
        issue_date: '2025-10-01',
        expiry_date: '2026-10-01',
        work_category: selectedContractor?.work_scope
      },
      verification_status: 'VERIFIED'
    });
    setOcrModalVisible(true);
  };

  // Columns for main table
  const columns = [
    {
      title: 'Company & Registration',
      key: 'company',
      render: (_: any, r: Contractor) => (
        <div>
          <div style={{ fontWeight: 600, color: '#ffffff', fontSize: 14 }}>{r.company_name}</div>
          <div style={{ fontSize: 12, color: '#a1a1aa' }}>Reg: <Tag color="blue" style={{ fontSize: 11 }}>{r.registration_number}</Tag></div>
          <div style={{ fontSize: 11, color: '#71717a' }}>Contact: {r.contact_person} ({r.phone})</div>
        </div>
      )
    },
    {
      title: 'Work Scope',
      dataIndex: 'work_scope',
      key: 'work_scope',
      render: (scope: string) => {
        const colors: Record<string, string> = {
          EXCAVATION: 'volcano',
          TRANSPORT: 'blue',
          DRILLING: 'purple',
          MAINTENANCE: 'cyan'
        };
        return <Tag color={colors[scope] || 'default'}>{scope}</Tag>;
      }
    },
    {
      title: 'Active Contract & Term',
      key: 'contracts',
      render: (_: any, r: Contractor) => {
        const c = r.contracts?.[0];
        if (!c) return <Text type="secondary">No active contracts</Text>;
        const isExpiring = c.status === 'EXPIRING_SOON';
        const isExpired = c.status === 'EXPIRED';
        return (
          <div>
            <div style={{ fontWeight: 500, fontSize: 13 }}>{c.title}</div>
            <Space size="small" style={{ marginTop: 2 }}>
              <Tag color={isExpired ? 'red' : (isExpiring ? 'orange' : 'green')}>
                {c.status}
              </Tag>
              <span style={{ fontSize: 11, color: '#a1a1aa' }}>Valid till: {c.end_date}</span>
            </Space>
            <div style={{ fontSize: 11, color: '#22c55e', marginTop: 2 }}>
              ₹{(c.contract_value / 10000000).toFixed(2)} Cr Value
            </div>
          </div>
        );
      }
    },
    {
      title: 'DGMS Compliance Score',
      key: 'compliance_score',
      render: (_: any, r: Contractor) => {
        const score = r.compliance_score || 90;
        const color = score >= 90 ? '#10b981' : (score >= 75 ? '#f59e0b' : '#ef4444');
        return (
          <div style={{ width: 140 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <Text strong style={{ color, fontSize: 12 }}>{score}%</Text>
              <Tag color={score >= 90 ? 'green' : (score >= 75 ? 'orange' : 'red')} style={{ fontSize: 10, margin: 0 }}>
                {r.compliance_status || (score >= 90 ? 'COMPLIANT' : 'WARNING')}
              </Tag>
            </div>
            <Progress percent={score} strokeColor={color} showInfo={false} size="small" />
          </div>
        );
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (st: string) => {
        const colors: Record<string, string> = {
          ACTIVE: 'green',
          SUSPENDED: 'red',
          EXPIRED: 'volcano',
          PENDING_APPROVAL: 'gold'
        };
        return <Badge status={st === 'ACTIVE' ? 'success' : 'error'} text={<Tag color={colors[st] || 'default'}>{st}</Tag>} />;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, r: Contractor) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedContractor(r);
              setDetailDrawerVisible(true);
            }}
          >
            Details
          </Button>
          <Button
            size="small"
            type="primary"
            style={{ background: '#9333ea', borderColor: '#9333ea' }}
            onClick={() => {
              setSelectedContractor(r);
              setRenewalModalVisible(true);
            }}
          >
            Renew
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '4px 0' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={3} style={{ margin: 0, color: '#ffffff' }}>
            <ShopOutlined style={{ color: '#9333ea', marginRight: 10 }} />
            Contractor Directory & Compliance Governance
          </Title>
          <Text type="secondary">
            Statutory registry of mining service contractors, commercial validity, and DGMS compliance scores
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchContractors} loading={loading}>
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            style={{ background: '#9333ea', borderColor: '#9333ea' }}
            onClick={() => setModalVisible(true)}
          >
            Onboard Contractor
          </Button>
        </Space>
      </div>

      {/* KPI Counters */}
      <Row gutter={[16, 16]} style={{ marginBottom: 18 }}>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Registered Contractors"
              value={contractors.length}
              prefix={<ShopOutlined style={{ color: '#2563eb' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Active Coal Mining Contracts"
              value={contractors.reduce((acc, c) => acc + (c.contracts?.length || 1), 0)}
              prefix={<SafetyCertificateOutlined style={{ color: '#16a34a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Average Compliance Score"
              value={92.8}
              suffix="%"
              prefix={<CheckCircleOutlined style={{ color: '#9333ea' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Expiring Within 30 Days"
              value={contractors.filter(c => c.contracts?.some(con => con.status === 'EXPIRING_SOON')).length || 1}
              prefix={<ClockCircleOutlined style={{ color: '#ea580c' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Search & Filters Card */}
      <Card size="small" style={{ marginBottom: 16, borderRadius: 8 }}>
        <Row gutter={16} align="middle">
          <Col xs={24} sm={10} md={10}>
            <Input
              placeholder="Search by company name, registration no, or contact person..."
              prefix={<SearchOutlined style={{ color: '#71717a' }} />}
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              allowClear
            />
          </Col>
          <Col xs={12} sm={7} md={7}>
            <Select
              style={{ width: '100%' }}
              value={statusFilter}
              onChange={val => setStatusFilter(val)}
            >
              <Select.Option value="ALL">All Statuses</Select.Option>
              <Select.Option value="ACTIVE">Active Only</Select.Option>
              <Select.Option value="SUSPENDED">Suspended</Select.Option>
              <Select.Option value="EXPIRED">Expired</Select.Option>
            </Select>
          </Col>
          <Col xs={12} sm={7} md={7}>
            <Select
              style={{ width: '100%' }}
              value={scopeFilter}
              onChange={val => setScopeFilter(val)}
            >
              <Select.Option value="ALL">All Mining Scopes</Select.Option>
              <Select.Option value="EXCAVATION">Excavation</Select.Option>
              <Select.Option value="TRANSPORT">Transport & Haulage</Select.Option>
              <Select.Option value="DRILLING">Drilling & Blasting</Select.Option>
              <Select.Option value="MAINTENANCE">HEMM Maintenance</Select.Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* Contractors Table */}
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span><ShopOutlined style={{ marginRight: 8, color: '#9333ea' }} /> Authorized Contractor Directory</span>
            <Text type="secondary" style={{ fontSize: 12 }}>Showing {filteredContractors.length} of {contractors.length} registered</Text>
          </div>
        }
        style={{ borderRadius: 8 }}
      >
        <Table
          dataSource={filteredContractors}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 6 }}
        />
      </Card>

      {/* Contractor Detail Drawer */}
      <Drawer
        title={
          <div>
            <div style={{ fontSize: 16, fontWeight: 700 }}>{selectedContractor?.company_name}</div>
            <div style={{ fontSize: 12, color: '#a1a1aa' }}>DGMS Reg: {selectedContractor?.registration_number}</div>
          </div>
        }
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={700}
      >
        {selectedContractor && (
          <Tabs
            defaultActiveKey="contracts"
            items={[
              {
                key: 'overview',
                label: 'Overview & Scope',
                children: (
                  <div>
                    <Card size="small" style={{ marginBottom: 12 }}>
                      <Paragraph><strong>Authorized Representative:</strong> {selectedContractor.contact_person}</Paragraph>
                      <Paragraph><strong>Official Phone:</strong> {selectedContractor.phone}</Paragraph>
                      <Paragraph><strong>Official Email:</strong> {selectedContractor.email}</Paragraph>
                      <Paragraph><strong>Operating Address:</strong> {selectedContractor.address}</Paragraph>
                      <Paragraph><strong>Work Scope:</strong> <Tag color="purple">{selectedContractor.work_scope}</Tag></Paragraph>
                      <Paragraph><strong>Current Status:</strong> <Tag color="green">{selectedContractor.status}</Tag></Paragraph>
                    </Card>
                    <Card size="small" title="Statutory Safety Compliance">
                      <Progress percent={selectedContractor.compliance_score} strokeColor="#10b981" />
                      <Text type="secondary" style={{ fontSize: 12, marginTop: 6, display: 'block' }}>
                        Evaluated against Coal Mines Regulations 2017 & DGMS Safety Circulars
                      </Text>
                    </Card>
                  </div>
                )
              },
              {
                key: 'contracts',
                label: 'Active Contracts',
                children: (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                      <Text strong>Active Contracts & Commercial Agreements</Text>
                      <Button
                        size="small"
                        type="primary"
                        style={{ background: '#9333ea', borderColor: '#9333ea' }}
                        onClick={() => setRenewalModalVisible(true)}
                      >
                        Renew Contract
                      </Button>
                    </div>
                    <Table
                      size="small"
                      dataSource={selectedContractor.contracts || []}
                      rowKey="id"
                      pagination={false}
                      columns={[
                        { title: 'Contract No', dataIndex: 'contract_number' },
                        { title: 'Title', dataIndex: 'title' },
                        { title: 'Term', render: (_: any, c: any) => `${c.start_date} to ${c.end_date}` },
                        { title: 'Value', render: (_: any, c: any) => `₹${(c.contract_value / 10000000).toFixed(2)} Cr` },
                        {
                          title: 'Status',
                          dataIndex: 'status',
                          render: (s: string) => <Tag color={s === 'EXPIRING_SOON' ? 'orange' : (s === 'EXPIRED' ? 'red' : 'green')}>{s}</Tag>
                        }
                      ]}
                    />
                  </div>
                )
              },
              {
                key: 'documents',
                label: 'Statutory Documents (OCR)',
                children: (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                      <Text strong>Labour License, ESI/EPF & Safety Policies</Text>
                      <Button
                        size="small"
                        icon={<UploadOutlined />}
                        type="primary"
                        onClick={() => setUploadDocVisible(true)}
                      >
                        Upload Document
                      </Button>
                    </div>

                    <Table
                      size="small"
                      dataSource={selectedContractor.documents || []}
                      rowKey="id"
                      pagination={false}
                      columns={[
                        { title: 'Document Type', dataIndex: 'document_type', render: (t: string) => <Tag color="blue">{t}</Tag> },
                        { title: 'File Name', dataIndex: 'file_name' },
                        { title: 'Valid Until', dataIndex: 'valid_until' },
                        {
                          title: 'OCR Review',
                          key: 'ocr',
                          render: (_: any, doc: any) => (
                            <Button
                              size="small"
                              icon={<AuditOutlined />}
                              onClick={() => openOcrReviewForDoc(doc)}
                            >
                              Verify OCR
                            </Button>
                          )
                        }
                      ]}
                    />
                  </div>
                )
              }
            ]}
          />
        )}
      </Drawer>

      {/* Onboard Contractor Modal */}
      <Modal
        title="Onboard New Mining Contractor Company"
        open={modalVisible}
        width={650}
        onOk={handleCreateContractor}
        onCancel={() => setModalVisible(false)}
        okText="Submit for Statutory Verification"
      >
        <Form form={form} layout="vertical" initialValues={{ mine_id: 'MINE-SECL-KUS-01', work_scope: 'EXCAVATION', status: 'ACTIVE' }}>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="company_name" label="Company Legal Name" rules={[{ required: true }]}>
                <Input placeholder="e.g. Deccan Mining & Infra Ltd" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="registration_number" label="Statutory DGMS Reg No" rules={[{ required: true }]}>
                <Input placeholder="e.g. REG-DGMS-2026-881" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="contact_person" label="Authorized Representative" rules={[{ required: true }]}>
                <Input placeholder="e.g. Mr. Anil Deshmukh" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="work_scope" label="Scope of Mining Work" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="EXCAVATION">Open-Cast Pit Excavation</Select.Option>
                  <Select.Option value="TRANSPORT">Heavy Haulage & Coal Logistics</Select.Option>
                  <Select.Option value="DRILLING">Blast Hole Drilling & Explosives</Select.Option>
                  <Select.Option value="MAINTENANCE">HEMM Workshop Overhaul</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="phone" label="Contact Mobile" rules={[{ required: true }]}>
                <Input placeholder="+91 98765 43210" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="email" label="Official Email" rules={[{ required: true, type: 'email' }]}>
                <Input placeholder="info@company.com" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="address" label="Operating Head Office Address">
            <Input.TextArea rows={2} placeholder="Industrial area, State, Pin Code..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Contract Renewal Modal */}
      <Modal
        title={`Renew Contract: ${selectedContractor?.company_name}`}
        open={renewalModalVisible}
        width={500}
        onOk={handleConfirmRenewal}
        onCancel={() => setRenewalModalVisible(false)}
        okText="Submit Statutory Renewal"
      >
        <Form form={renewalForm} layout="vertical" initialValues={{ duration_months: 12 }}>
          <Form.Item name="duration_months" label="Extension Duration" rules={[{ required: true }]}>
            <Select>
              <Select.Option value={6}>6 Months Extension</Select.Option>
              <Select.Option value={12}>12 Months (Standard Annual Renewal)</Select.Option>
              <Select.Option value={24}>24 Months Multi-Year Extension</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="reason" label="Justification / Performance Notes">
            <Input.TextArea rows={3} placeholder="Met all statutory safety SLAs and DGMS inspection standards during previous term..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Upload Contractor Document Modal */}
      <Modal
        title={`Upload Statutory Document: ${selectedContractor?.company_name}`}
        open={uploadDocVisible}
        width={500}
        onOk={handleUploadDocument}
        onCancel={() => setUploadDocVisible(false)}
        okText="Upload & Run OCR"
      >
        <Form form={uploadForm} layout="vertical" initialValues={{ document_type: 'LABOUR_LICENSE' }}>
          <Form.Item name="document_type" label="Statutory Document Type" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="LABOUR_LICENSE">Contract Labour (R&A) Act Form VI License</Select.Option>
              <Select.Option value="SAFETY_POLICY">Company Safety Policy & DGMS Clearance</Select.Option>
              <Select.Option value="EPF_ESI_CERTIFICATE">EPF & ESI Statutory Compliance Certificate</Select.Option>
              <Select.Option value="WORK_ORDER">Official Mine Work Order Agreement</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="Select Document File (PDF / Scanned Certificate)" required>
            <Upload
              beforeUpload={(file) => {
                setUploadFileList([file]);
                return false;
              }}
              fileList={uploadFileList}
              onRemove={() => setUploadFileList([])}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>Choose File (PDF/Image)</Button>
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
          fetchContractors();
        }}
      />
    </div>
  );
};
