"""
Tests for Equipment Asset Management and Automated Certificate OCR Extraction
"""

import os
import pytest
from app.ai.synthetic_generator import generate_synthetic_dgms_certificate


@pytest.mark.asyncio
async def test_equipment_asset_creation_and_ocr_pipeline(client, auth_headers):
    # 1. Create Mine and Zone
    mine_res = await client.post("/api/v1/mine/mines", json={
        "mine_code": "MINE-TEST-EQ",
        "name": "Test Mine EQ",
        "subsidiary": "ECL",
        "state": "West Bengal",
        "district": "Asansol",
        "latitude": 23.68,
        "longitude": 86.97
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    zone_res = await client.post(f"/api/v1/mine/mines/{mine_id}/zones", json={
        "zone_code": "ZONE-WRK-01",
        "name": "Workshop Zone",
        "zone_type": "WORKSHOP",
        "risk_weight": 1.0
    }, headers=auth_headers)
    zone_id = zone_res.json()["data"]["id"]

    # 2. Register Equipment Asset
    asset_res = await client.post("/api/v1/mine/equipment", json={
        "mine_id": mine_id,
        "zone_id": zone_id,
        "asset_code": "HEMM-DUMP-099",
        "name": "Heavy Dump Truck 99",
        "category": "DUMPER",
        "serial_number": "SN-CAT-DUMP-099",
        "make_model": "Caterpillar 777E",
        "working_condition": "OPERATIONAL"
    }, headers=auth_headers)
    assert asset_res.status_code == 200
    asset_data = asset_res.json()["data"]
    asset_id = asset_data["id"]
    assert "qr_code_data" in asset_data

    # 3. Generate Synthetic DGMS Certificate
    cert_path = generate_synthetic_dgms_certificate(
        output_filename="test_dgms_cert.png",
        cert_number="DGMS/EZ/HEMM/2026/099",
        asset_code="HEMM-DUMP-099",
        make_model="Caterpillar 777E",
        issue_date="2026-01-15",
        expiry_date="2027-01-14",
        status_text="FIT FOR HAULAGE"
    )

    # 4. Upload Certificate & Trigger OCR
    with open(cert_path, "rb") as f:
        upload_res = await client.post(
            f"/api/v1/mine/equipment/{asset_id}/documents",
            data={"document_type": "DGMS_FITNESS_CERTIFICATE"},
            files={"file": ("test_dgms_cert.png", f, "image/png")},
            headers=auth_headers
        )
    assert upload_res.status_code == 200
    doc_data = upload_res.json()["data"]
    assert doc_data["ocr_confidence"] >= 0.70
    assert doc_data["verification_status"] == "VERIFIED"
    assert doc_data["valid_until"] == "2027-01-14"

    # 5. Verify Asset Expiry Date was automatically updated
    updated_asset_res = await client.get("/api/v1/mine/equipment", params={"mine_id": mine_id})
    assert updated_asset_res.status_code == 200
    assets = updated_asset_res.json()["data"]
    target_asset = next(a for a in assets if a["id"] == asset_id)
    assert target_asset["fitness_expiry_date"] == "2027-01-14"
