import 'package:flutter/foundation.dart';
import '../core/sync/sync_engine.dart';

class SyncProvider extends ChangeNotifier {
  final SyncEngine _syncEngine;

  SyncProvider(this._syncEngine) {
    _syncEngine.addListener(_onSyncEngineChange);
  }

  bool get isSyncing => _syncEngine.isSyncing;
  int get pendingCount => _syncEngine.pendingCount;
  String? get lastSyncMessage => _syncEngine.lastSyncMessage;

  void _onSyncEngineChange() {
    notifyListeners();
  }

  Future<bool> triggerManualSync() {
    return _syncEngine.syncAllPending();
  }

  @override
  void dispose() {
    _syncEngine.removeListener(_onSyncEngineChange);
    super.dispose();
  }
}
