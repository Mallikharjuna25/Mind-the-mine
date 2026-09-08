// Global application types for AI MineGuard frontend

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Mine {
  id: string;
  mine_code: string;
  name: string;
  subsidiary: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  area_sqkm: number;
  is_active: boolean;
  created_at: string;
}

export interface MineZone {
  id: string;
  mine_id: string;
  zone_code: string;
  name: string;
  zone_type: string;
  risk_weight: number;
  is_restricted: boolean;
  polygon_geojson: Record<string, unknown>;
}

export interface Camera {
  id: string;
  mine_id: string;
  zone_id: string;
  camera_code: string;
  name: string;
  location_desc: string;
  latitude: number;
  longitude: number;
  status: string;
  ppe_check_enabled: boolean;
  restricted_zone_enabled: boolean;
  fire_smoke_enabled: boolean;
}

export interface DetectionEvent {
  id: string;
  camera_id: string;
  detection_type: string;
  raw_class_name: string;
  confidence_score: number;
  is_promoted: boolean;
  bounding_box_json: Record<string, unknown>;
  created_at: string;
}

export interface Violation {
  id: string;
  camera_id: string;
  zone_id: string;
  mine_id: string;
  violation_type: string;
  severity: string;
  description: string;
  confidence_score: number;
  status: string;
  created_at: string;
}

export interface EquipmentAsset {
  id: string;
  mine_id: string;
  zone_id: string;
  asset_code: string;
  name: string;
  category: string;
  serial_number: string;
  make_model: string;
  fitness_expiry_date: string;
  working_condition: string;
  status: string;
  created_at: string;
}

export interface EquipmentDocument {
  id: string;
  asset_id: string;
  document_type: string;
  file_name: string;
  ocr_confidence: number;
  valid_until: string;
  verification_status: string;
  created_at: string;
}

export interface EnvironmentalReading {
  id: string;
  mine_id: string;
  zone_id: string;
  sensor_code: string;
  methane_ch4_pct: number;
  carbon_monoxide_co_ppm: number;
  oxygen_o2_pct: number;
  temperature_c: number;
  humidity_pct: number;
  is_breach: boolean;
  breach_details_json: Record<string, unknown>;
  source: string;
  created_at: string;
}

export interface ProductionRecord {
  id: string;
  mine_id: string;
  shift_date: string;
  shift_type: string;
  target_tonnes: number;
  actual_tonnes: number;
  variance_pct: number;
  status: string;
}

export interface RiskScore {
  id: string;
  mine_id: string;
  zone_id: string;
  composite_score: number;
  violation_component: number;
  environment_component: number;
  production_component: number;
  equipment_component: number;
  risk_level: string;
  computed_at: string;
}

export interface Anomaly {
  id: string;
  mine_id: string;
  zone_id?: string;
  anomaly_type: string;
  description: string;
  severity: string;
  detected_at: string;
  is_acknowledged: boolean;
}

export interface Alert {
  id: string;
  mine_id: string;
  zone_id?: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  status: string;
  sla_level: number;
  sla_deadline: string;
  acknowledged_at?: string;
  created_at: string;
}

export interface CorrectiveAction {
  id: string;
  alert_id: string;
  mine_id: string;
  title: string;
  description: string;
  status: string;
  assigned_to?: string;
  due_date?: string;
  resolved_at?: string;
  created_at: string;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertSeverity = 'INFO' | 'WARNING' | 'HIGH' | 'CRITICAL' | 'EMERGENCY';
