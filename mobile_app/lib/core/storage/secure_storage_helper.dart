import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageHelper {
  static const String _keyToken = "jwt_access_token";
  static const String _keyUserId = "active_officer_id";
  static const String _keyMineId = "active_mine_id";
  static const String _keyRole = "active_role";

  final FlutterSecureStorage _storage;

  SecureStorageHelper([FlutterSecureStorage? storage])
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  Future<void> saveAuthSession({
    required String token,
    required String userId,
    required String mineId,
    required String role,
  }) async {
    await _storage.write(key: _keyToken, value: token);
    await _storage.write(key: _keyUserId, value: userId);
    await _storage.write(key: _keyMineId, value: mineId);
    await _storage.write(key: _keyRole, value: role);
  }

  Future<String?> getToken() => _storage.read(key: _keyToken);
  Future<String?> getUserId() => _storage.read(key: _keyUserId);
  Future<String?> getMineId() => _storage.read(key: _keyMineId);
  Future<String?> getRole() => _storage.read(key: _keyRole);

  Future<void> clearSession() async {
    await _storage.deleteAll();
  }
}
