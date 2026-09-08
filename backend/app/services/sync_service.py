from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.module2_models import (
    FieldReport, InspectionAudit, IncidentRecord, FieldVerification
)
from backend.app.schemas.module2_schemas import (
    BatchSyncRequest, BatchSyncResponse, BatchSyncResultItem
)
from backend.app.services.audit_service import AuditService

class SyncService:
    @staticmethod
    def process_batch(db: Session, batch: BatchSyncRequest) -> BatchSyncResponse:
        results: List[BatchSyncResultItem] = []

        # 1. Process Field Reports
        for rep in batch.field_reports:
            existing = db.query(FieldReport).filter(FieldReport.client_id == rep.client_id).first()
            if existing:
                results.append(BatchSyncResultItem(
                    client_id=rep.client_id,
                    server_id=existing.id,
                    entity_type="FIELD_REPORT",
                    status="SYNCED",
                    message="Already synced (idempotent ACK)"
                ))
            else:
                new_report = FieldReport(
                    client_id=rep.client_id,
                    mine_id=rep.mine_id,
                    zone_id=rep.zone_id,
                    officer_id=batch.officer_id,
                    category=rep.category,
                    severity=rep.severity,
                    description=rep.description,
                    latitude=rep.latitude,
                    longitude=rep.longitude,
                    accuracy=rep.accuracy,
                    capture_timestamp=rep.capture_timestamp or datetime.now(timezone.utc),
                    evidence_urls=rep.evidence_urls,
                    status="REPORTED",
                    sync_state="SYNCED"
                )
                db.add(new_report)
                db.flush()

                # Trigger field verification if report is critical/high
                if rep.severity in ["HIGH", "CRITICAL"]:
                    verification = FieldVerification(
                        issue_type="FIELD_REPORT",
                        source_id=new_report.id,
                        mine_id=rep.mine_id,
                        status="REPORTED",
                        remediation_notes=f"Auto-generated from high severity field observation: {rep.category}",
                        before_evidence_urls=rep.evidence_urls
                    )
                    db.add(verification)

                AuditService.log_event(db, "FIELD_REPORT", new_report.id, "SYNC_CREATED", batch.officer_id, {
                    "client_id": rep.client_id, "category": rep.category
                })

                results.append(BatchSyncResultItem(
                    client_id=rep.client_id,
                    server_id=new_report.id,
                    entity_type="FIELD_REPORT",
                    status="SYNCED",
                    message="Successfully synced to central database"
                ))

        # 2. Process Inspection Audits
        for audit in batch.inspections:
            existing = db.query(InspectionAudit).filter(InspectionAudit.client_id == audit.client_id).first()
            if existing:
                results.append(BatchSyncResultItem(
                    client_id=audit.client_id,
                    server_id=existing.id,
                    entity_type="INSPECTION",
                    status="SYNCED",
                    message="Already synced (idempotent ACK)"
                ))
            else:
                # Calculate overall compliance score
                total_items = len(audit.items_results)
                failed_items = [it for it in audit.items_results if it.result_status == "FAIL"]
                passed_items = [it for it in audit.items_results if it.result_status == "PASS"]
                
                score = 100.0
                if total_items > 0:
                    score = round((len(passed_items) / max(1, len(passed_items) + len(failed_items))) * 100.0, 1)

                new_audit = InspectionAudit(
                    client_id=audit.client_id,
                    template_id=audit.template_id,
                    mine_id=audit.mine_id,
                    zone_id=audit.zone_id,
                    inspector_id=batch.officer_id,
                    scheduled_date=audit.scheduled_date or datetime.now(timezone.utc),
                    shift=audit.shift,
                    status="SUBMITTED",
                    overall_score=score,
                    summary_findings=audit.summary_findings,
                    items_results=[it.model_dump() for it in audit.items_results]
                )
                db.add(new_audit)
                db.flush()

                # Automatically spawn corrective action verifications for failed checklist items
                for failed in failed_items:
                    verification = FieldVerification(
                        issue_type="INSPECTION_FAIL",
                        source_id=new_audit.id,
                        mine_id=audit.mine_id,
                        status="REPORTED",
                        remediation_notes=f"Checklist Item [{failed.item_code}] Failed: {failed.question}. Observation: {failed.observation}",
                        before_evidence_urls=failed.evidence_urls
                    )
                    db.add(verification)

                AuditService.log_event(db, "INSPECTION", new_audit.id, "SYNC_SUBMITTED", batch.officer_id, {
                    "score": score, "failed_items": len(failed_items)
                })

                results.append(BatchSyncResultItem(
                    client_id=audit.client_id,
                    server_id=new_audit.id,
                    entity_type="INSPECTION",
                    status="SYNCED",
                    message="Successfully synced inspection checklist"
                ))

        # 3. Process Incidents
        for inc in batch.incidents:
            existing = db.query(IncidentRecord).filter(IncidentRecord.client_id == inc.client_id).first()
            if existing:
                results.append(BatchSyncResultItem(
                    client_id=inc.client_id,
                    server_id=existing.id,
                    entity_type="INCIDENT",
                    status="SYNCED",
                    message="Already synced (idempotent ACK)"
                ))
            else:
                new_inc = IncidentRecord(
                    client_id=inc.client_id,
                    mine_id=inc.mine_id,
                    zone_id=inc.zone_id,
                    reporter_id=batch.officer_id,
                    incident_type=inc.incident_type,
                    severity=inc.severity,
                    occurrence_time=inc.occurrence_time or datetime.now(timezone.utc),
                    location_name=inc.location_name,
                    latitude=inc.latitude,
                    longitude=inc.longitude,
                    accuracy=inc.accuracy,
                    description=inc.description,
                    people_involved=inc.people_involved,
                    witnesses=inc.witnesses,
                    immediate_action=inc.immediate_action,
                    evidence_urls=inc.evidence_urls,
                    status="REPORTED"
                )
                db.add(new_inc)
                db.flush()

                # Spawn corrective action verification for all incidents
                verification = FieldVerification(
                    issue_type="INCIDENT",
                    source_id=new_inc.id,
                    mine_id=inc.mine_id,
                    status="REPORTED",
                    remediation_notes=f"Incident [{inc.incident_type}] Severity: {inc.severity}. Immediate Action: {inc.immediate_action}",
                    before_evidence_urls=inc.evidence_urls
                )
                db.add(verification)

                AuditService.log_event(db, "INCIDENT", new_inc.id, "SYNC_CREATED", batch.officer_id, {
                    "type": inc.incident_type, "severity": inc.severity
                })

                results.append(BatchSyncResultItem(
                    client_id=inc.client_id,
                    server_id=new_inc.id,
                    entity_type="INCIDENT",
                    status="SYNCED",
                    message="Successfully registered incident report"
                ))

        db.commit()

        return BatchSyncResponse(
            success=True,
            synced_at=datetime.now(timezone.utc),
            processed_count=len(results),
            results=results
        )
