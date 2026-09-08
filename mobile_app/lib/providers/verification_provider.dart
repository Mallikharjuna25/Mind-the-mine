import 'package:flutter/foundation.dart';
import '../data/models/verification_model.dart';
import '../data/repositories/offline_first_repository.dart';

class VerificationProvider extends ChangeNotifier {
  final OfflineFirstRepository _repo;

  List<FieldVerificationModel> _verifications = [];
  bool _isLoading = false;

  VerificationProvider(this._repo) {
    loadVerifications();
  }

  List<FieldVerificationModel> get verifications => _verifications;
  bool get isLoading => _isLoading;

  Future<void> loadVerifications() async {
    _isLoading = true;
    notifyListeners();
    _verifications = await _repo.getVerifications();
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> advanceWorkflow(String id, String targetStatus, {String? notes, List<String>? evidence}) async {
    final success = await _repo.transitionVerification(id, targetStatus, notes: notes, evidence: evidence);
    if (success) {
      await loadVerifications();
    }
    return success;
  }
}
