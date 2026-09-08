import React from 'react';
import { Button, Tooltip } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';

interface ThemeToggleProps {
  size?: 'small' | 'middle' | 'large';
  style?: React.CSSProperties;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ size = 'middle', style }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <Tooltip title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'} placement="bottom">
      <Button
        type="text"
        size={size}
        icon={isDark ? <SunOutlined style={{ color: '#facc15', fontSize: 16 }} /> : <MoonOutlined style={{ color: '#52525b', fontSize: 16 }} />}
        onClick={toggleTheme}
        aria-label="Toggle theme"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 8,
          border: isDark ? '1px solid #27272a' : '1px solid #e4e4e7',
          background: isDark ? '#111111' : '#ffffff',
          transition: 'all 0.2s ease',
          ...style,
        }}
      />
    </Tooltip>
  );
};
