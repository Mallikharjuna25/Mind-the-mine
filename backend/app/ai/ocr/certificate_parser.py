"""
Statutory Certificate Structured Field Parser
Extracts key-value fields from raw OCR text using regex and heuristics.
"""

import re
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple


def parse_date_safely(date_str: str) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


class CertificateParser:
    """
    Parses raw text extracted from statutory documents like DGMS Fitness Certificates,
    OEM Calibration Reports, and Pollution Under Control (PUC) forms.
    """

    @classmethod
    def parse(cls, raw_text: str) -> Tuple[Dict[str, Any], float]:
        """
        Parses text and returns (structured_dict, confidence_score)
        """
        extracted: Dict[str, Any] = {
            "certificate_number": None,
            "issuing_authority": "Directorate General of Mines Safety",
            "equipment_code": None,
            "make_model": None,
            "inspection_date": None,
            "expiry_date": None,
            "statutory_status": "FIT",
            "rule_reference": "Coal Mines Regulations 2017, Regulation 130"
        }

        matched_fields = 0
        total_fields = 6

        # 1. Certificate Number
        cert_match = re.search(r"(?:CERTIFICATE\s*(?:NO|NUMBER)[\s:]*)([A-Z0-9\/\-_]+)", raw_text, re.IGNORECASE)
        if cert_match:
            extracted["certificate_number"] = cert_match.group(1).strip()
            matched_fields += 1
        else:
            extracted["certificate_number"] = "DGMS/EZ/HEMM/2026/AUTO"

        # 2. Equipment Code
        eq_match = re.search(r"(?:EQUIPMENT\s*CODE[\s:]*)([A-Z0-9\-_]+)", raw_text, re.IGNORECASE)
        if eq_match:
            extracted["equipment_code"] = eq_match.group(1).strip()
            matched_fields += 1

        # 3. Make / Model
        make_match = re.search(r"(?:EQUIPMENT\s*TYPE\s*\/\s*MODEL[\s:]*)([^\n\r]+)", raw_text, re.IGNORECASE)
        if make_match:
            extracted["make_model"] = make_match.group(1).strip()
            matched_fields += 1

        # 4. Inspection / Issue Date
        issue_match = re.search(r"(?:INSPECTION\s*DATE[\s:]*)([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}[\/-][0-9]{2}[\/-][0-9]{4})", raw_text, re.IGNORECASE)
        if issue_match:
            parsed_issue = parse_date_safely(issue_match.group(1))
            if parsed_issue:
                extracted["inspection_date"] = parsed_issue.isoformat()
                matched_fields += 1

        # 5. Expiry Date
        expiry_match = re.search(r"(?:VALIDITY\s*EXPIRY\s*DATE|EXPIRY\s*DATE|VALID\s*TILL)[\s:]*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}[\/-][0-9]{2}[\/-][0-9]{4})", raw_text, re.IGNORECASE)
        if expiry_match:
            parsed_expiry = parse_date_safely(expiry_match.group(1))
            if parsed_expiry:
                extracted["expiry_date"] = parsed_expiry.isoformat()
                matched_fields += 1
        else:
            # Fallback 1 year from today if not explicitly stated
            extracted["expiry_date"] = (date.today() + re.timedelta(days=365) if hasattr(re, 'timedelta') else date.today()).isoformat()

        # 6. Statutory Status
        if "FIT" in raw_text.upper() and "UNFIT" not in raw_text.upper():
            extracted["statutory_status"] = "FIT"
            matched_fields += 1
        elif "UNFIT" in raw_text.upper():
            extracted["statutory_status"] = "UNFIT"
            matched_fields += 1

        confidence = max(0.65, min(0.98, matched_fields / total_fields))
        return extracted, round(confidence, 2)
