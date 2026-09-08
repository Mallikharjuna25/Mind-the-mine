import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/field_report_provider.dart';
import '../../widgets/offline_status_banner.dart';
import '../../widgets/evidence_attachment_tile.dart';

class QuickReportScreen extends StatefulWidget {
  const QuickReportScreen({super.key});

  @override
  State<QuickReportScreen> createState() => _QuickReportScreenState();
}

class _QuickReportScreenState extends State<QuickReportScreen> {
  final _descController = TextEditingController();
  final List<String> _categories = [
    'HAZARD',
    'SAFETY_OBSERVATION',
    'VIOLATION',
    'EQUIPMENT_MAINTENANCE',
    'ENVIRONMENTAL',
  ];
  final List<String> _severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

  @override
  void dispose() {
    _descController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final reportProv = context.watch<FieldReportProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Quick Field Observation')),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    color: AppColors.surface,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          const Icon(Icons.gps_fixed, color: AppColors.emeraldGreen, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Physical Geo-tag Coordinates', style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                                Text(
                                  '${reportProv.latitude.toStringAsFixed(4)}° N, ${reportProv.longitude.toStringAsFixed(4)}° E',
                                  style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                                ),
                              ],
                            ),
                          ),
                          Text('± ${reportProv.accuracy}m', style: const TextStyle(color: AppColors.textSecondary, fontSize: 11)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  DropdownButtonFormField<String>(
                    value: reportProv.category,
                    decoration: const InputDecoration(labelText: 'Observation Category'),
                    dropdownColor: AppColors.surface,
                    items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                    onChanged: (val) {
                      if (val != null) reportProv.setCategory(val);
                    },
                  ),
                  const SizedBox(height: 16),

                  DropdownButtonFormField<String>(
                    value: reportProv.severity,
                    decoration: const InputDecoration(labelText: 'Assessed Urgency / Severity'),
                    dropdownColor: AppColors.surface,
                    items: _severities.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                    onChanged: (val) {
                      if (val != null) reportProv.setSeverity(val);
                    },
                  ),
                  const SizedBox(height: 16),

                  TextField(
                    controller: _descController,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      labelText: 'Field Observation Notes',
                      hintText: 'e.g. Excessive coal spillage observed on incline belt 3, tension pulley loose...',
                    ),
                    onChanged: (val) => reportProv.setDescription(val),
                  ),
                  const SizedBox(height: 16),

                  EvidenceAttachmentTile(
                    evidenceUrls: reportProv.evidenceUrls,
                    onAddEvidence: (path) => reportProv.addEvidence(path),
                  ),
                  const SizedBox(height: 24),

                  ElevatedButton.icon(
                    onPressed: reportProv.isSubmitting
                        ? null
                        : () async {
                            reportProv.setDescription(_descController.text);
                            final ok = await reportProv.submitReport();
                            if (context.mounted && ok) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Field report saved to local SQLite & sync queue!'),
                                  backgroundColor: AppColors.emeraldGreen,
                                ),
                              );
                              Navigator.pop(context);
                            }
                          },
                    icon: reportProv.isSubmitting
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                        : const Icon(Icons.send),
                    label: const Text('LOG OBSERVATION'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
