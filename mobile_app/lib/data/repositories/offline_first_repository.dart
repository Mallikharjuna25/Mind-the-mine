import 'dart:convert';
import 'package:uuid/uuid.dart';
import '../../core/network/api_client.dart';
import '../../core/network/network_info.dart';
import '../../core/storage/database_helper.dart';
import '../../core/sync/sync_engine.dart';
import '../models/field_report_model.dart';
import '../models/inspection_model.dart';
import '../models/incident_model.dart';
import '../models/verification_model.dart';

class OfflineFirstRepository {
  final ApiClient _apiClient;
  final DatabaseHelper _dbHelper;
  final NetworkInfo _networkInfo;
  final SyncEngine _syncEngine;
  final Uuid _uuid = const Uuid();

  OfflineFirstRepository({
    ApiClient? apiClient,
    DatabaseHelper? dbHelper,
    NetworkInfo? networkInfo,
    SyncEngine? syncEngine,
  })  : _apiClient = apiClient ?? ApiClient(),
        _dbHelper = dbHelper ?? DatabaseHelper(),
        _networkInfo = networkInfo ?? NetworkInfo(),
        _syncEngine = syncEngine ?? SyncEngine();

  // --- Field Reports ---
  Future<void> submitFieldReport(FieldReportModel report) async {
    final db = await _dbHelper.database;
    // 1. Save to local SQLite
    await db.insert('local_field_reports', {
      'client_id': report.clientId,
      'mine_id': report.mineId,
      'zone_id': report.zoneId,
      'category': report.category,
      'severity': report.severity,
      'description': report.description,
      'latitude': report.latitude,
      'longitude': report.longitude,
      'accuracy': report.accuracy,
      'evidence_urls': jsonEncode(report.evidenceUrls),
      'status': 'REPORTED',
      'created_at': report.captureTimestamp.toIso8601String(),
    });

    // 2. Enqueue into sync queue
    await _dbHelper.enqueueItem(
      clientId: report.clientId,
      entityType: 'FIELD_REPORT',
      payload: report.toMap(),
    );

    // 3. Trigger auto-sync if network is available
    _syncEngine.syncAllPending();
  }

  // --- Inspections ---
  Future<void> submitInspection(InspectionAuditModel audit) async {
    final db = await _dbHelper.database;
    await db.insert('local_inspections', {
      'client_id': audit.clientId,
      'template_id': audit.templateId,
      'mine_id': audit.mineId,
      'zone_id': audit.zoneId,
      'inspector_id': 'CURRENT_OFFICER',
      'shift': audit.shift,
      'status': audit.status,
      'score': audit.overallScore,
      'results_json': jsonEncode(audit.itemsResults.map((e) => e.toMap()).toList()),
      'created_at': audit.createdAt.toIso8601String(),
    });

    await _dbHelper.enqueueItem(
      clientId: audit.clientId,
      entityType: 'INSPECTION',
      payload: audit.toMap(),
    );

    _syncEngine.syncAllPending();
  }

  // --- Incidents ---
  Future<void> submitIncident(IncidentModel incident) async {
    final db = await _dbHelper.database;
    await db.insert('local_incidents', {
      'client_id': incident.clientId,
      'mine_id': incident.mineId,
      'zone_id': incident.zoneId,
      'incident_type': incident.incidentType,
      'severity': incident.severity,
      'description': incident.description,
      'location_name': incident.locationName,
      'latitude': incident.latitude,
      'longitude': incident.longitude,
      'immediate_action': incident.immediateAction,
      'evidence_urls': jsonEncode(incident.evidenceUrls),
      'status': incident.status,
      'created_at': incident.occurrenceTime.toIso8601String(),
    });

    await _dbHelper.enqueueItem(
      clientId: incident.clientId,
      entityType: 'INCIDENT',
      payload: incident.toMap(),
    );

    _syncEngine.syncAllPending();
  }

  // --- AI Structuring ---
  Future<AIStructuringSuggestion> structureIncidentWithAI(String text, {String? mineId}) async {
    final isOnline = await _networkInfo.isConnected;
    if (isOnline) {
      try {
        final response = await _apiClient.post('/ai/structure-incident', data: {
          'raw_text': text,
          'mine_id': mineId ?? 'MINE-DHANBAD-01',
        });
        if (response.statusCode == 200) {
          return AIStructuringSuggestion.fromMap(response.data);
        }
      } catch (_) {
        // Fallback to offline rule-based parser
      }
    }

    // Local offline fallback parser
    final lower = text.toLowerCase();
    String type = 'SAFETY_OBSERVATION';
    String hazard = 'GENERAL_HAZARD';
    String severity = 'MODERATE';
    if (lower.contains('fire') || lower.contains('smoke')) {
      type = 'FIRE';
      hazard = 'FIRE_AND_SMOKE';
      severity = 'HIGH';
    } else if (lower.contains('dumper') || lower.contains('brake') || lower.contains('engine')) {
      type = 'EQUIPMENT_FAILURE';
      hazard = 'HEAVY_MACHINERY_MALFUNCTION';
    }

    return AIStructuringSuggestion(
      rawText: text,
      suggestedIncidentType: type,
      suggestedSeverity: severity,
      suggestedHazard: hazard,
      suggestedLocation: lower.contains('haul road') ? 'HAUL_ROAD' : 'WORKING_BENCH',
      suggestedInjury: lower.contains('no injur') ? 'NONE_REPORTED' : 'FIRST_AID_REQUIRED',
      confidenceScore: 0.82,
      reasoning: 'Parsed via local offline fallback heuristic',
    );
  }

  // --- Verifications ---
  Future<List<FieldVerificationModel>> getVerifications() async {
    try {
      final response = await _apiClient.get('/field-verifications');
      if (response.statusCode == 200) {
        final list = response.data as List<dynamic>;
        return list.map((e) => FieldVerificationModel.fromMap(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  Future<bool> transitionVerification(String id, String targetStatus, {String? notes, List<String>? evidence}) async {
    try {
      final response = await _apiClient.patch('/field-verifications//transition', data: {
        'status': targetStatus,
        if (notes != null) 'remediation_notes': notes,
        if (evidence != null) 'after_evidence_urls': evidence,
      });
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
