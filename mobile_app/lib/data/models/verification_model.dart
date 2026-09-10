class FieldVerificationModel {
  final String id;
  final String issueType; // FIELD_REPORT, INSPECTION_FAIL, INCIDENT
  final String sourceId;
  final String mineId;
  String status; // REPORTED, VERIFIED, CORRECTIVE_ACTION, EVIDENCE_SUBMITTED, SUPERVISOR_REVIEW, APPROVED, CLOSED
  String? assignedTo;
  String? remediationNotes;
  List<String> beforeEvidenceUrls;
  List<String> afterEvidenceUrls;
  String? supervisorNotes;
  String? verifiedBy;
  DateTime? verifiedAt;
  DateTime? closedAt;

  FieldVerificationModel({
    required this.id,
    required this.issueType,
    required this.sourceId,
    required this.mineId,
    this.status = 'REPORTED',
    this.assignedTo,
    this.remediationNotes,
    List<String>? beforeEvidenceUrls,
    List<String>? afterEvidenceUrls,
    this.supervisorNotes,
    this.verifiedBy,
    this.verifiedAt,
    this.closedAt,
  })  : beforeEvidenceUrls = beforeEvidenceUrls ?? [],
        afterEvidenceUrls = afterEvidenceUrls ?? [];

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'issue_type': issueType,
      'source_id': sourceId,
      'mine_id': mineId,
      'status': status,
      'assigned_to': assignedTo,
      'remediation_notes': remediationNotes,
      'before_evidence_urls': beforeEvidenceUrls,
      'after_evidence_urls': afterEvidenceUrls,
      'supervisor_notes': supervisorNotes,
      'verified_by': verifiedBy,
      'verified_at': verifiedAt?.toIso8601String(),
      'closed_at': closedAt?.toIso8601String(),
    };
  }

  factory FieldVerificationModel.fromMap(Map<String, dynamic> map) {
    return FieldVerificationModel(
      id: map['id'] ?? '',
      issueType: map['issue_type'] ?? 'FIELD_REPORT',
      sourceId: map['source_id'] ?? '',
      mineId: map['mine_id'] ?? '',
      status: map['status'] ?? 'REPORTED',
      assignedTo: map['assigned_to'],
      remediationNotes: map['remediation_notes'],
      beforeEvidenceUrls: map['before_evidence_urls'] != null ? List<String>.from(map['before_evidence_urls']) : [],
      afterEvidenceUrls: map['after_evidence_urls'] != null ? List<String>.from(map['after_evidence_urls']) : [],
      supervisorNotes: map['supervisor_notes'],
      verifiedBy: map['verified_by'],
      verifiedAt: map['verified_at'] != null ? DateTime.tryParse(map['verified_at']) : null,
      closedAt: map['closed_at'] != null ? DateTime.tryParse(map['closed_at']) : null,
    );
  }
}
