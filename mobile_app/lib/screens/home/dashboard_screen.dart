import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../../providers/sync_provider.dart';
import '../../widgets/offline_status_banner.dart';
import '../inspections/checklist_runner_screen.dart';
import '../incidents/incident_form_screen.dart';
import '../reports/quick_report_screen.dart';
import '../verification/remediation_tracker_screen.dart';
import '../gis/map_view_screen.dart';
import '../sync/sync_center_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final sync = context.watch<SyncProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Field Operations Hub', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text(' • ', style: const TextStyle(fontSize: 11, color: AppColors.safetyOrange)),
          ],
        ),
        actions: [
          IconButton(
            icon: Badge(
              label: Text(''),
              isLabelVisible: sync.pendingCount > 0,
              child: const Icon(Icons.sync),
            ),
            tooltip: 'Sync Center',
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SyncCenterScreen()));
            },
          ),
        ],
      ),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                // Quick Shift Metrics
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildMetricCol('SHIFT', 'A (Morning)', Icons.timer, AppColors.electricBlue),
                        _buildMetricCol('SYNC QUEUE', ' Local', Icons.cloud_queue, sync.pendingCount > 0 ? AppColors.safetyAmber : AppColors.emeraldGreen),
                        _buildMetricCol('ACTIVE GPS', '23.79° N, 86.43° E', Icons.my_location, AppColors.safetyOrange),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                const Text('Field Execution Modules', style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 8),

                // 1. Digital Checklists
                _buildActionCard(
                  context,
                  title: 'Statutory Inspection Checklist',
                  subtitle: 'Execute DGMS Fire Safety, MoEFCC & HEMM Machinery digital audits with photo evidence',
                  icon: Icons.assignment_turned_in,
                  iconColor: AppColors.safetyOrange,
                  badge: 'DGMS Standard',
                  onTap: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const ChecklistRunnerScreen()));
                  },
                ),
                const SizedBox(height: 12),

                // 2. Incident Management
                _buildActionCard(
                  context,
                  title: 'Report Mine Incident',
                  subtitle: 'Rapid reporting for accidents, equipment breakdown, fire, or strata collapse with AI Voice Structuring',
                  icon: Icons.warning_amber,
                  iconColor: AppColors.dangerRed,
                  badge: 'AI Assisted',
                  onTap: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const IncidentFormScreen()));
                  },
                ),
                const SizedBox(height: 12),

                // 3. Quick Field Observation
                _buildActionCard(
                  context,
                  title: 'Quick Field Observation',
                  subtitle: 'Instant geo-tagged hazard or violation capture with camera snapshot',
                  icon: Icons.camera_alt,
                  iconColor: AppColors.emeraldGreen,
                  onTap: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const QuickReportScreen()));
                  },
                ),
                const SizedBox(height: 12),

                // 4. Verification & Corrective Action
                _buildActionCard(
                  context,
                  title: 'Field Verification & Remediation',
                  subtitle: 'Review remediation evidence, verify contractor fixes, and digitally close safety findings',
                  icon: Icons.verified,
                  iconColor: AppColors.electricBlue,
                  badge: 'Governance',
                  onTap: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const RemediationTrackerScreen()));
                  },
                ),
                const SizedBox(height: 12),

                // 5. GIS Map Preview
                _buildActionCard(
                  context,
                  title: 'GIS Mine Pit Map',
                  subtitle: 'Interactive spatial map of geo-tagged inspection points, hazards, and active benches',
                  icon: Icons.map,
                  iconColor: AppColors.purpleAI,
                  onTap: () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => const MapViewScreen()));
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCol(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
        Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 10)),
      ],
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color iconColor,
    String? badge,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: iconColor.withOpacity(0.3)),
                ),
                child: Icon(icon, color: iconColor, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(title, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 14)),
                        if (badge != null) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: iconColor.withOpacity(0.12),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: iconColor.withOpacity(0.3)),
                            ),
                            child: Text(badge, style: TextStyle(color: iconColor, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(subtitle, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios, size: 14, color: AppColors.textMuted),
            ],
          ),
        ),
      ),
    );
  }
}
