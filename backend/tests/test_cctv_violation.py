"""
Tests for CCTV Ingestion, Confidence Threshold Gating, and Human-in-the-Loop Verification
"""

import pytest


@pytest.mark.asyncio
async def test_cctv_camera_and_detection_promotion(client, auth_headers):
    # 1. Create Mine
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-TEST-01",
        "name": "Test Opencast Mine",
        "subsidiary": "SECL",
        "state": "Chhattisgarh",
        "district": "Korba",
        "latitude": 22.31,
        "longitude": 82.68
    }, headers=auth_headers)
    assert mine_res.status_code == 200
    mine_id = mine_res.json()["data"]["id"]

    # 2. Create Zone
    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-PIT-A",
        "name": "Pit Face A",
        "zone_type": "OPEN_CAST_PIT",
        "risk_weight": 1.5
    }, headers=auth_headers)
    assert zone_res.status_code == 200
    zone_id = zone_res.json()["data"]["id"]

    # 3. Register Camera
    cam_res = await client.post("/api/v1/mine/cameras", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "camera_code": "CAM-TEST-01",
        "name": "Highwall Camera East"
    }, headers=auth_headers)
    assert cam_res.status_code == 200
    cam_id = cam_res.json()["data"]["id"]

    # 4. Ingest Detection BELOW Confidence Threshold (<0.75) -> Should NOT Promote
    low_res = await client.post("/api/v1/mine/detections/ingest", json={
        "camera_id": cam_id,
        "detection_type": "PPE_VIOLATION",
        "raw_class_name": "no_helmet",
        "confidence_score": 0.60
    })
    assert low_res.status_code == 200
    low_data = low_res.json()["data"]
    assert low_data["promoted"] is False
    assert low_data["reason"] == "BELOW_CONFIDENCE_THRESHOLD"

    # 5. Ingest Detection ABOVE Confidence Threshold (>=0.75) -> MUST Promote to CANDIDATE Violation
    high_res = await client.post("/api/v1/mine/detections/ingest", json={
        "camera_id": cam_id,
        "detection_type": "PPE_VIOLATION",
        "raw_class_name": "no_helmet_and_vest",
        "confidence_score": 0.94,
        "bounding_box_json": {"box": [0.3, 0.2, 0.5, 0.7]}
    })
    assert high_res.status_code == 200
    high_data = high_res.json()["data"]
    assert high_data["promoted"] is True
    assert "violation_id" in high_data
    violation_id = high_data["violation_id"]

    # 6. Verify Candidate Violation Exists
    v_res = await client.get(f"/api/v1/mine/violations/{violation_id}")
    assert v_res.status_code == 200
    v_data = v_res.json()["data"]
    assert v_data["status"] == "CANDIDATE"
    assert v_data["severity"] == "MEDIUM"

    # 7. Officer Human-in-the-Loop Confirmation (/verify)
    verify_res = await client.post(f"/api/v1/mine/violations/{violation_id}/verify", json={
        "decision": "CONFIRMED",
        "rule_reference": "CMR 2017 Reg 130",
        "adjusted_severity": "HIGH"
    }, headers=auth_headers)
    assert verify_res.status_code == 200
    verified_data = verify_res.json()["data"]
    assert verified_data["status"] == "CONFIRMED"
    assert verified_data["severity"] == "HIGH"
