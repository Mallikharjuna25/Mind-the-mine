import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/storage/database_helper.dart';
import '../../providers/sync_provider.dart';
import '../../widgets/offline_status_banner.dart';
import '../../widgets/severity_badge.dart';

class SyncCenterScreen extends StatefulWidget {
  const SyncCenterScreen({super.key});

  @override
  State<SyncCenterScreen> createState() => _SyncCenterScreenState();
}

class _SyncCenterScreenState extends State<SyncCenterScreen> {
  final DatabaseHelper _dbHelper = DatabaseHelper();
  List<Map<String, dynamic>> _queueItems = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadQueue();
  }

  Future<void> _loadQueue() async {
    setState(() => _isLoading = true);
    try {
      final db = await _dbHelper.database;
      final items = await db.query('offline_sync_queue', orderBy: 'id DESC');
      setState(() {
        _queueItems = items;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final sync = context.watch<SyncProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Offline Sync Engine & Storage'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadQueue,
          )
        ],
      ),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          // Queue Action Header
          Container(
            padding: const EdgeInsets.all(16.0),
            color: AppColors.surface,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Durable SQLite Storage Queue', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text(
                      '${sync.pendingCount} Pending Upload',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: sync.pendingCount > 0 ? AppColors.safetyOrange : AppColors.emeraldGreen,
                      ),
                    ),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: sync.isSyncing
                      ? null
                      : () async {
                          await sync.triggerManualSync();
                          await _loadQueue();
                        },
                  icon: sync.isSyncing
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                      : const Icon(Icons.sync),
                  label: const Text('FORCE SYNC NOW'),
                )
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.cardBorder),

          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppColors.safetyOrange))
                : _queueItems.isEmpty
                    ? const Center(
                        child: Text(
                          'Offline queue is empty. All observations synced.',
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16.0),
                        itemCount: _queueItems.length,
                        itemBuilder: (context, index) {
                          final item = _queueItems[index];
                          final status = item['status'] as String;
                          final entityType = item['entity_type'] as String;
                          final clientId = item['client_id'] as String;
                          final createdAt = item['created_at'] as String;

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(14.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Icon(
                                            entityType == 'INSPECTION'
                                                ? Icons.assignment
                                                : entityType == 'INCIDENT'
                                                    ? Icons.warning
                                                    : Icons.photo_camera,
                                            size: 16,
                                            color: AppColors.safetyOrange,
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            entityType,
                                            style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                                          ),
                                        ],
                                      ),
                                      SeverityBadge(severity: status),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    'Client UUID: $clientId',
                                    style: const TextStyle(color: AppColors.textMuted, fontSize: 11, fontFamily: 'monospace'),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    'Captured at: $createdAt',
                                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 11),
                                  ),
                                  if (item['last_error'] != null) ...[
                                    const SizedBox(height: 6),
                                    Text(
                                      'Error: ${item['last_error']}',
                                      style: const TextStyle(color: AppColors.dangerRed, fontSize: 11),
                                    ),
                                  ]
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
