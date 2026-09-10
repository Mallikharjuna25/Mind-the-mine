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

// ── MODULE 2: FIELD OPERATIONS & INSPECTION MANAGEMENT ───────────────────
export const inspectionsApi = {
  templates: () => api.get('/inspections/templates'),
  list: (params?: Record<string, unknown>) => api.get('/inspections', { params }),
  submit: (payload: unknown) => api.post('/inspections', payload),
  get: (id: string) => api.get(`/inspections/${id}`),
};

export const fieldReportsApi = {
  list: (params?: Record<string, unknown>) => api.get('/field-reports', { params }),
  create: (payload: unknown) => api.post('/field-reports', payload),
  get: (id: string) => api.get(`/field-reports/${id}`),
};

export const incidentsApi = {
  list: (params?: Record<string, unknown>) => api.get('/incidents', { params }),
  create: (payload: unknown) => api.post('/incidents', payload),
  get: (id: string) => api.get(`/incidents/${id}`),
};

export const verificationApi = {
  list: (params?: Record<string, unknown>) => api.get('/field-verifications', { params }),
  get: (id: string) => api.get(`/field-verifications/${id}`),
  transition: (id: string, payload: unknown) =>
    api.patch(`/field-verifications/${id}/transition`, payload),
};

export const gisApi = {
  features: (mineId?: string) => api.get('/gis/features', { params: { mine_id: mineId } }),
};

export const syncApi = {
  status: () => api.get('/sync/status'),
  batch: (payload: unknown) => api.post('/sync/batch', payload),
};

export const aiStructuringApi = {
  structure: (raw_text: string) => api.post('/ai/structure-incident', { raw_text }),
};

// ── MODULE 3: CONTRACTOR & WORKER COMPLIANCE MANAGEMENT ─────────────────
export const contractorsApi = {
  dashboard: (mineId?: string) =>
    api.get('/mine/contractors/dashboard', { params: { mine_id: mineId } }),
  list: (params?: Record<string, unknown>) => api.get('/mine/contractors', { params }),
  get: (id: string) => api.get(`/mine/contractors/${id}`),
  create: (payload: unknown) => api.post('/mine/contractors', payload),
  update: (id: string, payload: unknown) => api.put(`/mine/contractors/${id}`, payload),
  delete: (id: string) => api.delete(`/mine/contractors/${id}`),
  renewContract: (id: string, payload: unknown) =>
    api.post(`/mine/contracts/${id}/renew`, payload),
};

export const workersApi = {
  dashboard: (mineId?: string) =>
    api.get('/mine/workers/dashboard', { params: { mine_id: mineId } }),
  list: (params?: Record<string, unknown>) => api.get('/mine/workers', { params }),
  get: (id: string) => api.get(`/mine/workers/${id}`),
  create: (payload: unknown) => api.post('/mine/workers', payload),
  update: (id: string, payload: unknown) => api.put(`/mine/workers/${id}`, payload),
  delete: (id: string) => api.delete(`/mine/workers/${id}`),
  addAttendance: (payload: unknown) => api.post('/mine/workers/attendance', payload),
  addTraining: (payload: unknown) => api.post('/mine/workers/training', payload),
  issuePPE: (payload: unknown) => api.post('/mine/workers/ppe', payload),
  grantPermit: (payload: unknown) => api.post('/mine/workers/authorize', payload),
};

export const governanceApi = {
  dashboard: (mineId: string) =>
    api.get('/mine/governance/dashboard', { params: { mine_id: mineId } }),
  grievances: (params?: Record<string, unknown>) =>
    api.get('/mine/governance/grievances', { params }),
  createGrievance: (payload: unknown) =>
    api.post('/mine/governance/grievances', payload),
  resolveGrievance: (id: string, payload: unknown) =>
    api.post(`/mine/governance/grievances/${id}/resolve`, payload),
  approvalRequests: (params?: Record<string, unknown>) =>
    api.get('/mine/governance/approvals', { params }),
  createApproval: (payload: unknown) =>
    api.post('/mine/governance/approvals', payload),
  actionApproval: (id: string, payload: unknown) =>
    api.post(`/mine/governance/approvals/${id}/action`, payload),
  evaluateEscalations: (mineId: string) =>
    api.post('/mine/governance/escalations/evaluate', null, { params: { mine_id: mineId } }),
  auditTrail: (mineId: string) =>
    api.get('/mine/governance/audit-trail', { params: { mine_id: mineId } }),
};

export default api;

