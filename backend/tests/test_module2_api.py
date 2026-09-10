import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_current_user, TokenPayload
from app.core.database import sync_engine, Base

@pytest.fixture(autouse=True)
def setup_module2_test():
    Base.metadata.create_all(bind=sync_engine)
    app.dependency_overrides[get_current_user] = lambda: TokenPayload(
        sub="OFFICER-DEV-01",
        email="officer@mineguard.in",
        role="FIELD_INSPECTOR",
        permissions=["*"]
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_inspection_templates_seed(client):
    response = client.get("/api/v1/inspections/templates")
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) >= 3
    categories = [t["category"] for t in templates]
    assert "FIRE_SAFETY" in categories
    assert "ENVIRONMENTAL" in categories
    assert "MACHINERY" in categories

def test_create_field_report(client):
    payload = {
        "client_id": "test-rep-001",
        "mine_id": "MINE-DHANBAD-01",
        "zone_id": "PIT-FACE-02",
        "category": "HAZARD",
        "severity": "HIGH",
        "description": "Loose boulder observed near upper bench edge above haul road",
        "latitude": 23.7957,
        "longitude": 86.4304,
        "accuracy": 4.5,
        "evidence_urls": ["/storage/uploads/boulder_hazard.jpg"]
    }
    response = client.post("/api/v1/field-reports", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["category"] == "HAZARD"
    assert data["severity"] == "HIGH"
    assert data["status"] == "REPORTED"

def test_submit_inspection_with_compliance_score(client):
    payload = {
        "client_id": "test-audit-001",
        "template_id": "TMPL-DGMS-FIRE-01",
        "mine_id": "MINE-DHANBAD-01",
        "zone_id": "HAUL-ROAD-01",
        "shift": "SHIFT_A",
        "summary_findings": "Pre-shift fire safety inspection completed",
        "items_results": [
            {
                "item_code": "FIRE-01",
                "question": "Are portable fire extinguishers charged and within annual inspection date?",
                "result_status": "PASS",
                "observation": "Checked 5 units at sub-station, pressure green"
            },
            {
                "item_code": "FIRE-02",
                "question": "Is stone dust barrier properly maintained?",
                "result_status": "FAIL",
                "observation": "Shelf 3 damaged by dust accumulation",
                "severity": "HIGH",
                "evidence_urls": ["/storage/uploads/stone_dust_fail.jpg"],
                "incident_generated": True
            },
            {
                "item_code": "FIRE-03",
                "question": "Are emergency water spray hydrants operational?",
                "result_status": "PASS",
                "observation": "Flow pressure verified"
            }
        ]
    }
    response = client.post("/api/v1/inspections", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert data["overall_score"] == 66.7  # 2 passed out of 3 = 66.7%

def test_ai_incident_structuring(client):
    raw_voice_note = (
        "At the north haul road around 10:20, the dumper stopped suddenly and smoke was noticed "
        "near the engine compartment. No injury observed."
    )
    payload = {
        "raw_text": raw_voice_note,
        "mine_id": "MINE-DHANBAD-01"
    }
    response = client.post("/api/v1/ai/structure-incident", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["suggested_incident_type"] == "FIRE" or res["suggested_incident_type"] == "EQUIPMENT_FAILURE"
    assert res["suggested_hazard"] == "FIRE_AND_SMOKE"
    assert res["suggested_injury"] == "NONE_REPORTED"
    assert res["suggested_location"] == "HAUL_ROAD"
    assert res["confidence_score"] >= 0.75

def test_sync_engine_batch_and_idempotency(client):
    batch_payload = {
        "officer_id": "INSP-DHANBAD-05",
        "sync_timestamp": datetime.now(timezone.utc).isoformat(),
        "field_reports": [
            {
                "client_id": "sync-rep-unique-101",
                "mine_id": "MINE-DHANBAD-01",
                "zone_id": "PIT-01",
                "category": "SAFETY_OBSERVATION",
                "severity": "MEDIUM",
                "description": "Berm height along crest is below DGMS specification of 2m",
                "latitude": 23.7912,
                "longitude": 86.4250,
                "accuracy": 3.2
            }
        ],
        "inspections": [],
        "incidents": [
            {
                "client_id": "sync-inc-unique-201",
                "mine_id": "MINE-DHANBAD-01",
                "incident_type": "EQUIPMENT_FAILURE",
                "severity": "MODERATE",
                "location_name": "Haul Road Crossing B",
                "latitude": 23.7925,
                "longitude": 86.4265,
                "description": "Hydraulic hose rupture on Komatsu loader HD-785",
                "immediate_action": "Area cordoned off, spill kit deployed"
            }
        ]
    }

    # 1. First sync submission
    resp1 = client.post("/api/v1/sync/batch", json=batch_payload)
    assert resp1.status_code == 200
    res1 = resp1.json()
    assert res1["success"] is True
    assert res1["processed_count"] == 2
    assert all(r["status"] == "SYNCED" for r in res1["results"])

    # 2. Duplicate sync attempt (idempotency verification)
    resp2 = client.post("/api/v1/sync/batch", json=batch_payload)
    assert resp2.status_code == 200
    res2 = resp2.json()
    assert res2["processed_count"] == 2
    for item in res2["results"]:
        assert "idempotent ACK" in item["message"]

def test_field_verification_lifecycle(client):
    # Fetch verifications generated automatically by failed checklist or incident
    verifications = client.get("/api/v1/field-verifications?status=REPORTED").json()
    assert len(verifications) > 0
    target_id = verifications[0]["id"]
    assert verifications[0]["status"] == "REPORTED"

    # 1. Transition: REPORTED -> VERIFIED
    r1 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={"status": "VERIFIED"})
    assert r1.status_code == 200
    assert r1.json()["status"] == "VERIFIED"

    # 2. Transition: VERIFIED -> CORRECTIVE_ACTION
    r2 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={
        "status": "CORRECTIVE_ACTION",
        "remediation_notes": "Contractor assigned to rebuild shelf barrier"
    })
    assert r2.status_code == 200
    assert r2.json()["status"] == "CORRECTIVE_ACTION"

    # 3. Transition: CORRECTIVE_ACTION -> EVIDENCE_SUBMITTED
    r3 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={
        "status": "EVIDENCE_SUBMITTED",
        "after_evidence_urls": ["/storage/uploads/repaired_barrier_photo.jpg"]
    })
    assert r3.status_code == 200

    # 4. Transition: EVIDENCE_SUBMITTED -> SUPERVISOR_REVIEW
    r4 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={
        "status": "SUPERVISOR_REVIEW",
        "supervisor_notes": "Reviewing contractor photo evidence"
    })
    assert r4.status_code == 200

    # 5. Transition: SUPERVISOR_REVIEW -> APPROVED
    r5 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={"status": "APPROVED"})
    assert r5.status_code == 200

    # 6. Transition: APPROVED -> CLOSED
    r6 = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={"status": "CLOSED"})
    assert r6.status_code == 200
    assert r6.json()["status"] == "CLOSED"

    # 7. Invalid transition test: CLOSED -> VERIFIED should fail
    r_invalid = client.patch(f"/api/v1/field-verifications/{target_id}/transition", json={"status": "VERIFIED"})
    assert r_invalid.status_code == 400

def test_gis_features_handoff(client):
    response = client.get("/api/v1/gis/features")
    assert response.status_code == 200
    geo = response.json()
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) > 0
    for f in geo["features"]:
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Point"
        assert len(f["geometry"]["coordinates"]) == 2
