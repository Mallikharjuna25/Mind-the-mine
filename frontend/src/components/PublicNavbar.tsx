import React, { useState } from 'react';
import { Button, Space, Drawer, Divider } from 'antd';
import {
  UserOutlined,
  MenuOutlined,
  HomeOutlined,
  PhoneOutlined,
  InfoCircleOutlined,
  AppstoreOutlined,
  CompassOutlined,
  UserAddOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { ThemeToggle } from './ThemeToggle';
import logo from '../assets/logo.svg';

export const PublicNavbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark } = useTheme();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const isHome = location.pathname === '/' || location.pathname === '/landing';
  const isAbout = location.pathname === '/about';
  const isContact = location.pathname === '/contact';

  const borderColor = isDark ? '#27272a' : '#e4e4e7';
  const textColor = isDark ? '#ffffff' : '#18181b';
  const secondaryColor = isDark ? '#a1a1aa' : '#71717a';
  const navBg = isDark ? 'rgba(17, 17, 17, 0.94)' : 'rgba(255, 255, 255, 0.94)';

  const handleHomeClick = () => {
    setDrawerOpen(false);
    if (isHome) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      navigate('/');
    }
  };

  const handleSectionClick = (sectionId: string) => {
    setDrawerOpen(false);
    if (isHome) {
      const el = document.getElementById(sectionId);
      if (el) {
        const yOffset = -76;
        const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    } else {
      navigate(`/#${sectionId}`);
      // Wait for navigation then scroll
      setTimeout(() => {
        const el = document.getElementById(sectionId);
        if (el) {
          const yOffset = -76;
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }, 150);
    }
  };

  return (
    <>
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          background: navBg,
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: `1px solid ${borderColor}`,
          padding: '0 28px',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          transition: 'background-color 0.2s ease, border-color 0.2s ease',
        }}
      >
        {/* Brand Logo & Name */}
        <div
          style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', flexShrink: 0 }}
          onClick={handleHomeClick}
        >
          <img src={logo} alt="AI MineGuard Logo" style={{ width: 32, height: 32 }} />
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: -0.3, lineHeight: 1.2, color: textColor }}>
              AI MineGuard
            </div>
            <div style={{ fontSize: 10, color: secondaryColor, fontWeight: 500 }}>
              Mining Safety & Operational Intelligence
            </div>
          </div>
        </div>

        {/* Center Navigation Links - Desktop */}
        <nav
          style={{
            display: 'flex',
            gap: 6,
            alignItems: 'center',
          }}
          className="public-nav-desktop"
        >
          <Button
            type="text"
            onClick={handleHomeClick}
            style={{
              color: isHome ? (isDark ? '#38bdf8' : '#0284c7') : secondaryColor,
              fontWeight: isHome ? 600 : 500,
              fontSize: 14,
              padding: '4px 12px',
              height: 36,
              borderRadius: 6,
              background: isHome ? (isDark ? 'rgba(56, 189, 248, 0.1)' : 'rgba(2, 132, 199, 0.08)') : 'transparent',
            }}
          >
            Home
          </Button>

          <Button
            type="text"
            onClick={() => handleSectionClick('solution')}
            style={{
              color: secondaryColor,
              fontWeight: 500,
              fontSize: 14,
              padding: '4px 12px',
              height: 36,
              borderRadius: 6,
            }}
          >
            Our Solution
          </Button>

          <Button
            type="text"
            onClick={() => handleSectionClick('platform-use')}
            style={{
              color: secondaryColor,
              fontWeight: 500,
              fontSize: 14,
              padding: '4px 12px',
              height: 36,
              borderRadius: 6,
            }}
          >
            How It Is Used
          </Button>

          <Button
            type="text"
            onClick={() => { navigate('/about'); }}
            style={{
              color: isAbout ? (isDark ? '#38bdf8' : '#0284c7') : secondaryColor,
              fontWeight: isAbout ? 600 : 500,
              fontSize: 14,
              padding: '4px 12px',
              height: 36,
              borderRadius: 6,
              background: isAbout ? (isDark ? 'rgba(56, 189, 248, 0.1)' : 'rgba(2, 132, 199, 0.08)') : 'transparent',
            }}
          >
            About Platform
          </Button>

          <Button
            type="text"
            onClick={() => { navigate('/contact'); }}
            style={{
              color: isContact ? (isDark ? '#38bdf8' : '#0284c7') : secondaryColor,
              fontWeight: isContact ? 600 : 500,
              fontSize: 14,
              padding: '4px 12px',
              height: 36,
              borderRadius: 6,
              background: isContact ? (isDark ? 'rgba(56, 189, 248, 0.1)' : 'rgba(2, 132, 199, 0.08)') : 'transparent',
            }}
          >
            Safety Desk
          </Button>
        </nav>

        {/* Right Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <ThemeToggle size="middle" />

          <Space size={8} className="public-nav-desktop-actions">
            <Button
              onClick={() => navigate('/login?mode=signin')}
              style={{
                fontWeight: 500,
                borderColor,
                background: isDark ? '#18181b' : '#ffffff',
                color: isDark ? '#ffffff' : '#18181b',
                height: 36,
                borderRadius: 6,
              }}
            >
              <UserOutlined /> Sign In
            </Button>

            <Button
              type="primary"
              onClick={() => navigate('/login?mode=signup')}
              style={{
                background: '#0284c7',
                borderColor: '#0284c7',
                color: '#ffffff',
                fontWeight: 600,
                height: 36,
                borderRadius: 6,
                boxShadow: '0 2px 6px rgba(2, 132, 199, 0.25)',
              }}
            >
              <UserAddOutlined /> Create Account
            </Button>
          </Space>

          {/* Mobile hamburger button */}
          <Button
            type="text"
            icon={<MenuOutlined style={{ fontSize: 18 }} />}
            onClick={() => setDrawerOpen(true)}
            style={{ display: 'none', height: 36, width: 36 }}
            className="public-nav-mobile-toggle"
          />
        </div>
      </header>

      {/* ── MOBILE DRAWER ────────────────────────────────────────── */}
      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src={logo} alt="AI MineGuard" style={{ width: 26, height: 26 }} />
            <span style={{ fontWeight: 700, fontSize: 16 }}>AI MineGuard</span>
          </div>
        }
        placement="right"
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
        styles={{
          body: {
            background: isDark ? '#111111' : '#ffffff',
            color: textColor,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            padding: '20px 16px',
          },
          header: {
            background: isDark ? '#111111' : '#ffffff',
            borderBottom: `1px solid ${borderColor}`,
          },
        }}
      >
        <Button
          type="text"
          block
          icon={<HomeOutlined />}
          onClick={handleHomeClick}
          style={{
            textAlign: 'left',
            height: 42,
            fontSize: 14,
            fontWeight: isHome ? 600 : 500,
            color: isHome ? (isDark ? '#38bdf8' : '#0284c7') : textColor,
          }}
        >
          Home
        </Button>

        <Button
          type="text"
          block
          icon={<AppstoreOutlined />}
          onClick={() => handleSectionClick('solution')}
          style={{ textAlign: 'left', height: 42, fontSize: 14, color: secondaryColor }}
        >
          Our Solution
        </Button>

        <Button
          type="text"
          block
          icon={<CompassOutlined />}
          onClick={() => handleSectionClick('platform-use')}
          style={{ textAlign: 'left', height: 42, fontSize: 14, color: secondaryColor }}
        >
          How It Is Used
        </Button>

        <Button
          type="text"
          block
          icon={<InfoCircleOutlined />}
          onClick={() => { setDrawerOpen(false); navigate('/about'); }}
          style={{
            textAlign: 'left',
            height: 42,
            fontSize: 14,
            fontWeight: isAbout ? 600 : 500,
            color: isAbout ? (isDark ? '#38bdf8' : '#0284c7') : textColor,
          }}
        >
          About Platform
        </Button>

        <Button
          type="text"
          block
          icon={<PhoneOutlined />}
          onClick={() => { setDrawerOpen(false); navigate('/contact'); }}
          style={{
            textAlign: 'left',
            height: 42,
            fontSize: 14,
            fontWeight: isContact ? 600 : 500,
            color: isContact ? (isDark ? '#38bdf8' : '#0284c7') : textColor,
          }}
        >
          Safety Desk
        </Button>

        <Divider style={{ margin: '14px 0', borderColor }} />

        <Button
          block
          size="large"
          icon={<UserOutlined />}
          onClick={() => { setDrawerOpen(false); navigate('/login?mode=signin'); }}
          style={{ height: 44, fontWeight: 600 }}
        >
          Sign In
        </Button>

        <Button
          type="primary"
          block
          size="large"
          icon={<UserAddOutlined />}
          onClick={() => { setDrawerOpen(false); navigate('/login?mode=signup'); }}
          style={{ height: 44, fontWeight: 600, background: '#0284c7', borderColor: '#0284c7' }}
        >
          Create Account
        </Button>
      </Drawer>

      {/* Responsive media rules */}
      <style>{`
        @media (max-width: 900px) {
          .public-nav-desktop {
            display: none !important;
          }
          .public-nav-desktop-actions {
            display: none !important;
          }
          .public-nav-mobile-toggle {
            display: inline-flex !important;
          }
        }
      `}</style>
    </>
  );
};
