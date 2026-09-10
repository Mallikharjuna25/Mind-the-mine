import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import 'checklist_runner_screen.dart';

class InspectionListScreen extends StatelessWidget {
  const InspectionListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Assigned Statutory Inspections')),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          _buildInspectionCard(
            context,
            code: 'TMPL-DGMS-FIRE-01',
            title: 'DGMS Fire Safety & Gas Inundation Inspection',
            category: 'FIRE_SAFETY',
            scheduledShift: 'Shift A (Morning)',
            targetZone: 'Pit 1 - Working Seam 4',
            itemCount: 5,
          ),
          const SizedBox(height: 12),
          _buildInspectionCard(
            context,
            code: 'TMPL-ENV-MON-02',
            title: 'MoEFCC Environmental & Dust Compliance Audit',
            category: 'ENVIRONMENTAL',
            scheduledShift: 'Shift B (Afternoon)',
            targetZone: 'North Haul Road & Settling Pond',
            itemCount: 3,
          ),
          const SizedBox(height: 12),
          _buildInspectionCard(
            context,
            code: 'TMPL-HEMM-STAT-03',
            title: 'HEMM Heavy Machinery Pre-Shift Mechanical Audit',
            category: 'MACHINERY',
            scheduledShift: 'Shift A (Pre-deployment)',
            targetZone: 'Central Workshop / Fleet Yard',
            itemCount: 3,
          ),
        ],
      ),
    );
  }

  Widget _buildInspectionCard(
    BuildContext context, {
    required String code,
    required String title,
    required String category,
    required String scheduledShift,
    required String targetZone,
    required int itemCount,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.safetyOrange.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(code, style: const TextStyle(color: AppColors.safetyOrange, fontWeight: FontWeight.bold, fontSize: 11)),
                ),
                Text('$itemCount Items', style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
              ],
            ),
            const SizedBox(height: 10),
            Text(title, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 14)),
            const SizedBox(height: 6),
            Text('Target: $targetZone', style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
            Text('Scheduled: $scheduledShift', style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
            const SizedBox(height: 14),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const ChecklistRunnerScreen()));
                },
                icon: const Icon(Icons.play_arrow, size: 16),
                label: const Text('START AUDIT'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
