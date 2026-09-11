import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { theme } from 'antd';
import type { ConfigProviderProps } from 'antd';

interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
  configProps: ConfigProviderProps;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDark, setIsDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('mineguard_theme');
    if (saved) return saved === 'dark';
    return false; // default light mode
  });

  useEffect(() => {
    localStorage.setItem('mineguard_theme', isDark ? 'dark' : 'light');
    if (isDark) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
      document.body.style.backgroundColor = '#050505';
      document.body.style.color = 'rgba(255, 255, 255, 0.88)';
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
      document.body.style.backgroundColor = '#fafafa';
      document.body.style.color = '#18181b';
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark((prev) => !prev);

  // User's exact theme specifications combined with light/dark algorithms
  const configProps = useMemo<ConfigProviderProps>(() => {
    if (isDark) {
      return {
        theme: {
          algorithm: theme.darkAlgorithm,
          token: {
            colorPrimary: '#1677ff',
            colorBgBase: '#050505',
            colorTextBase: 'rgba(255, 255, 255, 0.88)',
            colorBorder: '#27272a',
            colorBorderSecondary: '#1f1f23',
            borderRadius: 6,
          },
          components: {
            Layout: {
              bodyBg: '#050505',
              footerBg: '#050505',
              headerBg: '#111111',
              headerColor: 'rgba(255, 255, 255, 0.88)',
              siderBg: '#050505',
              triggerBg: '#111111',
              triggerColor: 'rgba(255, 255, 255, 0.88)',
            },
            Menu: {
              darkItemBg: 'transparent',
              darkItemColor: 'rgba(255, 255, 255, 0.68)',
              darkItemHoverBg: 'rgba(255, 255, 255, 0.08)',
              darkItemHoverColor: '#fff',
              darkItemSelectedBg: 'rgba(22, 119, 255, 0.28)',
              darkItemSelectedColor: '#fff',
              darkSubMenuItemBg: 'transparent',
              itemBg: 'transparent',
              itemColor: 'rgba(255, 255, 255, 0.68)',
              itemHoverBg: 'rgba(255, 255, 255, 0.08)',
              itemHoverColor: '#fff',
              itemSelectedBg: 'rgba(22, 119, 255, 0.28)',
              itemSelectedColor: '#fff',
              subMenuItemBg: 'transparent',
            },
            Card: {
              colorBgContainer: '#111111',
              colorBorderSecondary: '#27272a',
            },
            Button: {
              primaryShadow: 'none',
              defaultShadow: 'none',
            },
            Alert: {
              colorInfoBg: '#111b27',
              colorInfoBorder: '#15325b',
            },
            Modal: {
              contentBg: '#111111',
              headerBg: '#111111',
            },
            Tooltip: {},
            Checkbox: {},
            Radio: {},
            Table: {
              colorBgContainer: '#111111',
              headerBg: '#141416',
              headerColor: '#ffffff',
              rowHoverBg: '#182234',
              borderColor: '#27272a',
            },
            Descriptions: {
              labelBg: '#141416',
              titleColor: '#ffffff',
              contentColor: 'rgba(255, 255, 255, 0.9)',
            },
            Dropdown: {
              colorBgElevated: '#18181b',
            },
            Select: {
              colorBgContainer: '#111111',
              colorBgElevated: '#18181b',
              colorBorder: '#27272a',
              optionSelectedBg: 'rgba(22, 119, 255, 0.25)',
              optionActiveBg: 'rgba(255, 255, 255, 0.08)',
            },
            Input: {
              colorBgContainer: '#111111',
              colorBorder: '#27272a',
            },
            Switch: {},
            Progress: {
              circleTextColor: 'rgba(255, 255, 255, 0.88)',
              defaultColor: '#1677FF',
              remainingColor: 'rgba(255, 255, 255, 0.12)',
            },
            Steps: {},
            Slider: {},
            ColorPicker: {},
            Notification: {
              colorBgElevated: '#111111',
            },
          },
        },
      };
    }

    // Light Theme
    return {
      theme: {
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#18181b',
          colorBgBase: '#ffffff',
          colorTextBase: '#18181b',
          colorBorder: '#e4e4e7',
          colorBorderSecondary: '#f4f4f5',
          borderRadius: 6,
        },
        components: {
          Layout: {
            bodyBg: '#fafafa',
            footerBg: '#fafafa',
            headerBg: '#ffffff',
            headerColor: '#18181b',
            siderBg: '#ffffff',
            triggerBg: '#f4f4f5',
            triggerColor: '#18181b',
          },
          Menu: {
            itemBg: 'transparent',
            itemColor: '#52525b',
            itemHoverBg: '#f4f4f5',
            itemHoverColor: '#18181b',
            itemSelectedBg: '#f4f4f5',
            itemSelectedColor: '#18181b',
            subMenuItemBg: 'transparent',
          },
          Table: {
            colorBgContainer: '#ffffff',
            headerBg: '#f8fafc',
            headerColor: '#0f172a',
            rowHoverBg: '#f1f5f9',
            borderColor: '#e2e8f0',
          },
          Card: {
            colorBgContainer: '#ffffff',
            colorBorderSecondary: '#e4e4e7',
          },
          Button: {
            primaryShadow: 'none',
            defaultShadow: 'none',
          },
          Progress: {
            circleTextColor: '#18181b',
            defaultColor: '#18181b',
            remainingColor: '#f4f4f5',
          },
        },
      },
    };
  }, [isDark]);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, configProps }}>
      {children}
    </ThemeContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};
