import 'dart:convert';
import '../lib/data/models/field_report_model.dart';
import '../lib/data/models/inspection_model.dart';
import '../lib/data/models/incident_model.dart';
import '../lib/core/sync/sync_queue_item.dart';

void main() {
  print('========================================');
  print('RUNNING MODULE 2 DART & FLUTTER TESTS');
  print('========================================\n');

  int passed = 0;
  int total = 0;

  void test(String name, void Function() fn) {
    total++;
    try {
      fn();
      print(' [PASS] $name');
      passed++;
    } catch (e) {
      print(' [FAIL] $name: $e');
    }
  }

  // 1. FieldReportModel
  test('FieldReportModel serialization & geo-coordinate preservation', () {
    final report = FieldReportModel(
      clientId: 'rep-uuid-001',
      mineId: 'MINE-DHANBAD-01',
      zoneId: 'PIT-01',
      category: 'HAZARD',
      severity: 'HIGH',
      description: 'Loose rock on crest bench',
      latitude: 23.795,
      longitude: 86.430,
      accuracy: 3.5,
      evidenceUrls: ['/storage/uploads/rock.jpg'],
    );

    final map = report.toMap();
    assert(map['client_id'] == 'rep-uuid-001', 'client_id mismatch');
    assert(map['category'] == 'HAZARD', 'category mismatch');
    assert(map['severity'] == 'HIGH', 'severity mismatch');
    assert(map['latitude'] == 23.795, 'latitude mismatch');

    final fromMap = FieldReportModel.fromMap(map);
    assert(fromMap.clientId == 'rep-uuid-001', 'deserialized client_id mismatch');
    assert(fromMap.category == 'HAZARD', 'deserialized category mismatch');
    assert(fromMap.evidenceUrls.length == 1, 'evidenceUrls length mismatch');
  });

  // 2. InspectionAuditModel
  test('InspectionAuditModel compliance scoring calculation', () {
    final items = [
      ChecklistItemResult(itemCode: 'FIRE-01', question: 'Extinguisher check', resultStatus: 'PASS'),
      ChecklistItemResult(itemCode: 'FIRE-02', question: 'Stone dust barrier', resultStatus: 'FAIL'),
      ChecklistItemResult(itemCode: 'FIRE-03', question: 'Hydrant check', resultStatus: 'PASS'),
    ];

    final passedItems = items.where((i) => i.resultStatus == 'PASS').length;
    final score = (passedItems / items.length) * 100.0;

    final audit = InspectionAuditModel(
      clientId: 'audit-uuid-001',
      templateId: 'TMPL-DGMS-FIRE-01',
      mineId: 'MINE-DHANBAD-01',
      itemsResults: items,
      overallScore: score,
    );

    assert(audit.itemsResults.length == 3, 'Items count mismatch');
    assert((audit.overallScore - 66.66).abs() < 0.1, 'Score mismatch: ${audit.overallScore}');

    final map = audit.toMap();
    final fromMap = InspectionAuditModel.fromMap(map);
    assert(fromMap.itemsResults.length == 3, 'Items count mismatch in fromMap');
    assert(fromMap.itemsResults[1].resultStatus == 'FAIL', 'Failed item status not preserved');
  });

  // 3. AI Structuring Suggestion
  test('AIStructuringSuggestion parsing from AI service response', () {
    final jsonSuggestion = {
      'raw_text': 'Dumper stopped with smoke near engine at haul road',
      'suggested_incident_type': 'FIRE',
      'suggested_severity': 'HIGH',
      'suggested_hazard': 'FIRE_AND_SMOKE',
      'suggested_location': 'HAUL_ROAD',
      'suggested_injury': 'NONE_REPORTED',
      'confidence_score': 0.92,
      'reasoning': 'Keywords detected combustion/flame indicator',
    };

    final suggestion = AIStructuringSuggestion.fromMap(jsonSuggestion);
    assert(suggestion.suggestedIncidentType == 'FIRE', 'AI suggested type mismatch');
    assert(suggestion.suggestedSeverity == 'HIGH', 'AI suggested severity mismatch');
    assert(suggestion.suggestedLocation == 'HAUL_ROAD', 'AI suggested location mismatch');
    assert(suggestion.confidenceScore == 0.92, 'AI confidence mismatch');
  });

  // 4. SyncStatus Enum & Queue transitions
  test('SyncStatus Enum state machine mapping', () {
    assert(SyncStatus.readyToSync.toDbString() == 'READY_TO_SYNC', 'READY_TO_SYNC conversion error');
    assert(SyncStatus.fromString('READY_TO_SYNC') == SyncStatus.readyToSync, 'readyToSync reverse error');
    assert(SyncStatus.fromString('SYNCED') == SyncStatus.synced, 'synced reverse error');
    assert(SyncStatus.fromString('SYNC_FAILED') == SyncStatus.syncFailed, 'syncFailed reverse error');
    assert(SyncStatus.fromString('DRAFT') == SyncStatus.draft, 'draft reverse error');
  });

  print('\n========================================');
  print('TEST RESULTS: $passed / $total PASSED');
  print('========================================');

  if (passed != total) {
    throw Exception('Some tests failed');
  }
}
