import React, { useState, useEffect } from 'react';
import {
  Button,
  Form,
  Input,
  Card,
  Typography,
  Space,
  Select,
  Row,
  Col,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  IdcardOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { PublicNavbar } from '../components/PublicNavbar';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

export const LoginPage: React.FC = () => {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useTheme();

  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [signInForm] = Form.useForm();
  const [signUpForm] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // Parse query params (?mode=signin|signup, ?role=worker|admin)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const modeParam = params.get('mode');
    const roleParam = params.get('role');

    if (modeParam === 'signup') {
      setAuthMode('signup');
    } else {
      setAuthMode('signin');
    }

    if (roleParam === 'worker') {
      signUpForm.setFieldsValue({ role: 'WORKER', designation: 'Pit Operator' });
    } else if (roleParam === 'admin') {
      signUpForm.setFieldsValue({ role: 'SUPER_ADMIN', designation: 'Safety & Mine Administrator' });
    }
  }, [location.search, signUpForm]);

  const handleSignIn = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const success = await login(values.email, values.password);
      if (success) {
        // Redirect based on role in user object or email heuristic
        const storedUser = localStorage.getItem('user_role');
        if (values.email.toLowerCase().includes('worker') || storedUser === 'WORKER') {
          navigate('/worker-portal');
        } else {
          navigate('/dashboard');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (values: {
    fullName: string;
    email: string;
    password: string;
    role: string;
    designation?: string;
    phoneNumber?: string;
  }) => {
    setLoading(true);
    try {
      const success = await register({
        full_name: values.fullName,
        email: values.email,
        password: values.password,
        role: values.role,
        designation: values.designation || undefined,
        phone_number: values.phoneNumber || undefined,
      });

      if (success) {
        if (values.role === 'WORKER') {
          navigate('/worker-portal');
        } else {
          navigate('/dashboard');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const cardBg = isDark ? '#111111' : '#ffffff';
  const borderColor = isDark ? '#27272a' : '#e4e4e7';
  const textColor = isDark ? '#ffffff' : '#18181b';
  const secondaryTextColor = isDark ? '#a1a1aa' : '#71717a';

  return (
    <div
      style={{
        minHeight: '100vh',
        background: isDark ? '#050505' : '#fafafa',
        display: 'flex',
        flexDirection: 'column',
        transition: 'background-color 0.2s ease',
      }}
    >
      <PublicNavbar />

      <div
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 16px',
        }}
      >
        <div style={{ width: '100%', maxWidth: authMode === 'signup' ? 540 : 440 }}>
          {/* Header Description */}
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <Title
              level={2}
              style={{
                margin: '0 0 8px',
                color: textColor,
                fontSize: 26,
                fontWeight: 700,
                letterSpacing: -0.5,
              }}
            >
              {authMode === 'signin' ? 'Sign In to AI MineGuard' : 'Create an Account'}
            </Title>
            <Paragraph
              style={{
                fontSize: 14,
                color: secondaryTextColor,
                margin: 0,
                lineHeight: 1.5,
              }}
            >
              {authMode === 'signin'
                ? 'Enter your credentials to access your mining portal'
                : 'Register an authorized account for worker self-service or safety administration'}
            </Paragraph>
          </div>

          {/* Toggle Tab between Sign In and Sign Up */}
          <div
            style={{
              display: 'flex',
              background: isDark ? '#18181b' : '#f4f4f5',
              borderRadius: 8,
              padding: 4,
              marginBottom: 20,
              border: `1px solid ${borderColor}`,
            }}
          >
            <button
              type="button"
              onClick={() => {
                setAuthMode('signin');
                navigate('/login?mode=signin', { replace: true });
              }}
              style={{
                flex: 1,
                padding: '10px 0',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                fontWeight: authMode === 'signin' ? 600 : 500,
                fontSize: 14,
                background: authMode === 'signin' ? (isDark ? '#27272a' : '#ffffff') : 'transparent',
                color: authMode === 'signin' ? textColor : secondaryTextColor,
                boxShadow: authMode === 'signin' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                transition: 'all 0.15s ease',
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('signup');
                navigate('/login?mode=signup', { replace: true });
              }}
              style={{
                flex: 1,
                padding: '10px 0',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                fontWeight: authMode === 'signup' ? 600 : 500,
                fontSize: 14,
                background: authMode === 'signup' ? (isDark ? '#27272a' : '#ffffff') : 'transparent',
                color: authMode === 'signup' ? textColor : secondaryTextColor,
                boxShadow: authMode === 'signup' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                transition: 'all 0.15s ease',
              }}
            >
              Create Account
            </button>
          </div>

          {/* Main Form Card */}
          <Card
            bordered
            style={{
              borderRadius: 12,
              background: cardBg,
              borderColor,
              boxShadow: isDark ? '0 8px 30px rgba(0,0,0,0.5)' : '0 8px 24px rgba(0,0,0,0.06)',
            }}
          >
            {authMode === 'signin' ? (
              /* ── SIGN IN FORM ────────────────────────────────────────── */
              <Form
                form={signInForm}
                layout="vertical"
                onFinish={handleSignIn}
                autoComplete="off"
                requiredMark={false}
              >
                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Email Address</span>}
                  name="email"
                  rules={[
                    { required: true, message: 'Please enter your email address' },
                    { type: 'email', message: 'Please enter a valid email format' },
                  ]}
                >
                  <Input
                    prefix={<MailOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="name@mineguard.in"
                    autoComplete="email"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Password</span>}
                  name="password"
                  rules={[{ required: true, message: 'Please enter your password' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  block
                  loading={loading}
                  style={{
                    height: 46,
                    fontWeight: 600,
                    fontSize: 15,
                    borderRadius: 6,
                    background: '#0284c7',
                    borderColor: '#0284c7',
                    boxShadow: '0 2px 8px rgba(2, 132, 199, 0.25)',
                    marginTop: 8,
                  }}
                >
                  Sign In <ArrowRightOutlined />
                </Button>

                <div style={{ textAlign: 'center', marginTop: 18 }}>
                  <Text style={{ fontSize: 13, color: secondaryTextColor }}>
                    Don't have an account?{' '}
                    <span
                      onClick={() => {
                        setAuthMode('signup');
                        navigate('/login?mode=signup', { replace: true });
                      }}
                      style={{
                        color: isDark ? '#38bdf8' : '#0284c7',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Create one here
                    </span>
                  </Text>
                </div>
              </Form>
            ) : (
              /* ── SIGN UP FORM ────────────────────────────────────────── */
              <Form
                form={signUpForm}
                layout="vertical"
                onFinish={handleSignUp}
                autoComplete="off"
                initialValues={{
                  role: 'WORKER',
                  designation: 'Pit Operator',
                }}
                requiredMark={false}
              >
                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Full Name</span>}
                  name="fullName"
                  rules={[{ required: true, message: 'Please enter your full name' }]}
                >
                  <Input
                    prefix={<UserOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="e.g. Ramesh Kumar"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Email Address</span>}
                  name="email"
                  rules={[
                    { required: true, message: 'Please enter a valid email address' },
                    { type: 'email', message: 'Enter a valid email format' },
                  ]}
                >
                  <Input
                    prefix={<MailOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="e.g. ramesh.kumar@mineguard.in"
                    autoComplete="email"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Account Role</span>}
                  name="role"
                  rules={[{ required: true, message: 'Select your operational role' }]}
                >
                  <Select size="large" style={{ borderRadius: 6 }}>
                    <Option value="WORKER">
                      <Space>
                        <UserOutlined /> Mine Worker (Self-Service Portal)
                      </Space>
                    </Option>
                    <Option value="SAFETY_OFFICER">
                      <Space>
                        <SafetyCertificateOutlined /> Safety Officer (Inspections & Audits)
                      </Space>
                    </Option>
                    <Option value="MINE_MANAGER">
                      <Space>
                        <TeamOutlined /> Mine Manager (Operations & Production)
                      </Space>
                    </Option>
                    <Option value="SUPER_ADMIN">
                      <Space>
                        <SafetyCertificateOutlined /> Administrator (Central Command)
                      </Space>
                    </Option>
                  </Select>
                </Form.Item>

                <Row gutter={12}>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label={<span style={{ fontWeight: 500, color: textColor }}>Designation / Title</span>}
                      name="designation"
                    >
                      <Input
                        prefix={<IdcardOutlined style={{ color: secondaryTextColor }} />}
                        size="large"
                        placeholder="e.g. Excavator Operator"
                        style={{ borderRadius: 6 }}
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label={<span style={{ fontWeight: 500, color: textColor }}>Phone Number</span>}
                      name="phoneNumber"
                    >
                      <Input
                        prefix={<PhoneOutlined style={{ color: secondaryTextColor }} />}
                        size="large"
                        placeholder="+91 98765 43210"
                        style={{ borderRadius: 6 }}
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Password</span>}
                  name="password"
                  rules={[
                    { required: true, message: 'Please create a password' },
                    { min: 6, message: 'Password must be at least 6 characters' },
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="Minimum 6 characters"
                    autoComplete="new-password"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Form.Item
                  label={<span style={{ fontWeight: 500, color: textColor }}>Confirm Password</span>}
                  name="confirmPassword"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: 'Please confirm your password' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('Passwords do not match'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: secondaryTextColor }} />}
                    size="large"
                    placeholder="Repeat your password"
                    autoComplete="new-password"
                    style={{ borderRadius: 6 }}
                  />
                </Form.Item>

                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  block
                  loading={loading}
                  style={{
                    height: 46,
                    fontWeight: 600,
                    fontSize: 15,
                    borderRadius: 6,
                    background: '#0284c7',
                    borderColor: '#0284c7',
                    boxShadow: '0 2px 8px rgba(2, 132, 199, 0.25)',
                    marginTop: 8,
                  }}
                >
                  Register Account <CheckCircleOutlined />
                </Button>

                <div style={{ textAlign: 'center', marginTop: 18 }}>
                  <Text style={{ fontSize: 13, color: secondaryTextColor }}>
                    Already have an account?{' '}
                    <span
                      onClick={() => {
                        setAuthMode('signin');
                        navigate('/login?mode=signin', { replace: true });
                      }}
                      style={{
                        color: isDark ? '#38bdf8' : '#0284c7',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Sign in here
                    </span>
                  </Text>
                </div>
              </Form>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
export default LoginPage;
