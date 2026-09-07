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

        # 5. Add Demo Users (Super Admin, Safety Officer, Mine Manager)
        users_data = [
            ("admin@mineguard.in", "Admin@12345", "Director General / Super Admin", UserRole.SUPER_ADMIN, "Chief Inspector of Mines"),
            ("manager@mineguard.in", "Manager@12345", "Rajesh Sharma", UserRole.MINE_MANAGER, "General Manager (Kusmunda)"),
            ("safety@mineguard.in", "Safety@12345", "Amitabh Verma", UserRole.SAFETY_OFFICER, "Senior Safety Officer"),
            ("env@mineguard.in", "Env@12345", "Pooja Banerjee", UserRole.ENVIRONMENT_OFFICER, "Environmental Engineer")
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

        await db.commit()

        # 6. Compute Initial Risk Scores
        await risk_engine_service.compute_mine_all_zones(db, mine.id)

    return ApiResponse(
        message="Demo synthetic coal mine data successfully seeded!",
        data={
            "mine_code": "MINE-SECL-KUS-01",
            "demo_credentials": {
                "admin": {"email": "admin@mineguard.in", "password": "Admin@12345"},
                "safety_officer": {"email": "safety@mineguard.in", "password": "Safety@12345"},
                "mine_manager": {"email": "manager@mineguard.in", "password": "Manager@12345"}
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
