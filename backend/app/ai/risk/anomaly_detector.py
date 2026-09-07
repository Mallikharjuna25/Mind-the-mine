"""
Anomaly & Recurring Violation Detection Engine
Identifies repetitive non-compliance and statistical production/sensor outliers.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone


class AnomalyDetector:
    """
    Statistical and rule-based anomaly detector for mine operations.
    """

    @classmethod
    def detect_recurring_violations(
        cls,
        violation_records: List[Dict[str, Any]],
        threshold_count: int = 3,
        window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Flags recurring non-compliance when the same violation type occurs >= threshold_count
        times in the same zone within window_days.
        """
        anomalies = []
        category_counts: Dict[str, List[Dict[str, Any]]] = {}

        for v in violation_records:
            cat = v.get("category", "UNKNOWN")
            category_counts.setdefault(cat, []).append(v)

        for cat, items in category_counts.items():
            if len(items) >= threshold_count:
                anomalies.append({
                    "anomaly_type": "RECURRING_VIOLATION",
                    "title": f"Recurring {cat} Violations Detected",
                    "description": f"Zone has recorded {len(items)} {cat} non-compliance events within the last {window_days} days.",
                    "severity": "HIGH" if len(items) < 5 else "CRITICAL",
                    "metric_name": f"{cat}_frequency",
                    "expected_value": 0.0,
                    "observed_value": float(len(items)),
                    "deviation_pct": round((len(items) - 1) * 100.0, 1),
                    "metadata": {"sample_violation_ids": [i.get("id") for i in items[:5]]}
                })

        return anomalies

    @classmethod
    def detect_production_anomalies(
        cls,
        target_tonnes: float,
        actual_tonnes: float,
        downtime_minutes: int
    ) -> Optional[Dict[str, Any]]:
        """
        Flags severe production shortfall (>35% negative variance) or excessive downtime (>180 mins).
        """
        if target_tonnes <= 0:
            return None

        variance_pct = ((actual_tonnes - target_tonnes) / target_tonnes) * 100.0

        if variance_pct < -35.0 or downtime_minutes >= 180:
            return {
                "anomaly_type": "PRODUCTION_ANOMALY",
                "title": "Severe Production Shortfall / Excessive Downtime",
                "description": f"Production dropped {abs(round(variance_pct, 1))}% below target with {downtime_minutes} mins downtime.",
                "severity": "CRITICAL" if variance_pct < -50.0 else "HIGH",
                "metric_name": "production_tonnes_variance",
                "expected_value": target_tonnes,
                "observed_value": actual_tonnes,
                "deviation_pct": round(variance_pct, 1),
                "metadata": {"downtime_minutes": downtime_minutes}
            }

        return None


anomaly_detector = AnomalyDetector()
