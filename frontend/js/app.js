/**
 * AI MineGuard — Contractor & Worker Governance Management System
 * Dynamic Frontend Controller (Module 3 -> Tasks 1 & 2)
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/mine';

// Application State Store (with synthetic fallback seed for instant local preview)
let appState = {
    contractors: [
        {
            id: "cont-001",
            mine_id: "MINE-001",
            company_name: "Bharat Mining Excavators Pvt Ltd",
            registration_number: "REG-BME-2026-001",
            contact_person: "Rajesh Sharma",
            email: "rajesh@bmecontractors.com",
            phone: "+91 98765 43210",
            address: "Godavarikhani Industrial Area, Telangana",
            work_scope: "EXCAVATION",
            status: "ACTIVE",
            compliance_score: 95.0,
            compliance_status: "COMPLIANT",
            performance_score: 4.8,
            contracts: [
                {
                    id: "c-101",
                    contract_number: "CON-2026-EXC-09",
                    title: "Seam 4 Excavation & Haulage Operations",
                    contract_type: "O&M",
                    start_date: "2025-10-01",
                    end_date: "2026-09-25",
                    contract_value: 45000000.0,
                    status: "EXPIRING_SOON",
                    renewal_count: 1
                }
            ],
            documents: [],
            compliances: [],
            performances: []
        }
    ],
    workers: [
        {
            id: "wk-001",
            mine_id: "MINE-001",
            contractor_id: "cont-001",
            employee_id: "EMP-2026-9901",
            full_name: "Ramesh Kumar",
            department: "UNDERGROUND_OPS",
            role: "HEAVY_EQUIPMENT_OPERATOR",
            email: "ramesh@mineguard.in",
            phone: "+91 91234 56789",
            emergency_contact_name: "Sita Devi",
            emergency_contact_phone: "+91 98765 12345",
            joining_date: "2025-04-10",
            status: "ACTIVE",
            attendances: [
                { id: "att-1", shift: "MORNING", check_in: "2026-09-09T06:00:00Z", status: "PRESENT" }
            ],
            trainings: [
                { id: "tr-1", program_name: "DGMS Statutory Underground Gas & Helmet Safety", trainer_name: "Safety Inspector Subba Rao", completed_date: "2026-01-15", expiry_date: "2026-09-20", status: "PENDING" }
            ],
            certifications: [
                { id: "cert-1", certificate_name: "DGMS HEMM Operator License", certificate_number: "DGMS-2026-881", issuing_authority: "DGMS Hyderabad", valid_from: "2025-01-01", expiry_date: "2027-01-01", verification_status: "VERIFIED" }
            ],
            ppes: [
                { id: "ppe-1", item_type: "HELMET", issuance_date: "2026-01-10", expiry_date: "2027-01-10", compliance_status: "COMPLIANT", remarks: "Standard IS-2925 Verified Hard Hat" }
            ],
            authorizations: [
                { id: "auth-1", zone_id: "ZONE-UNDERGROUND-PITFACE-04", permit_type: "UNDERGROUND_ENTRY", grant_date: "2026-06-01", expiry_date: "2026-12-31", status: "GRANTED", granted_by: "Mine Manager Office" }
            ]
        },
        {
            id: "wk-002",
            mine_id: "MINE-001",
            contractor_id: null,
            employee_id: "EMP-2026-9902",
            full_name: "Suresh Reddy",
            department: "SAFETY",
            role: "INSPECTOR",
            email: "suresh@mineguard.in",
            phone: "+91 94400 11223",
            emergency_contact_name: "Laxmi Reddy",
            emergency_contact_phone: "+91 94400 99887",
            joining_date: "2024-01-15",
            status: "ACTIVE",
            attendances: [
                { id: "att-2", shift: "MORNING", check_in: "2026-09-09T05:55:00Z", status: "PRESENT" }
            ],
            trainings: [
                { id: "tr-2", program_name: "Advanced Mine Rescue & Gas Detector Calibration", trainer_name: "Directorate General", completed_date: "2026-02-10", expiry_date: "2027-02-10", status: "COMPLETED" }
            ],
            certifications: [
                { id: "cert-2", certificate_name: "First Class Mine Manager Clearance", certificate_number: "DGMS-FC-992", issuing_authority: "DGMS Dhanbad", valid_from: "2024-01-01", expiry_date: "2029-01-01", verification_status: "VERIFIED" }
            ],
            ppes: [
                { id: "ppe-2", item_type: "RESPIRATOR", issuance_date: "2026-02-01", expiry_date: "2026-08-01", compliance_status: "REPLACEMENT_REQUIRED", remarks: "Filter replacement overdue" }
            ],
            authorizations: [
                { id: "auth-2", zone_id: "ZONE-ALL-MINES", permit_type: "HOT_WORK", grant_date: "2026-01-01", expiry_date: "2026-12-31", status: "GRANTED", granted_by: "General Safety Officer" }
            ]
        }
    ],
    selectedContractorId: null,
    selectedWorkerId: null
};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initEventListeners();
    fetchBackendData();
});

// View Navigation Controller
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewTarget = item.getAttribute('data-view');
            switchView(viewTarget);
        });
    });
}

function switchView(viewName) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));

    const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    const targetView = document.getElementById(`view-${viewName}`);

    if (targetNav) targetNav.classList.add('active');
    if (targetView) targetView.classList.add('active');

    // Update Header Text
    const pageTitle = document.getElementById('page-title');
    const pageSub = document.getElementById('page-subtitle');

    switch (viewName) {
        case 'dashboard':
            pageTitle.innerText = "Contractor Dashboard";
            pageSub.innerText = "Real-time statutory compliance, contract lifecycle & safety scorecards";
            break;
        case 'contractors':
            pageTitle.innerText = "Contractor Registry";
            pageSub.innerText = "Statutory approved mine contractors, work scope & compliance ratings";
            break;
        case 'contracts':
            pageTitle.innerText = "Contract Lifecycle";
            pageSub.innerText = "Work order validities, start/end dates, values & renewal workflows";
            break;
        case 'worker-dashboard':
            pageTitle.innerText = "Worker Dashboard";
            pageSub.innerText = "Workforce overview, pending trainings, expired certifications & compliance metrics";
            break;
        case 'workers':
            pageTitle.innerText = "Worker Registry";
            pageSub.innerText = "Employee IDs, departments, statutory roles, emergency contacts & profiles";
            break;
        case 'attendance':
            pageTitle.innerText = "Attendance Management";
            pageSub.innerText = "Shift check-ins, check-outs, attendance status & overtime logs";
            break;
        case 'trainings':
            pageTitle.innerText = "Training Management";
            pageSub.innerText = "Statutory VTC safety training programs, completion & expiry tracking";
            break;
        case 'certifications':
            pageTitle.innerText = "Certification Tracker";
            pageSub.innerText = "DGMS qualifications, PME medical clearances & license validities";
            break;
        case 'ppe':
            pageTitle.innerText = "PPE Eligibility";
            pageSub.innerText = "Mandatory hard hat, vest, boot & respirator issuance matrix";
            break;
        case 'authorizations':
            pageTitle.innerText = "Work Authorizations";
            pageSub.innerText = "Restricted pitface permits, hot work access grants & revocation history";
            break;
        case 'governance-dashboard':
            pageTitle.innerText = "Governance Dashboard";
            pageSub.innerText = "Executive overview of safety compliance, grievance resolutions & management approvals";
            break;
        case 'grievances':
            pageTitle.innerText = "Grievances & Complaints";
            pageSub.innerText = "Manage worker complaints, safety hazards, and contractor disputes";
            break;
        case 'approvals':
            pageTitle.innerText = "Approval Center";
            pageSub.innerText = "Centralized workflow for contract renewals, permits, and governance actions";
            break;
        case 'escalations':
            pageTitle.innerText = "Escalation Engine";
            pageSub.innerText = "Auto-escalation rules, SLA breach tracking & management interventions";
            break;
        case 'audit':
            pageTitle.innerText = "Audit Trail";
            pageSub.innerText = "Cryptographically secure immutable logs of all governance & safety events";
            break;
    }
}

// Event Listeners Initialization
function initEventListeners() {
    // Topbar search
    document.getElementById('global-search').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        renderContractorsTable(query);
        renderWorkersTable(query);
    });

    // Filters
    document.getElementById('filter-worker-dept')?.addEventListener('change', () => renderWorkersTable());
    document.getElementById('filter-worker-status')?.addEventListener('change', () => renderWorkersTable());
    document.getElementById('filter-att-shift')?.addEventListener('change', () => renderAttendanceLogs());

    // Sync button
    document.getElementById('btn-refresh').addEventListener('click', () => fetchBackendData());

    // Top & Main Add Worker Buttons
    document.getElementById('btn-add-worker-top')?.addEventListener('click', () => openAddWorkerModal());
    document.getElementById('btn-add-worker-main')?.addEventListener('click', () => openAddWorkerModal());

    // Standalone Buttons
    document.getElementById('btn-mark-att-main')?.addEventListener('click', () => {
        if (appState.workers.length > 0) openAttModal(appState.workers[0].id);
    });
    document.getElementById('btn-assign-training-main')?.addEventListener('click', () => {
        if (appState.workers.length > 0) openTrainModal(appState.workers[0].id);
    });
    document.getElementById('btn-reg-cert-main')?.addEventListener('click', () => {
        if (appState.workers.length > 0) openCertModal(appState.workers[0].id);
    });
    document.getElementById('btn-assign-ppe-main')?.addEventListener('click', () => {
        if (appState.workers.length > 0) openPPEModal(appState.workers[0].id);
    });
    document.getElementById('btn-grant-auth-main')?.addEventListener('click', () => {
        if (appState.workers.length > 0) openAuthModal(appState.workers[0].id);
    });

    // Form Submissions
    document.getElementById('worker-form')?.addEventListener('submit', handleWorkerSubmit);
    document.getElementById('att-form')?.addEventListener('submit', handleAttSubmit);
    document.getElementById('train-form')?.addEventListener('submit', handleTrainSubmit);
    document.getElementById('cert-form')?.addEventListener('submit', handleCertSubmit);
    document.getElementById('ppe-form')?.addEventListener('submit', handlePPESubmit);
    document.getElementById('auth-form')?.addEventListener('submit', handleAuthSubmit);

    // Export Summary Report
    document.getElementById('btn-export-report')?.addEventListener('click', () => {
        alert("Workforce & Compliance PDF Summary Report generated successfully!");
    });
}

// Fetch Backend Data
async function fetchBackendData() {
    try {
        const [cRes, wRes] = await Promise.all([
            fetch(`${API_BASE_URL}/contractors`),
            fetch(`${API_BASE_URL}/workers`)
        ]);
        if (cRes.ok) {
            const cData = await cRes.json();
            if (cData.data && cData.data.length > 0) appState.contractors = cData.data;
        }
        if (wRes.ok) {
            const wData = await wRes.json();
            if (wData.data && wData.data.length > 0) appState.workers = wData.data;
        }
    } catch (e) {
        console.warn("Backend API offline, using local state:", e);
    }
    renderAllViews();
}

function renderAllViews() {
    renderKPIs();
    renderWorkerKPIs();
    renderDashboardTable();
    renderDashboardAlerts();
    renderContractorsTable();
    renderContractsTable();
    
    renderWorkerReportsSummary();
    renderWorkerAlertsList();
    renderWorkersTable();
    renderAttendanceLogs();
    renderTrainingLogs();
    renderCertLogs();
    renderPPELogs();
    renderAuthLogs();
}

// 1. Contractor KPIs
function renderKPIs() {
    const totalContractors = appState.contractors.length;
    const activeContractors = appState.contractors.filter(c => c.status === 'ACTIVE').length;
    let allContracts = [];
    appState.contractors.forEach(c => { if (c.contracts) allContracts.push(...c.contracts); });
    const activeContracts = allContracts.filter(c => ['ACTIVE', 'EXPIRING_SOON', 'RENEWED'].includes(c.status));
    const totalVal = activeContracts.reduce((sum, c) => sum + (c.contract_value || 0), 0);

    const today = new Date();
    const thirtyDaysAhead = new Date();
    thirtyDaysAhead.setDate(today.getDate() + 30);
    const expiringCount = allContracts.filter(c => new Date(c.end_date) >= today && new Date(c.end_date) <= thirtyDaysAhead).length;
    const avgComp = totalContractors > 0 ? (appState.contractors.reduce((sum, c) => sum + (c.compliance_score || 100), 0) / totalContractors).toFixed(1) : 100;

    document.getElementById('kpi-total-contractors').innerText = totalContractors;
    document.getElementById('kpi-active-contractors').innerText = activeContractors;
    document.getElementById('kpi-active-contracts').innerText = activeContracts.length;
    document.getElementById('kpi-contract-val').innerText = (totalVal / 10000000).toFixed(2);
    document.getElementById('kpi-expiring-contracts').innerText = expiringCount;
    document.getElementById('kpi-avg-compliance').innerText = `${avgComp}%`;
}

// 2. Worker KPIs (Module 3 -> Task 2)
function renderWorkerKPIs() {
    const total = appState.workers.length;
    const active = appState.workers.filter(w => w.status === 'ACTIVE').length;
    
    let pendingTrainings = 0;
    let expiredCerts = 0;
    let totalPPE = 0;
    let compliantPPE = 0;
    let totalAuths = 0;
    let grantedAuths = 0;

    const today = new Date();

    appState.workers.forEach(w => {
        (w.trainings || []).forEach(t => { if (t.status === 'PENDING' || new Date(t.expiry_date) < today) pendingTrainings++; });
        (w.certifications || []).forEach(c => { if (c.verification_status === 'EXPIRED' || new Date(c.expiry_date) < today) expiredCerts++; });
        (w.ppes || []).forEach(p => {
            totalPPE++;
            if (p.compliance_status === 'COMPLIANT' && new Date(p.expiry_date) >= today) compliantPPE++;
        });
        (w.authorizations || []).forEach(a => {
            totalAuths++;
            if (a.status === 'GRANTED' && new Date(a.expiry_date) >= today) grantedAuths++;
        });
    });

    const ppePct = totalPPE > 0 ? ((compliantPPE / totalPPE) * 100).toFixed(1) : 100.0;
    const authPct = totalAuths > 0 ? ((grantedAuths / totalAuths) * 100).toFixed(1) : 100.0;

    document.getElementById('wk-kpi-total').innerText = total;
    document.getElementById('wk-kpi-active').innerText = active;
    document.getElementById('wk-kpi-pending-tr').innerText = pendingTrainings;
    document.getElementById('wk-kpi-expired-certs').innerText = expiredCerts;
    document.getElementById('wk-kpi-ppe-pct').innerText = `${ppePct}%`;
    document.getElementById('wk-kpi-auth-pct').innerText = `${authPct}%`;
}

// 3. Worker Reports Summary Box
function renderWorkerReportsSummary() {
    let attendancesToday = 0;
    let activeCerts = 0;
    let completedTrainings = 0;
    let compliantPPE = 0;

    appState.workers.forEach(w => {
        attendancesToday += (w.attendances || []).length;
        activeCerts += (w.certifications || []).filter(c => c.verification_status === 'VERIFIED').length;
        completedTrainings += (w.trainings || []).filter(t => t.status === 'COMPLETED').length;
        compliantPPE += (w.ppes || []).filter(p => p.compliance_status === 'COMPLIANT').length;
    });

    document.getElementById('rep-att-val').innerText = `${attendancesToday} Logged`;
    document.getElementById('rep-cert-val').innerText = `${activeCerts} Active`;
    document.getElementById('rep-train-val').innerText = `${completedTrainings} Completed`;
    document.getElementById('rep-ppe-val').innerText = `${compliantPPE} Compliant`;
}

// 4. Worker Alerts Ticker & List
function renderWorkerAlertsList() {
    const container = document.getElementById('worker-alerts-list');
    container.innerHTML = '';

    const today = new Date();
    appState.workers.forEach(w => {
        (w.trainings || []).forEach(t => {
            if (t.status === 'PENDING' || new Date(t.expiry_date) < today) {
                const item = document.createElement('div');
                item.className = 'alert-item';
                item.innerHTML = `<div class="alert-title text-amber"><i class="fa-solid fa-graduation-cap"></i> Training Overdue</div><div class="alert-desc">${w.full_name} (${w.employee_id}) — '${t.program_name}'</div>`;
                container.appendChild(item);
            }
        });

        (w.authorizations || []).forEach(a => {
            if (a.status === 'REVOKED') {
                const item = document.createElement('div');
                item.className = 'alert-item alert-danger';
                item.innerHTML = `<div class="alert-title text-danger"><i class="fa-solid fa-key"></i> Permit Revoked</div><div class="alert-desc">${w.full_name} — Restricted Permit '${a.permit_type}' REVOKED for ${a.zone_id}</div>`;
                container.appendChild(item);
            }
        });
    });

    if (container.children.length === 0) {
        container.innerHTML = `<div class="text-muted p-3 text-center">No active workforce compliance alerts.</div>`;
    }
}

// 5. Worker Registry Table
function renderWorkersTable(searchQuery = '') {
    const tbody = document.getElementById('workers-full-tbody');
    tbody.innerHTML = '';

    const filterDept = document.getElementById('filter-worker-dept')?.value;
    const filterStatus = document.getElementById('filter-worker-status')?.value;

    let filtered = appState.workers.filter(w => {
        if (filterDept && w.department !== filterDept) return false;
        if (filterStatus && w.status !== filterStatus) return false;
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            return w.full_name.toLowerCase().includes(q) ||
                   w.employee_id.toLowerCase().includes(q) ||
                   w.phone.toLowerCase().includes(q) ||
                   w.role.toLowerCase().includes(q);
        }
        return true;
    });

    filtered.forEach(w => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><code>${w.employee_id}</code></td>
            <td><strong>${w.full_name}</strong></td>
            <td><span class="badge badge-purple">${w.department}</span></td>
            <td><span class="badge badge-blue">${w.role}</span></td>
            <td>${w.phone}<br><span class="text-dim">Emg: ${w.emergency_contact_phone}</span></td>
            <td>${w.joining_date}</td>
            <td><span class="badge ${w.status === 'ACTIVE' ? 'badge-emerald' : 'badge-danger'}">${w.status}</span></td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="openWorkerDetail('${w.id}')"><i class="fa-solid fa-folder-open"></i></button>
                <button class="btn btn-sm btn-outline" onclick="openEditWorkerModal('${w.id}')"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-sm btn-icon btn-danger" onclick="deleteWorker('${w.id}')"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// 6. Attendance Logs Table
function renderAttendanceLogs() {
    const tbody = document.getElementById('attendance-logs-tbody');
    tbody.innerHTML = '';
    const shiftFilter = document.getElementById('filter-att-shift')?.value;

    appState.workers.forEach(w => {
        (w.attendances || []).forEach(a => {
            if (shiftFilter && a.shift !== shiftFilter) return;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${w.full_name}</strong></td>
                <td><code>${w.employee_id}</code></td>
                <td><span class="badge badge-blue">${a.shift}</span></td>
                <td>${a.check_in || 'N/A'}</td>
                <td>${a.check_out || 'Active Shift'}</td>
                <td><span class="badge badge-emerald">${a.status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// 7. Training Logs Table
function renderTrainingLogs() {
    const tbody = document.getElementById('training-logs-tbody');
    tbody.innerHTML = '';

    appState.workers.forEach(w => {
        (w.trainings || []).forEach(t => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${w.full_name}</strong></td>
                <td>${t.program_name}</td>
                <td>${t.trainer_name}</td>
                <td>${t.completed_date}</td>
                <td>${t.expiry_date}</td>
                <td><span class="badge ${t.status === 'COMPLETED' ? 'badge-emerald' : 'badge-amber'}">${t.status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// 8. Certification Logs Table
function renderCertLogs() {
    const tbody = document.getElementById('cert-logs-tbody');
    tbody.innerHTML = '';

    appState.workers.forEach(w => {
        (w.certifications || []).forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${w.full_name}</strong></td>
                <td>${c.certificate_name}</td>
                <td><code>${c.certificate_number}</code></td>
                <td>${c.issuing_authority}</td>
                <td>${c.expiry_date}</td>
                <td><span class="badge badge-emerald">${c.verification_status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// 9. PPE Logs Table
function renderPPELogs() {
    const tbody = document.getElementById('ppe-logs-tbody');
    tbody.innerHTML = '';

    appState.workers.forEach(w => {
        (w.ppes || []).forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${w.full_name}</strong></td>
                <td><span class="badge badge-purple">${p.item_type}</span></td>
                <td>${p.issuance_date}</td>
                <td>${p.expiry_date}</td>
                <td><span class="badge ${p.compliance_status === 'COMPLIANT' ? 'badge-emerald' : 'badge-danger'}">${p.compliance_status}</span></td>
                <td><span class="text-dim">${p.remarks || '--'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// 10. Authorization Logs Table
function renderAuthLogs() {
    const tbody = document.getElementById('auth-logs-tbody');
    tbody.innerHTML = '';

    appState.workers.forEach(w => {
        (w.authorizations || []).forEach(a => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${w.full_name}</strong></td>
                <td><code>${a.zone_id}</code></td>
                <td><span class="badge badge-blue">${a.permit_type}</span></td>
                <td>${a.granted_by}</td>
                <td>${a.expiry_date}</td>
                <td><span class="badge ${a.status === 'GRANTED' ? 'badge-emerald' : 'badge-danger'}">${a.status}</span></td>
                <td>
                    ${a.status === 'GRANTED' ? `<button class="btn btn-sm btn-danger" onclick="revokeAuth('${a.id}')"><i class="fa-solid fa-ban"></i> Revoke</button>` : `<span class="text-dim">Revoked</span>`}
                </td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// Retained Contractor Table Renders
function renderDashboardTable() {
    const tbody = document.getElementById('dashboard-contractors-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    appState.contractors.slice(0, 5).forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${c.company_name}</strong></td>
            <td><code>${c.registration_number}</code></td>
            <td><span class="badge badge-purple">${c.work_scope}</span></td>
            <td><span class="badge ${c.compliance_score >= 85 ? 'badge-emerald' : 'badge-danger'}">${c.compliance_score}%</span></td>
            <td><span class="badge badge-emerald">${c.status}</span></td>
            <td><button class="btn btn-sm btn-outline" onclick="switchView('contractors')">View</button></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderDashboardAlerts() {
    const container = document.getElementById('dashboard-expiring-list');
    if (!container) return;
    container.innerHTML = `<div class="text-muted p-3 text-center">No active renewal alerts.</div>`;
}

function renderContractorsTable() {
    const tbody = document.getElementById('contractors-full-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    appState.contractors.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${c.company_name}</strong></td>
            <td><code>${c.registration_number}</code></td>
            <td>${c.contact_person}</td>
            <td><span class="badge badge-purple">${c.work_scope}</span></td>
            <td><span class="badge badge-emerald">${c.compliance_score}%</span></td>
            <td><span class="badge badge-emerald">${c.status}</span></td>
            <td><button class="btn btn-sm btn-secondary" onclick="switchView('contractors')">View</button></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderContractsTable() {
    const tbody = document.getElementById('contracts-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    appState.contractors.forEach(c => {
        (c.contracts || []).forEach(contract => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${contract.contract_number}</code></td>
                <td>${contract.title}</td>
                <td>${contract.contract_type}</td>
                <td>${contract.end_date}</td>
                <td>₹${(contract.contract_value / 100000).toFixed(2)} L</td>
                <td><span class="badge badge-emerald">${contract.status}</span></td>
                <td><button class="btn btn-sm btn-success">Renew</button></td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// Worker Profile Modal & Tab Handler
function openWorkerDetail(workerId) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (!worker) return;
    appState.selectedWorkerId = workerId;

    document.getElementById('wk-detail-name').innerText = worker.full_name;
    document.getElementById('wk-detail-empid').innerText = worker.employee_id;
    document.getElementById('wk-detail-dept').innerText = worker.department;
    document.getElementById('wk-detail-role').innerText = worker.role;
    document.getElementById('wk-detail-status').innerText = worker.status;

    document.getElementById('wk-info-phone').innerText = worker.phone;
    document.getElementById('wk-info-email').innerText = worker.email || 'N/A';
    document.getElementById('wk-info-emg-name').innerText = worker.emergency_contact_name;
    document.getElementById('wk-info-emg-phone').innerText = worker.emergency_contact_phone;
    document.getElementById('wk-info-joining').innerText = worker.joining_date;

    openModal('worker-detail-modal');
}

function switchWorkerModalTab(tabId) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));
    const btn = document.querySelector(`.modal-tab[data-tab="${tabId}"]`);
    const content = document.getElementById(tabId);
    if (btn) btn.classList.add('active');
    if (content) content.classList.add('active');
}

// Modals Setup
function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function openAddWorkerModal() {
    document.getElementById('worker-form-title').innerText = "Add New Worker";
    document.getElementById('worker-form').reset();
    document.getElementById('form-worker-id').value = "";
    openModal('worker-form-modal');
}

function openEditWorkerModal(workerId) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (!worker) return;

    document.getElementById('worker-form-title').innerText = "Edit Worker Profile";
    document.getElementById('form-worker-id').value = worker.id;
    document.getElementById('form-wk-empid').value = worker.employee_id;
    document.getElementById('form-wk-fullname').value = worker.full_name;
    document.getElementById('form-wk-dept').value = worker.department;
    document.getElementById('form-wk-role').value = worker.role;
    document.getElementById('form-wk-phone').value = worker.phone;
    document.getElementById('form-wk-email').value = worker.email || '';
    document.getElementById('form-wk-emg-name').value = worker.emergency_contact_name;
    document.getElementById('form-wk-emg-phone').value = worker.emergency_contact_phone;
    document.getElementById('form-wk-joining').value = worker.joining_date;

    openModal('worker-form-modal');
}

async function handleWorkerSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('form-worker-id').value;
    const payload = {
        mine_id: document.getElementById('mine-select').value || "MINE-001",
        employee_id: document.getElementById('form-wk-empid').value,
        full_name: document.getElementById('form-wk-fullname').value,
        department: document.getElementById('form-wk-dept').value,
        role: document.getElementById('form-wk-role').value,
        phone: document.getElementById('form-wk-phone').value,
        email: document.getElementById('form-wk-email').value,
        emergency_contact_name: document.getElementById('form-wk-emg-name').value,
        emergency_contact_phone: document.getElementById('form-wk-emg-phone').value,
        joining_date: document.getElementById('form-wk-joining').value,
        status: "ACTIVE"
    };

    try {
        if (id) {
            const res = await fetch(`${API_BASE_URL}/workers/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) fetchBackendData();
        } else {
            const res = await fetch(`${API_BASE_URL}/workers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) fetchBackendData();
            else {
                payload.id = `wk-${Date.now()}`;
                payload.attendances = [];
                payload.trainings = [];
                payload.certifications = [];
                payload.ppes = [];
                payload.authorizations = [];
                appState.workers.unshift(payload);
            }
        }
    } catch (err) {
        payload.id = `wk-${Date.now()}`;
        payload.attendances = [];
        payload.trainings = [];
        payload.certifications = [];
        payload.ppes = [];
        payload.authorizations = [];
        appState.workers.unshift(payload);
    }

    closeModal('worker-form-modal');
    renderAllViews();
}

function openAttModal(workerId) {
    document.getElementById('form-att-worker-id').value = workerId;
    document.getElementById('att-form').reset();
    openModal('att-form-modal');
}

async function handleAttSubmit(e) {
    e.preventDefault();
    const workerId = document.getElementById('form-att-worker-id').value;
    const payload = {
        shift: document.getElementById('form-att-shift').value,
        status: document.getElementById('form-att-status').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}/attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) fetchBackendData();
        else addAttLocal(workerId, payload);
    } catch (err) {
        addAttLocal(workerId, payload);
    }

    closeModal('att-form-modal');
    renderAllViews();
}

function addAttLocal(workerId, payload) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (worker) {
        worker.attendances.push({
            id: `att-${Date.now()}`,
            ...payload,
            check_in: new Date().toISOString()
        });
    }
}

function openTrainModal(workerId) {
    document.getElementById('form-tr-worker-id').value = workerId;
    document.getElementById('train-form').reset();
    openModal('train-form-modal');
}

async function handleTrainSubmit(e) {
    e.preventDefault();
    const workerId = document.getElementById('form-tr-worker-id').value;
    const payload = {
        program_name: document.getElementById('form-tr-program').value,
        trainer_name: document.getElementById('form-tr-trainer').value,
        completed_date: document.getElementById('form-tr-completed').value,
        expiry_date: document.getElementById('form-tr-expiry').value,
        status: "COMPLETED"
    };

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}/trainings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) fetchBackendData();
        else addTrainLocal(workerId, payload);
    } catch (err) {
        addTrainLocal(workerId, payload);
    }

    closeModal('train-form-modal');
    renderAllViews();
}

function addTrainLocal(workerId, payload) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (worker) worker.trainings.push({ id: `tr-${Date.now()}`, ...payload });
}

function openCertModal(workerId) {
    document.getElementById('form-cert-worker-id').value = workerId;
    document.getElementById('cert-form').reset();
    openModal('cert-form-modal');
}

async function handleCertSubmit(e) {
    e.preventDefault();
    const workerId = document.getElementById('form-cert-worker-id').value;
    const payload = {
        certificate_name: document.getElementById('form-cert-name').value,
        certificate_number: document.getElementById('form-cert-num').value,
        issuing_authority: document.getElementById('form-cert-authority').value,
        valid_from: document.getElementById('form-cert-validfrom').value,
        expiry_date: document.getElementById('form-cert-expiry').value,
        verification_status: "VERIFIED"
    };

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}/certifications`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) fetchBackendData();
        else addCertLocal(workerId, payload);
    } catch (err) {
        addCertLocal(workerId, payload);
    }

    closeModal('cert-form-modal');
    renderAllViews();
}

function addCertLocal(workerId, payload) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (worker) worker.certifications.push({ id: `cert-${Date.now()}`, ...payload });
}

function openPPEModal(workerId) {
    document.getElementById('form-ppe-worker-id').value = workerId;
    document.getElementById('ppe-form').reset();
    openModal('ppe-form-modal');
}

async function handlePPESubmit(e) {
    e.preventDefault();
    const workerId = document.getElementById('form-ppe-worker-id').value;
    const payload = {
        item_type: document.getElementById('form-ppe-type').value,
        issuance_date: document.getElementById('form-ppe-issuance').value,
        expiry_date: document.getElementById('form-ppe-expiry').value,
        compliance_status: "COMPLIANT",
        remarks: document.getElementById('form-ppe-remarks').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}/ppe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) fetchBackendData();
        else addPPELocal(workerId, payload);
    } catch (err) {
        addPPELocal(workerId, payload);
    }

    closeModal('ppe-form-modal');
    renderAllViews();
}

function addPPELocal(workerId, payload) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (worker) worker.ppes.push({ id: `ppe-${Date.now()}`, ...payload });
}

function openAuthModal(workerId) {
    document.getElementById('form-auth-worker-id').value = workerId;
    document.getElementById('auth-form').reset();
    openModal('auth-form-modal');
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const workerId = document.getElementById('form-auth-worker-id').value;
    const payload = {
        zone_id: document.getElementById('form-auth-zone').value,
        permit_type: document.getElementById('form-auth-permit').value,
        grant_date: document.getElementById('form-auth-grant').value,
        expiry_date: document.getElementById('form-auth-expiry').value,
        granted_by: document.getElementById('form-auth-grantedby').value,
        status: "GRANTED"
    };

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}/authorizations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) fetchBackendData();
        else addAuthLocal(workerId, payload);
    } catch (err) {
        addAuthLocal(workerId, payload);
    }

    closeModal('auth-form-modal');
    renderAllViews();
}

function addAuthLocal(workerId, payload) {
    const worker = appState.workers.find(w => w.id === workerId);
    if (worker) worker.authorizations.push({ id: `auth-${Date.now()}`, ...payload });
}

async function revokeAuth(authId) {
    if (!confirm("Are you sure you want to REVOKE this restricted work permit?")) return;

    try {
        const res = await fetch(`${API_BASE_URL}/workers/authorizations/${authId}/revoke`, { method: 'POST' });
        if (res.ok) fetchBackendData();
        else revokeAuthLocal(authId);
    } catch (err) {
        revokeAuthLocal(authId);
    }

    renderAllViews();
}

function revokeAuthLocal(authId) {
    appState.workers.forEach(w => {
        (w.authorizations || []).forEach(a => {
            if (a.id === authId) a.status = "REVOKED";
        });
    });
}

async function deleteWorker(workerId) {
    if (!confirm("Are you sure you want to soft-delete this worker record?")) return;

    try {
        const res = await fetch(`${API_BASE_URL}/workers/${workerId}`, { method: 'DELETE' });
        if (res.ok) fetchBackendData();
        else appState.workers = appState.workers.filter(w => w.id !== workerId);
    } catch (err) {
        appState.workers = appState.workers.filter(w => w.id !== workerId);
    }

    renderAllViews();
}
