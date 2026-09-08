import 'dart:convert';

class FieldReportModel {
  final String clientId;
  final String mineId;
  final String? zoneId;
  final String category; // HAZARD, SAFETY_OBSERVATION, VIOLATION, etc.
  final String severity; // LOW, MEDIUM, HIGH, CRITICAL
  final String description;
  final double? latitude;
  final double? longitude;
  final double? accuracy;
  final DateTime captureTimestamp;
  final List<String> evidenceUrls;
  final String status;

  FieldReportModel({
    required this.clientId,
    required this.mineId,
    this.zoneId,
    required this.category,
    this.severity = 'MEDIUM',
    required this.description,
    this.latitude,
    this.longitude,
    this.accuracy,
    DateTime? captureTimestamp,
    List<String>? evidenceUrls,
    this.status = 'REPORTED',
  })  : captureTimestamp = captureTimestamp ?? DateTime.now(),
        evidenceUrls = evidenceUrls ?? [];

  Map<String, dynamic> toMap() {
    return {
      'client_id': clientId,
      'mine_id': mineId,
      'zone_id': zoneId,
      'category': category,
      'severity': severity,
      'description': description,
      'latitude': latitude,
      'longitude': longitude,
      'accuracy': accuracy,
      'capture_timestamp': captureTimestamp.toIso8601String(),
      'evidence_urls': evidenceUrls,
      'status': status,
    };
  }

  factory FieldReportModel.fromMap(Map<String, dynamic> map) {
    List<String> evidence = [];
    if (map['evidence_urls'] != null) {
      if (map['evidence_urls'] is String) {
        try {
          evidence = List<String>.from(jsonDecode(map['evidence_urls']));
        } catch (_) {}
      } else if (map['evidence_urls'] is List) {
        evidence = List<String>.from(map['evidence_urls']);
      }
    }

    return FieldReportModel(
      clientId: map['client_id'] ?? '',
      mineId: map['mine_id'] ?? '',
      zoneId: map['zone_id'],
      category: map['category'] ?? 'HAZARD',
      severity: map['severity'] ?? 'MEDIUM',
      description: map['description'] ?? '',
      latitude: map['latitude'] != null ? (map['latitude'] as num).toDouble() : null,
      longitude: map['longitude'] != null ? (map['longitude'] as num).toDouble() : null,
      accuracy: map['accuracy'] != null ? (map['accuracy'] as num).toDouble() : null,
      captureTimestamp: map['capture_timestamp'] != null
          ? DateTime.tryParse(map['capture_timestamp'])
          : null,
      evidenceUrls: evidence,
      status: map['status'] ?? 'REPORTED',
    );
  }
}
