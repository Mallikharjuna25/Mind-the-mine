import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../data/models/incident_model.dart';
import '../../widgets/severity_badge.dart';

class AIReviewDialog extends StatelessWidget {
  final AIStructuringSuggestion suggestion;
  final VoidCallback onConfirm;

  const AIReviewDialog({
    super.key,
    required this.suggestion,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.surface,
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: AppColors.purpleAI.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.auto_awesome, color: AppColors.purpleAI, size: 20),
          ),
          const SizedBox(width: 10),
          const Text('AI Assistive Structuring', style: TextStyle(fontSize: 16)),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Original Voice / Text Note:', style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '"${suggestion.rawText}"',
                style: const TextStyle(color: AppColors.textSecondary, fontStyle: FontStyle.italic, fontSize: 12),
              ),
            ),
            const SizedBox(height: 16),
            const Text('AI Suggested Extraction:', style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 8),
            _buildFieldRow('Incident Type', suggestion.suggestedIncidentType),
            _buildFieldRow('Hazard Category', suggestion.suggestedHazard),
            _buildFieldRow('Identified Location', suggestion.suggestedLocation),
            _buildFieldRow('Injury Status', suggestion.suggestedInjury),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Assessed Severity:', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                  SeverityBadge(severity: suggestion.suggestedSeverity),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.verified_user, color: AppColors.emeraldGreen, size: 14),
                const SizedBox(width: 4),
                Text(
                  'Confidence: ${(suggestion.confidenceScore * 100).toInt()}% • Assistive Governance',
                  style: const TextStyle(color: AppColors.emeraldGreen, fontSize: 11),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel / Keep Raw', style: TextStyle(color: AppColors.textMuted)),
        ),
        ElevatedButton(
          onPressed: () {
            onConfirm();
            Navigator.pop(context);
          },
          child: const Text('CONFIRM & APPLY'),
        ),
      ],
    );
  }

  Widget _buildFieldRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('$label:', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
          Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 12)),
        ],
      ),
    );
  }
}
