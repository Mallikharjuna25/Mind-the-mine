import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/constants/app_colors.dart';
import '../providers/connectivity_provider.dart';
import '../providers/sync_provider.dart';

class OfflineStatusBanner extends StatelessWidget {
  const OfflineStatusBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final connectivity = context.watch<ConnectivityProvider>();
    final sync = context.watch<SyncProvider>();

    if (!connectivity.isOnline) {
      return Container(
        width: double.infinity,
        color: AppColors.offline.withOpacity(0.2),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          children: [
            const Icon(Icons.cloud_off, color: AppColors.offline, size: 18),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                'Offline Mode —  records stored locally in SQLite.',
                style: const TextStyle(color: AppColors.offline, fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.info_outline, color: AppColors.offline, size: 16),
              onPressed: () {
                connectivity.toggleSimulatedOffline();
              },
              tooltip: 'Toggle Network Simulation',
            )
          ],
        ),
      );
    }

    if (sync.isSyncing) {
      return Container(
        width: double.infinity,
        color: AppColors.syncing.withOpacity(0.2),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: const Row(
          children: [
            SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.syncing),
            ),
            SizedBox(width: 8),
            Text(
              'Syncing local queue with Central MineGuard Server...',
              style: TextStyle(color: AppColors.syncing, fontSize: 12, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      color: AppColors.online.withOpacity(0.12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(color: AppColors.online, shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
              Text(
                'Connected to Central Server | Queue:  pending',
                style: const TextStyle(color: AppColors.online, fontSize: 11),
              ),
            ],
          ),
          InkWell(
            onTap: () => connectivity.toggleSimulatedOffline(),
            child: const Text('Simulate Offline', style: TextStyle(color: AppColors.textMuted, fontSize: 11, decoration: TextDecoration.underline)),
          )
        ],
      ),
    );
  }
}
