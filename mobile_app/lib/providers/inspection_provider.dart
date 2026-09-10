import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../data/models/inspection_model.dart';
import '../data/repositories/offline_first_repository.dart';

class InspectionProvider extends ChangeNotifier {
  final OfflineFirstRepository _repo;
  final Uuid _uuid = const Uuid();

  List<ChecklistItemResult> _currentChecklist = [];
  String _templateId = 'TMPL-DGMS-FIRE-01';
  String _templateTitle = 'DGMS Fire Safety & Gas Inundation Inspection';
  String _mineId = 'MINE-DHANBAD-01';
  String _zoneId = 'PIT-FACE-01';
  String _shift = 'SHIFT_A';
  bool _isSubmitting = false;
  String? _submissionStatus;

  InspectionProvider(this._repo) {
    loadDefaultChecklist();
  }

  List<ChecklistItemResult> get currentChecklist => _currentChecklist;
  String get templateTitle => _templateTitle;
  double get currentScore {
    if (_currentChecklist.isEmpty) return 100.0;
    final passed = _currentChecklist.where((i) => i.resultStatus == 'PASS').length;
    final failed = _currentChecklist.where((i) => i.resultStatus == 'FAIL').length;
    if (passed + failed == 0) return 100.0;
    return (passed / (passed + failed)) * 100.0;
  }
  bool get isSubmitting => _isSubmitting;
  String? get submissionStatus => _submissionStatus;

  void loadDefaultChecklist() {
    _currentChecklist = [
      ChecklistItemResult(
        itemCode: 'FIRE-01',
        question: 'Are portable fire extinguishers charged and within annual inspection date?',
        resultStatus: 'PASS',
      ),
      ChecklistItemResult(
        itemCode: 'FIRE-02',
        question: 'Is stone dust barrier properly maintained in accordance with DGMS norms?',
        resultStatus: 'PASS',
      ),
      ChecklistItemResult(
        itemCode: 'FIRE-03',
        question: 'Are emergency water spray hydrants operational along conveyor transfer points?',
        resultStatus: 'PASS',
      ),
      ChecklistItemResult(
        itemCode: 'FIRE-04',
        question: 'Are flameproof electrical enclosures properly bolted and sealed?',
        resultStatus: 'PASS',
      ),
      ChecklistItemResult(
        itemCode: 'FIRE-05',
        question: 'Are emergency escape routes clearly illuminated and free from obstructions?',
        resultStatus: 'PASS',
      ),
    ];
    notifyListeners();
  }

  void updateItemResult(int index, String status) {
    if (index >= 0 && index < _currentChecklist.length) {
      _currentChecklist[index].resultStatus = status;
      notifyListeners();
    }
  }

  void updateItemObservation(int index, String observation, {String? severity}) {
    if (index >= 0 && index < _currentChecklist.length) {
      _currentChecklist[index].observation = observation;
      if (severity != null) _currentChecklist[index].severity = severity;
      notifyListeners();
    }
  }

  void addItemEvidence(int index, String evidenceUrl) {
    if (index >= 0 && index < _currentChecklist.length) {
      _currentChecklist[index].evidenceUrls.add(evidenceUrl);
      notifyListeners();
    }
  }

  Future<bool> submitChecklistAudit() async {
    _isSubmitting = true;
    notifyListeners();

    try {
      final audit = InspectionAuditModel(
        clientId: _uuid.v4(),
        templateId: _templateId,
        mineId: _mineId,
        zoneId: _zoneId,
        shift: _shift,
        status: 'SUBMITTED',
        overallScore: currentScore,
        summaryFindings: 'Field inspection completed with score %',
        itemsResults: _currentChecklist,
      );

      await _repo.submitInspection(audit);
      _submissionStatus = 'Saved locally and queued for synchronization.';
      _isSubmitting = false;
      notifyListeners();
      return true;
    } catch (e) {
      _submissionStatus = 'Submission error: ';
      _isSubmitting = false;
      notifyListeners();
      return false;
    }
  }
}
