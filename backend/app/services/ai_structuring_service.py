import re
from typing import Dict, Any

class AIIncidentStructuringService:
    @staticmethod
    def structure_unstructured_input(raw_text: str) -> Dict[str, Any]:
        text_lower = raw_text.lower()
        
        incident_type = "SAFETY_OBSERVATION"
        severity = "MODERATE"
        hazard = "UNSPECIFIED_HAZARD"
        location = "GENERAL_MINE_AREA"
        injury = "NONE_REPORTED"
        confidence = 0.88
        reasoning_points = []

        # 1. Detect Incident Type
        if any(w in text_lower for w in ["fire", "smoke", "spark", "flame", "burning"]):
            incident_type = "FIRE"
            hazard = "FIRE_AND_SMOKE"
            severity = "HIGH"
            reasoning_points.append("Keywords detected combustion/flame indicator")
        elif any(w in text_lower for w in ["dumper", "truck", "loader", "excavator", "engine", "brake", "mechanical", "breakdown", "overheating"]):
            incident_type = "EQUIPMENT_FAILURE"
            hazard = "HEAVY_MACHINERY_MALFUNCTION"
            reasoning_points.append("Keywords indicated machinery or vehicle mechanical failure")
        elif any(w in text_lower for w in ["roof", "collapse", "strata", "fall of ground", "rock fall"]):
            incident_type = "ROOF_FALL"
            hazard = "STRATA_COLLAPSE"
            severity = "CRITICAL"
            reasoning_points.append("Strata/roof collapse detected - escalated to critical")
        elif any(w in text_lower for w in ["gas", "methane", "ch4", "co2", "ventilation", "asphyxia"]):
            incident_type = "GAS_HAZARD"
            hazard = "TOXIC_OR_INFLAMMABLE_GAS"
            severity = "HIGH"
            reasoning_points.append("Gas or ventilation anomaly keywords found")
        elif any(w in text_lower for w in ["spill", "effluent", "drainage", "water accumulation", "dust"]):
            incident_type = "ENVIRONMENTAL"
            hazard = "ENVIRONMENTAL_POLLUTION"
            reasoning_points.append("Environmental disturbance terminology identified")

        # 2. Detect Severity
        if any(w in text_lower for w in ["fatal", "death", "casualty", "collapse of main bench"]):
            severity = "FATAL"
            confidence = 0.95
        elif any(w in text_lower for w in ["critical", "explosion", "severe", "major emergency", "urgent"]):
            severity = "CRITICAL"
        elif any(w in text_lower for w in ["major", "hospital", "fracture", "heavy damage"]):
            severity = "MAJOR"
        elif any(w in text_lower for w in ["minor", "slight", "small", "superficial", "no disruption"]):
            severity = "MINOR"

        # 3. Detect Injury
        if any(w in text_lower for w in ["no injury", "no injuries", "uninjured", "safe", "everyone fine"]):
            injury = "NONE_REPORTED"
            reasoning_points.append("Explicit declaration of zero injuries confirmed")
        elif any(w in text_lower for w in ["first aid", "bruise", "cut", "scratched"]):
            injury = "FIRST_AID_ADMINISTERED"
        elif any(w in text_lower for w in ["injured", "hospitalized", "fracture", "bleeding"]):
            injury = "MEDICAL_TREATMENT_REQUIRED"
            if severity in ["MINOR", "MODERATE"]:
                severity = "MAJOR"

        # 4. Detect Location Context
        loc_patterns = [
            (r"\bhaul\s*road\b", "HAUL_ROAD"),
            (r"\bpit[\s-]*\d*\b", "OPENCAST_PIT"),
            (r"\bbench[\s-]*\d*\b", "WORKING_BENCH"),
            (r"\bface[\s-]*\d*\b", "COAL_SEAM_FACE"),
            (r"\bconveyor[\s-]*\d*\b", "CONVEYOR_BELT"),
            (r"\b(workshop|garage)\b", "HEMM_WORKSHOP"),
            (r"\b(substation|switchgear)\b", "ELECTRICAL_SUBSTATION"),
            (r"\b(magazine|explosive store)\b", "EXPLOSIVES_MAGAZINE")
        ]
        for pattern, loc_tag in loc_patterns:
            match = re.search(pattern, text_lower)
            if match:
                location = loc_tag
                reasoning_points.append(f"Spatial anchor identified: {location}")
                break

        return {
            "suggested_incident_type": incident_type,
            "suggested_severity": severity,
            "suggested_hazard": hazard,
            "suggested_location": location,
            "suggested_injury": injury,
            "confidence_score": min(0.99, max(0.70, confidence)),
            "reasoning": "; ".join(reasoning_points) or "Extracted using MineGuard NLP parser"
        }
