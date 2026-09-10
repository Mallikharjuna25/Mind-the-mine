import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../data/models/field_report_model.dart';
import '../data/repositories/offline_first_repository.dart';

class FieldReportProvider extends ChangeNotifier {
  final OfflineFirstRepository _repo;
  final Uuid _uuid = const Uuid();

  String _category = 'HAZARD';
  String _severity = 'HIGH';
  String _description = '';
  double _latitude = 23.7957;
  double _longitude = 86.4304;
  double _accuracy = 3.5;
  List<String> _evidenceUrls = [];
  bool _isSubmitting = false;

  FieldReportProvider(this._repo);

  String get category => _category;
  String get severity => _severity;
  String get description => _description;
  double get latitude => _latitude;
  double get longitude => _longitude;
  double get accuracy => _accuracy;
  List<String> get evidenceUrls => _evidenceUrls;
  bool get isSubmitting => _isSubmitting;

  void setCategory(String cat) {
    _category = cat;
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

  void setLocation(double lat, double lng, [double acc = 3.0]) {
    _latitude = lat;
    _longitude = lng;
    _accuracy = acc;
    notifyListeners();
  }

  void addEvidence(String path) {
    _evidenceUrls.add(path);
    notifyListeners();
  }

  Future<bool> submitReport() async {
    _isSubmitting = true;
    notifyListeners();

    try {
      final report = FieldReportModel(
        clientId: _uuid.v4(),
        mineId: 'MINE-DHANBAD-01',
        zoneId: 'PIT-FACE-01',
        category: _category,
        severity: _severity,
        description: _description,
        latitude: _latitude,
        longitude: _longitude,
        accuracy: _accuracy,
        evidenceUrls: _evidenceUrls,
        status: 'REPORTED',
      );

      await _repo.submitFieldReport(report);
      _description = '';
      _evidenceUrls = [];
      _isSubmitting = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isSubmitting = false;
      notifyListeners();
      return false;
    }
  }
}
