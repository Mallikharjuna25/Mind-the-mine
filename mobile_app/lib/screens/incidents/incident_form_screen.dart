import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/incident_provider.dart';
import '../../widgets/offline_status_banner.dart';
import '../../widgets/evidence_attachment_tile.dart';
import 'ai_review_dialog.dart';

class IncidentFormScreen extends StatefulWidget {
  final String? prefilledDescription;

  const IncidentFormScreen({super.key, this.prefilledDescription});

  @override
  State<IncidentFormScreen> createState() => _IncidentFormScreenState();
}

class _IncidentFormScreenState extends State<IncidentFormScreen> {
  late TextEditingController _descController;
  late TextEditingController _locController;
  late TextEditingController _actionController;

  final List<String> _incidentTypes = [
    'EQUIPMENT_FAILURE',
    'FIRE',
    'ACCIDENT',
    'INJURY',
    'ROOF_FALL',
    'GAS_HAZARD',
    'ENVIRONMENTAL',
    'SAFETY_OBSERVATION',
  ];

  final List<String> _severities = [
    'MINOR',
    'MODERATE',
    'MAJOR',
    'CRITICAL',
    'FATAL',
  ];

  @override
  void initState() {
    super.initState();
    _descController = TextEditingController(text: widget.prefilledDescription ?? '');
    _locController = TextEditingController(text: 'Haul Road Junction 3');
    _actionController = TextEditingController();
  }

  @override
  void dispose() {
    _descController.dispose();
    _locController.dispose();
    _actionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final incidentProv = context.watch<IncidentProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Rapid Incident Reporting'),
      ),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // GPS Location Badge
                  Card(
                    color: AppColors.surface,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          const Icon(Icons.location_on, color: AppColors.safetyOrange, size: 20),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Current Geo-coordinates (Auto-captured)', style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                                Text('23.7957° N, 86.4304° E (± 3.2m accuracy)', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppColors.emeraldGreen.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text('GPS LOCKED', style: TextStyle(color: AppColors.emeraldGreen, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // AI Assistive Voice Input Banner
                  Container(
                    padding: const EdgeInsets.all(12.0),
                    decoration: BoxDecoration(
                      color: AppColors.purpleAI.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppColors.purpleAI.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.mic, color: AppColors.purpleAI, size: 24),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('AI Voice-to-Incident Structuring', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
                              Text('Dictate or type raw observations; AI will structure taxonomy.', style: TextStyle(color: AppColors.textSecondary, fontSize: 11)),
                            ],
                          ),
                        ),
                        ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.purpleAI,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          ),
                          onPressed: incidentProv.isLoadingAI
                              ? null
                              : () async {
                                  // Analyze input with AI
                                  await incidentProv.analyzeNotesWithAI(_descController.text);
                                  if (context.mounted && incidentProv.currentAISuggestion != null) {
                                    showDialog(
                                      context: context,
                                      builder: (_) => AIReviewDialog(
                                        suggestion: incidentProv.currentAISuggestion!,
                                        onConfirm: () {
                                          final sug = incidentProv.currentAISuggestion!;
                                          incidentProv.applyAISuggestions(sug);
                                          _locController.text = sug.suggestedLocation;
                                        },
                                      ),
                                    );
                                  }
                                },
                          icon: incidentProv.isLoadingAI
                              ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Icon(Icons.auto_awesome, size: 16),
                          label: const Text('Analyze', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Classification Dropdowns
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: incidentProv.incidentType,
                          decoration: const InputDecoration(labelText: 'Incident Type'),
                          dropdownColor: AppColors.surface,
                          items: _incidentTypes.map((t) => DropdownMenuItem(value: t, child: Text(t, style: const TextStyle(fontSize: 12)))).toList(),
                          onChanged: (val) {
                            if (val != null) incidentProv.setIncidentType(val);
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: incidentProv.severity,
                          decoration: const InputDecoration(labelText: 'Severity Rating'),
                          dropdownColor: AppColors.surface,
                          items: _severities.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontSize: 12)))).toList(),
                          onChanged: (val) {
                            if (val != null) incidentProv.setSeverity(val);
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  TextField(
                    controller: _locController,
                    decoration: const InputDecoration(
                      labelText: 'Specific Location / Landmark Name',
                      prefixIcon: Icon(Icons.signpost, color: AppColors.safetyOrange),
                    ),
                    onChanged: (val) => incidentProv.setLocationName(val),
                  ),
                  const SizedBox(height: 16),

                  TextField(
                    controller: _descController,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      labelText: 'Incident Description / Voice Note Transcript',
                      hintText: 'e.g. Near haul road 4 around 10:30, dumper brake failed, smoke near engine...',
                    ),
                    onChanged: (val) => incidentProv.setDescription(val),
                  ),
                  const SizedBox(height: 16),

                  TextField(
                    controller: _actionController,
                    decoration: const InputDecoration(
                      labelText: 'Immediate Action Taken at Site',
                      hintText: 'e.g. Area cordoned off, emergency siren blown, first-aid summoned',
                      prefixIcon: Icon(Icons.shield, color: AppColors.emeraldGreen),
                    ),
                    onChanged: (val) => incidentProv.setImmediateAction(val),
                  ),
                  const SizedBox(height: 16),

                  EvidenceAttachmentTile(
                    evidenceUrls: incidentProv.evidenceUrls,
                    onAddEvidence: (path) => incidentProv.addEvidence(path),
                  ),
                  const SizedBox(height: 24),

                  ElevatedButton.icon(
                    onPressed: incidentProv.isSubmitting
                        ? null
                        : () async {
                            incidentProv.setDescription(_descController.text);
                            incidentProv.setLocationName(_locController.text);
                            incidentProv.setImmediateAction(_actionController.text);
                            final ok = await incidentProv.submitIncident();
                            if (context.mounted && ok) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Incident reported! Saved locally to SQLite & queued for sync.'),
                                  backgroundColor: AppColors.emeraldGreen,
                                ),
                              );
                              Navigator.pop(context);
                            }
                          },
                    icon: incidentProv.isSubmitting
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                        : const Icon(Icons.report_problem),
                    label: const Text('SUBMIT INCIDENT RECORD'),
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
