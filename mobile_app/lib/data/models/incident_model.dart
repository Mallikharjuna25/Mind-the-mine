import 'dart:convert';

class AIStructuringSuggestion {
  final String rawText;
  final String suggestedIncidentType;
  final String suggestedSeverity;
  final String suggestedHazard;
  final String suggestedLocation;
  final String suggestedInjury;
  final double confidenceScore;
  final String reasoning;

  AIStructuringSuggestion({
    required this.rawText,
    required this.suggestedIncidentType,
    required this.suggestedSeverity,
    required this.suggestedHazard,
    required this.suggestedLocation,
    required this.suggestedInjury,
    required this.confidenceScore,
    required this.reasoning,
  });

  factory AIStructuringSuggestion.fromMap(Map<String, dynamic> map) {
    return AIStructuringSuggestion(
      rawText: map['raw_text'] ?? '',
      suggestedIncidentType: map['suggested_incident_type'] ?? 'EQUIPMENT_FAILURE',
      suggestedSeverity: map['suggested_severity'] ?? 'MODERATE',
      suggestedHazard: map['suggested_hazard'] ?? 'UNSPECIFIED',
      suggestedLocation: map['suggested_location'] ?? 'GENERAL_MINE_AREA',
      suggestedInjury: map['suggested_injury'] ?? 'NONE_REPORTED',
      confidenceScore: (map['confidence_score'] as num?)?.toDouble() ?? 0.85,
      reasoning: map['reasoning'] ?? '',
    );
  }
}

class IncidentModel {
  final String clientId;
  final String mineId;
  final String? zoneId;
  final String incidentType;
  final String severity; // MINOR, MODERATE, MAJOR, FATAL, CRITICAL
  final String description;
  final String? locationName;
  final double? latitude;
  final double? longitude;
  final String? immediateAction;
  final List<String> peopleInvolved;
  final List<String> witnesses;
  final List<String> evidenceUrls;
  final String status;
  final DateTime occurrenceTime;

  IncidentModel({
    required this.clientId,
    required this.mineId,
    this.zoneId,
    required this.incidentType,
    this.severity = 'MODERATE',
    required this.description,
    this.locationName,
    this.latitude,
    this.longitude,
    this.immediateAction,
    List<String>? peopleInvolved,
    List<String>? witnesses,
    List<String>? evidenceUrls,
    this.status = 'REPORTED',
    DateTime? occurrenceTime,
  })  : peopleInvolved = peopleInvolved ?? [],
        witnesses = witnesses ?? [],
        evidenceUrls = evidenceUrls ?? [],
        occurrenceTime = occurrenceTime ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'client_id': clientId,
      'mine_id': mineId,
      'zone_id': zoneId,
      'incident_type': incidentType,
      'severity': severity,
      'description': description,
      'location_name': locationName,
      'latitude': latitude,
      'longitude': longitude,
      'immediate_action': immediateAction,
      'people_involved': peopleInvolved,
      'witnesses': witnesses,
      'evidence_urls': evidenceUrls,
      'status': status,
      'occurrence_time': occurrenceTime.toIso8601String(),
    };
  }

  factory IncidentModel.fromMap(Map<String, dynamic> map) {
    return IncidentModel(
      clientId: map['client_id'] ?? '',
      mineId: map['mine_id'] ?? '',
      zoneId: map['zone_id'],
      incidentType: map['incident_type'] ?? 'ACCIDENT',
      severity: map['severity'] ?? 'MODERATE',
      description: map['description'] ?? '',
      locationName: map['location_name'],
      latitude: map['latitude'] != null ? (map['latitude'] as num).toDouble() : null,
      longitude: map['longitude'] != null ? (map['longitude'] as num).toDouble() : null,
      immediateAction: map['immediate_action'],
      peopleInvolved: map['people_involved'] != null ? List<String>.from(map['people_involved']) : [],
      witnesses: map['witnesses'] != null ? List<String>.from(map['witnesses']) : [],
      evidenceUrls: map['evidence_urls'] != null ? List<String>.from(map['evidence_urls']) : [],
      status: map['status'] ?? 'REPORTED',
      occurrenceTime: map['occurrence_time'] != null ? DateTime.tryParse(map['occurrence_time']) : null,
    );
  }
}
