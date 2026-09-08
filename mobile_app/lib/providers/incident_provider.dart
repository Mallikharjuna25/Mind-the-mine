import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../data/models/incident_model.dart';
import '../data/repositories/offline_first_repository.dart';

class IncidentProvider extends ChangeNotifier {
  final OfflineFirstRepository _repo;
  final Uuid _uuid = const Uuid();

  String _incidentType = 'EQUIPMENT_FAILURE';
  String _severity = 'MODERATE';
  String _description = '';
  String _locationName = 'Haul Road Section 4';
  String _immediateAction = '';
  List<String> _evidenceUrls = [];
  AIStructuringSuggestion? _currentAISuggestion;
  bool _isLoadingAI = false;
  bool _isSubmitting = false;

  IncidentProvider(this._repo);

  String get incidentType => _incidentType;
  String get severity => _severity;
  String get description => _description;
  String get locationName => _locationName;
  String get immediateAction => _immediateAction;
  List<String> get evidenceUrls => _evidenceUrls;
  AIStructuringSuggestion? get currentAISuggestion => _currentAISuggestion;
  bool get isLoadingAI => _isLoadingAI;
  bool get isSubmitting => _isSubmitting;

  void setIncidentType(String type) {
    _incidentType = type;
    notifyListeners();
  }

  void setSeverity(String sev) {
    _severity = sev;
    notifyListeners();
  }

  void setDescription(String desc) {
    _description = desc;
    notifyListeners();
  }

  void setLocationName(String loc) {
    _locationName = loc;
    notifyListeners();
  }

  void setImmediateAction(String action) {
    _immediateAction = action;
    notifyListeners();
  }

  void addEvidence(String path) {
    _evidenceUrls.add(path);
    notifyListeners();
  }

  Future<void> analyzeNotesWithAI(String voiceOrText) async {
    _isLoadingAI = true;
    notifyListeners();

    try {
      final suggestion = await _repo.structureIncidentWithAI(voiceOrText);
      _currentAISuggestion = suggestion;
    } catch (_) {}

    _isLoadingAI = false;
    notifyListeners();
  }

  void applyAISuggestions(AIStructuringSuggestion suggestion) {
    _incidentType = suggestion.suggestedIncidentType;
    _severity = suggestion.suggestedSeverity;
    _locationName = suggestion.suggestedLocation;
    notifyListeners();
  }

  Future<bool> submitIncident({double? lat, double? lng}) async {
    _isSubmitting = true;
    notifyListeners();

    try {
      final incident = IncidentModel(
        clientId: _uuid.v4(),
        mineId: 'MINE-DHANBAD-01',
        zoneId: 'PIT-01',
        incidentType: _incidentType,
        severity: _severity,
        description: _description,
        locationName: _locationName,
        latitude: lat ?? 23.7957,
        longitude: lng ?? 86.4304,
        immediateAction: _immediateAction,
        evidenceUrls: _evidenceUrls,
        status: 'REPORTED',
      );

      await _repo.submitIncident(incident);
      _isSubmitting = false;
      // Reset form
      _description = '';
      _immediateAction = '';
      _evidenceUrls = [];
      _currentAISuggestion = null;
      notifyListeners();
      return true;
    } catch (e) {
      _isSubmitting = false;
      notifyListeners();
      return false;
    }
  }
}
