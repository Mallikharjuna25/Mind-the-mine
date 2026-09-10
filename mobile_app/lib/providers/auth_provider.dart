import 'package:flutter/foundation.dart';
import '../core/storage/secure_storage_helper.dart';

class AuthProvider extends ChangeNotifier {
  final SecureStorageHelper _secureStorage;

  String _userId = 'INSP-DHANBAD-05';
  String _name = 'Inspector Ramesh Kumar';
  String _role = 'INSPECTOR';
  String _mineId = 'MINE-DHANBAD-01';
  bool _isAuthenticated = true;

  AuthProvider([SecureStorageHelper? secureStorage])
      : _secureStorage = secureStorage ?? SecureStorageHelper();

  String get userId => _userId;
  String get name => _name;
  String get role => _role;
  String get mineId => _mineId;
  bool get isAuthenticated => _isAuthenticated;

  void selectMine(String mineId) {
    _mineId = mineId;
    notifyListeners();
  }

  void switchRole(String role) {
    _role = role;
    notifyListeners();
  }

  Future<void> login(String userId, String password, String mineId) async {
    _userId = userId;
    _name = 'Inspector ';
    _mineId = mineId;
    _isAuthenticated = true;
    await _secureStorage.saveAuthSession(
      token: 'demo-jwt-token-sih26024',
      userId: userId,
      mineId: mineId,
      role: _role,
    );
    notifyListeners();
  }

  Future<void> logout() async {
    _isAuthenticated = false;
    await _secureStorage.clearSession();
    notifyListeners();
  }
}
