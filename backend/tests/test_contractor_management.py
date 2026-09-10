"""
Contractor Management Integration Tests (Module 3 -> Task 1)
Validates Contractor CRUD, Contracts, Compliance, Performance, Document Uploads & Renewals.
"""

import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_contractor_lifecycle(client, auth_headers):
    # 1. Create Mine first for FK
    mine_payload = {
        "name": "Singareni Collieries Pit-03",
        "mine_code": "SCCL-PIT-03",
        "subsidiary": "SCCL",
        "state": "Telangana",
        "district": "Bhadradri Kothagudem",
        "latitude": 17.55,
        "longitude": 80.62,
        "mine_type": "UNDERGROUND",
        "max_capacity_tonnes": 50000.0
    }
    mine_resp = await client.post("/api/v1/mine/mines", json=mine_payload, headers=auth_headers)
    assert mine_resp.status_code == 200
    mine_id = mine_resp.json()["data"]["id"]

    # 2. Register Contractor
    contractor_payload = {
        "mine_id": mine_id,
        "company_name": "Bharat Mining Excavators Pvt Ltd",
        "registration_number": "REG-BME-2026-001",
        "contact_person": "Rajesh Sharma",
        "email": "rajesh@bmecontractors.com",
        "phone": "+91 98765 43210",
        "address": "Godavarikhani Industrial Area, Telangana",
        "work_scope": "EXCAVATION",
        "status": "ACTIVE"
    }
    create_resp = await client.post("/api/v1/mine/contractors", json=contractor_payload, headers=auth_headers)
    assert create_resp.status_code == 200
    contractor_data = create_resp.json()["data"]
    contractor_id = contractor_data["id"]
    assert contractor_data["company_name"] == "Bharat Mining Excavators Pvt Ltd"
    assert contractor_data["compliance_score"] == 100.0
    assert contractor_data["performance_score"] == 5.0

    # 3. Add Contract
    today = date.today()
    contract_payload = {
        "mine_id": mine_id,
        "contract_number": "CON-2026-EXC-09",
        "title": "Seam 4 Excavation & Haulage Operations",
        "contract_type": "O&M",
        "start_date": str(today),
        "end_date": str(today + timedelta(days=20)),  # Expiring soon
        "contract_value": 4500000.0,
        "status": "ACTIVE"
    }
    contract_resp = await client.post(f"/api/v1/mine/contractors/{contractor_id}/contracts", json=contract_payload, headers=auth_headers)
    assert contract_resp.status_code == 200
    contract_data = contract_resp.json()["data"]
    contract_id = contract_data["id"]

    # 4. List Expiring Contracts (Triggers alert and status transition)
    exp_resp = await client.get(f"/api/v1/mine/contracts/expiring?mine_id={mine_id}&days=30", headers=auth_headers)
    assert exp_resp.status_code == 200
    exp_contracts = exp_resp.json()["data"]
    assert len(exp_contracts) >= 1
    assert exp_contracts[0]["status"] == "EXPIRING_SOON"

    # 5. Renew Contract
    renew_payload = {
        "new_end_date": str(today + timedelta(days=365)),
        "revised_value": 5000000.0,
        "remarks": "Annual contract extension approved based on high performance"
    }
    renew_resp = await client.post(f"/api/v1/mine/contracts/{contract_id}/renew", json=renew_payload, headers=auth_headers)
    assert renew_resp.status_code == 200
    renewed_data = renew_resp.json()["data"]
    assert renewed_data["status"] == "RENEWED"
    assert renewed_data["renewal_count"] == 1
    assert renewed_data["contract_value"] == 5000000.0

    # 6. Record Compliance Check (Non-Compliant deduction)
    comp_payload = {
        "compliance_item": "DGMS Vocational Training Certificate Audit",
        "category": "STATUTORY",
        "status": "NON_COMPLIANT",
        "score_deduction": 20.0,
        "remarks": "2 equipment operators missing updated VTC cards"
    }
    comp_resp = await client.post(f"/api/v1/mine/contractors/{contractor_id}/compliance", json=comp_payload, headers=auth_headers)
    assert comp_resp.status_code == 200

    # Verify score recalculated
    detail_resp = await client.get(f"/api/v1/mine/contractors/{contractor_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()["data"]
    assert detail_data["compliance_score"] == 80.0
    assert detail_data["compliance_status"] == "WARNING"

    # 7. Record Performance Evaluation
    perf_payload = {
        "contract_id": contract_id,
        "rating": 4.5,
        "period": "2026-Q1",
        "evaluated_by": "Safety Officer Ramesh",
        "sla_adherence_percent": 95.0,
        "safety_incident_count": 0,
        "remarks": "Exceeded daily tonnage targets with zero LTI"
    }
    perf_resp = await client.post(f"/api/v1/mine/contractors/{contractor_id}/performance", json=perf_payload, headers=auth_headers)
    assert perf_resp.status_code == 200

    # 8. Dashboard Statistics
    dash_resp = await client.get(f"/api/v1/mine/contractors/dashboard?mine_id={mine_id}", headers=auth_headers)
    assert dash_resp.status_code == 200
    dash_stats = dash_resp.json()["data"]
    assert dash_stats["total_contractors"] == 1
    assert dash_stats["total_active_contracts"] == 1
    assert dash_stats["average_compliance_score"] == 80.0
