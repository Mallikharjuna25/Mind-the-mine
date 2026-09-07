"""
Tests for Unified Risk Engine and Anomaly Detection
"""

import pytest
from app.ai.risk.risk_calculator import risk_calculator, RiskBand


def test_deterministic_risk_calculator_formula():
    # Test Base Formula: R = 0.40*V + 0.25*E + 0.15*P + 0.20*S
    score, band, subscores, factors = risk_calculator.calculate_composite_score(
        active_violations_count=2,
        critical_violations_count=1,
        high_violations_count=1,
        environmental_breaches_count=1,
        production_variance_pct=-20.0,
        overdue_equipment_count=1,
        zone_risk_weight=1.0
    )
    assert 0.0 <= score <= 100.0
    assert band in [RiskBand.LOW, RiskBand.MODERATE, RiskBand.HIGH, RiskBand.CRITICAL]
    assert "primary_driver" in factors
    assert subscores["violation_subscore"] > 0
    assert subscores["environment_subscore"] > 0


@pytest.mark.asyncio
async def test_risk_score_api_recomputation(client, auth_headers):
    # Setup Mine & Zone
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-RISK-01",
        "name": "Risk Engine Mine",
        "subsidiary": "WCL",
        "state": "Maharashtra",
        "district": "Nagpur",
        "latitude": 21.14,
        "longitude": 79.08
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-HIGH-RISK",
        "name": "High Risk Blasting Zone",
        "zone_type": "BLASTING_ZONE",
        "risk_weight": 2.0
    }, headers=auth_headers)
    zone_id = zone_res.json()["data"]["id"]

    # Trigger Risk Recomputation
    calc_res = await client.post("/api/v1/mine/risk-scores/compute", json={
        "mine_id": mine_id,
        "zone_id": zone_id
    }, headers=auth_headers)
    assert calc_res.status_code == 200
    calc_data = calc_res.json()["data"]
    assert len(calc_data) == 1
    assert "composite_score" in calc_data[0]
    assert "risk_band" in calc_data[0]

    # Fetch Latest Risk Scores
    latest_res = await client.get("/api/v1/mine/risk-scores/latest", params={"mine_id": mine_id})
    assert latest_res.status_code == 200
    assert len(latest_res.json()["data"]) >= 1
