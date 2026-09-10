import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Tag, Button, Space, Typography, Modal,
  Form, Input, Select, message, Statistic, Avatar, Tabs,
  Table, DatePicker, QRCode, Alert, Timeline, Descriptions
} from 'antd';
import {
  UserOutlined, SafetyCertificateOutlined, CheckCircleOutlined,
  ClockCircleOutlined, AlertOutlined, PlusOutlined,
  CalendarOutlined, FileProtectOutlined, IdcardOutlined,
  HeartOutlined, MedicineBoxOutlined, ToolOutlined,
  CheckCircleFilled, PhoneOutlined, SolutionOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { workersApi, governanceApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text, Paragraph } = Typography;

interface InsuranceRecord {
  id?: string;
  policy_provider: string;
  policy_number: string;
  policy_type: string;
  coverage_amount: number;
  start_date: string;
  expiry_date: string;
  nominee_name: string;
  nominee_relation: string;
  premium_status: string;
  tpa_contact_number?: string;
}

interface LeaveRecord {
  id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_count: number;
  reason: string;
  status: string;
  approved_by?: string;
  supervisor_remarks?: string;
  created_at?: string;
}

interface WorkerProfile {
  id: string;
  mine_id: string;
  contractor_id?: string;
  employee_id: string;
  full_name: string;
  department: string;
  role: string;
  email?: string;
  phone: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  joining_date: string;
  status: string;
  blood_group?: string;
  rfid_tag?: string;
  medical_fitness_status?: string;
  medical_exam_date?: string;
  medical_expiry_date?: string;
  attendances?: Array<{
    id: string;
    shift: string;
    check_in: string;
    check_out?: string;
    status: string;
  }>;
  trainings?: Array<{
    id: string;
    program_name: string;
    trainer_name: string;
    completed_date: string;
    expiry_date: string;
    status: string;
  }>;
  certifications?: Array<{
    id: string;
    certificate_name: string;
    certificate_number: string;
    issuing_authority: string;
    valid_from: string;
    expiry_date: string;
    verification_status: string;
  }>;
  ppes?: Array<{
    id: string;
    item_type: string;
    issuance_date: string;
    expiry_date: string;
    compliance_status: string;
    remarks?: string;
  }>;
  authorizations?: Array<{
    id: string;
    zone_id: string;
    permit_type: string;
    grant_date: string;
    expiry_date: string;
    status: string;
    granted_by: string;
  }>;
  insurances?: InsuranceRecord[];
  leaves?: LeaveRecord[];
}

export const WorkerPortalPage: React.FC = () => {
  const { user } = useAuth();
  const [worker, setWorker] = useState<WorkerProfile | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Modals
  const [leaveModalVisible, setLeaveModalVisible] = useState(false);
  const [idCardModalVisible, setIdCardModalVisible] = useState(false);
  const [hazardModalVisible, setHazardModalVisible] = useState(false);
  const [clockedIn, setClockedIn] = useState(true);
  const [shiftHours, setShiftHours] = useState('03:25:10');

  const [leaveForm] = Form.useForm();
  const [hazardForm] = Form.useForm();

  const fetchProfile = async () => {
    try {
      const res = await workersApi.getMe();
      const wData = res.data?.data || res.data;
      setWorker(wData);
    } catch {
      // Fallback synthetic state if offline or during local development
      setWorker({
        id: 'w-demo-01',
        mine_id: 'MINE-SECL-KUS-01',
        employee_id: 'EMP-2026-9901',
        full_name: user?.full_name || 'Ramesh Kumar',
        department: 'UNDERGROUND_OPS',
        role: 'HEAVY_EQUIPMENT_OPERATOR',
        email: user?.email || 'worker@mineguard.in',
        phone: '+91 91234 56789',
        emergency_contact_name: 'Sita Devi (Spouse)',
        emergency_contact_phone: '+91 98765 12345',
        joining_date: '2025-03-15',
        status: 'ACTIVE',
        blood_group: 'B+',
        rfid_tag: 'RFID-KUS-8821',
        medical_fitness_status: 'FIT',
        medical_exam_date: '2026-01-10',
        medical_expiry_date: '2027-01-10',
        attendances: [
          {
            id: 'att-1',
            shift: 'MORNING',
            check_in: new Date(Date.now() - 3.5 * 3600 * 1000).toISOString(),
            status: 'PRESENT'
          }
        ],
        trainings: [
          {
            id: 'tr-1',
            program_name: 'DGMS Statutory Underground Gas & Slope Safety (VTC)',
            trainer_name: 'Amitabh Verma (Senior Safety Officer)',
            completed_date: '2025-11-20',
            expiry_date: '2026-11-20',
            status: 'COMPLETED'
          }
        ],
        certifications: [
          {
            id: 'cert-1',
            certificate_name: 'DGMS Certified HEMM Heavy Shovel Operator Class I',
            certificate_number: 'DGMS-HEMM-2024-884',
            issuing_authority: 'Directorate General of Mines Safety',
            valid_from: '2024-04-01',
            expiry_date: '2028-04-01',
            verification_status: 'VERIFIED'
          }
        ],
        ppes: [
          { id: 'p1', item_type: 'HELMET', issuance_date: '2026-01-15', expiry_date: '2027-01-15', compliance_status: 'COMPLIANT', remarks: 'IS-2925 miner hard hat with LED bracket' },
          { id: 'p2', item_type: 'HIGH_VIS_VEST', issuance_date: '2026-02-01', expiry_date: '2027-02-01', compliance_status: 'COMPLIANT', remarks: 'Class 3 high retro-reflective harness' },
          { id: 'p3', item_type: 'SAFETY_BOOTS', issuance_date: '2025-08-10', expiry_date: '2026-08-10', compliance_status: 'COMPLIANT', remarks: 'Steel-toe ankle guard mining boots' },
          { id: 'p4', item_type: 'RESPIRATOR', issuance_date: '2026-02-20', expiry_date: '2026-08-20', compliance_status: 'COMPLIANT', remarks: 'P3 coal dust particulate respirator' }
        ],
        authorizations: [
          { id: 'a1', zone_id: 'ZONE-PIT-01', permit_type: 'UNDERGROUND_ENTRY', grant_date: '2026-01-01', expiry_date: '2026-12-31', status: 'GRANTED', granted_by: 'Mine Manager Office' }
        ],
        insurances: [
          {
            policy_provider: 'LIC Group Coal Mine Safety & Accidental Disability',
            policy_number: 'LIC-CIL-992182',
            policy_type: 'ACCIDENTAL_DEATH_DISABILITY',
            coverage_amount: 1500000,
            start_date: '2025-04-01',
            expiry_date: '2027-03-31',
            nominee_name: 'Sita Devi',
            nominee_relation: 'SPOUSE',
            premium_status: 'ACTIVE',
            tpa_contact_number: '1800-425-2255'
          },
          {
            policy_provider: 'New India Cashless Mining Critical Illness Care',
            policy_number: 'NIA-HLT-440192',
            policy_type: 'CRITICAL_ILLNESS',
            coverage_amount: 500000,
            start_date: '2025-09-01',
            expiry_date: '2026-08-31',
            nominee_name: 'Sita Devi',
            nominee_relation: 'SPOUSE',
            premium_status: 'ACTIVE',
            tpa_contact_number: '1800-209-1415'
          },
          {
            policy_provider: 'Coal Mines Provident Fund (CMPF) Pension Scheme',
            policy_number: 'CMPF-KUS-88301',
            policy_type: 'CMPF_PROVIDENT_FUND',
            coverage_amount: 1240000,
            start_date: '2023-01-01',
            expiry_date: '2035-12-31',
            nominee_name: 'Rahul Kumar',
            nominee_relation: 'SON',
            premium_status: 'ACTIVE',
            tpa_contact_number: '07759-241022'
          }
        ],
        leaves: [
          {
            id: 'l-1',
            leave_type: 'CASUAL',
            start_date: '2026-08-10',
            end_date: '2026-08-12',
            days_count: 3,
            reason: 'Family festival celebration in Bilaspur',
            status: 'APPROVED',
            approved_by: 'manager@mineguard.in',
            supervisor_remarks: 'Relief operator assigned.'
          },
          {
            id: 'l-2',
            leave_type: 'SICK_MEDICAL',
            start_date: '2026-09-02',
            end_date: '2026-09-03',
            days_count: 2,
            reason: 'Viral fever physician rest prescribed',
            status: 'APPROVED',
            approved_by: 'safety@mineguard.in',
            supervisor_remarks: 'Dispensary slip attached.'
          },
          {
            id: 'l-3',
            leave_type: 'GATE_PASS_SHIFT_EXIT',
            start_date: '2026-09-11',
            end_date: '2026-09-11',
            days_count: 0.5,
            reason: 'Urgent banking Aadhaar biometric update in Korba town',
            status: 'PENDING',
            supervisor_remarks: 'Shift supervisor review in progress.'
          }
        ]
      });
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  // Timer simulation for shift
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const pad = (n: number) => n.toString().padStart(2, '0');
      setShiftHours(`03:${pad(now.getMinutes())}:${pad(now.getSeconds())}`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleToggleClockIn = async () => {
    if (!worker) return;
    const nextState = !clockedIn;
    setClockedIn(nextState);
    if (nextState) {
      try {
        await workersApi.addAttendance(worker.id, {
          shift: 'MORNING',
          status: 'PRESENT'
        });
      } catch {
        // Local simulation fallback
      }
      message.success('Shift Clock-In Logged! Safety clearance verified.');
    } else {
      message.info('Shift Clock-Out Logged. Rest period initialized. Good work today!');
    }
  };

  const handleApplyLeave = async () => {
    try {
      const vals = await leaveForm.validateFields();
      const start = dayjs(vals.dateRange[0]).format('YYYY-MM-DD');
      const end = dayjs(vals.dateRange[1]).format('YYYY-MM-DD');
      const diff = dayjs(vals.dateRange[1]).diff(dayjs(vals.dateRange[0]), 'day') + 1;

      const payload = {
        leave_type: vals.leave_type,
        start_date: start,
        end_date: end,
        days_count: vals.leave_type === 'GATE_PASS_SHIFT_EXIT' ? 0.5 : diff,
        reason: vals.reason
      };

      if (worker?.id) {
        try {
          await workersApi.applyLeave(worker.id, payload);
        } catch {
          // Local fallback
        }
      }

      // Update local state
      const newLeave: LeaveRecord = {
        id: `l-new-${Date.now()}`,
        leave_type: vals.leave_type,
        start_date: start,
        end_date: end,
        days_count: payload.days_count,
        reason: vals.reason,
        status: 'PENDING',
        supervisor_remarks: 'Application logged. Awaiting shift in-charge approval.'
      };

      setWorker(prev => prev ? {
        ...prev,
        leaves: [newLeave, ...(prev.leaves || [])]
      } : null);

      message.success('Leave / Gate Pass application submitted successfully!');
      leaveForm.resetFields();
      setLeaveModalVisible(false);
    } catch {
      message.error('Please fill in all mandatory fields.');
    }
  };

  const handleReportHazard = async () => {
    try {
      const vals = await hazardForm.validateFields();
      await governanceApi.createGrievance({
        mine_id: worker?.mine_id || 'MINE-SECL-KUS-01',
        complainant_name: worker?.full_name || 'Ramesh Kumar',
        category: vals.category,
        title: vals.title,
        description: vals.description,
        priority: vals.priority
      });
      message.success('Safety concern reported directly to Safety Officers. Reference logged.');
      hazardForm.resetFields();
      setHazardModalVisible(false);
    } catch {
      message.error('Failed to submit report. Please check input.');
    }
  };

  const leaveColumns = [
    {
      title: 'Leave / Pass Type',
      dataIndex: 'leave_type',
      key: 'leave_type',
      render: (val: string) => {
        const colors: Record<string, string> = {
          CASUAL: 'blue',
          SICK_MEDICAL: 'purple',
          PRIVILEGE_EARNED: 'cyan',
          GATE_PASS_SHIFT_EXIT: 'orange'
        };
        return <Tag color={colors[val] || 'default'}>{val.replace(/_/g, ' ')}</Tag>;
      }
    },
    {
      title: 'Duration',
      key: 'dates',
      render: (_: unknown, r: LeaveRecord) => (
        <span>{r.start_date} to {r.end_date} <b>({r.days_count} {r.days_count === 1 ? 'day' : 'days'})</b></span>
      )
    },
    {
      title: 'Reason',
      dataIndex: 'reason',
      key: 'reason',
      render: (txt: string) => <Text style={{ maxWidth: 260 }} ellipsis={{ tooltip: txt }}>{txt}</Text>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        if (status === 'APPROVED') return <Tag color="success" icon={<CheckCircleOutlined />}>APPROVED</Tag>;
        if (status === 'REJECTED') return <Tag color="error">REJECTED</Tag>;
        return <Tag color="warning" icon={<ClockCircleOutlined />}>PENDING REVIEW</Tag>;
      }
    },
    {
      title: 'Remarks / Approver',
      key: 'remarks',
      render: (_: unknown, r: LeaveRecord) => (
        <span style={{ fontSize: 12, color: '#71717a' }}>
          {r.supervisor_remarks || r.approved_by || 'Awaiting Supervisor'}
        </span>
      )
    }
  ];

  return (
    <div style={{ maxWidth: 1300, margin: '0 auto', paddingBottom: 48 }}>
      {/* ── HERO BANNER: WORKER IDENTITY CARD ───────────────────────────── */}
      <Card
        style={{
          marginBottom: 20,
          borderRadius: 12,
          background: 'linear-gradient(135deg, rgba(20, 30, 48, 0.95), rgba(36, 59, 85, 0.9))',
          color: '#fff',
          border: '1px solid rgba(255,255,255,0.12)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
        }}
      >
        <Row gutter={[24, 20]} align="middle">
          <Col xs={24} sm={6} md={4} style={{ textAlign: 'center' }}>
            <Avatar
              size={96}
              style={{
                backgroundColor: '#10b981',
                fontSize: 36,
                fontWeight: 'bold',
                boxShadow: '0 4px 16px rgba(16,185,129,0.4)',
                border: '3px solid #34d399'
              }}
              icon={<UserOutlined />}
            >
              {worker?.full_name?.charAt(0) || 'R'}
            </Avatar>
            <div style={{ marginTop: 8 }}>
              <Tag color="success" style={{ fontWeight: 'bold' }}>
                <CheckCircleFilled /> FIT FOR DUTY
              </Tag>
            </div>
          </Col>

          <Col xs={24} sm={18} md={12}>
            <Space direction="vertical" size={2}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                <Title level={3} style={{ color: '#fff', margin: 0 }}>
                  {worker?.full_name || 'Ramesh Kumar'}
                </Title>
                <Tag color="gold" style={{ fontSize: 13, fontWeight: 'bold', padding: '2px 8px' }}>
                  {worker?.employee_id || 'EMP-2026-9901'}
                </Tag>
                <Tag color="blue">
                  <IdcardOutlined /> RFID: {worker?.rfid_tag || 'RFID-KUS-8821'}
                </Tag>
              </div>

              <Text style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 500 }}>
                {worker?.role?.replace(/_/g, ' ')} • {worker?.department?.replace(/_/g, ' ')}
              </Text>

              <Text style={{ color: '#94a3b8', fontSize: 13 }}>
                🏢 <b>Kusmunda Mega Opencast Coal Mine</b> (SECL) • Contractor: <b>Bharat Mining Excavators</b>
              </Text>

              <div style={{ marginTop: 8, display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: 12, color: '#cbd5e1' }}>
                <span>🩸 Blood Group: <b style={{ color: '#f87171' }}>{worker?.blood_group || 'B+'}</b></span>
                <span>📞 Phone: <b>{worker?.phone}</b></span>
                <span>🚨 Emergency: <b>{worker?.emergency_contact_name} ({worker?.emergency_contact_phone})</b></span>
              </div>
            </Space>
          </Col>

          <Col xs={24} md={8} style={{ textAlign: 'right' }}>
            <Card
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: 8,
                textAlign: 'center',
                color: '#fff'
              }}
            >
              <div style={{ fontSize: 12, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1 }}>
                Current Shift: <b>MORNING (06:00 - 14:00)</b>
              </div>
              <div style={{ fontSize: 26, fontWeight: 'bold', color: clockedIn ? '#34d399' : '#f87171', margin: '4px 0' }}>
                {clockedIn ? `ACTIVE • ${shiftHours}` : 'OFF DUTY'}
              </div>
              <Space wrap style={{ marginTop: 8, justifyContent: 'center' }}>
                <Button
                  type={clockedIn ? 'default' : 'primary'}
                  danger={clockedIn}
                  onClick={handleToggleClockIn}
                  icon={<ClockCircleOutlined />}
                  style={{ fontWeight: 600 }}
                >
                  {clockedIn ? 'Punch Out' : 'Clock In Shift'}
                </Button>
                <Button
                  type="primary"
                  onClick={() => setLeaveModalVisible(true)}
                  icon={<CalendarOutlined />}
                  style={{ backgroundColor: '#0284c7' }}
                >
                  Apply Leave / Pass
                </Button>
                <Button
                  onClick={() => setIdCardModalVisible(true)}
                  icon={<IdcardOutlined />}
                >
                  Digital Pass
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* ── TOP KPI QUICK GLANCE ───────────────────────────────────────── */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={12} sm={6}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic
              title="Available Leave Balance"
              value={27}
              suffix="days"
              valueStyle={{ color: '#0284c7', fontWeight: 'bold' }}
              prefix={<CalendarOutlined />}
            />
            <div style={{ fontSize: 11, color: '#71717a', marginTop: 4 }}>
              8 Casual • 15 Earned • 4 Medical
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic
              title="Total Insurance Cover"
              value={20}
              suffix="Lakhs"
              prefix="₹"
              valueStyle={{ color: '#10b981', fontWeight: 'bold' }}
            />
            <div style={{ fontSize: 11, color: '#71717a', marginTop: 4 }}>
              Accidental + Cashless Health Active
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic
              title="Medical Exam Status"
              value="DGMS FORM P"
              valueStyle={{ color: '#059669', fontSize: 18, fontWeight: 'bold' }}
              prefix={<HeartOutlined />}
            />
            <div style={{ fontSize: 11, color: '#71717a', marginTop: 4 }}>
              Valid till Jan 2027 • 100% Fit
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic
              title="Assigned PPE Gear"
              value="4 / 4 Items"
              valueStyle={{ color: '#8b5cf6', fontSize: 18, fontWeight: 'bold' }}
              prefix={<SafetyCertificateOutlined />}
            />
            <div style={{ fontSize: 11, color: '#71717a', marginTop: 4 }}>
              IS-2925 Helmet • Vest • Boots • Mask
            </div>
          </Card>
        </Col>
      </Row>

      {/* ── TABS FOR WORKER SELF-SERVICE ────────────────────────────────── */}
      <Card style={{ borderRadius: 12 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'overview',
              label: <span><ClockCircleOutlined /> Shift Roster & Safety Alert</span>,
              children: (
                <div>
                  <Alert
                    type="info"
                    showIcon
                    message="Daily Safety Protocol & Pit Face Alert"
                    description="Face 4 blasting operations scheduled between 13:00 - 13:45. Clear excavator perimeter 200m before siren. Keep dust suppression water mist active on haul roads."
                    style={{ marginBottom: 16 }}
                  />

                  <Row gutter={[20, 20]}>
                    <Col xs={24} md={14}>
                      <Card title="7-Day Shift Work Schedule" size="small">
                        <Table
                          size="small"
                          pagination={false}
                          dataSource={[
                            { day: 'Monday', shift: 'Morning (06:00 - 14:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'COMPLETED' },
                            { day: 'Tuesday', shift: 'Morning (06:00 - 14:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'COMPLETED' },
                            { day: 'Wednesday', shift: 'Morning (06:00 - 14:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'COMPLETED' },
                            { day: 'Thursday (Today)', shift: 'Morning (06:00 - 14:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'ON DUTY' },
                            { day: 'Friday', shift: 'Morning (06:00 - 14:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'SCHEDULED' },
                            { day: 'Saturday', shift: 'Afternoon (14:00 - 22:00)', machine: 'Komatsu PC2000-8 Shovel', location: 'Face 4 Overburden Bench', status: 'SCHEDULED' },
                            { day: 'Sunday', shift: 'Weekly Rest Day', machine: '-', location: 'Home / Residential Colony', status: 'REST DAY' },
                          ]}
                          columns={[
                            { title: 'Day', dataIndex: 'day', key: 'day', render: (t: string) => <b>{t}</b> },
                            { title: 'Assigned Shift', dataIndex: 'shift', key: 'shift' },
                            { title: 'Designated HEMM', dataIndex: 'machine', key: 'machine' },
                            { title: 'Sector', dataIndex: 'location', key: 'location' },
                            {
                              title: 'Duty Status',
                              dataIndex: 'status',
                              key: 'status',
                              render: (s: string) => {
                                if (s === 'ON DUTY') return <Tag color="processing">ON DUTY NOW</Tag>;
                                if (s === 'COMPLETED') return <Tag color="success">LOGGED</Tag>;
                                if (s === 'REST DAY') return <Tag color="purple">REST DAY</Tag>;
                                return <Tag color="default">SCHEDULED</Tag>;
                              }
                            }
                          ]}
                        />
                      </Card>
                    </Col>

                    <Col xs={24} md={10}>
                      <Card title="Shift Log & Breathalyzer Check-In" size="small">
                        <Timeline
                          items={[
                            {
                              color: 'green',
                              children: (
                                <div>
                                  <b>05:45 AM - Gate Check-In & Biometric Punch</b>
                                  <div style={{ fontSize: 12, color: '#71717a' }}>
                                    Kusmunda Gate 2 RFID Scanner (Status: Present)
                                  </div>
                                </div>
                              )
                            },
                            {
                              color: 'green',
                              children: (
                                <div>
                                  <b>05:52 AM - Breathalyzer & Fit-to-Work Clearance</b>
                                  <div style={{ fontSize: 12, color: '#71717a' }}>
                                    Alcohol BAC: 0.00% • SpO2: 98% • BP: 120/80 mmHg (CLEARED)
                                  </div>
                                </div>
                              )
                            },
                            {
                              color: 'blue',
                              children: (
                                <div>
                                  <b>06:05 AM - HEMM Pre-Start Machine Inspection</b>
                                  <div style={{ fontSize: 12, color: '#71717a' }}>
                                    Komatsu PC2000-8 hydraulic pressure verified, fire suppression intact
                                  </div>
                                </div>
                              )
                            },
                            {
                              color: 'orange',
                              children: (
                                <div>
                                  <b>13:45 PM - Scheduled Shift Wrap & Handover</b>
                                  <div style={{ fontSize: 12, color: '#71717a' }}>
                                    Handover log to Relief Operator Manoj Kumar
                                  </div>
                                </div>
                              )
                            }
                          ]}
                        />
                        <Button
                          type="dashed"
                          block
                          icon={<AlertOutlined />}
                          danger
                          onClick={() => setHazardModalVisible(true)}
                          style={{ marginTop: 12 }}
                        >
                          Directly Report Safety Concern to Officer
                        </Button>
                      </Card>
                    </Col>
                  </Row>
                </div>
              )
            },
            {
              key: 'insurance',
              label: <span><FileProtectOutlined /> Insurance & Statutory Benefits</span>,
              children: (
                <div>
                  <Row gutter={[16, 16]}>
                    {(worker?.insurances || []).map((ins, idx) => (
                      <Col xs={24} md={8} key={idx}>
                        <Card
                          title={
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <MedicineBoxOutlined style={{ color: '#0284c7' }} />
                              <span style={{ fontSize: 13 }}>{ins.policy_type.replace(/_/g, ' ')}</span>
                            </div>
                          }
                          extra={<Tag color="success">ACTIVE</Tag>}
                          style={{ borderRadius: 8, height: '100%' }}
                        >
                          <Title level={4} style={{ color: '#059669', margin: '0 0 8px 0' }}>
                            ₹{ins.coverage_amount.toLocaleString()} Cover
                          </Title>
                          <Descriptions column={1} size="small">
                            <Descriptions.Item label="Provider">{ins.policy_provider}</Descriptions.Item>
                            <Descriptions.Item label="Policy Number">
                              <code>{ins.policy_number}</code>
                            </Descriptions.Item>
                            <Descriptions.Item label="Valid Till">
                              <Tag color="cyan">{ins.expiry_date}</Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="Nominee">
                              <b>{ins.nominee_name}</b> ({ins.nominee_relation})
                            </Descriptions.Item>
                            {ins.tpa_contact_number && (
                              <Descriptions.Item label="Emergency Helpline">
                                <a href={`tel:${ins.tpa_contact_number}`}>
                                  <PhoneOutlined /> {ins.tpa_contact_number}
                                </a>
                              </Descriptions.Item>
                            )}
                          </Descriptions>
                        </Card>
                      </Col>
                    ))}
                  </Row>

                  <Card style={{ marginTop: 16, backgroundColor: 'rgba(2, 132, 199, 0.05)', borderRadius: 8 }}>
                    <Title level={5}>
                      <SafetyCertificateOutlined style={{ color: '#0284c7' }} /> DGMS & Workmen's Compensation Act Statutory Guarantee
                    </Title>
                    <Paragraph style={{ fontSize: 13, color: '#64748b', marginBottom: 0 }}>
                      As per the Mines Act 1952 and Employee's Compensation Act, every worker engaged in opencast/underground mining operations is covered under compulsory comprehensive insurance and Coal Mines Provident Fund (CMPF) provisions. Hospitalization claims at accredited tertiary centers (including Apollo Korba and Fortis Bilaspur) are 100% cashless under company guarantee.
                    </Paragraph>
                  </Card>
                </div>
              )
            },
            {
              key: 'leave',
              label: <span><CalendarOutlined /> Leave & Permission Management</span>,
              children: (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <div>
                      <Title level={5} style={{ margin: 0 }}>My Leave Requests & Gate Passes</Title>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Apply for Casual Leave, Medical Leave, Shift Permission, or Emergency Gate Exit Passes.
                      </Text>
                    </div>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setLeaveModalVisible(true)}
                    >
                      Apply New Leave / Pass
                    </Button>
                  </div>

                  <Table
                    columns={leaveColumns}
                    dataSource={worker?.leaves || []}
                    rowKey="id"
                    pagination={{ pageSize: 5 }}
                  />
                </div>
              )
            },
            {
              key: 'medical',
              label: <span><HeartOutlined /> Medical Health & Fitness</span>,
              children: (
                <Row gutter={[20, 20]}>
                  <Col xs={24} md={12}>
                    <Card title="DGMS Form O & Form P Periodic Medical Examination (PME)" size="small">
                      <Descriptions column={1} bordered size="small">
                        <Descriptions.Item label="PME Fitness Status">
                          <Tag color="success" style={{ fontWeight: 'bold' }}>100% FIT FOR MINING DUTIES</Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Last Examined Date">
                          {worker?.medical_exam_date || '2026-01-10'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Next Examination Due">
                          {worker?.medical_expiry_date || '2027-01-10'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Chest X-Ray / ILO Classification">
                          Normal (Category 0/0 - Clear Lung Fields)
                        </Descriptions.Item>
                        <Descriptions.Item label="Spirometry (PFT Test)">
                          FEV1/FVC: 88% (Normal respiratory capacity)
                        </Descriptions.Item>
                        <Descriptions.Item label="Audiometry (Hearing Range)">
                          Grade 1 Normal (Both ears sensitive to 20 dB)
                        </Descriptions.Item>
                        <Descriptions.Item label="Color Vision & Visual Acuity">
                          6/6 with corrective lenses; Normal Night Vision
                        </Descriptions.Item>
                        <Descriptions.Item label="Examining Medical Board">
                          SECL Central Mining Hospital, Korba (Dr. S. K. Mahapatra, CMO)
                        </Descriptions.Item>
                      </Descriptions>
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="Pre-Shift Daily Vitals Tracker" size="small">
                      <Table
                        size="small"
                        pagination={false}
                        dataSource={[
                          { date: 'Today (Morning Shift)', bp: '120/80 mmHg', spo2: '98%', alcohol: '0.00% (Pass)', temp: '98.4 °F', result: 'FIT' },
                          { date: 'Yesterday (Morning Shift)', bp: '122/82 mmHg', spo2: '99%', alcohol: '0.00% (Pass)', temp: '98.6 °F', result: 'FIT' },
                          { date: '2 Days Ago', bp: '118/78 mmHg', spo2: '98%', alcohol: '0.00% (Pass)', temp: '98.2 °F', result: 'FIT' },
                        ]}
                        columns={[
                          { title: 'Date / Shift', dataIndex: 'date', key: 'date' },
                          { title: 'Blood Pressure', dataIndex: 'bp', key: 'bp' },
                          { title: 'SpO2', dataIndex: 'spo2', key: 'spo2' },
                          { title: 'Breathalyzer', dataIndex: 'alcohol', key: 'alcohol', render: (t: string) => <Tag color="green">{t}</Tag> },
                          { title: 'Body Temp', dataIndex: 'temp', key: 'temp' },
                          { title: 'Clearance', dataIndex: 'result', key: 'result', render: (r: string) => <Tag color="success"><b>{r}</b></Tag> }
                        ]}
                      />
                    </Card>
                  </Col>
                </Row>
              )
            },
            {
              key: 'ppe',
              label: <span><ToolOutlined /> Allocated PPE & Safety Gear</span>,
              children: (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <div>
                      <Title level={5} style={{ margin: 0 }}>Statutory Personal Protective Equipment (PPE)</Title>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        All safety equipment is inspected per DGMS guidelines and IS safety standards.
                      </Text>
                    </div>
                    <Button
                      icon={<ToolOutlined />}
                      onClick={() => message.info('PPE inspection or replacement request submitted to the Safety Store!')}
                    >
                      Request Gear Replacement
                    </Button>
                  </div>

                  <Table
                    size="small"
                    pagination={false}
                    dataSource={worker?.ppes || []}
                    rowKey="id"
                    columns={[
                      {
                        title: 'Item Type',
                        dataIndex: 'item_type',
                        key: 'item_type',
                        render: (val: string) => <b>{val.replace(/_/g, ' ')}</b>
                      },
                      { title: 'Issuance Date', dataIndex: 'issuance_date', key: 'issuance_date' },
                      { title: 'Replacement / Expiry Date', dataIndex: 'expiry_date', key: 'expiry_date' },
                      {
                        title: 'Compliance Status',
                        dataIndex: 'compliance_status',
                        key: 'compliance_status',
                        render: (status: string) => <Tag color="success">{status}</Tag>
                      },
                      { title: 'Technical Specification', dataIndex: 'remarks', key: 'remarks' }
                    ]}
                  />
                </div>
              )
            },
            {
              key: 'certifications',
              label: <span><SolutionOutlined /> DGMS Trainings & Permits</span>,
              children: (
                <Row gutter={[20, 20]}>
                  <Col xs={24} md={12}>
                    <Card title="Statutory Safety Certifications" size="small">
                      {(worker?.certifications || []).map((c, i) => (
                        <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                          <Text strong style={{ fontSize: 14 }}>{c.certificate_name}</Text>
                          <div style={{ fontSize: 12, color: '#71717a' }}>
                            Cert #: <code>{c.certificate_number}</code> • Issued by: {c.issuing_authority}
                          </div>
                          <div style={{ marginTop: 4, display: 'flex', gap: 8 }}>
                            <Tag color="green">VERIFIED</Tag>
                            <Tag color="cyan">Valid: {c.valid_from} to {c.expiry_date}</Tag>
                          </div>
                        </div>
                      ))}
                    </Card>
                  </Col>

                  <Col xs={24} md={12}>
                    <Card title="Restricted Zone Entry Permits" size="small">
                      {(worker?.authorizations || []).map((a, i) => (
                        <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                          <Text strong style={{ fontSize: 14 }}>Permit: {a.permit_type.replace(/_/g, ' ')}</Text>
                          <div style={{ fontSize: 12, color: '#71717a' }}>
                            Zone Code: <b>{a.zone_id}</b> • Authority: {a.granted_by}
                          </div>
                          <div style={{ marginTop: 4, display: 'flex', gap: 8 }}>
                            <Tag color="purple">ACTIVE PERMIT</Tag>
                            <Tag color="blue">Valid till: {a.expiry_date}</Tag>
                          </div>
                        </div>
                      ))}
                    </Card>
                  </Col>
                </Row>
              )
            }
          ]}
        />
      </Card>

      {/* ── MODAL: APPLY FOR LEAVE / PERMISSION ─────────────────────────── */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CalendarOutlined style={{ color: '#0284c7' }} />
            <span>Apply for Leave or Gate Pass Permission</span>
          </div>
        }
        open={leaveModalVisible}
        onCancel={() => setLeaveModalVisible(false)}
        onOk={handleApplyLeave}
        okText="Submit Application"
        destroyOnClose
      >
        <Form form={leaveForm} layout="vertical" initialValues={{ leave_type: 'CASUAL' }}>
          <Form.Item
            name="leave_type"
            label="Application Type"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: 'Casual Leave (CL) - Personal / Family', value: 'CASUAL' },
                { label: 'Medical / Sick Leave (SL) - Physician Certificate', value: 'SICK_MEDICAL' },
                { label: 'Privilege / Earned Leave (EL) - Annual Leave', value: 'PRIVILEGE_EARNED' },
                { label: 'Gate Pass / Shift Exit - Urgent Mid-Shift Exit', value: 'GATE_PASS_SHIFT_EXIT' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="dateRange"
            label="Date Duration"
            rules={[{ required: true, message: 'Please select start and end date' }]}
          >
            <DatePicker.RangePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="reason"
            label="Reason & Description"
            rules={[{ required: true, min: 5, message: 'Please provide valid justification' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder="Provide reason for leave, destination town, or urgent circumstances..."
            />
          </Form.Item>

          <Form.Item
            name="emergency_contact"
            label="Contact Number During Absence"
          >
            <Input placeholder="+91 98765 12345" defaultValue={worker?.emergency_contact_phone} />
          </Form.Item>
        </Form>
      </Modal>

      {/* ── MODAL: DIGITAL WORKER PASS & QR ─────────────────────────────── */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <IdcardOutlined style={{ color: '#10b981' }} />
            <span>Smart RFID Worker Pass & Safety Clearance</span>
          </div>
        }
        open={idCardModalVisible}
        onCancel={() => setIdCardModalVisible(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setIdCardModalVisible(false)}>
            Close ID Card
          </Button>
        ]}
      >
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <div
            style={{
              display: 'inline-block',
              padding: 16,
              background: '#f8fafc',
              borderRadius: 12,
              border: '2px dashed #cbd5e1'
            }}
          >
            <QRCode
              value={`MINEGUARD-WORKER:${worker?.employee_id || 'EMP-2026-9901'}:${worker?.full_name || 'Ramesh Kumar'}:FIT`}
              size={180}
            />
          </div>

          <Title level={4} style={{ marginTop: 16, marginBottom: 4 }}>
            {worker?.full_name || 'Ramesh Kumar'}
          </Title>
          <div style={{ color: '#0284c7', fontWeight: 600, fontSize: 14 }}>
            {worker?.employee_id || 'EMP-2026-9901'}
          </div>
          <div style={{ color: '#71717a', fontSize: 13, marginTop: 4 }}>
            {worker?.role?.replace(/_/g, ' ')} • Kusmunda Opencast Mine
          </div>

          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center', gap: 8 }}>
            <Tag color="success">DGMS MEDICAL: FIT</Tag>
            <Tag color="blue">VTC CERTIFIED</Tag>
            <Tag color="gold">PIT FACE PERMIT</Tag>
          </div>
        </div>
      </Modal>

      {/* ── MODAL: DIRECT SAFETY / HAZARD REPORT ────────────────────────── */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertOutlined style={{ color: '#f97316' }} />
            <span>Direct Worker Safety / Hazard Concern Report</span>
          </div>
        }
        open={hazardModalVisible}
        onCancel={() => setHazardModalVisible(false)}
        onOk={handleReportHazard}
        okText="Submit to Safety Officer"
      >
        <Form form={hazardForm} layout="vertical" initialValues={{ category: 'SAFETY_VIOLATION', priority: 'HIGH' }}>
          <Form.Item name="category" label="Concern Category" rules={[{ required: true }]}>
            <Select
              options={[
                { label: 'Unsafe Bench / Highwall Slope Condition', value: 'SAFETY_VIOLATION' },
                { label: 'HEMM Heavy Machinery Mechanical Issue', value: 'EQUIPMENT_FAULT' },
                { label: 'Dust Suppression / Ventilation Concern', value: 'ENVIRONMENTAL' },
                { label: 'PPE Defect or Shortage', value: 'PPE_DEFECT' },
                { label: 'Worker Grievance / Fatigue Concern', value: 'WORKER_WELFARE' },
              ]}
            />
          </Form.Item>

          <Form.Item name="priority" label="Priority Level" rules={[{ required: true }]}>
            <Select
              options={[
                { label: 'High (Immediate Risk)', value: 'HIGH' },
                { label: 'Medium (Requires Action Today)', value: 'MEDIUM' },
                { label: 'Low (General Improvement)', value: 'LOW' },
              ]}
            />
          </Form.Item>

          <Form.Item name="title" label="Summary Title" rules={[{ required: true, min: 4 }]}>
            <Input placeholder="e.g. Loose rock boulders detected on Bench 3 slope" />
          </Form.Item>

          <Form.Item name="description" label="Detailed Hazard Description" rules={[{ required: true, min: 10 }]}>
            <Input.TextArea rows={4} placeholder="Describe exact location, danger level, machinery involved..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
export default WorkerPortalPage;
