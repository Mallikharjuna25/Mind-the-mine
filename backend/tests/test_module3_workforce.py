"""
Comprehensive Integration & Verification Tests for Module 3: Workforce Governance
Tests:
1. RFID Pass Lifecycle & Duplicate UID Rejection
2. OCR Deterministic Parsing, Gating Threshold (0.85) & Human-in-the-loop Sign-off
3. Deterministic Zone Access Clearance Engine (DGMS, Medical, Blasting rules)
4. Grievance Resolution & Cryptographic SHA-256 Audit Trail
5. Expiry & Compliance Monitoring Scheduler Jobs
"""

import pytest
from datetime import date, timedelta
import io

from app.ai.ocr.workforce_document_parsers import WorkforceDocumentParser
from app.ai.ocr.ocr_validator import OCRValidator


@pytest.mark.asyncio
async def test_rfid_pass_lifecycle_and_duplicate_rejection(client, auth_headers):
    # 1. Create a Mine
    mine_res = await client.post("/api/v1/mine/mines", json={
        "name": "Kusmunda Deep OpenCast",
        "mine_code": "KUS-M3-TEST",
        "subsidiary": "SECL",
        "state": "Chhattisgarh",
        "district": "Korba",
        "latitude": 22.3,
        "longitude": 82.6,
        "mine_type": "OPENCAST",
        "max_capacity_tonnes": 50000.0
    }, headers=auth_headers)
    assert mine_res.status_code == 200
    mine_id = mine_res.json()["data"]["id"]

    # 2. Create Worker 1 and Worker 2
    w1_res = await client.post("/api/v1/mine/workers", json={
        "mine_id": mine_id,
        "employee_id": "EMP-M3-001",
        "full_name": "Kishan Lal",
        "department": "BLASTING",
        "role": "DRILLER",
        "phone": "+91 99999 11111",
        "emergency_contact_name": "Devi",
        "emergency_contact_phone": "+91 99999 22222",
        "joining_date": str(date.today()),
        "status": "ACTIVE"
    }, headers=auth_headers)
    assert w1_res.status_code == 200
    w1_id = w1_res.json()["data"]["id"]

    w2_res = await client.post("/api/v1/mine/workers", json={
        "mine_id": mine_id,
        "employee_id": "EMP-M3-002",
        "full_name": "Mohan Lal",
        "department": "HAULAGE",
        "role": "DRIVER",
        "phone": "+91 99999 33333",
        "emergency_contact_name": "Gita",
        "emergency_contact_phone": "+91 99999 44444",
        "joining_date": str(date.today()),
        "status": "ACTIVE"
    }, headers=auth_headers)
    assert w2_res.status_code == 200
    w2_id = w2_res.json()["data"]["id"]

    # 3. Issue RFID Pass to Worker 1
    pass_res = await client.post(f"/api/v1/mine/workers/{w1_id}/passes", json={
        "rfid_uid": "RFID-M3-DUAL-CHECK",
        "pass_number": "PASS-KUS-101",
        "access_level": "LEVEL_2_OPERATIONAL",
        "permitted_zones": ["ZONE-PIT-01", "ZONE-HAUL-02"]
    }, headers=auth_headers)
    assert pass_res.status_code == 200
    pass_data = pass_res.json()["data"]
    pass_id = pass_data["id"]
    assert pass_data["status"] == "ACTIVE"
    assert pass_data["rfid_uid"] == "RFID-M3-DUAL-CHECK"

    # 4. Attempt to issue the SAME rfid_uid to Worker 2 -> Expect 409 Conflict
    dup_res = await client.post(f"/api/v1/mine/workers/{w2_id}/passes", json={
        "rfid_uid": "RFID-M3-DUAL-CHECK",
        "pass_number": "PASS-KUS-102",
        "access_level": "LEVEL_1_GENERAL",
        "permitted_zones": ["ZONE-PIT-01"]
    }, headers=auth_headers)
    assert dup_res.status_code == 409
    assert "Already assigned to active worker pass" in dup_res.json()["error"]["message"]

    # 5. Suspend Pass for Worker 1
    action_res = await client.put(f"/api/v1/mine/workers/passes/{pass_id}/action", json={
        "action": "SUSPEND",
        "revocation_reason": "Safety audit pending investigation"
    }, headers=auth_headers)
    assert action_res.status_code == 200
    assert action_res.json()["data"]["status"] == "SUSPENDED"

    # 6. Revoke Pass
    revoke_res = await client.put(f"/api/v1/mine/workers/passes/{pass_id}/action", json={
        "action": "REVOKE",
        "revocation_reason": "Contractor term ended"
    }, headers=auth_headers)
    assert revoke_res.status_code == 200
    assert revoke_res.json()["data"]["status"] == "REVOKED"


@pytest.mark.asyncio
async def test_ocr_parser_and_deterministic_validation():
    # 1. Test DGMS Medical Fitness Form O/P Parser
    form_p_text = """
    DIRECTORATE GENERAL OF MINES SAFETY (DGMS)
    FORM P - CERTIFICATE OF MEDICAL FITNESS
    [Under Rule 29B of Mines Rules, 1955]
    Report No: DGMS/MED/2026/8941
    Worker Name: Ramesh Kumar
    Examined Date: 2026-01-20
    Valid Until: 2027-01-19
    Doctor Name: Dr. S. K. Mukherjee, CMO SECL
    Registration No: MCI-54321
    Clinical Conclusion: The candidate is examined and found FIT FOR MINING DUTIES.
    """
    extracted, confidences, overall = WorkforceDocumentParser.parse_medical_fitness(form_p_text)
    assert extracted.get("medical_fitness_status") == "FIT"
    assert "Dr. S. K. Mukherjee" in str(extracted.get("examining_doctor"))
    assert overall >= 0.85

    # 2. Validation Gate Check (High Confidence Pass)
    is_valid, status, errors = OCRValidator.validate_extracted_data(
        document_type="FITNESS_CERTIFICATE_FORM_O_P",
        extracted_data=extracted,
        overall_confidence=overall,
        expected_worker_name="Ramesh Kumar"
    )
    assert is_valid is True
    assert status == "AUTO_ACCEPTED"
    assert len(errors) == 0

    # 3. Test Mismatch Name -> Flags Error
    is_valid_mismatch, status_mismatch, errors_mismatch = OCRValidator.validate_extracted_data(
        document_type="FITNESS_CERTIFICATE_FORM_O_P",
        extracted_data=extracted,
        overall_confidence=overall,
        expected_worker_name="Suresh Verma"
    )
    assert is_valid_mismatch is False
    assert len(errors_mismatch) > 0
    assert any("Worker name mismatch" in e for e in errors_mismatch)

    # 4. Test Low Confidence Gating (< 0.85 requires human review)
    extracted_unclear, _, overall_unclear = WorkforceDocumentParser.parse_medical_fitness("DGMS blurry scan")
    is_valid_unclear, status_unclear, errors_unclear = OCRValidator.validate_extracted_data(
        document_type="FITNESS_CERTIFICATE_FORM_O_P",
        extracted_data=extracted_unclear,
        overall_confidence=overall_unclear,
        expected_worker_name="Ramesh Kumar"
    )
    assert is_valid_unclear is False
    assert status_unclear == "NEEDS_REVIEW"


@pytest.mark.asyncio
async def test_worker_document_upload_and_review_workflow(client, auth_headers):
    # 1. Create Mine & Worker
    mine_res = await client.post("/api/v1/mine/mines", json={
        "name": "Gevra Mega Pit",
        "mine_code": "GEV-M3-TEST",
        "subsidiary": "SECL",
        "state": "Chhattisgarh",
        "district": "Korba",
        "latitude": 22.3,
        "longitude": 82.5,
        "mine_type": "OPENCAST",
        "max_capacity_tonnes": 80000.0
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    w_res = await client.post("/api/v1/mine/workers", json={
        "mine_id": mine_id,
        "employee_id": "EMP-GEV-101",
        "full_name": "Arun Prasad",
        "department": "ELECTRICAL",
        "role": "ELECTRICIAN",
        "phone": "+91 94000 11111",
        "emergency_contact_name": "Kamla",
        "emergency_contact_phone": "+91 94000 22222",
        "joining_date": str(date.today()),
        "status": "ACTIVE"
    }, headers=auth_headers)
    worker_id = w_res.json()["data"]["id"]

    # 2. Upload Document via Multipart
    fake_file_content = b"DIRECTORATE GENERAL OF MINES SAFETY FORM P MEDICAL FITNESS FIT Examined Date: 2026-01-10 Valid Until: 2027-01-10 Doctor: Dr. Roy"
    files = {"file": ("form_p.txt", io.BytesIO(fake_file_content), "text/plain")}
    data = {"document_type": "FITNESS_CERTIFICATE_FORM_O_P"}

    upload_res = await client.post(
        f"/api/v1/mine/workers/{worker_id}/documents",
        files=files,
        data=data,
        headers=auth_headers
    )
    assert upload_res.status_code == 200
    doc_data = upload_res.json()["data"]
    doc_id = doc_data["id"]
    assert doc_data["document_type"] == "FITNESS_CERTIFICATE_FORM_O_P"

    # 3. Authorized Human Review (Safety Officer Approves after verification)
    review_res = await client.put(
        f"/api/v1/mine/workers/documents/{doc_id}/review",
        json={
            "decision": "APPROVE",
            "corrected_data": {
                "document_number": "DGMS-MED-2026-9912",
                "issue_date": "2026-01-10",
                "expiry_date": "2027-01-10",
                "remarks": "Verified physical stamp and signature against DGMS register."
            }
        },
        headers=auth_headers
    )
    assert review_res.status_code == 200
    assert review_res.json()["data"]["verification_status"] == "VERIFIED"


@pytest.mark.asyncio
async def test_deterministic_zone_clearance_engine(client, auth_headers):
    # 1. Create Mine & Worker
    mine_res = await client.post("/api/v1/mine/mines", json={
        "name": "Dipka Deep Pit",
        "mine_code": "DIP-M3-TEST",
        "subsidiary": "SECL",
        "state": "Chhattisgarh",
        "district": "Korba",
        "latitude": 22.3,
        "longitude": 82.5,
        "mine_type": "OPENCAST",
        "max_capacity_tonnes": 70000.0
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    w_res = await client.post("/api/v1/mine/workers", json={
        "mine_id": mine_id,
        "employee_id": "EMP-DIP-501",
        "full_name": "Santosh Yadav",
        "department": "MINING",
        "role": "BLASTER",
        "phone": "+91 93000 11111",
        "emergency_contact_name": "Maya",
        "emergency_contact_phone": "+91 93000 22222",
        "joining_date": str(date.today()),
        "status": "ACTIVE"
    }, headers=auth_headers)
    worker_id = w_res.json()["data"]["id"]

    # 2. Check Clearance for High-Risk Blasting Zone without Pass -> Expect BLOCKED
    clearance_res = await client.get(
        f"/api/v1/mine/workers/{worker_id}/zone-clearance?zone_id=ZONE-PIT-BLAST-01",
        headers=auth_headers
    )
    assert clearance_res.status_code == 200
    clearance = clearance_res.json()["data"]
    assert clearance["is_access_eligible"] is False
    assert clearance["clearance_status"] == "BLOCKED"
    assert len(clearance["blocking_reasons"]) > 0

    # 3. Issue Level 3 RFID Pass with Blasting Zone permission
    await client.post(f"/api/v1/mine/workers/{worker_id}/passes", json={
        "rfid_uid": "RFID-BLAST-9999",
        "pass_number": "PASS-DIP-9999",
        "access_level": "BLASTING_ZONE",
        "permitted_zones": ["ZONE-PIT-BLAST-01", "ZONE-PIT-01"]
    }, headers=auth_headers)

    # 4. Add DGMS Safety Induction
    ind_res = await client.post(f"/api/v1/mine/workers/{worker_id}/inductions", json={
        "induction_type": "DGMS_INITIAL",
        "training_title": "DGMS Mines Vocational Training (MVR 1966) Rule 28",
        "trainer_name": "DGMS VTC Superintendent Sharma",
        "training_date": str(date.today() - timedelta(days=10)),
        "validity_months": 12,
        "score_percent": 95.0,
        "remarks": "Passed highwall blasting and gas safety protocols."
    }, headers=auth_headers)
    assert ind_res.status_code == 200

    # 5. Check Clearance Again -> Now GRANTED
    clearance_res2 = await client.get(
        f"/api/v1/mine/workers/{worker_id}/zone-clearance?zone_id=ZONE-PIT-BLAST-01",
        headers=auth_headers
    )
    assert clearance_res2.status_code == 200
    clearance2 = clearance_res2.json()["data"]
    assert clearance2["is_access_eligible"] is True
    assert clearance2["clearance_status"] == "CLEARED"
    assert clearance2["checks"]["active_rfid_pass"] is True
    assert clearance2["checks"]["induction_valid"] is True


@pytest.mark.asyncio
async def test_grievance_workflow_and_cryptographic_audit_trail(client, auth_headers):
    # 1. Create Mine
    mine_res = await client.post("/api/v1/mine/mines", json={
        "name": "Manikpur OpenCast",
        "mine_code": "MNK-M3-TEST",
        "subsidiary": "SECL",
        "state": "Chhattisgarh",
        "district": "Korba",
        "latitude": 22.3,
        "longitude": 82.6,
        "mine_type": "OPENCAST",
        "max_capacity_tonnes": 40000.0
    }, headers=auth_headers)
    mine_id = mine_res.json()["data"]["id"]

    # 2. File a Safety Grievance
    g_res = await client.post("/api/v1/mine/governance/grievances", json={
        "mine_id": mine_id,
        "complainant_name": "Santosh Yadav",
        "complainant_contact": "+91 98888 00000",
        "category": "SAFETY_HAZARD",
        "title": "Loose boulder overhang near bench 4 haul road",
        "description": "Risk of boulder rolling onto dumper trucks during heavy rain",
        "priority": "HIGH"
    }, headers=auth_headers)
    assert g_res.status_code == 200
    grievance_id = g_res.json()["data"]["id"]

    # 3. Resolve Grievance
    resolve_res = await client.post(f"/api/v1/mine/governance/grievances/{grievance_id}/resolve", json={
        "resolution_action": "REPAIRED",
        "resolution_notes": "Blasting supervisor dislodged boulder using controlled water jet and hydraulic hammer."
    }, headers=auth_headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["data"]["status"] == "RESOLVED"

    # 4. Trigger Expiry & SLA Escalation Evaluator
    eval_res = await client.post("/api/v1/mine/governance/evaluate-expiries", headers=auth_headers)
    assert eval_res.status_code == 200
    assert "expiring_passes" in eval_res.json()["data"]

    # 5. Verify Cryptographic SHA-256 Audit Trail
    audit_res = await client.get(f"/api/v1/mine/governance/audit-trail?mine_id={mine_id}&limit=10", headers=auth_headers)
    assert audit_res.status_code == 200
    audit_entries = audit_res.json()["data"]
    assert len(audit_entries) > 0

    # Ensure hash chaining is present
    latest_entry = audit_entries[0]
    assert "current_hash" in latest_entry
    assert len(latest_entry["current_hash"]) == 64  # SHA-256 hex string length
