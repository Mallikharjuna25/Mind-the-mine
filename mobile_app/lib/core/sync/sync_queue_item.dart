enum SyncStatus {
  draft,
  readyToSync,
  syncing,
  synced,
  syncFailed,
  conflict;

  static SyncStatus fromString(String value) {
    switch (value.toUpperCase()) {
      case 'DRAFT':
        return SyncStatus.draft;
      case 'READY_TO_SYNC':
        return SyncStatus.readyToSync;
      case 'SYNCING':
        return SyncStatus.syncing;
      case 'SYNCED':
        return SyncStatus.synced;
      case 'CONFLICT':
        return SyncStatus.conflict;
      case 'SYNC_FAILED':
      default:
        return SyncStatus.syncFailed;
    }
  }

  String toDbString() {
    switch (this) {
      case SyncStatus.draft:
        return 'DRAFT';
      case SyncStatus.readyToSync:
        return 'READY_TO_SYNC';
      case SyncStatus.syncing:
        return 'SYNCING';
      case SyncStatus.synced:
        return 'SYNCED';
      case SyncStatus.conflict:
        return 'CONFLICT';
      case SyncStatus.syncFailed:
        return 'SYNC_FAILED';
    }
  }
}

class SyncQueueItem {
  final int? id;
  final String clientId;
  final String entityType; // FIELD_REPORT, INSPECTION, INCIDENT
  final Map<String, dynamic> payload;
  final SyncStatus status;
  final int retryCount;
  final DateTime createdAt;
  final String? lastError;

  SyncQueueItem({
    this.id,
    required this.clientId,
    required this.entityType,
    required this.payload,
    required this.status,
    this.retryCount = 0,
    required this.createdAt,
    this.lastError,
  });
}
