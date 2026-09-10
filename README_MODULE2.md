# AI MineGuard — Module 2: Field Operations & Inspection Management

SIH26024 — AI-Based Smart Governance and Compliance Monitoring System for Coal Mines

---

## 1. Overview & Core Mission

Module 2 serves as the **tactical field execution, offline-first digital notebook, and evidence collection layer** of AI MineGuard. In coal mining operations (open-cast pits, underground seams, haulage roads, and overburden benches), continuous cellular/Wi-Fi coverage is rarely guaranteed. 

Module 2 guarantees **zero data loss in zero-connectivity environments**:
- Inspectors can create, validate, and store statutory audits, incident reports, and geo-tagged observations locally on the device using **SQLite**.
- A reactive **Sync Engine** monitors connection interfaces via **Connectivity Plus** and dispatches queued payloads to the **FastAPI + PostgreSQL** backend with UUID idempotency keys.
- **Assistive AI Incident Structuring** parses spoken voice notes and unstructured text to extract standard hazard categories, locations, and severities for inspector confirmation without overwriting original source testimony.
- Issues move through a rigorous **Field Verification & Remediation Lifecycle** (`REPORTED` → `VERIFIED` → `CORRECTIVE ACTION` → `EVIDENCE SUBMITTED` → `SUPERVISOR REVIEW` → `APPROVED` → `CLOSED`), backed by an immutable SHA-256 chained audit trail.

---

## 2. Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Mobile App** | **Dart & Flutter** | Cross-platform mobile client with coal-mining industrial dark UI |
| **State Management** | **Provider** | Reactive state coordination across sync, inspection, and incident flows |
| **Local Storage** | **SQLite (`sqflite`)** | Durable on-device storage queue for offline operations |
| **Network Monitor** | **`connectivity_plus`** | Detects Wi-Fi, Mobile Data, Ethernet, or Disconnected states |
| **HTTP Transport** | **`dio`** | Multipart media evidence uploads, token interceptors, and retries |
| **Token Security** | **`flutter_secure_storage`** | Hardware-backed encrypted keychain storage for JWT tokens |
| **Sync Engine** | **Custom Sync Engine** | Offline batching, retry mechanism, and UUID idempotency |
| **Backend API** | **FastAPI (Python 3.11+)** | High-performance asynchronous REST API backend |
| **Central Database**| **PostgreSQL / SQLite** | Central relational store with spatial and audit capabilities |

---

## 3. Features Implemented

- **F2-01: Field Report:** Geo-tagged observations with severity and evidence.
- **F2-02: GPS Capture:** Automatic latitude, longitude, and accuracy recording.
- **F2-03: Evidence Capture:** Multi-modal photo, video, and audio voice note attachments.
- **F2-04: Offline Submit:** Local SQLite queuing with `READY_TO_SYNC` state.
- **F2-05: Auto Sync:** Network-triggered batch dispatch upon reconnection.
- **F2-06: Sync Status UI:** Real-time sync center and queue inspection screen.
- **F2-07: Inspection Templates:** DGMS Fire Safety, MoEFCC Environmental, and HEMM Machinery checklists.
- **F2-08: Inspection Scheduling:** Shift assignment, compliance scoring, and failure escalation.
- **F2-09: Incident Management:** Dedicated fast-path reporting for accidents and breakdowns.
- **F2-10: AI Incident Structuring:** Natural language extraction from voice/text notes.
- **F2-11: GIS Handoff:** GeoJSON feature collections for digital twin maps.
- **F2-12: Field Verification:** 7-stage remediation state machine with proof comparison.
- **F2-13: Evidence Timeline & Audit:** Tamper-evident SHA-256 audit logging.
- **F2-14: In-App Alerts:** Real-time offline warnings and sync feedback.

---

## 4. Quick Start & Execution

### 4.1 Backend (FastAPI)

1. **Activate Environment & Install Requirements:**
   ```powershell
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Run Pytest Suite (All 8 Test Suites):**
   ```powershell
   $env:PYTHONPATH = "."
   pytest backend/tests/test_module2_api.py -v
   ```

3. **Start FastAPI Backend Server:**
   ```powershell
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Interactive Swagger Documentation will be live at `http://localhost:8000/docs`.*

### 4.2 Flutter Mobile App

1. **Get Dependencies:**
   ```powershell
   cd mobile_app
   flutter pub get
   ```

2. **Run Dart Model & Sync Engine Tests:**
   ```powershell
   dart run --enable-asserts test/run_dart_tests.dart
   ```

3. **Run Mobile App on Device/Emulator:**
   ```powershell
   flutter run
   ```

---

## 5. Demonstration Script (Step-by-Step)

1. **Login & Context:** Launch the app as `INSP-DHANBAD-05`, select `MINE-DHANBAD-01`, and enter the pit dashboard.
2. **Statutory Audit:** Open **Statutory Inspection Checklist** (DGMS Fire Safety). Verify automatic GPS lock. Mark items; fail `FIRE-02` (Stone Dust Barrier); attach photo proof and observation remarks.
3. **Simulate Offline:** Tap **Simulate Offline** in the header banner. Notice banner changes to red: *"Offline Mode — Stored locally in SQLite"*.
4. **Offline Submission:** Tap **SUBMIT AUDIT**. Notice submission succeeds immediately without network errors and queues item with `READY_TO_SYNC`.
5. **AI Voice Incident:** Go to **Report Mine Incident**. Type or dictate: *"At the north haul road around 10:20, the dumper stopped suddenly and smoke was noticed near the engine compartment. No injury observed."* Tap **Analyze with AI**. The modal suggests `EQUIPMENT_FAILURE`, `FIRE_AND_SMOKE`, `HAUL_ROAD`, and `NONE_REPORTED` with 92% confidence. Tap **Confirm & Apply**, then submit.
6. **Reconnection & Auto-Sync:** Tap **Simulate Offline** to restore connection. The Sync Engine automatically dispatches the batch payload to `/api/v1/sync/batch`. Open **Sync Center** to verify all items transitioned to `SYNCED`.
7. **Remediation & Closure:** Open **Field Verification & Remediation**. Notice verification tasks were automatically spawned from the failed inspection item and incident. Progress through `VERIFY ISSUE` → `ASSIGN ACTION` → `UPLOAD FIX EVIDENCE` → `REVIEW` → `APPROVE` → `CLOSE CASE`.
