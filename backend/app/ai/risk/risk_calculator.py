"""
Unified Risk Calculation Engine
Implements deterministic, explainable composite risk scoring:
R = w_v * V + w_e * E + w_p * P + w_s * S
"""

from typing import Dict, Any, Tuple
from app.core.config import settings


class RiskBand:
    LOW = "LOW"            # 0.0 - 25.0
    MODERATE = "MODERATE"  # 25.1 - 50.0
    HIGH = "HIGH"          # 50.1 - 75.0
    CRITICAL = "CRITICAL"  # 75.1 - 100.0


class UnifiedRiskCalculator:
    """
    Computes explainable, multi-factor risk scores per mine zone and mine aggregate.
    """

    @classmethod
    def calculate_composite_score(
        cls,
        active_violations_count: int,
        critical_violations_count: int,
        high_violations_count: int,
        environmental_breaches_count: int,
        production_variance_pct: float,
        overdue_equipment_count: int,
        zone_risk_weight: float = 1.0
    ) -> Tuple[float, str, Dict[str, float], Dict[str, Any]]:
        """
        Calculates composite score (0-100), risk band, subscores, and contributing factors.
        """
        # 1. Violation Subscore (V)
        # Severity weights: Critical=25, High=15, Medium/Other=5
        raw_v = (critical_violations_count * 25.0) + (high_violations_count * 15.0) + (active_violations_count * 5.0)
        v_subscore = min(100.0, raw_v * zone_risk_weight)

        # 2. Environmental Subscore (E)
        # Each active gas/dust breach adds 30 points
        e_subscore = min(100.0, environmental_breaches_count * 30.0)

        # 3. Production Subscore (P)
        # Significant negative variance or high downtime increases operational stress risk
        p_subscore = min(100.0, max(0.0, abs(min(0.0, production_variance_pct)) * 2.5))

        # 4. Equipment Subscore (S)
        # Each expired statutory certificate adds 25 points
        s_subscore = min(100.0, overdue_equipment_count * 25.0)

        # Weighted Composite Score: R = w_v*V + w_e*E + w_p*P + w_s*S
        composite = (
            settings.RISK_WEIGHT_VIOLATIONS * v_subscore +
            settings.RISK_WEIGHT_ENVIRONMENT * e_subscore +
            settings.RISK_WEIGHT_PRODUCTION * p_subscore +
            settings.RISK_WEIGHT_EQUIPMENT_SAFETY * s_subscore
        )
        composite = round(min(100.0, max(0.0, composite)), 1)

        # Determine Risk Band
        if composite <= 25.0:
            band = RiskBand.LOW
        elif composite <= 50.0:
            band = RiskBand.MODERATE
        elif composite <= 75.0:
            band = RiskBand.HIGH
        else:
            band = RiskBand.CRITICAL

        subscores = {
            "violation_subscore": round(v_subscore, 1),
            "environment_subscore": round(e_subscore, 1),
            "production_subscore": round(p_subscore, 1),
            "equipment_subscore": round(s_subscore, 1)
        }

        factors = {
            "primary_driver": max(subscores, key=subscores.get),
            "zone_weight_applied": zone_risk_weight,
            "critical_violations": critical_violations_count,
            "environmental_breaches": environmental_breaches_count,
            "overdue_equipment": overdue_equipment_count,
            "production_variance_pct": production_variance_pct
        }

        return composite, band, subscores, factors


risk_calculator = UnifiedRiskCalculator()
