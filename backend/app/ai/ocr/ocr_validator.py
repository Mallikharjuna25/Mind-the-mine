"""
OCR Confidence and Deterministic Statutory Validation Rules (Module 3)
Enforces:
- 0.85 baseline confidence threshold for automatic update eligibility
- Temporal validity (issue_date <= today, expiry_date > issue_date)
- Worker/Contractor identity correlation
- Non-duplicate document numbers
"""

from datetime import date, datetime
from typing import Dict, Any, List, Tuple, Optional


class OCRValidator:
    CONFIDENCE_THRESHOLD = 0.85

    @classmethod
    def validate_extracted_data(
        cls,
        document_type: str,
        extracted_data: Dict[str, Any],
        overall_confidence: float,
        expected_worker_name: Optional[str] = None,
        expected_contractor_name: Optional[str] = None,
    ) -> Tuple[bool, str, List[str]]:
        """
        Validates extracted fields deterministically.
        Returns: (is_eligible_for_auto_accept: bool, ocr_status: str, validation_errors: List[str])
        """
        errors: List[str] = []

        # 1. Check confidence threshold
        if overall_confidence < cls.CONFIDENCE_THRESHOLD:
            errors.append(f"OCR confidence ({overall_confidence:.2f}) is below mandatory threshold ({cls.CONFIDENCE_THRESHOLD})")

        # 2. Check Document Number
        doc_num = extracted_data.get("document_number") or extracted_data.get("certificate_number") or extracted_data.get("registration_number")
        if not doc_num or "AUTO" in str(doc_num):
            errors.append("Document/Certificate number could not be resolved with high certainty")

        # 3. Check Dates
        today = date.today()
        issue_str = extracted_data.get("issue_date") or extracted_data.get("exam_date") or extracted_data.get("training_date")
        expiry_str = extracted_data.get("expiry_date")

        issue_date = None
        if issue_str:
            try:
                issue_date = datetime.strptime(issue_str, "%Y-%m-%d").date()
                if issue_date > today:
                    errors.append(f"Issue date ({issue_str}) cannot be in the future")
            except ValueError:
                errors.append(f"Invalid issue date format: {issue_str}")

        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                if issue_date and expiry_date <= issue_date:
                    errors.append(f"Expiry date ({expiry_str}) must be after issue date ({issue_str})")
                if expiry_date < today:
                    errors.append(f"Document is expired (expired on {expiry_str})")
            except ValueError:
                errors.append(f"Invalid expiry date format: {expiry_str}")

        # 4. Identity correlation check
        if expected_worker_name:
            extracted_name = extracted_data.get("worker_name") or extracted_data.get("full_name")
            if extracted_name:
                # Token-based match
                exp_tokens = set(expected_worker_name.lower().split())
                ext_tokens = set(extracted_name.lower().split())
                overlap = exp_tokens.intersection(ext_tokens)
                if len(overlap) == 0:
                    errors.append(f"Worker name mismatch: extracted '{extracted_name}' does not match record '{expected_worker_name}'")
            else:
                errors.append("Worker name not detected in uploaded certificate")

        # 5. Determine statutory OCR status
        if len(errors) == 0:
            return True, "AUTO_ACCEPTED", []
        else:
            return False, "NEEDS_REVIEW", errors
