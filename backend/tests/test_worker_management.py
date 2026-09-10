"""
Worker & Compliance Management Integration Tests (Module 3 -> Task 2)
Validates Worker CRUD, Attendance, Training, Certifications, PPE, Work Authorization & Reports.
"""

import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_worker_lifecycle(client, auth_headers):
    # 1. Create Mine
    mine_payload = {
        "name": "Singareni Collieries Pit-05",
        "mine_code": "SCCL-PIT-05",
        "subsidiary": "SCCL",
        "state": "Telangana",
        "district": "Bhadradri Kothagudem",
        "latitude": 17.56,
        "longitude": 80.63,
        "mine_type": "UNDERGROUND",
        "max_capacity_tonnes": 60000.0
    }
    mine_resp = await client.post("/api/v1/mine/mines", json=mine_payload, headers=auth_headers)
    assert mine_resp.status_code == 200
    mine_id = mine_resp.json()["data"]["id"]

    # 2. Add Worker
    today = date.today()
    worker_payload = {
        "mine_id": mine_id,
        "employee_id": "EMP-2026-9901",
        "full_name": "Ramesh Kumar",
        "department": "UNDERGROUND_OPS",
        "role": "HEAVY_EQUIPMENT_OPERATOR",
        "email": "ramesh@mineguard.in",
        "phone": "+91 91234 56789",
        "emergency_contact_name": "Sita Devi",
        "emergency_contact_phone": "+91 98765 12345",
        "joining_date": str(today - timedelta(days=180)),
        "status": "ACTIVE"
    }
    create_resp = await client.post("/api/v1/mine/workers", json=worker_payload, headers=auth_headers)
    assert create_resp.status_code == 200
    worker_data = create_resp.json()["data"]
    worker_id = worker_data["id"]
    assert worker_data["full_name"] == "Ramesh Kumar"
    assert worker_data["employee_id"] == "EMP-2026-9901"

    # 3. Mark Attendance
    att_payload = {
        "shift": "MORNING",
        "status": "PRESENT"
    }
    att_resp = await client.post(f"/api/v1/mine/workers/{worker_id}/attendance", json=att_payload, headers=auth_headers)
    assert att_resp.status_code == 200

    # 4. Assign Training
    tr_payload = {
        "program_name": "DGMS Statutory Underground Gas & Helmet Safety",
        "trainer_name": "Safety Inspector Subba Rao",
        "completed_date": str(today - timedelta(days=30)),
        "expiry_date": str(today + timedelta(days=335)),
        "status": "COMPLETED"
    }
    tr_resp = await client.post(f"/api/v1/mine/workers/{worker_id}/trainings", json=tr_payload, headers=auth_headers)
    assert tr_resp.status_code == 200

    # 5. Register Certification
    cert_payload = {
        "certificate_name": "DGMS HEMM Operator Fitness Certification",
        "certificate_number": "DGMS-HEMM-2026-881",
        "issuing_authority": "Directorate General of Mines Safety",
        "valid_from": str(today - timedelta(days=100)),
        "expiry_date": str(today + timedelta(days=265)),
        "verification_status": "VERIFIED"
    }
    cert_resp = await client.post(f"/api/v1/mine/workers/{worker_id}/certifications", json=cert_payload, headers=auth_headers)
    assert cert_resp.status_code == 200

    # 6. Assign PPE Item
    ppe_payload = {
        "item_type": "HELMET",
        "issuance_date": str(today - timedelta(days=60)),
        "expiry_date": str(today + timedelta(days=300)),
        "compliance_status": "COMPLIANT",
        "remarks": "Standard IS-2925 Coal Mine Hard Hat issued"
    }
    ppe_resp = await client.post(f"/api/v1/mine/workers/{worker_id}/ppe", json=ppe_payload, headers=auth_headers)
    assert ppe_resp.status_code == 200

    # 7. Grant Work Authorization Permit
    auth_payload = {
        "zone_id": "ZONE-UNDERGROUND-PITFACE-04",
        "permit_type": "UNDERGROUND_ENTRY",
        "grant_date": str(today),
        "expiry_date": str(today + timedelta(days=90)),
        "granted_by": "Mine Manager General Office",
        "status": "GRANTED"
    }
    grant_resp = await client.post(f"/api/v1/mine/workers/{worker_id}/authorizations", json=auth_payload, headers=auth_headers)
    assert grant_resp.status_code == 200
    auth_data = grant_resp.json()["data"]
    auth_id = auth_data["id"]

    # 8. Revoke Work Authorization Permit (Triggers CRITICAL Alert)
    revoke_resp = await client.post(f"/api/v1/mine/workers/authorizations/{auth_id}/revoke", headers=auth_headers)
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["data"]["status"] == "REVOKED"

    # 9. Test Worker Dashboard Statistics
    dash_resp = await client.get(f"/api/v1/mine/workers/dashboard?mine_id={mine_id}", headers=auth_headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()["data"]
    assert dash_data["total_workers"] == 1
    assert dash_data["active_workers"] == 1

    # 10. Test Worker Reports Summary
    rep_resp = await client.get(f"/api/v1/mine/workers/reports/summary?mine_id={mine_id}", headers=auth_headers)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()["data"]
    assert rep_data["present_today_count"] == 1
    assert rep_data["revoked_permits_count"] == 1
