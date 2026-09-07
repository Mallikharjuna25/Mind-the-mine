"""
Tests for Environmental Gas Telemetry and Production Output Logging
"""

import pytest


@pytest.mark.asyncio
async def test_environmental_reading_breach_detection(client, auth_headers):
    # 1. Setup Mine & Zone
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-ENV-01",
        "name": "Env Test Mine",
        "subsidiary": "BCCL",
        "state": "Jharkhand",
        "district": "Dhanbad",
        "latitude": 23.79,
        "longitude": 86.43
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-UNDERGROUND-01",
        "name": "Underground Gallery 1",
        "zone_type": "OPEN_CAST_PIT",
        "risk_weight": 2.0
    }, headers=auth_headers)
    zone_id = zone_res.json()["data"]["id"]

    # 2. Normal Reading (No breach)
    normal_res = await client.post("/api/v1/mine/environmental-readings", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "sensor_code": "LORA-NODE-01",
        "methane_ch4_pct": 0.20,
        "carbon_monoxide_co_ppm": 12.0,
        "oxygen_o2_pct": 20.8
    })
    assert normal_res.status_code == 200
    assert normal_res.json()["data"]["is_breach"] is False

    # 3. Hazardous Reading (Methane = 1.40% > 0.75%, CO = 65ppm > 50ppm)
    hazard_res = await client.post("/api/v1/mine/environmental-readings", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "sensor_code": "LORA-NODE-01",
        "methane_ch4_pct": 1.40,
        "carbon_monoxide_co_ppm": 65.0,
        "oxygen_o2_pct": 18.2
    })
    assert hazard_res.status_code == 200
    h_data = hazard_res.json()["data"]
    assert h_data["is_breach"] is True
    assert len(h_data["breach_details_json"]["breaches"]) >= 2

    # 4. Check that a Gas Alarm Alert was automatically created
    alerts_res = await client.get("/api/v1/mine/alerts", params={"mine_id": mine_id})
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()["data"]
    assert any(a["alert_type"] == "GAS_ALARM" for a in alerts)


@pytest.mark.asyncio
async def test_production_logging_and_variance(client, auth_headers):
    # Setup
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-PROD-01",
        "name": "Prod Mine",
        "subsidiary": "MCL",
        "state": "Odisha",
        "district": "Jharsuguda",
        "latitude": 21.85,
        "longitude": 84.01
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-SEAM-1",
        "name": "Main Seam Pit",
        "zone_type": "OPEN_CAST_PIT",
        "risk_weight": 1.0
    }, headers=auth_headers)
    zone_id = zone_res.json()["data"]["id"]

    # Log Production with Significant Shortfall (-40%)
    prod_res = await client.post("/api/v1/mine/production-records", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "shift_date": "2026-09-07",
        "shift_number": 1,
        "seam_name": "Seam 1",
        "target_tonnes": 5000.0,
        "actual_tonnes": 3000.0,
        "downtime_minutes": 200,
        "downtime_reason": "Shovel hydraulic failure"
    }, headers=auth_headers)
    assert prod_res.status_code == 200
    prod_data = prod_res.json()["data"]
    assert prod_data["variance_pct"] == -40.0

    # Verify Production Anomaly was flagged
    anomalies_res = await client.get("/api/v1/mine/anomalies", params={"mine_id": mine_id})
    assert anomalies_res.status_code == 200
    anomalies = anomalies_res.json()["data"]
    assert any(a["anomaly_type"] == "PRODUCTION_ANOMALY" for a in anomalies)
