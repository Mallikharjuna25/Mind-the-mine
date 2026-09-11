import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authApi } from '../services/api';
import { notification } from 'antd';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  designation: string;
  mine_id: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (payload: {
    email: string;
    password: string;
    full_name: string;
    role: string;
    designation?: string;
    phone_number?: string;
    mine_id?: string;
  }) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authApi
        .me()
        .then((res) => setUser(res.data?.data || res.data))
        .catch(() => {
          localStorage.removeItem('access_token');
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const res = await authApi.login(email, password);
      const access_token = res.data?.data?.access_token || res.data?.access_token;
      if (!access_token) {
        throw new Error('Access token not found in response');
      }
      localStorage.setItem('access_token', access_token);
      setToken(access_token);
      const me = await authApi.me();
      setUser(me.data?.data || me.data);
      return true;
    } catch {
      notification.error({ message: 'Login Failed', description: 'Invalid credentials.' });
      return false;
    }
  };

  const register = async (payload: {
    email: string;
    password: string;
    full_name: string;
    role: string;
    designation?: string;
    phone_number?: string;
    mine_id?: string;
  }): Promise<boolean> => {
    try {
      await authApi.register(payload);
      notification.success({
        message: 'Account Created',
        description: 'Registration successful! Logging you in...',
      });
      return await login(payload.email, payload.password);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      notification.error({
        message: 'Registration Failed',
        description: axiosErr?.response?.data?.detail || 'Could not register user. Please check your details.',
      });
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  const isAdmin = Boolean(user && (user.role === 'SUPER_ADMIN' || user.role === 'ADMIN'));

  return (
    <AuthContext.Provider value={{ user, token, isAdmin, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
};
