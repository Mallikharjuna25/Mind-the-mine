import 'dart:convert';

class ChecklistItemResult {
  final String itemCode;
  final String question;
  String resultStatus; // PASS, FAIL, NA
  String observation;
  String severity;
  List<String> evidenceUrls;
  bool incidentGenerated;

  ChecklistItemResult({
    required this.itemCode,
    required this.question,
    this.resultStatus = 'PASS',
    this.observation = '',
    this.severity = 'LOW',
    List<String>? evidenceUrls,
    this.incidentGenerated = false,
  }) : evidenceUrls = evidenceUrls ?? [];

  Map<String, dynamic> toMap() {
    return {
      'item_code': itemCode,
      'question': question,
      'result_status': resultStatus,
      'observation': observation,
      'severity': severity,
      'evidence_urls': evidenceUrls,
      'incident_generated': incidentGenerated,
    };
  }

  factory ChecklistItemResult.fromMap(Map<String, dynamic> map) {
    return ChecklistItemResult(
      itemCode: map['item_code'] ?? '',
      question: map['question'] ?? '',
      resultStatus: map['result_status'] ?? 'PASS',
      observation: map['observation'] ?? '',
      severity: map['severity'] ?? 'LOW',
      evidenceUrls: map['evidence_urls'] != null ? List<String>.from(map['evidence_urls']) : [],
      incidentGenerated: map['incident_generated'] ?? false,
    );
  }
}

class InspectionAuditModel {
  final String clientId;
  final String templateId;
  final String mineId;
  final String? zoneId;
  final String shift;
  final String status;
  final double overallScore;
  final String summaryFindings;
  final List<ChecklistItemResult> itemsResults;
  final DateTime createdAt;

  InspectionAuditModel({
    required this.clientId,
    required this.templateId,
    required this.mineId,
    this.zoneId,
    this.shift = 'SHIFT_A',
    this.status = 'SUBMITTED',
    this.overallScore = 100.0,
    this.summaryFindings = '',
    List<ChecklistItemResult>? itemsResults,
    DateTime? createdAt,
  })  : itemsResults = itemsResults ?? [],
        createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'client_id': clientId,
      'template_id': templateId,
      'mine_id': mineId,
      'zone_id': zoneId,
      'shift': shift,
      'status': status,
      'summary_findings': summaryFindings,
      'items_results': itemsResults.map((e) => e.toMap()).toList(),
    };
  }

  factory InspectionAuditModel.fromMap(Map<String, dynamic> map) {
    List<ChecklistItemResult> results = [];
    if (map['items_results'] != null) {
      if (map['items_results'] is String) {
        final decoded = jsonDecode(map['items_results']) as List<dynamic>;
        results = decoded.map((e) => ChecklistItemResult.fromMap(e)).toList();
      } else if (map['items_results'] is List) {
        results = (map['items_results'] as List).map((e) => ChecklistItemResult.fromMap(e)).toList();
      }
    }

    return InspectionAuditModel(
      clientId: map['client_id'] ?? '',
      templateId: map['template_id'] ?? '',
      mineId: map['mine_id'] ?? '',
      zoneId: map['zone_id'],
      shift: map['shift'] ?? 'SHIFT_A',
      status: map['status'] ?? 'SUBMITTED',
      overallScore: map['overall_score'] != null ? (map['overall_score'] as num).toDouble() : 100.0,
      summaryFindings: map['summary_findings'] ?? '',
      itemsResults: results,
      createdAt: map['created_at'] != null ? DateTime.tryParse(map['created_at']) : null,
    );
  }
}
