/**
 * PRAHARI-NET System Constants and TypeScript Definitions
 * Smart India Hackathon 2026 - Problem Statement SIH26178
 */

export type HazardType = 'FLOOD' | 'FIRE' | 'LANDSLIDE';

export type RiskBand = 'NORMAL' | 'WATCH' | 'WARNING' | 'CRITICAL';

export type AlertState = 'NEW' | 'ACKNOWLEDGED' | 'MONITORING' | 'RESOLVED';

export type NodeStatus = 'ONLINE' | 'DEGRADED' | 'MAINTENANCE' | 'OFFLINE';

export type NetworkMode = 'ONLINE' | 'LOCAL_EDGE' | 'DISCONNECTED';

export type ModelSource = 'RULE_FUSION' | 'ANOMALY_MODEL' | 'SUPERVISED_MODEL' | 'SIMULATION';

export interface BaseNodeTelemetry {
  version: number;
  node_id: 'JALA-01' | 'AGNI-02' | 'BHUMI-03';
  sequence: number;
  timestamp: string;
  rssi: number;
  battery_pct: number;
}

export interface JalaTelemetryMetrics {
  water_level_cm: number;
  water_distance_cm: number;
  water_rise_rate_cm_min: number;
  water_rise_acceleration: number;
  rain_intensity: number;
  temperature_c: number;
  humidity_pct: number;
  solar_voltage: number;
  signal_rssi: number;
  packet_loss: number;
  uptime: number;
}

export interface AgniTelemetryMetrics {
  mq2_raw: number;
  mq135_raw: number;
  smoke_index: number;
  gas_index: number;
  temperature_c: number;
  humidity_pct: number;
  flame_detected: boolean;
  camera_fire_confidence: number;
  camera_smoke_confidence: number;
  signal_rssi: number;
  packet_loss: number;
  uptime: number;
}

export interface BhumiTelemetryMetrics {
  soil_moisture_upper_pct: number;
  soil_moisture_lower_pct: number;
  tilt_x_deg: number;
  tilt_y_deg: number;
  tilt_delta_deg: number;
  vibration_level: number;
  vibration_rms: number;
  rain_context: number;
  temperature_c: number;
  signal_rssi: number;
  packet_loss: number;
  uptime: number;
}

export interface RiskAssessment {
  id: string;
  node_id: string;
  timestamp: string;
  risk_score: number; // 0 - 100
  risk_band: RiskBand;
  confidence: number; // 0 - 100
  anomaly_score: number; // 0.0 - 1.0
  sensor_trust: Record<string, number>; // e.g. { water_sensor: 95, rain_sensor: 92 }
  contributing_factors: Array<{ factor: string; weight: number; value: number | string }>;
  explanation: {
    human_readable: string;
    machine_readable: Record<string, any>;
  };
  recommended_action: string;
  model_source: ModelSource;
  estimated_crossing_time?: string | null;
  risk_trend?: 'STABLE' | 'RISING' | 'RAPIDLY_RISING' | 'FALLING';
}

export interface AlertItem {
  id: string;
  severity: RiskBand;
  hazard: HazardType;
  node_id: string;
  location_name: string;
  created_at: string;
  acknowledged_at?: string | null;
  acknowledged_by?: string | null;
  resolved_at?: string | null;
  resolved_by?: string | null;
  state: AlertState;
  confidence: number;
  risk_score: number;
  headline: string;
  summary: string;
  action_recommended: string;
  evidence: Record<string, any>;
}
