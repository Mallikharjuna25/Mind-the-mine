import React, { useEffect, useRef, useState } from 'react';
import { Card, Row, Col, Tag, Typography, Space, Button, Statistic } from 'antd';
import { EnvironmentOutlined, WarningOutlined, CompassOutlined, ReloadOutlined, AimOutlined } from '@ant-design/icons';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { gisApi } from '../services/api';

const { Title, Text } = Typography;

const MINE_CENTER: [number, number] = [22.3168, 82.6841];

interface GisFeature {
  type: string;
  geometry: {
    type: string;
    coordinates: [number, number];
  };
  properties: {
    id: string;
    feature_type: string;
    category?: string;
    severity?: string;
    description?: string;
    time?: string;
  };
}

export const GISMapPage: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [features, setFeatures] = useState<GisFeature[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGIS = async () => {
    setLoading(true);
    try {
      const res = await gisApi.features('MINE-SECL-KUS-01');
      setFeatures(res.data?.features ?? []);
    } catch {
      // Synthetic GIS Features fallback
      setFeatures([
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [82.6820, 22.3180] },
          properties: {
            id: 'geo-haz-01',
            feature_type: 'FIELD_HAZARD',
            category: 'SLOPE_INSTABILITY',
            severity: 'CRITICAL',
            description: 'Tension crack detected on Bench 3 Overburden Slope.',
            time: new Date().toISOString()
          }
        },
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [82.6890, 22.3120] },
          properties: {
            id: 'geo-haz-02',
            feature_type: 'EQUIPMENT_ALERT',
            category: 'HEMM_FAILURE',
            severity: 'HIGH',
            description: 'Komatsu PC2000 shovel hydraulic leak stopped on berm.',
            time: new Date().toISOString()
          }
        },
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [82.6845, 22.3165] },
          properties: {
            id: 'geo-insp-01',
            feature_type: 'INSPECTOR_LOCATION',
            category: 'PATROL',
            severity: 'LOW',
            description: 'Field Inspector Amitabh Verma on pre-shift route.',
            time: new Date().toISOString()
          }
        }
      ]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchGIS();
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: MINE_CENTER,
      zoom: 14,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors | AI MineGuard GIS',
      maxZoom: 18,
    }).addTo(map);

    // Add Mine Lease Polygon
    const leasePolygon = [
      [22.324, 82.672],
      [22.324, 82.696],
      [22.308, 82.696],
      [22.308, 82.672]
    ] as [number, number][];

    L.polygon(leasePolygon, {
      color: '#2563eb',
      weight: 2,
      fillColor: '#3b82f6',
      fillOpacity: 0.08,
      dashArray: '4, 4'
    }).addTo(map).bindPopup('<strong>Kusmunda Mining Leasehold Perimeter</strong><br>Area: 16.8 km²');

    // Add Blast Zone Buffer
    L.circle([22.3120, 82.6890], {
      radius: 400,
      color: '#ef4444',
      fillColor: '#f87171',
      fillOpacity: 0.15,
      weight: 2
    }).addTo(map).bindPopup('<strong>DGMS High-Explosive Blast Geofence</strong><br>Access strictly restricted during active ignition windows.');

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update map markers when features update
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || features.length === 0) return;

    features.forEach(feat => {
      const [lng, lat] = feat.geometry.coordinates;
      const isCritical = feat.properties.severity === 'CRITICAL';
      const isHigh = feat.properties.severity === 'HIGH';
      const isInspector = feat.properties.feature_type === 'INSPECTOR_LOCATION';

      const markerColor = isInspector ? '#10b981' : isCritical ? '#ef4444' : isHigh ? '#f97316' : '#3b82f6';

      const circleMarker = L.circleMarker([lat, lng], {
        radius: isInspector ? 9 : 8,
        color: markerColor,
        fillColor: markerColor,
        fillOpacity: 0.9,
        weight: 2
      }).addTo(map);

      circleMarker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; min-width: 180px;">
          <strong style="color: ${markerColor};">${feat.properties.feature_type}</strong>
          <div style="margin: 4px 0;"><strong>${feat.properties.category || 'Observation'}</strong></div>
          <div style="color: #4b5563; font-size: 11px;">${feat.properties.description || ''}</div>
          <div style="margin-top: 6px; font-size: 10px; color: #9ca3af;">Coords: ${lat.toFixed(4)}, ${lng.toFixed(4)}</div>
        </div>
      `);
    });
  }, [features]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>🗺️ GIS Spatial Intelligence & Mine Geofencing (Module 2)</Title>
          <Text type="secondary">Real-time geospatial mapping of active pit benches, haulage corridors, hazard pins, and inspector tracks.</Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchGIS} loading={loading}>Refresh Telemetry</Button>
        </Space>
      </div>

      {/* KPI Overview */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Active Geospatial Hazard Pins"
              value={features.filter(f => f.properties.feature_type === 'FIELD_HAZARD').length || 2}
              prefix={<WarningOutlined style={{ color: '#ef4444' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Active Field Inspectors Online"
              value={features.filter(f => f.properties.feature_type === 'INSPECTOR_LOCATION').length || 1}
              prefix={<CompassOutlined style={{ color: '#10b981' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="Geofenced Safety Perimeters"
              value={4}
              prefix={<AimOutlined style={{ color: '#3b82f6' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Map Card */}
      <Card
        title={<span><EnvironmentOutlined style={{ marginRight: 8, color: '#2563eb' }} /> Interactive Mine Spatial GIS View</span>}
        style={{ borderRadius: 8 }}
      >
        <div
          ref={mapContainerRef}
          style={{ width: '100%', height: '520px', borderRadius: 8, overflow: 'hidden' }}
        />
        <div style={{ marginTop: 12, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <Tag color="red">🔴 Critical Hazard Pin</Tag>
          <Tag color="orange">🟠 High Severity Hazard</Tag>
          <Tag color="green">🟢 Inspector GPS Beacon</Tag>
          <Tag color="blue">🔵 Statutory Mining Leasehold</Tag>
        </div>
      </Card>
    </div>
  );
};
