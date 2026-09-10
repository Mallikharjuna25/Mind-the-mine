"""
Synthetic Demo Asset Generator
Generates realistic demo test assets:
1. Synthetic CCTV snapshots with bounding box overlays for PPE, Restricted Zones, and Fire.
2. Synthetic DGMS statutory equipment fitness certificates with authentic text and layout for OCR testing.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date, timedelta

ASSET_DIR = "storage/synthetic_assets"
os.makedirs(ASSET_DIR, exist_ok=True)


def generate_synthetic_cctv_frame(
    output_filename: str = "cctv_snapshot_demo.jpg",
    detection_type: str = "PPE_VIOLATION",
    label: str = "NO_HELMET"
) -> str:
    """
    Generates a realistic 1280x720 CCTV snapshot image with camera metadata,
    timestamp, coal mine pit backdrop colors, and bounding boxes.
    """
    filepath = os.path.join(ASSET_DIR, output_filename)
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(30, 34, 42))  # Dark industrial base
    draw = ImageDraw.Draw(img)

    # Draw simulated mine pit terrain / benches
    draw.polygon([(0, 400), (1280, 450), (1280, 720), (0, 720)], fill=(45, 42, 38))
    draw.polygon([(200, 300), (1080, 320), (1280, 500), (0, 480)], fill=(55, 50, 45))
    draw.rectangle([(450, 380), (800, 580)], fill=(70, 70, 75), outline=(100, 100, 110), width=3)  # Heavy Excavator

    # Draw simulated worker
    worker_box = [600, 400, 680, 560]
    draw.rectangle(worker_box, fill=(50, 60, 80))  # Worker body

    # Draw Bounding Box and Detection Label
    box_color = (239, 68, 68) if "VIOLATION" in detection_type or "FIRE" in detection_type else (34, 197, 94)
    draw.rectangle([590, 380, 690, 570], outline=box_color, width=4)
    
    # Label banner
    draw.rectangle([590, 350, 750, 380], fill=box_color)
    draw.text((595, 355), f"{label} (0.92)", fill=(255, 255, 255))

    # CCTV OSD (On-Screen Display) Metadata
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    osd_text = f"CAM-01 [PIT-ZONE-A] | FPS: 25.0 | {timestamp_str} | AI MINEGUARD LIVE"
    draw.rectangle([0, 0, 1280, 40], fill=(0, 0, 0))
    draw.text((20, 12), osd_text, fill=(0, 255, 128))

    img.save(filepath, format="JPEG", quality=85)
    return filepath


def generate_synthetic_dgms_certificate(
    output_filename: str = "dgms_fitness_cert_demo.png",
    cert_number: str = "DGMS/EZ/HEMM/2026/8841",
    asset_code: str = "HEMM-DUMP-042",
    make_model: str = "Caterpillar 777E",
    issue_date: str = "2026-01-15",
    expiry_date: str = "2027-01-14",
    status_text: str = "FIT FOR UNDERGROUND & OPENCAST HAULAGE"
) -> str:
    """
    Generates a realistic statutory DGMS Fitness Certificate image with clean typography
    and structured layout that can be parsed by the OCR pipeline.
    """
    filepath = os.path.join(ASSET_DIR, output_filename)
    width, height = 900, 1200
    img = Image.new("RGB", (width, height), color=(252, 252, 250))
    draw = ImageDraw.Draw(img)

    # Decorative Border
    draw.rectangle([30, 30, 870, 1170], outline=(100, 40, 20), width=4)
    draw.rectangle([40, 40, 860, 1160], outline=(150, 100, 50), width=1)

    # Header
    draw.text((240, 70), "GOVERNMENT OF INDIA", fill=(0, 0, 0))
    draw.text((180, 100), "MINISTRY OF LABOUR & EMPLOYMENT", fill=(0, 0, 0))
    draw.text((150, 130), "DIRECTORATE GENERAL OF MINES SAFETY (DGMS)", fill=(120, 20, 20))
    draw.text((220, 165), "STATUTORY FITNESS & SAFETY CERTIFICATE", fill=(0, 0, 100))
    draw.line([(60, 200), (840, 200)], fill=(0, 0, 0), width=2)

    # Certificate Fields
    fields = [
        ("CERTIFICATE NO:", cert_number),
        ("ISSUING REGION:", "Eastern Zone, Dhanbad Directorate"),
        ("STATUTORY AUTHORITY:", "DGMS Inspection Division"),
        ("EQUIPMENT CODE:", asset_code),
        ("EQUIPMENT TYPE / MODEL:", make_model),
        ("SERIAL NUMBER:", "SN-CAT777-99214"),
        ("INSPECTION DATE:", issue_date),
        ("VALIDITY EXPIRY DATE:", expiry_date),
        ("STATUTORY STATUS:", status_text),
        ("COMPLIANCE REGULATION:", "Coal Mines Regulations 2017, Regulation 130")
    ]

    y = 240
    for label, val in fields:
        draw.text((80, y), label, fill=(50, 50, 50))
        draw.text((360, y), val, fill=(10, 10, 10))
        draw.line([(80, y + 30), (820, y + 30)], fill=(220, 220, 220), width=1)
        y += 55

    # Seal & Signature Simulation
    draw.ellipse([580, 860, 740, 1020], outline=(180, 30, 30), width=3)
    draw.text((610, 920), "OFFICIAL SEAL", fill=(180, 30, 30))
    draw.text((600, 950), "DGMS GOVT OF INDIA", fill=(180, 30, 30))
    
    draw.text((100, 980), "Authorized Inspector Signature: __________________", fill=(50, 50, 50))
    draw.text((100, 1010), "Dr. S. K. Mukherjee, Deputy Director of Mines Safety", fill=(80, 80, 80))

    img.save(filepath, format="PNG")
    return filepath
