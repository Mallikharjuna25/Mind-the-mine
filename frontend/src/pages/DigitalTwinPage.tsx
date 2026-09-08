import React, { useEffect, useRef } from 'react';
import { Card, Row, Col, Tag, Typography, Badge } from 'antd';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const { Title, Text } = Typography;

// Kusmunda coal mine coordinates
const MINE_CENTER: [number, number] = [22.3168, 82.6841];

const ZONES = [
  {
    code: 'ZONE-PIT-01',
    name: 'Active Extraction Pit (Face 4)',
    type: 'OPEN_CAST_PIT',
    color: '#ef4444',
    coords: [[22.318, 22.318, 22.315, 22.315, 22.318], [82.678, 82.688, 82.688, 82.678, 82.678]] as [number[], number[]],
    polygonCoords: [
      [22.318, 82.678], [22.318, 82.688], [22.315, 82.688], [22.315, 82.678],
    ] as [number, number][],
    risk: 'HIGH',
    riskScore: 0.71,
  },
  {
    code: 'ZONE-BLAST-02',
    name: 'Deep Blasting & Highwall Sector',
    type: 'BLASTING_ZONE',
    color: '#7c3aed',
    polygonCoords: [
      [22.313, 82.686], [22.313, 82.694], [22.31, 82.694], [22.31, 82.686],
    ] as [number, number][],
    risk: 'CRITICAL',
    riskScore: 0.88,
  },
  {
    code: 'ZONE-HAUL-03',
    name: 'Main Haul Road Corridors',
    type: 'HAUL_ROAD',
    color: '#f97316',
    polygonCoords: [
      [22.32, 82.68], [22.32, 82.692], [22.319, 82.692], [22.319, 82.68],
    ] as [number, number][],
    risk: 'MEDIUM',
    riskScore: 0.42,
  },
  {
    code: 'ZONE-CHP-04',
    name: 'Coal Handling & Crushing Plant',
    type: 'COAL_STOCKYARD',
    color: '#0ea5e9',
    polygonCoords: [
      [22.315, 82.678], [22.315, 82.683], [22.313, 82.683], [22.313, 82.678],
    ] as [number, number][],
    risk: 'MEDIUM',
    riskScore: 0.38,
  },
  {
    code: 'ZONE-WRK-05',
    name: 'HEMM Heavy Maintenance Workshop',
    type: 'WORKSHOP',
    color: '#22c55e',
    polygonCoords: [
      [22.322, 82.682], [22.322, 82.686], [22.32, 82.686], [22.32, 82.682],
    ] as [number, number][],
    risk: 'LOW',
    riskScore: 0.18,
  },
];

const CAMERAS = [
  { id: 'CAM-01', name: 'Pit Face East Highwall Cam', lat: 22.318, lng: 82.682, active: true },
  { id: 'CAM-02', name: 'Blasting Perimeter PTZ Cam', lat: 22.312, lng: 82.689, active: true },
];

const SENSORS = [
  { id: 'GAS-01', name: 'LoRa Gas Node 04', lat: 22.3165, lng: 82.685, breach: true },
  { id: 'GAS-02', name: 'LoRa Gas Node 08', lat: 22.321, lng: 82.687, breach: false },
];

const RISK_COLOR: Record<string, string> = {
  LOW: 'success', MEDIUM: 'warning', HIGH: 'error', CRITICAL: 'magenta',
};

export const DigitalTwinPage: React.FC = () => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: MINE_CENTER,
      zoom: 14,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    // Draw zone polygons
    ZONES.forEach((z) => {
      const polygon = L.polygon(z.polygonCoords, {
        color: z.color,
        fillColor: z.color,
        fillOpacity: 0.18,
        weight: 2.5,
        dashArray: z.type === 'BLASTING_ZONE' ? '6 4' : undefined,
      }).addTo(map);

      polygon.bindTooltip(
        `<div style="font-family:Inter,sans-serif;font-size:12px;">
          <strong>${z.name}</strong><br/>
          Risk: <b style="color:${z.color}">${z.risk}</b> (${(z.riskScore * 100).toFixed(0)}%)
        </div>`,
        { sticky: true },
      );
    });

    // Camera markers
    const camIcon = L.divIcon({
      html: `<div style="width:24px;height:24px;background:#18181b;border:2px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;">📷</div>`,
      iconSize: [24, 24],
      className: '',
    });

    CAMERAS.forEach((cam) => {
      L.marker([cam.lat, cam.lng], { icon: camIcon })
        .addTo(map)
        .bindPopup(`<strong>${cam.name}</strong><br/>Status: ${cam.active ? '🟢 ACTIVE' : '🔴 OFFLINE'}`);
    });

    // Gas sensor markers
    SENSORS.forEach((sensor) => {
      const gasIcon = L.divIcon({
        html: `<div style="width:22px;height:22px;background:${sensor.breach ? '#ef4444' : '#22c55e'};border:2px solid white;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;color:white;">⚗</div>`,
        iconSize: [22, 22],
        className: '',
      });
      L.marker([sensor.lat, sensor.lng], { icon: gasIcon })
        .addTo(map)
        .bindPopup(`<strong>${sensor.name}</strong><br/>Status: ${sensor.breach ? '🔴 BREACH DETECTED' : '🟢 Normal'}`);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>GIS Digital Twin — Mine Zone Heatmap</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            Kusmunda Mega Opencast Project · Interactive Live Zone Risk Overlay
          </Text>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Map */}
        <Col xs={24} lg={17}>
          <Card
            bordered
            style={{ borderRadius: 10, padding: 0, overflow: 'hidden' }}
            bodyStyle={{ padding: 0 }}
          >
            <div ref={containerRef} style={{ height: 580, width: '100%', borderRadius: 10 }} />
          </Card>
        </Col>

        {/* Legend & zone list */}
        <Col xs={24} lg={7}>
          <Card title="Zone Risk Index" bordered style={{ borderRadius: 10, marginBottom: 12 }}>
            {ZONES.map((z) => (
              <div
                key={z.code}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 0',
                  borderBottom: '1px solid #f5f5f5',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: 2,
                      background: z.color,
                      flexShrink: 0,
                    }}
                  />
                  <Text style={{ fontSize: 12 }}>{z.name}</Text>
                </div>
                <Tag color={RISK_COLOR[z.risk]} style={{ fontSize: 11 }}>
                  {(z.riskScore * 100).toFixed(0)}%
                </Tag>
              </div>
            ))}
          </Card>

          <Card title="Live Sensor Status" bordered style={{ borderRadius: 10 }}>
            {CAMERAS.map((c) => (
              <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontSize: 12 }}>
                <span>📷 {c.name}</span>
                <Badge status="success" text="Active" />
              </div>
            ))}
            {SENSORS.map((s) => (
              <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontSize: 12 }}>
                <span>⚗ {s.name}</span>
                <Badge status={s.breach ? 'error' : 'success'} text={s.breach ? 'BREACH' : 'Normal'} />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};
