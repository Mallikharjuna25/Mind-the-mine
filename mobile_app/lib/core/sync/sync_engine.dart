import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../network/network_info.dart';
import '../network/api_client.dart';
import '../storage/database_helper.dart';
import '../storage/secure_storage_helper.dart';
import 'sync_queue_item.dart';

class SyncEngine extends ChangeNotifier {
  final NetworkInfo _networkInfo;
  final ApiClient _apiClient;
  final DatabaseHelper _dbHelper;
  final SecureStorageHelper _secureStorage;

  StreamSubscription<bool>? _connectivitySub;
  bool _isSyncing = false;
  int _pendingCount = 0;
  String? _lastSyncMessage;

  SyncEngine({
    NetworkInfo? networkInfo,
    ApiClient? apiClient,
    DatabaseHelper? dbHelper,
    SecureStorageHelper? secureStorage,
  })  : _networkInfo = networkInfo ?? NetworkInfo(),
        _apiClient = apiClient ?? ApiClient(),
        _dbHelper = dbHelper ?? DatabaseHelper(),
        _secureStorage = secureStorage ?? SecureStorageHelper() {
    _initEngine();
  }

  bool get isSyncing => _isSyncing;
  int get pendingCount => _pendingCount;
  String? get lastSyncMessage => _lastSyncMessage;

  void _initEngine() {
    refreshPendingCount();
    _connectivitySub = _networkInfo.onConnectivityChanged.listen((isConnected) {
      if (isConnected && !_isSyncing) {
        syncAllPending();
      }
    });
  }

  Future<void> refreshPendingCount() async {
    try {
      _pendingCount = await _dbHelper.getPendingQueueCount();
      notifyListeners();
    } catch (_) {}
  }

  Future<bool> syncAllPending() async {
    final online = await _networkInfo.isConnected;
    if (!online) {
      _lastSyncMessage = 'No network connectivity detected. Retaining local queue.';
      notifyListeners();
      return false;
    }

    if (_isSyncing) return false;
    _isSyncing = true;
    notifyListeners();

    try {
      final pendingRows = await _dbHelper.getPendingQueueItems();
      if (pendingRows.isEmpty) {
        _isSyncing = false;
        _pendingCount = 0;
        _lastSyncMessage = 'All records synchronized.';
        notifyListeners();
        return true;
      }

      final officerId = await _secureStorage.getUserId() ?? 'INSP-DEV-001';

      // Group payloads by entity type
      final List<Map<String, dynamic>> fieldReports = [];
      final List<Map<String, dynamic>> inspections = [];
      final List<Map<String, dynamic>> incidents = [];

      for (var row in pendingRows) {
        final entityType = row['entity_type'] as String;
        final payload = jsonDecode(row['payload'] as String) as Map<String, dynamic>;
        final clientId = row['client_id'] as String;

        // Mark local queue item as SYNCING
        await _dbHelper.updateQueueStatus(clientId, 'SYNCING');

        if (entityType == 'FIELD_REPORT') {
          fieldReports.add(payload);
        } else if (entityType == 'INSPECTION') {
          inspections.add(payload);
        } else if (entityType == 'INCIDENT') {
          incidents.add(payload);
        }
      }

      final batchRequest = {
        'officer_id': officerId,
        'sync_timestamp': DateTime.now().toIso8601String(),
        'field_reports': fieldReports,
        'inspections': inspections,
        'incidents': incidents,
      };

      final response = await _apiClient.post('/sync/batch', data: batchRequest);

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final results = data['results'] as List<dynamic>? ?? [];

        for (var res in results) {
          final clientId = res['client_id'] as String;
          final status = res['status'] as String;
          if (status == 'SYNCED') {
            await _dbHelper.updateQueueStatus(clientId, 'SYNCED');
          } else {
            await _dbHelper.updateQueueStatus(clientId, 'SYNC_FAILED', error: res['message']?.toString());
          }
        }

        await refreshPendingCount();
        _lastSyncMessage = 'Synchronized  items successfully.';
        _isSyncing = false;
        notifyListeners();
        return true;
      } else {
        throw Exception('Server returned status code: ');
      }
    } catch (e) {
      _lastSyncMessage = 'Sync failed: . Will retry automatically upon reconnection.';
      _isSyncing = false;
      await refreshPendingCount();
      notifyListeners();
      return false;
    }
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    super.dispose();
  }
}
