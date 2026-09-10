import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_governance_dashboard(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/mine/governance/dashboard?mine_id=test-mine-id", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_grievances" in data["data"]

async def test_create_grievance(client: AsyncClient, token_headers: dict):
    payload = {
        "mine_id": "test-mine-id",
        "complainant_name": "John Doe",
        "complainant_contact": "john.doe@example.com",
        "category": "SAFETY",
        "title": "Unsafe Working Conditions",
        "description": "Exposed wires in Sector A",
        "priority": "HIGH"
    }
    response = await client.post("/api/v1/mine/governance/grievances", json=payload, headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Unsafe Working Conditions"
    assert data["data"]["status"] == "OPEN"
    
    grievance_id = data["data"]["id"]
    return grievance_id

async def test_resolve_grievance(client: AsyncClient, token_headers: dict):
    grievance_id = await test_create_grievance(client, token_headers)
    payload = {
        "resolution_action": "Fixed the exposed wires",
        "resolution_notes": "All safely insulated now."
    }
    response = await client.post(f"/api/v1/mine/governance/grievances/{grievance_id}/resolve", json=payload, headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "RESOLVED"

async def test_create_approval_request(client: AsyncClient, token_headers: dict):
    payload = {
        "mine_id": "test-mine-id",
        "approval_type": "CONTRACTOR_APPROVAL",
        "title": "Approve Contractor A",
        "entity_type": "Contractor",
        "entity_id": "contractor-123",
        "remarks": "Please review their updated documents"
    }
    response = await client.post("/api/v1/mine/governance/approvals", json=payload, headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "PENDING"
    
    approval_id = data["data"]["id"]
    return approval_id

async def test_action_approval_request(client: AsyncClient, token_headers: dict):
    approval_id = await test_create_approval_request(client, token_headers)
    payload = {
        "action": "APPROVE",
        "remarks": "Documents look good."
    }
    response = await client.post(f"/api/v1/mine/governance/approvals/{approval_id}/action", json=payload, headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "APPROVED"

async def test_evaluate_escalations(client: AsyncClient, token_headers: dict):
    response = await client.post("/api/v1/mine/governance/escalations/evaluate?mine_id=test-mine-id", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "escalated_count" in data["data"]

async def test_get_audit_trail(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/mine/governance/audit-trail?mine_id=test-mine-id", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
