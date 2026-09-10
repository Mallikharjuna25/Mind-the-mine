// ========== shadcnTheme.ts ==========

import { useMemo } from 'react';
import { theme } from 'antd';
import type { ConfigProviderProps } from 'antd';
import { createStyles } from 'antd-style';
import { clsx } from 'clsx';

const useStyles = createStyles(({ css }) => {
  return {
    buttonPrimary: css({
      backgroundColor: '#18181b',
      color: '#ffffff',
      border: '1px solid #18181b',
      fontWeight: 500,
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    }),
    buttonDefault: css({
      backgroundColor: '#ffffff',
      color: '#18181b',
      border: '1px solid #e4e4e7',
      fontWeight: 500,
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    }),
    buttonDanger: css({
      backgroundColor: '#dc2626',
      color: '#ffffff',
      border: '1px solid #dc2626',
      fontWeight: 500,
    }),
    inputRoot: css({
      borderColor: '#e4e4e7',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    }),
    inputElement: css({
      color: '#18181b',
    }),
    inputError: css({
      borderColor: '#dc2626',
    }),
    selectRoot: css({
      borderColor: '#e4e4e7',
    }),
    selectPopup: css({
      borderRadius: '8px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    }),
    notificationRoot: css({
      '&.ant-notification-notice, & .ant-notification-notice': {
        border: '1px solid #e4e4e7',
        borderRadius: 8,
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      },
    }),
    notificationTitle: css({
      fontWeight: 600,
    }),
    notificationDescription: css({
      color: '#525252',
    }),
  };
});

const useShadcnTheme = () => {
  const { styles } = useStyles();

  return useMemo<ConfigProviderProps>(
    () => ({
      theme: {
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#3b82f6',
          colorSuccess: '#10b981',
          colorWarning: '#f59e0b',
          colorError: '#ef4444',
          colorInfo: '#06b6d4',
          colorTextBase: '#e2e8f0',
          colorBgBase: '#0b0f14',
          colorBgLayout: '#0b0f14',
          colorBgContainer: '#11161d',
          colorBgElevated: '#151b23',
          colorText: '#e2e8f0',
          colorTextSecondary: '#94a3b8',
          colorBorder: '#1e293b',
          colorBorderSecondary: '#334155',
          borderRadius: 8,
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        },
        components: {
          Layout: {
            bodyBg: '#0b0f14',
            headerBg: '#11161d',
            siderBg: '#11161d',
            headerColor: '#e2e8f0',
          },
          Card: {
            colorBgContainer: '#11161d',
            colorBorderSecondary: '#1e293b',
          },
          Menu: {
            itemBg: 'transparent',
            subMenuItemBg: 'transparent',
            itemHoverBg: '#1e293b',
            itemSelectedBg: '#1e3a8a',
            itemSelectedColor: '#60a5fa',
          },
          Table: {
            colorBgContainer: '#11161d',
            headerBg: '#151b23',
            rowHoverBg: '#1e293b',
          },
          Button: {
            defaultBg: '#1e293b',
            defaultBorderColor: '#334155',
            defaultColor: '#e2e8f0',
            defaultHoverBg: '#334155',
            defaultHoverBorderColor: '#475569',
          },
        },
      },
      button: {
        classNames: ({ props }: { props: { type?: string; danger?: boolean } }) => ({
          root: clsx(
            props.type === 'primary' && styles.buttonPrimary,
            props.type === 'default' && styles.buttonDefault,
            props.danger && styles.buttonDanger,
          ),
        }),
      },
      input: {
        classNames: ({ props }: { props: { status?: string } }) => ({
          root: clsx(styles.inputRoot, props.status === 'error' && styles.inputError),
          input: styles.inputElement,
        }),
      },
      select: {
        classNames: {
          root: styles.selectRoot,
        },
      },
      notification: {
        classNames: {
          root: styles.notificationRoot,
          title: styles.notificationTitle,
          description: styles.notificationDescription,
        },
      },
      wave: {},
      app: {},
      card: {},
      modal: {},
      alert: {},
      colorPicker: {},
      checkbox: {},
      dropdown: {},
      datePicker: {},
      inputNumber: {},
      popover: {},
      tooltip: {},
      switch: {},
      radio: {},
      segmented: {},
      progress: {},
    }),
    [
      styles.buttonDanger,
      styles.buttonDefault,
      styles.buttonPrimary,
      styles.inputElement,
      styles.inputError,
      styles.inputRoot,
      styles.notificationDescription,
      styles.notificationRoot,
      styles.notificationTitle,
      styles.selectRoot,
    ],
  );
};

export default useShadcnTheme;
