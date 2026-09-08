import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class EvidenceAttachmentTile extends StatelessWidget {
  final List<String> evidenceUrls;
  final Function(String) onAddEvidence;

  const EvidenceAttachmentTile({
    super.key,
    required this.evidenceUrls,
    required this.onAddEvidence,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Digital Evidence (Photos, Audio, Video)',
          style: TextStyle(color: AppColors.textSecondary, fontSize: 13, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...evidenceUrls.map((url) => Chip(
              backgroundColor: AppColors.surface,
              avatar: const Icon(Icons.attach_file, color: AppColors.safetyOrange, size: 16),
              label: Text(
                url.split('/').last,
                style: const TextStyle(color: AppColors.textPrimary, fontSize: 12),
              ),
            )),
            ActionChip(
              backgroundColor: AppColors.surface,
              avatar: const Icon(Icons.camera_alt, color: AppColors.safetyOrange, size: 18),
              label: const Text('Add Photo', style: TextStyle(color: AppColors.safetyOrange, fontSize: 12)),
              onPressed: () {
                onAddEvidence('/storage/uploads/photo_.jpg');
              },
            ),
            ActionChip(
              backgroundColor: AppColors.surface,
              avatar: const Icon(Icons.mic, color: AppColors.purpleAI, size: 18),
              label: const Text('Add Voice Note', style: TextStyle(color: AppColors.purpleAI, fontSize: 12)),
              onPressed: () {
                onAddEvidence('/storage/uploads/voice_note_.m4a');
              },
            ),
          ],
        )
      ],
    );
  }
}
