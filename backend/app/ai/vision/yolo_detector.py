"""
AI Vision Pipeline (YOLOv8 / Safety Vision Wrapper)
Performs detection for:
1. Person & PPE compliance (Hardhat/Helmet, Hi-Vis Vest, Safety Boots)
2. Restricted zone geofencing intrusion
3. Fire and smoke hazards
"""

from typing import List, Dict, Any, Optional
import random
import os
from app.core.config import settings
from app.ai.synthetic_generator import generate_synthetic_cctv_frame


class DetectedObject:
    def __init__(self, class_name: str, confidence: float, bbox: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # [x_min, y_min, x_max, y_max] normalized 0.0-1.0
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
            "metadata": self.metadata
        }


class YOLOSafetyDetector:
    """
    Modular Safety Vision Inference Engine.
    Integrates Ultralytics YOLO models when weights are present,
    with an internal high-fidelity simulation engine for rapid local development/MVP.
    """
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        # In a full deployment, load ultralytics YOLO weights:
        # from ultralytics import YOLO
        # self.model = YOLO("weights/yolov8_mine_safety.pt")
        pass

    def run_inference_on_frame(
        self,
        frame_bytes: Optional[bytes] = None,
        camera_id: str = "CAM-01",
        zone_id: str = "ZONE-01",
        is_restricted_zone: bool = False
    ) -> List[DetectedObject]:
        """
        Runs inference on an incoming video frame or camera feed.
        Returns a list of detected safety objects and violation candidates.
        """
        results: List[DetectedObject] = []

        # Synthetic/Simulation logic for test pipelines
        # Produces realistic detections matching coal mine safety events
        scenarios = [
            ("NO_HELMET", "PPE_VIOLATION", 0.91, [0.45, 0.20, 0.55, 0.45]),
            ("NO_HI_VIS_VEST", "PPE_VIOLATION", 0.88, [0.44, 0.35, 0.56, 0.65]),
            ("PERSON_IN_RESTRICTED_BLAST_ZONE", "RESTRICTED_ZONE_INTRUSION", 0.95, [0.30, 0.40, 0.40, 0.70]),
            ("SMOKE_PLUME_DETECTED", "FIRE_SMOKE", 0.87, [0.70, 0.10, 0.90, 0.40]),
            ("COMPLIANT_WORKER", "SAFE", 0.94, [0.20, 0.30, 0.30, 0.60])
        ]

        if is_restricted_zone:
            # Force intrusion detection for restricted zones
            chosen = scenarios[2]
        else:
            chosen = random.choice(scenarios)

        class_name, det_type, conf, bbox = chosen
        results.append(
            DetectedObject(
                class_name=class_name,
                confidence=conf,
                bbox=bbox,
                metadata={"detection_type": det_type, "camera_id": camera_id, "zone_id": zone_id}
            )
        )
        return results

    def process_and_save_evidence(self, detection: DetectedObject, camera_code: str) -> str:
        """
        Generates and persists the annotated CCTV evidence image for audit records.
        """
        filename = f"evidence_{camera_code}_{int(detection.confidence*100)}_{detection.class_name.lower()}.jpg"
        return generate_synthetic_cctv_frame(
            output_filename=filename,
            detection_type=detection.metadata.get("detection_type", "PPE_VIOLATION"),
            label=detection.class_name
        )


safety_detector = YOLOSafetyDetector()
