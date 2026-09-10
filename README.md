# Mind the Mine (SIH26024) - Module 3

## Contractor Management, Worker Registry & Compliance, and Governance Workflow

### Overview
This repository branch contains the complete **Module 3** implementation for the **Mind the Mine** safety and compliance management platform (SIH Problem Statement SIH26024).

### Key Features
1. **Contractor Management**:
   - Company registry, active contracts, document vault (DGMS/GST/PF), compliance scoring, and renewal pipelines.
2. **Worker & Workforce Compliance**:
   - Biometric/RFID shift attendance, safety training logs, DGMS certifications, PPE distribution tracking, and automated work authorization validation.
3. **Governance & Multi-Tier Approvals**:
   - Digital grievance redressal with SLA tracking, priority escalation, and multi-tier approval workflows (Mine Manager, Safety Officer, DGMS).
4. **Interactive Executive Dashboard**:
   - Glassmorphism UI with real-time KPI metrics, contractor cards, workforce directory, grievance tracking, and role-based actions.

### Repository Layout
- backend/ : FastAPI backend application, SQLite database, Pydantic schemas, and pytest suite.
- frontend/ : Interactive HTML5, CSS3, and JavaScript executive dashboard.

### Running Locally

#### Backend
\\ash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
\Interactive API documentation will be available at http://localhost:8000/docs.

#### Running Tests
\\ash
cd backend
pytest
\
#### Frontend
Open \rontend/index.html\ directly in any modern web browser or serve with a static web server:
\\ash
cd frontend
python -m http.server 3000
\