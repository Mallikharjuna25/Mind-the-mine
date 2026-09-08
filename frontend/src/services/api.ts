import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── AUTH ──────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  register: (payload: unknown) => api.post('/auth/register', payload),
};

// ── MINES ─────────────────────────────────────────────────────────────
export const mineApi = {
  list: () => api.get('/mine/mines'),
  get: (id: string) => api.get(`/mine/mines/${id}`),
  zones: (mineId: string) => api.get(`/mine/mines/${mineId}/zones`),
};

// ── CCTV ──────────────────────────────────────────────────────────────
export const cctvApi = {
  cameras: (params?: Record<string, unknown>) => api.get('/mine/cameras', { params }),
  detections: (params?: Record<string, unknown>) => api.get('/mine/detections', { params }),
  violations: (params?: Record<string, unknown>) => api.get('/mine/violations', { params }),
  getViolation: (id: string) => api.get(`/mine/violations/${id}`),
  verifyViolation: (id: string, payload: unknown) => api.post(`/mine/violations/${id}/verify`, payload),
  ingestDetection: (payload: unknown) => api.post('/mine/detections/ingest', payload),
};

// ── COMPLIANCE ─────────────────────────────────────────────────────────
export const complianceApi = {
  violations: (params?: Record<string, unknown>) => api.get('/mine/violations', { params }),
};

// ── EQUIPMENT ─────────────────────────────────────────────────────────
export const equipmentApi = {
  assets: (params?: Record<string, unknown>) => api.get('/mine/equipment', { params }),
  get: (id: string) => api.get(`/mine/equipment/${id}`),
  expiryAlerts: () => api.get('/mine/equipment/expiring'),
  documents: (assetId: string) => api.get(`/mine/equipment/${assetId}/documents`),
};

// ── ENVIRONMENT ────────────────────────────────────────────────────────
export const environmentApi = {
  readings: (params?: Record<string, unknown>) =>
    api.get('/mine/environmental-readings', { params }),
  breaches: (params?: Record<string, unknown>) =>
    api.get('/mine/environmental-readings', { params: { ...params, is_breach: true } }),
};

// ── PRODUCTION ─────────────────────────────────────────────────────────
export const productionApi = {
  records: (params?: Record<string, unknown>) =>
    api.get('/mine/production-records', { params }),
};

// ── RISK ENGINE ────────────────────────────────────────────────────────
export const riskApi = {
  latestScores: (params?: Record<string, unknown>) =>
    api.get('/mine/risk-scores/latest', { params }),
  scores: (params?: Record<string, unknown>) =>
    api.get('/mine/risk-scores/latest', { params }),
  compute: (payload: unknown) => api.post('/mine/risk-scores/compute', payload),
  recompute: (mineId: string, zoneId?: string) =>
    api.post('/mine/risk-scores/compute', { mine_id: mineId, zone_id: zoneId }),
  anomalies: (params?: Record<string, unknown>) => api.get('/mine/anomalies', { params }),
  resolveAnomaly: (id: string) => api.post(`/mine/anomalies/${id}/resolve`),
};

// ── WORKFLOWS & ALERTS ─────────────────────────────────────────────────
export const workflowApi = {
  alerts: (params?: Record<string, unknown>) => api.get('/mine/alerts', { params }),
  acknowledge: (alertId: string) => api.post(`/mine/alerts/${alertId}/acknowledge`),
  correctiveActions: (params?: Record<string, unknown>) =>
    api.get('/mine/corrective-actions', { params }),
  createCA: (payload: unknown) => api.post('/mine/corrective-actions', payload),
  verifyCA: (id: string) => api.post(`/mine/corrective-actions/${id}/verify`),
  escalations: (params?: Record<string, unknown>) => api.get('/mine/escalations', { params }),
  evaluateSla: () => api.post('/mine/escalations/evaluate-sla'),
};

// ── DEMO SIMULATION ────────────────────────────────────────────────────
export const demoApi = {
  seed: () => api.post('/demo/seed'),
  simulateViolation: () => api.post('/demo/simulate-violation'),
  simulateOcr: () => api.post('/demo/simulate-ocr'),
  simulateGasBreach: () => api.post('/demo/simulate-gas-breach'),
};

export default api;
