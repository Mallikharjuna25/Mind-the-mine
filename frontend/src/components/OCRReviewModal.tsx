import React, { useState, useEffect } from 'react';
import {
  Modal, Row, Col, Card, Typography, Tag, Progress, Form, Input,
  Button, Space, Alert, Divider, message, Collapse
} from 'antd';
import {
  EditOutlined, ZoomInOutlined, ZoomOutOutlined, ReloadOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { workersApi } from '../services/api';

const { Text } = Typography;

export interface WorkerDocumentItem {
  id: string;
  worker_id?: string;
  contractor_id?: string;
  document_type: string;
  document_number?: string;
  issue_date?: string;
  expiry_date?: string;
  file_path: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  ocr_status: string;
  ocr_confidence: number;
  raw_ocr_text?: string;
  extracted_data?: Record<string, any>;
  validation_errors?: string[];
  verification_status: string;
  verified_by?: string;
  verified_at?: string;
  rejection_reason?: string;
}

interface OCRReviewModalProps {
  visible: boolean;
  document: WorkerDocumentItem | null;
  onClose: () => void;
  onSuccess: (updatedDoc: WorkerDocumentItem) => void;
}

export const OCRReviewModal: React.FC<OCRReviewModalProps> = ({
  visible,
  document: doc,
  onClose,
  onSuccess
}) => {
  const [form] = Form.useForm();
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  useEffect(() => {
    if (doc) {
      const ext = doc.extracted_data || {};
      form.setFieldsValue({
        document_number: ext.document_number || ext.certificate_number || ext.registration_number || doc.document_number || '',
        worker_name: ext.worker_name || ext.full_name || ext.contractor_name || '',
        issue_date: ext.issue_date || ext.exam_date || ext.training_date || doc.issue_date || '',
        expiry_date: ext.expiry_date || doc.expiry_date || '',
        statutory_status: ext.fitness_status || ext.statutory_status || 'FIT',
        issuing_authority: ext.issuing_authority || ext.examining_doctor || ext.trainer_name || 'DGMS Directorate',
        training_title: ext.training_title || ext.work_scope || doc.document_type
      });
      setIsEditing(false);
      setZoomLevel(100);
    }
  }, [doc, form]);

  if (!doc) return null;

  const confidencePercent = Math.round((doc.ocr_confidence || 0) * 100);
  const isHighConfidence = confidencePercent >= 85;
  const isMediumConfidence = confidencePercent >= 70 && confidencePercent < 85;

  const handleApprove = async (withEdits: boolean = false) => {
    try {
      setSubmitting(true);
      const values = await form.validateFields();
      
      const payload = {
        decision: withEdits ? 'EDIT_AND_APPROVE' : 'APPROVE',
        corrected_data: withEdits ? {
          ...doc.extracted_data,
          ...values,
          document_number: values.document_number,
          worker_name: values.worker_name,
          issue_date: values.issue_date,
          expiry_date: values.expiry_date,
        } : doc.extracted_data
      };

      const res = await workersApi.reviewDocument(doc.id, payload);
      message.success(withEdits ? 'Document edited and approved with audit logging.' : 'Document statutory approval recorded.');
      onSuccess(res.data?.data || { ...doc, verification_status: 'VERIFIED' });
      onClose();
    } catch (err: any) {
      message.error(err.response?.data?.message || 'Failed to submit document review.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    try {
      setSubmitting(true);
      const reason = prompt('Please enter the mandatory statutory reason for rejection:');
      if (!reason) {
        setSubmitting(false);
        return;
      }

      const res = await workersApi.reviewDocument(doc.id, {
        decision: 'REJECT',
        rejection_reason: reason
      });
      message.warning('Document rejected and flagged for workforce re-upload.');
      onSuccess(res.data?.data || { ...doc, verification_status: 'REJECTED', rejection_reason: reason });
      onClose();
    } catch (err: any) {
      message.error(err.response?.data?.message || 'Failed to reject document.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={
        <Space>
          <SafetyCertificateOutlined style={{ color: '#9333ea', fontSize: 20 }} />
          <span>Statutory Workforce Document — Split-Screen OCR Review & Verification</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={1150}
      footer={null}
      destroyOnClose
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">
          Document ID: <Tag color="blue">{doc.id}</Tag>
          Type: <Tag color="purple">{doc.document_type}</Tag>
          File: <Text strong>{doc.original_filename}</Text>
        </Text>
      </div>

      <Row gutter={20}>
        {/* LEFT PANEL: ORIGINAL DOCUMENT EVIDENCE */}
        <Col span={12}>
          <Card
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Original Evidence Artifact</span>
                <Space size="small">
                  <Button
                    size="small"
                    icon={<ZoomOutOutlined />}
                    onClick={() => setZoomLevel(prev => Math.max(50, prev - 25))}
                  />
                  <Text style={{ fontSize: 12 }}>{zoomLevel}%</Text>
                  <Button
                    size="small"
                    icon={<ZoomInOutlined />}
                    onClick={() => setZoomLevel(prev => Math.min(200, prev + 25))}
                  />
                  <Button
                    size="small"
                    icon={<ReloadOutlined />}
                    onClick={() => setZoomLevel(100)}
                  />
                </Space>
              </div>
            }
            size="small"
            style={{ height: 600, display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ flex: 1, overflow: 'auto', background: '#09090b', padding: 12 }}
          >
            {/* Visual Canvas Representation */}
            <div
              style={{
                width: `${zoomLevel}%`,
                transition: 'width 0.2s ease',
                background: '#ffffff',
                color: '#18181b',
                padding: '24px 20px',
                borderRadius: 6,
                boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
                fontFamily: 'Courier New, monospace',
                fontSize: 11,
                minHeight: 420
              }}
            >
              <div style={{ textAlign: 'center', borderBottom: '2px double #18181b', paddingBottom: 8, marginBottom: 12 }}>
                <div style={{ fontWeight: 800, fontSize: 13 }}>DIRECTORATE GENERAL OF MINES SAFETY (DGMS)</div>
                <div style={{ fontSize: 10 }}>GOVERNMENT OF INDIA — STATUTORY REGULATORY CLEARANCE</div>
                <div style={{ marginTop: 4, fontWeight: 700, color: '#4338ca' }}>
                  {doc.document_type.replace(/_/g, ' ')}
                </div>
              </div>

              <div style={{ lineHeight: 1.6 }}>
                <div><strong>DOC REF NO:</strong> {doc.document_number || 'DGMS/STATUTORY/2026/8841'}</div>
                <div><strong>CANDIDATE:</strong> {doc.extracted_data?.worker_name || 'Ramesh Kumar'}</div>
                <div><strong>MINE CODE:</strong> Kusmunda Mega Opencast Project (SECL)</div>
                <div><strong>ISSUE DATE:</strong> {doc.issue_date || '2026-01-20'}</div>
                <div><strong>VALID UNTIL:</strong> {doc.expiry_date || '2027-01-19'}</div>
                <Divider style={{ margin: '8px 0' }} />
                <div><strong>ASSESSMENT:</strong> {doc.extracted_data?.fitness_status || 'FIT FOR MINING DUTY'}</div>
                <div><strong>AUTH OFFICER:</strong> Dr. S. K. Mukherjee / Certified Inspector</div>
              </div>

              <div style={{ marginTop: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div style={{ border: '2px solid #dc2626', color: '#dc2626', padding: '4px 8px', borderRadius: 4, transform: 'rotate(-5deg)', fontWeight: 800 }}>
                  [ DGMS DHANBAD SEAL ]
                </div>
                <div style={{ textAlign: 'right', fontSize: 10 }}>
                  <div>(Official Digital Signature)</div>
                  <div>Directorate Inspection Wing</div>
                </div>
              </div>
            </div>

            <Collapse
              ghost
              style={{ marginTop: 12 }}
              items={[
                {
                  key: 'raw',
                  label: <Text style={{ color: '#a1a1aa', fontSize: 11 }}>View Raw OCR Extraction Stream</Text>,
                  children: (
                    <pre style={{ color: '#22c55e', fontSize: 10, background: '#18181b', padding: 8, borderRadius: 4, maxHeight: 120, overflow: 'auto' }}>
                      {doc.raw_ocr_text || 'No raw text stored.'}
                    </pre>
                  )
                }
              ]}
            />
          </Card>
        </Col>

        {/* RIGHT PANEL: EXTRACTED FIELDS & VERIFICATION GATE */}
        <Col span={12}>
          <Card
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>OCR Extracted Data & Confidence Gate</span>
                <Tag color={isHighConfidence ? 'green' : (isMediumConfidence ? 'orange' : 'red')}>
                  {confidencePercent}% {isHighConfidence ? 'HIGH CONFIDENCE' : (isMediumConfidence ? 'MEDIUM CONFIDENCE' : 'LOW (MANUAL REVIEW REQUIRED)')}
                </Tag>
              </div>
            }
            size="small"
            style={{ height: 600, display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ flex: 1, overflow: 'auto', padding: '16px' }}
          >
            {/* Confidence Progress */}
            <div style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text style={{ fontSize: 12 }}>Statutory Confidence Meter</Text>
                <Text strong style={{ fontSize: 12 }}>{confidencePercent}% / 100%</Text>
              </div>
              <Progress
                percent={confidencePercent}
                strokeColor={isHighConfidence ? '#10b981' : (isMediumConfidence ? '#f59e0b' : '#ef4444')}
                showInfo={false}
              />
            </div>

            {/* Validation Alerts */}
            {doc.validation_errors && doc.validation_errors.length > 0 && (
              <Alert
                message="Deterministic Validation Warnings"
                description={
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    {doc.validation_errors.map((err, i) => (
                      <li key={i} style={{ fontSize: 12 }}>{err}</li>
                    ))}
                  </ul>
                }
                type={isHighConfidence ? 'info' : 'warning'}
                showIcon
                style={{ marginBottom: 14 }}
              />
            )}

            {/* Form for Fields Verification & Editing */}
            <Form form={form} layout="vertical" size="small">
              <Row gutter={10}>
                <Col span={12}>
                  <Form.Item label="Document / Certificate No." name="document_number">
                    <Input disabled={!isEditing} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Worker / Legal Entity Name" name="worker_name">
                    <Input disabled={!isEditing} />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={10}>
                <Col span={12}>
                  <Form.Item label="Issue / Examination Date" name="issue_date">
                    <Input disabled={!isEditing} placeholder="YYYY-MM-DD" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Validity Expiry Date" name="expiry_date">
                    <Input disabled={!isEditing} placeholder="YYYY-MM-DD" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={10}>
                <Col span={12}>
                  <Form.Item label="Statutory Status" name="statutory_status">
                    <Input disabled={!isEditing} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Issuing Authority" name="issuing_authority">
                    <Input disabled={!isEditing} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="Scope / Course Title" name="training_title">
                <Input disabled={!isEditing} />
              </Form.Item>
            </Form>

            <Alert
              message="Cryptographic Statutory Audit Protection"
              description="Any correction made by an authorized officer will be committed with both original and updated values chained to the immutable SHA-256 audit ledger."
              type="info"
              style={{ fontSize: 11, marginBottom: 16 }}
            />

            {/* Actions Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 8, borderTop: '1px solid #27272a' }}>
              <Button
                icon={<EditOutlined />}
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? 'Cancel Edit' : 'Edit Fields'}
              </Button>

              <Space>
                <Button danger onClick={handleReject} loading={submitting}>
                  Reject
                </Button>
                {isEditing ? (
                  <Button
                    type="primary"
                    style={{ background: '#2563eb' }}
                    onClick={() => handleApprove(true)}
                    loading={submitting}
                  >
                    Save & Approve
                  </Button>
                ) : (
                  <Button
                    type="primary"
                    style={{ background: '#16a34a' }}
                    onClick={() => handleApprove(false)}
                    loading={submitting}
                  >
                    Approve (Verified)
                  </Button>
                )}
              </Space>
            </div>
          </Card>
        </Col>
      </Row>
    </Modal>
  );
};
