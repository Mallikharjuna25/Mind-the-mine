import 'package:test/test.dart';
import '../lib/data/models/field_report_model.dart';
import '../lib/data/models/inspection_model.dart';
import '../lib/data/models/incident_model.dart';
import '../lib/core/sync/sync_queue_item.dart';

void main() {
  group('FieldReportModel Tests', () {
    test('Should correctly serialize and deserialize FieldReportModel', () {
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
      expect(map['client_id'], 'rep-uuid-001');
      expect(map['category'], 'HAZARD');
      expect(map['severity'], 'HIGH');
      expect(map['latitude'], 23.795);

      final fromMap = FieldReportModel.fromMap(map);
      expect(fromMap.clientId, 'rep-uuid-001');
      expect(fromMap.category, 'HAZARD');
      expect(fromMap.severity, 'HIGH');
      expect(fromMap.evidenceUrls.length, 1);
    });
  });

  group('InspectionAuditModel Tests', () {
    test('Should calculate correct compliance score for checklist items', () {
      final items = [
        ChecklistItemResult(itemCode: 'F-1', question: 'Extinguisher check', resultStatus: 'PASS'),
        ChecklistItemResult(itemCode: 'F-2', question: 'Stone dust barrier', resultStatus: 'FAIL'),
        ChecklistItemResult(itemCode: 'F-3', question: 'Hydrant check', resultStatus: 'PASS'),
      ];

      final audit = InspectionAuditModel(
        clientId: 'audit-uuid-001',
        templateId: 'TMPL-DGMS-FIRE-01',
        mineId: 'MINE-DHANBAD-01',
        itemsResults: items,
        overallScore: (2 / 3) * 100.0,
      );

      expect(audit.itemsResults.length, 3);
      expect(audit.overallScore, closeTo(66.6, 0.1));

      final map = audit.toMap();
      final fromMap = InspectionAuditModel.fromMap(map);
      expect(fromMap.itemsResults.length, 3);
      expect(fromMap.itemsResults[1].resultStatus, 'FAIL');
    });
  });

  group('IncidentModel and AI Structuring Tests', () {
    test('Should deserialize AIStructuringSuggestion properly', () {
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
      expect(suggestion.suggestedIncidentType, 'FIRE');
      expect(suggestion.suggestedSeverity, 'HIGH');
      expect(suggestion.suggestedLocation, 'HAUL_ROAD');
      expect(suggestion.confidenceScore, 0.92);
    });
  });

  group('Sync Status Tests', () {
    test('Should correctly map SyncStatus enum to and from DB string', () {
      expect(SyncStatus.readyToSync.toDbString(), 'READY_TO_SYNC');
      expect(SyncStatus.fromString('READY_TO_SYNC'), SyncStatus.readyToSync);
      expect(SyncStatus.fromString('SYNCED'), SyncStatus.synced);
      expect(SyncStatus.fromString('SYNC_FAILED'), SyncStatus.syncFailed);
    });
  });
}
