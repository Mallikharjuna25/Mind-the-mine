"""
Demo & Synthetic Simulation Router
Provides one-click seed and simulation endpoints for live hackathon demonstrations and testing.
"""

from typing import Dict, Any
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_password_hash, UserRole
from app.models.base import utc_now
from app.models.user_models import User
from app.models.mine_models import Mine, MineZone
from app.models.cctv_models import CameraRegistry
from app.models.equipment_models import EquipmentAsset
from app.schemas.common_schemas import ApiResponse
from app.schemas.cctv_schemas import DetectionIngestRequest
from app.schemas.environment_schemas import EnvironmentalReadingCreate
from app.services.cctv_service import cctv_service
from app.services.equipment_service import equipment_service
from app.services.environment_service import environment_service
from app.services.risk_engine_service import risk_engine_service
from app.ai.synthetic_generator import generate_synthetic_dgms_certificate

router = APIRouter(prefix="/demo", tags=["Demo & Synthetic Simulation"])


@router.post("/seed", response_model=ApiResponse[Dict[str, Any]])
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """
    Seeds initial synthetic coal mine, zones, users, cameras, and assets.
    """
    # 1. Create or get demo mine
    stmt = select(Mine).where(Mine.mine_code == "MINE-SECL-KUS-01")
    res = await db.execute(stmt)
    mine = res.scalars().first()

    if not mine:
        mine = Mine(
            mine_code="MINE-SECL-KUS-01",
            name="Kusmunda Mega Opencast Project",
            subsidiary="South Eastern Coalfields Limited (SECL)",
            state="Chhattisgarh",
            district="Korba",
            latitude=22.3168,
            longitude=82.6841,
            area_sqkm=16.8,
            lease_boundary_geojson={
                "type": "Polygon",
                "coordinates": [[[82.670, 22.300], [82.695, 22.300], [82.695, 22.330], [82.670, 22.330], [82.670, 22.300]]]
            }
        )
        db.add(mine)
        await db.flush()

        # 2. Add Mine Zones
        zones_data = [
            ("ZONE-PIT-01", "Active Extraction Pit (Face 4)", "OPEN_CAST_PIT", 1.8, False),
            ("ZONE-BLAST-02", "Deep Blasting & Highwall Sector", "BLASTING_ZONE", 2.5, True),
            ("ZONE-HAUL-03", "Main Haul Road Corridors", "HAUL_ROAD", 1.2, False),
            ("ZONE-CHP-04", "Coal Handling & Crushing Plant", "COAL_STOCKYARD", 1.4, False),
            ("ZONE-WRK-05", "HEMM Heavy Maintenance Workshop", "WORKSHOP", 1.0, False),
        ]
        created_zones = []
        for code, name, ztype, weight, is_rest in zones_data:
            zone = MineZone(
                mine_id=mine.id,
                zone_code=code,
                name=name,
                zone_type=ztype,
                risk_weight=weight,
                is_restricted=is_rest,
                polygon_geojson={"type": "Polygon", "coordinates": [[[82.675, 22.305], [82.685, 22.305], [82.685, 22.315], [82.675, 22.305]]]}
            )
            db.add(zone)
            created_zones.append(zone)
        await db.flush()

        # 3. Add Demo Cameras
        cam1 = CameraRegistry(
            mine_id=mine.id,
            zone_id=created_zones[0].id,
            camera_code="CAM-PIT-FACE-01",
            name="Pit Face East Highwall Cam",
            location_desc="Bench 3 Overburden Slope",
            latitude=22.3180,
            longitude=82.6820,
            status="ACTIVE",
            ppe_check_enabled=True,
            restricted_zone_enabled=True,
            fire_smoke_enabled=True
        )
        cam2 = CameraRegistry(
            mine_id=mine.id,
            zone_id=created_zones[1].id,
            camera_code="CAM-BLAST-ZONE-02",
            name="Blasting Perimeter PTZ Cam",
            location_desc="Restricted Blast Perimeter South",
            latitude=22.3120,
            longitude=82.6890,
            status="ACTIVE",
            ppe_check_enabled=True,
            restricted_zone_enabled=True,
            fire_smoke_enabled=True
        )
        db.add_all([cam1, cam2])

        # 4. Add Demo Equipment Assets
        eq1 = EquipmentAsset(
            mine_id=mine.id,
            zone_id=created_zones[0].id,
            asset_code="HEMM-DUMP-042",
            name="Caterpillar 777E Off-Highway Dump Truck",
            category="DUMPER",
            serial_number="SN-CAT777-99214",
            make_model="Caterpillar 777E",
            fitness_expiry_date=date.today() + timedelta(days=120),
            working_condition="OPERATIONAL"
        )
        eq2 = EquipmentAsset(
            mine_id=mine.id,
            zone_id=created_zones[1].id,
            asset_code="HEMM-EXCV-018",
            name="Komatsu PC2000-8 Hydraulic Mining Shovel",
            category="EXCAVATOR",
            serial_number="SN-KOMPC2000-110",
            make_model="Komatsu PC2000-8",
            fitness_expiry_date=date.today() - timedelta(days=5),  # Overdue
            working_condition="OPERATIONAL"
        )
        db.add_all([eq1, eq2])

        # 5. Add Demo Users (Super Admin, Safety Officer, Mine Manager, Worker)
        users_data = [
            ("admin@mineguard.in", "Admin@12345", "Director General / Super Admin", UserRole.SUPER_ADMIN, "Chief Inspector of Mines"),
            ("manager@mineguard.in", "Manager@12345", "Rajesh Sharma", UserRole.MINE_MANAGER, "General Manager (Kusmunda)"),
            ("safety@mineguard.in", "Safety@12345", "Amitabh Verma", UserRole.SAFETY_OFFICER, "Senior Safety Officer"),
            ("env@mineguard.in", "Env@12345", "Pooja Banerjee", UserRole.ENVIRONMENT_OFFICER, "Environmental Engineer"),
            ("worker@mineguard.in", "Worker@12345", "Ramesh Kumar", UserRole.WORKER, "HEMM Heavy Shovel Operator"),
        ]
        for email, pwd, name, role, desig in users_data:
            u = User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role,
                designation=desig,
                mine_id=mine.id,
                is_active=True
            )
            db.add(u)

        await db.flush()

        # 6. Add Demo Contractors & Workers (Module 3)
        from app.models.contractor_models import Contractor
        from app.models.worker_models import (
            Worker, WorkerAttendance, WorkerTraining, WorkerCertification,
            WorkerPPE, WorkerAuthorization, WorkerInsurance, WorkerLeave
        )

        cont1 = Contractor(
            mine_id=mine.id,
            company_name="Bharat Mining Excavators Pvt Ltd",
            registration_number="REG-BME-2026-001",
            contact_person="Rajesh Sharma",
            email="rajesh@bmecontractors.com",
            phone="+91 98765 43210",
            address="Godavarikhani Industrial Area, Telangana",
            work_scope="EXCAVATION",
            status="ACTIVE",
            compliance_score=95.0
        )
        cont2 = Contractor(
            mine_id=mine.id,
            company_name="Singhania Heavy Haulage & Earthmovers",
            registration_number="REG-SHE-2026-008",
            contact_person="Vikas Singhania",
            email="vikas@singhaniahaulage.in",
            phone="+91 98480 12345",
            address="Korba Industrial Sector 3, Chhattisgarh",
            work_scope="TRANSPORT",
            status="ACTIVE",
            compliance_score=91.5
        )
        db.add_all([cont1, cont2])
        await db.flush()

        w1 = Worker(
            mine_id=mine.id,
            contractor_id=cont1.id,
            employee_id="EMP-2026-9901",
            full_name="Ramesh Kumar",
            department="UNDERGROUND_OPS",
            role="HEAVY_EQUIPMENT_OPERATOR",
            email="worker@mineguard.in",
            phone="+91 91234 56789",
            emergency_contact_name="Sita Devi",
            emergency_contact_phone="+91 98765 12345",
            joining_date=date.today() - timedelta(days=365),
            status="ACTIVE",
            blood_group="B+",
            rfid_tag="RFID-KUS-8821",
            medical_fitness_status="FIT",
            medical_exam_date=date.today() - timedelta(days=45),
            medical_expiry_date=date.today() + timedelta(days=320)
        )
        w2 = Worker(
            mine_id=mine.id,
            contractor_id=None,
            employee_id="EMP-2026-9902",
            full_name="Suresh Reddy",
            department="SAFETY",
            role="INSPECTOR",
            email="suresh@mineguard.in",
            phone="+91 94400 11223",
            emergency_contact_name="Laxmi Reddy",
            emergency_contact_phone="+91 94400 99887",
            joining_date=date.today() - timedelta(days=500),
            status="ACTIVE",
            blood_group="O+",
            rfid_tag="RFID-KUS-8822",
            medical_fitness_status="FIT",
            medical_exam_date=date.today() - timedelta(days=90),
            medical_expiry_date=date.today() + timedelta(days=275)
        )
        w3 = Worker(
            mine_id=mine.id,
            contractor_id=cont2.id,
            employee_id="EMP-2026-9903",
            full_name="Manoj Singh",
            department="EXCAVATION",
            role="BLASTER",
            email="manoj@mineguard.in",
            phone="+91 93300 44556",
            emergency_contact_name="Meena Singh",
            emergency_contact_phone="+91 93300 11223",
            joining_date=date.today() - timedelta(days=180),
            status="ACTIVE",
            blood_group="A+",
            rfid_tag="RFID-KUS-8823",
            medical_fitness_status="FIT",
            medical_exam_date=date.today() - timedelta(days=30),
            medical_expiry_date=date.today() + timedelta(days=335)
        )
        db.add_all([w1, w2, w3])
        await db.flush()

        # Add worker PPE
        db.add_all([
            WorkerPPE(
                worker_id=w1.id,
                item_type="HELMET",
                issuance_date=date.today() - timedelta(days=60),
                expiry_date=date.today() + timedelta(days=300),
                compliance_status="COMPLIANT",
                remarks="Standard IS-2925 Verified Hard Hat with Miner Cap Lamp Mount"
            ),
            WorkerPPE(
                worker_id=w1.id,
                item_type="HIGH_VIS_VEST",
                issuance_date=date.today() - timedelta(days=45),
                expiry_date=date.today() + timedelta(days=320),
                compliance_status="COMPLIANT",
                remarks="Class 3 Reflective Retro-Fluorescent Harness"
            ),
            WorkerPPE(
                worker_id=w1.id,
                item_type="SAFETY_BOOTS",
                issuance_date=date.today() - timedelta(days=90),
                expiry_date=date.today() + timedelta(days=275),
                compliance_status="COMPLIANT",
                remarks="Steel-Toe Ankle Guard Mining Boots (IS 15298)"
            ),
            WorkerPPE(
                worker_id=w1.id,
                item_type="RESPIRATOR",
                issuance_date=date.today() - timedelta(days=30),
                expiry_date=date.today() + timedelta(days=150),
                compliance_status="COMPLIANT",
                remarks="P3 Dust Filter Half-Face Respirator"
            )
        ])

        # Add Worker Trainings & Certifications
        db.add(WorkerTraining(
            worker_id=w1.id,
            program_name="DGMS Statutory Underground Gas, Slope & Helmet Safety (VTC)",
            trainer_name="Senior Safety Officer Amitabh Verma",
            completed_date=date.today() - timedelta(days=90),
            expiry_date=date.today() + timedelta(days=275),
            status="COMPLETED"
        ))
        db.add(WorkerCertification(
            worker_id=w1.id,
            certificate_name="DGMS Certified HEMM Heavy Shovel Operator Class I",
            certificate_number="DGMS-HEMM-2024-884",
            issuing_authority="Directorate General of Mines Safety (DGMS)",
            valid_from=date.today() - timedelta(days=400),
            expiry_date=date.today() + timedelta(days=695),
            verification_status="VERIFIED"
        ))

        # Add Worker Authorization
        db.add(WorkerAuthorization(
            worker_id=w1.id,
            zone_id="ZONE-PIT-01",
            permit_type="UNDERGROUND_ENTRY",
            grant_date=date.today() - timedelta(days=60),
            expiry_date=date.today() + timedelta(days=305),
            status="GRANTED",
            granted_by="Mine Manager Office"
        ))

        # Add Worker Attendances (Shift Clock-In)
        db.add_all([
            WorkerAttendance(
                worker_id=w1.id,
                mine_id=mine.id,
                shift="MORNING",
                check_in=datetime.now(timezone.utc) - timedelta(hours=3, minutes=15),
                status="PRESENT"
            ),
            WorkerAttendance(
                worker_id=w1.id,
                mine_id=mine.id,
                shift="MORNING",
                check_in=datetime.now(timezone.utc) - timedelta(days=1, hours=8),
                check_out=datetime.now(timezone.utc) - timedelta(days=1),
                status="PRESENT"
            ),
            WorkerAttendance(
                worker_id=w1.id,
                mine_id=mine.id,
                shift="MORNING",
                check_in=datetime.now(timezone.utc) - timedelta(days=2, hours=8),
                check_out=datetime.now(timezone.utc) - timedelta(days=2),
                status="PRESENT"
            )
        ])

        # Add Worker Insurance Policies
        db.add_all([
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="LIC Group Coal Mine Safety & Disability Scheme",
                policy_number="LIC-CIL-992182",
                policy_type="ACCIDENTAL_DEATH_DISABILITY",
                coverage_amount=1500000.0,
                start_date=date.today() - timedelta(days=365),
                expiry_date=date.today() + timedelta(days=365),
                nominee_name="Sita Devi",
                nominee_relation="SPOUSE",
                premium_status="ACTIVE",
                tpa_contact_number="1800-425-2255"
            ),
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="New India Cashless Mining Health Cover",
                policy_number="NIA-HLT-440192",
                policy_type="CRITICAL_ILLNESS",
                coverage_amount=500000.0,
                start_date=date.today() - timedelta(days=180),
                expiry_date=date.today() + timedelta(days=185),
                nominee_name="Sita Devi",
                nominee_relation="SPOUSE",
                premium_status="ACTIVE",
                tpa_contact_number="1800-209-1415"
            ),
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="Coal Mines Provident Fund (CMPF) Statutory Pension",
                policy_number="CMPF-KUS-88301",
                policy_type="CMPF_PROVIDENT_FUND",
                coverage_amount=1240000.0,
                start_date=date.today() - timedelta(days=730),
                expiry_date=date.today() + timedelta(days=3650),
                nominee_name="Rahul Kumar",
                nominee_relation="SON",
                premium_status="ACTIVE",
                tpa_contact_number="07759-241022"
            )
        ])

        # Add Worker Leaves & Gate Pass
        db.add_all([
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="CASUAL",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() - timedelta(days=28),
                days_count=3.0,
                reason="Family festival celebration in Bilaspur",
                status="APPROVED",
                approved_by="manager@mineguard.in",
                supervisor_remarks="Approved with relief operator assigned."
            ),
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="SICK_MEDICAL",
                start_date=date.today() - timedelta(days=10),
                end_date=date.today() - timedelta(days=8),
                days_count=2.0,
                reason="Viral fever physician rest prescribed",
                status="APPROVED",
                approved_by="safety@mineguard.in",
                supervisor_remarks="Medical certificate verified by mine dispensary."
            ),
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="GATE_PASS_SHIFT_EXIT",
                start_date=date.today(),
                end_date=date.today(),
                days_count=0.5,
                reason="Urgent banking Aadhaar biometric update in Korba town",
                status="PENDING",
                supervisor_remarks="Shift supervisor review in progress."
            )
        ])

        await db.commit()

        # 7. Compute Initial Risk Scores
        await risk_engine_service.compute_mine_all_zones(db, mine.id)

    # 8. Ensure Worker User and Self-Service Profile always exist idempotently
    from app.models.worker_models import (
        Worker, WorkerAttendance, WorkerTraining, WorkerCertification,
        WorkerPPE, WorkerAuthorization, WorkerInsurance, WorkerLeave,
        WorkerPass, WorkerDocument, WorkerInduction
    )
    worker_user = (await db.execute(select(User).where(User.email == "worker@mineguard.in"))).scalars().first()
    if not worker_user:
        worker_user = User(
            email="worker@mineguard.in",
            hashed_password=get_password_hash("Worker@12345"),
            full_name="Ramesh Kumar",
            role=UserRole.WORKER,
            designation="HEMM Heavy Shovel Operator",
            mine_id=mine.id,
            is_active=True
        )
        db.add(worker_user)
        await db.flush()

    w1 = (await db.execute(select(Worker).where(Worker.employee_id == "EMP-2026-9901"))).scalars().first()
    if not w1:
        w1 = Worker(
            mine_id=mine.id,
            employee_id="EMP-2026-9901",
            full_name="Ramesh Kumar",
            department="UNDERGROUND_OPS",
            role="HEAVY_EQUIPMENT_OPERATOR",
            email="worker@mineguard.in",
            phone="+91 91234 56789",
            emergency_contact_name="Sita Devi",
            emergency_contact_phone="+91 98765 12345",
            joining_date=date.today() - timedelta(days=365),
            status="ACTIVE",
            blood_group="B+",
            rfid_tag="RFID-KUS-8821",
            medical_fitness_status="FIT",
            medical_exam_date=date.today() - timedelta(days=45),
            medical_expiry_date=date.today() + timedelta(days=320)
        )
        db.add(w1)
        await db.flush()
    else:
        w1.email = "worker@mineguard.in"
        w1.blood_group = "B+"
        w1.rfid_tag = "RFID-KUS-8821"
        w1.medical_fitness_status = "FIT"
        w1.medical_exam_date = date.today() - timedelta(days=45)
        w1.medical_expiry_date = date.today() + timedelta(days=320)
        await db.flush()

    # Ensure insurances exist for w1
    existing_ins = (await db.execute(select(WorkerInsurance).where(WorkerInsurance.worker_id == w1.id))).scalars().first()
    if not existing_ins:
        db.add_all([
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="LIC Group Coal Mine Safety & Disability Scheme",
                policy_number="LIC-CIL-992182",
                policy_type="ACCIDENTAL_DEATH_DISABILITY",
                coverage_amount=1500000.0,
                start_date=date.today() - timedelta(days=365),
                expiry_date=date.today() + timedelta(days=365),
                nominee_name="Sita Devi",
                nominee_relation="SPOUSE",
                premium_status="ACTIVE",
                tpa_contact_number="1800-425-2255"
            ),
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="New India Cashless Mining Health Cover",
                policy_number="NIA-HLT-440192",
                policy_type="CRITICAL_ILLNESS",
                coverage_amount=500000.0,
                start_date=date.today() - timedelta(days=180),
                expiry_date=date.today() + timedelta(days=185),
                nominee_name="Sita Devi",
                nominee_relation="SPOUSE",
                premium_status="ACTIVE",
                tpa_contact_number="1800-209-1415"
            ),
            WorkerInsurance(
                worker_id=w1.id,
                policy_provider="Coal Mines Provident Fund (CMPF) Statutory Pension",
                policy_number="CMPF-KUS-88301",
                policy_type="CMPF_PROVIDENT_FUND",
                coverage_amount=1240000.0,
                start_date=date.today() - timedelta(days=730),
                expiry_date=date.today() + timedelta(days=3650),
                nominee_name="Rahul Kumar",
                nominee_relation="SON",
                premium_status="ACTIVE",
                tpa_contact_number="07759-241022"
            )
        ])

    # Ensure leaves exist for w1
    existing_leaves = (await db.execute(select(WorkerLeave).where(WorkerLeave.worker_id == w1.id))).scalars().first()
    if not existing_leaves:
        db.add_all([
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="CASUAL",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() - timedelta(days=28),
                days_count=3.0,
                reason="Family festival celebration in Bilaspur",
                status="APPROVED",
                approved_by="manager@mineguard.in",
                supervisor_remarks="Approved with relief operator assigned."
            ),
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="SICK_MEDICAL",
                start_date=date.today() - timedelta(days=10),
                end_date=date.today() - timedelta(days=8),
                days_count=2.0,
                reason="Viral fever physician rest prescribed",
                status="APPROVED",
                approved_by="safety@mineguard.in",
                supervisor_remarks="Medical certificate verified by mine dispensary."
            ),
            WorkerLeave(
                worker_id=w1.id,
                mine_id=mine.id,
                leave_type="GATE_PASS_SHIFT_EXIT",
                start_date=date.today(),
                end_date=date.today(),
                days_count=0.5,
                reason="Urgent banking Aadhaar biometric update in Korba town",
                status="PENDING",
                supervisor_remarks="Shift supervisor review in progress."
            )
        ])

    # Ensure RFID Pass exists for w1
    existing_pass = (await db.execute(select(WorkerPass).where(WorkerPass.worker_id == w1.id))).scalars().first()
    if not existing_pass:
        db.add(
            WorkerPass(
                worker_id=w1.id,
                mine_id=mine.id,
                rfid_uid="RFID-KUS-8821",
                pass_number="PASS-KUS-8821",
                issue_date=date.today() - timedelta(days=60),
                expiry_date=date.today() + timedelta(days=305),
                status="ACTIVE",
                access_level="UNDERGROUND",
                permitted_zones=["ZONE-PIT-01", "ZONE-BLAST-02", "HAUL_ROAD_01", "GENERAL_SURFACE"],
                issued_by="safety@mineguard.in"
            )
        )

    # Ensure Worker Documents exist for w1 (Includes 1 Auto-Accepted and 1 Needs-Review for live demo)
    existing_docs = (await db.execute(select(WorkerDocument).where(WorkerDocument.worker_id == w1.id))).scalars().first()
    if not existing_docs:
        doc1 = WorkerDocument(
            worker_id=w1.id,
            document_type="FITNESS_CERTIFICATE_FORM_O_P",
            document_number="DGMS/PME/2026/0914",
            issue_date=date.today() - timedelta(days=45),
            expiry_date=date.today() + timedelta(days=320),
            file_path="storage/uploads/worker_fitness_cert_pme.png",
            original_filename="DGMS_Form_P_Periodic_Medical_Exam.png",
            mime_type="image/png",
            file_size_bytes=1048576,
            ocr_status="AUTO_ACCEPTED",
            ocr_confidence=0.94,
            raw_ocr_text="FORM P MEDICAL CERTIFICATE - DGMS APPROVED. EXAM DATE: 2026-01-20. STATUS: FIT.",
            extracted_data={
                "worker_name": "Ramesh Kumar",
                "certificate_number": "DGMS/PME/2026/0914",
                "exam_date": (date.today() - timedelta(days=45)).isoformat(),
                "expiry_date": (date.today() + timedelta(days=320)).isoformat(),
                "fitness_status": "FIT",
                "examining_doctor": "Dr. S. K. Mukherjee, Chief Medical Officer, DGMS Approved"
            },
            verification_status="VERIFIED",
            verified_by="medical_officer@mineguard.in",
            verified_at=utc_now()
        )
        doc2 = WorkerDocument(
            worker_id=w1.id,
            document_type="DGMS_VOCATIONAL_TRAINING",
            document_number="DGMS/VTC/MVR/2026/4412",
            issue_date=date.today() - timedelta(days=60),
            expiry_date=date.today() + timedelta(days=305),
            file_path="storage/uploads/worker_training_cert.png",
            original_filename="DGMS_MVR_1966_Induction_Certificate.png",
            mime_type="image/png",
            file_size_bytes=894210,
            ocr_status="AUTO_ACCEPTED",
            ocr_confidence=0.91,
            raw_ocr_text="MINES VOCATIONAL TRAINING RULES 1966 RULE 28. PASSED WITH HONOURS 92%.",
            extracted_data={
                "worker_name": "Ramesh Kumar",
                "certificate_number": "DGMS/VTC/MVR/2026/4412",
                "training_title": "DGMS Statutory Underground Gas & Helmet Safety Induction",
                "trainer_name": "Sr Safety Officer Amitabh Verma",
                "training_date": (date.today() - timedelta(days=60)).isoformat(),
                "expiry_date": (date.today() + timedelta(days=305)).isoformat(),
                "score_percent": 92.0
            },
            verification_status="VERIFIED",
            verified_by="safety@mineguard.in",
            verified_at=utc_now()
        )
        doc3 = WorkerDocument(
            worker_id=w1.id,
            document_type="BLASTING_COMPETENCY",
            document_number="BLAST-PERMIT-2026-X8",
            issue_date=date.today() - timedelta(days=15),
            expiry_date=date.today() + timedelta(days=165),
            file_path="storage/uploads/blasting_clearance_sample.png",
            original_filename="Highwall_Blasting_Competency_Pass.png",
            mime_type="image/png",
            file_size_bytes=642010,
            ocr_status="NEEDS_REVIEW",
            ocr_confidence=0.74,
            raw_ocr_text="HIGHWALL BLASTING PERMIT. PARTIALLY BLURRED AUTHORITY STAMP. REG NO: BLAST-PERMIT-2026-X8",
            extracted_data={
                "worker_name": "Ramesh Kumar",
                "certificate_number": "BLAST-PERMIT-2026-X8",
                "issue_date": (date.today() - timedelta(days=15)).isoformat(),
                "expiry_date": (date.today() + timedelta(days=165)).isoformat(),
                "permit_type": "HIGHWALL_CONTROLLED_BLASTING"
            },
            validation_errors=[
                "OCR confidence (0.74) is below statutory threshold (0.85)",
                "Official authority seal partially obscured by fold in paper"
            ],
            verification_status="PENDING"
        )
        db.add_all([doc1, doc2, doc3])

    # Ensure Worker Induction exists for w1
    existing_ind = (await db.execute(select(WorkerInduction).where(WorkerInduction.worker_id == w1.id))).scalars().first()
    if not existing_ind:
        db.add(
            WorkerInduction(
                worker_id=w1.id,
                mine_id=mine.id,
                induction_type="INITIAL_STATUTORY",
                training_title="DGMS Statutory Underground Gas & Helmet Safety Induction",
                trainer_name="Sr Safety Officer Amitabh Verma, DGMS Certified Instructor",
                training_date=date.today() - timedelta(days=60),
                validity_months=12,
                expiry_date=date.today() + timedelta(days=305),
                score_percent=92.0,
                verification_status="VERIFIED",
                status="COMPLETED",
                remarks="Full marks in methane detection and self-contained self-rescuer (SCSR) donning."
            )
        )

    await db.commit()

    return ApiResponse(
        message="Demo synthetic coal mine data (Modules 1, 2, and 3) successfully seeded!",
        data={
            "mine_code": "MINE-SECL-KUS-01",
            "demo_credentials": {
                "admin": {"email": "admin@mineguard.in", "password": "Admin@12345"},
                "safety_officer": {"email": "safety@mineguard.in", "password": "Safety@12345"},
                "mine_manager": {"email": "manager@mineguard.in", "password": "Manager@12345"},
                "worker": {"email": "worker@mineguard.in", "password": "Worker@12345"}
            }
        }
    )


@router.post("/simulate-violation", response_model=ApiResponse[Dict[str, Any]])
async def simulate_ai_violation(db: AsyncSession = Depends(get_db)):
    """
    Simulates a live AI camera event (e.g. Worker without Hardhat & Hi-Vis Vest).
    """
    stmt = select(CameraRegistry).where(CameraRegistry.status == "ACTIVE")
    res = await db.execute(stmt)
    cam = res.scalars().first()
    if not cam:
        return ApiResponse(success=False, message="Please run /demo/seed first to create cameras")

    payload = DetectionIngestRequest(
        camera_id=cam.id,
        detection_type="PPE_VIOLATION",
        raw_class_name="NO_HELMET_AND_VEST",
        confidence_score=0.92,
        bounding_box_json={"box": [0.45, 0.20, 0.55, 0.65]},
        metadata={"simulated": True, "weather": "Cloudy", "lighting": "Optimal"}
    )
    result = await cctv_service.process_detection_ingest(db=db, payload=payload)
    return ApiResponse(message="Simulated CCTV detection processed", data=result)


@router.post("/simulate-ocr", response_model=ApiResponse[Dict[str, Any]])
async def simulate_certificate_ocr(db: AsyncSession = Depends(get_db)):
    """
    Generates a synthetic DGMS fitness certificate and runs the complete OCR pipeline.
    """
    stmt = select(EquipmentAsset).where(EquipmentAsset.status == "ACTIVE")
    res = await db.execute(stmt)
    asset = res.scalars().first()
    if not asset:
        return ApiResponse(success=False, message="Please run /demo/seed first to create equipment")

    # Generate synthetic image
    cert_path = generate_synthetic_dgms_certificate(
        output_filename=f"dgms_cert_{asset.asset_code}.png",
        cert_number=f"DGMS/EZ/HEMM/2026/{asset.asset_code}",
        asset_code=asset.asset_code,
        make_model=asset.make_model,
        issue_date="2026-03-01",
        expiry_date="2027-02-28",
        status_text="FIT FOR HEAVY OPENCAST HAULAGE OPERATIONS"
    )

    doc = await equipment_service.process_document_upload(
        db=db,
        asset_id=asset.id,
        document_type="DGMS_FITNESS_CERTIFICATE",
        file_path=cert_path,
        file_name=f"dgms_cert_{asset.asset_code}.png",
        file_size=102400,
        mime_type="image/png"
    )

    return ApiResponse(
        message="Simulated DGMS certificate generated & OCR pipeline completed",
        data={
            "document_id": doc.id,
            "ocr_confidence": doc.ocr_confidence,
            "extracted_expiry": str(doc.valid_until),
            "updated_asset_expiry": str(asset.fitness_expiry_date),
            "verification_status": doc.verification_status
        }
    )


@router.post("/simulate-gas-breach", response_model=ApiResponse[Dict[str, Any]])
async def simulate_gas_breach(db: AsyncSession = Depends(get_db)):
    """
    Simulates high methane gas telemetry (CH4 = 1.35%) breaching DGMS limits.
    """
    stmt = select(MineZone).limit(1)
    res = await db.execute(stmt)
    zone = res.scalars().first()
    if not zone:
        return ApiResponse(success=False, message="Please run /demo/seed first")

    reading = await environment_service.record_reading(
        db=db,
        payload=EnvironmentalReadingCreate(
            mine_id=zone.mine_id,
            zone_id=zone.id,
            sensor_code="LORA-GAS-NODE-04",
            methane_ch4_pct=1.35,  # Above 1.25% Critical threshold
            carbon_monoxide_co_ppm=58.0,
            oxygen_o2_pct=18.4,
            temperature_c=34.5,
            humidity_pct=88.0,
            source="LORA_TELEMETRY"
        )
    )

    return ApiResponse(
        message="Gas breach telemetry recorded. Emergency alarm alert triggered.",
        data={
            "reading_id": reading.id,
            "is_breach": reading.is_breach,
            "breach_details": reading.breach_details_json
        }
    )
