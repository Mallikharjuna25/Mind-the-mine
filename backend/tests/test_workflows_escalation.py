"""
Tests for Alert Acknowledgment, Corrective Action Remediation, and SLA Escalations
"""

import pytest
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_alert_acknowledgment_and_corrective_action(client, auth_headers):
    # Setup
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-WF-01",
        "name": "Workflow Mine",
        "subsidiary": "CCL",
        "state": "Jharkhand",
        "district": "Ranchi",
        "latitude": 23.34,
        "longitude": 85.30
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-WF-1",
        "name": "Haul Road North",
        "zone_type": "HAUL_ROAD",
        "risk_weight": 1.0
    }, headers=auth_headers)
    zone_id = zone_res.json()["data"]["id"]

    # Ingest breach to trigger alert
    await client.post("/api/v1/mine/environmental-readings", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "sensor_code": "SN-WF-01",
        "methane_ch4_pct": 1.50
    })

    # Fetch Alerts
    alerts_res = await client.get("/api/v1/mine/alerts", params={"mine_id": mine_id})
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()["data"]
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    # Acknowledge Alert
    ack_res = await client.post(f"/api/v1/mine/alerts/{alert_id}/acknowledge", headers=auth_headers)
    assert ack_res.status_code == 200
    assert ack_res.json()["data"]["status"] == "ACKNOWLEDGED"

    # Create Corrective Action
    deadline_iso = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    action_res = await client.post("/api/v1/mine/corrective-actions", json={
        "mine_id": mine_id,
        "title": "Install Auxiliary Methane Exhaust Fan",
        "description": "Deploy emergency ventilation fans at north gallery.",
        "priority": "CRITICAL",
        "deadline": deadline_iso
    }, headers=auth_headers)
    assert action_res.status_code == 200
    action_data = action_res.json()["data"]
    action_id = action_data["id"]
    assert action_data["status"] == "OPEN"

    # Verify and Close Action
    verify_res = await client.post(f"/api/v1/mine/corrective-actions/{action_id}/verify", json={
        "status": "CLOSED",
        "remediation_notes": "Ventilation installed and verified. Gas levels down to 0.15%."
    }, headers=auth_headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["data"]["status"] == "CLOSED"


@pytest.mark.asyncio
async def test_demo_seed_and_simulation_endpoints(client):
    # Test One-Click Demo Seeder
    seed_res = await client.post("/api/v1/demo/seed")
    assert seed_res.status_code == 200
    seed_data = seed_res.json()
    assert seed_data["success"] is True
    assert "demo_credentials" in seed_data["data"]

    # Test One-Click Simulated Violation
    vio_res = await client.post("/api/v1/demo/simulate-violation")
    assert vio_res.status_code == 200
    assert vio_res.json()["success"] is True

    # Test One-Click Simulated OCR
    ocr_res = await client.post("/api/v1/demo/simulate-ocr")
    assert ocr_res.status_code == 200
    assert ocr_res.json()["success"] is True

    # Test One-Click Simulated Gas Breach
    gas_res = await client.post("/api/v1/demo/simulate-gas-breach")
    assert gas_res.status_code == 200
    assert gas_res.json()["success"] is True
