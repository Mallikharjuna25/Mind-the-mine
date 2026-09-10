import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/verification_provider.dart';
import '../../widgets/offline_status_banner.dart';
import '../../widgets/severity_badge.dart';

class RemediationTrackerScreen extends StatelessWidget {
  const RemediationTrackerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final verProv = context.watch<VerificationProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Field Verification & Closure'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => verProv.loadVerifications(),
          )
        ],
      ),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          // Workflow Lifecycle Legend
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: AppColors.surface,
            child: const SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  Text('Lifecycle: ', style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                  Text('REPORTED → ', style: TextStyle(color: AppColors.textSecondary, fontSize: 11)),
                  Text('VERIFIED → ', style: TextStyle(color: AppColors.safetyOrange, fontSize: 11)),
                  Text('CORRECTIVE ACTION → ', style: TextStyle(color: AppColors.electricBlue, fontSize: 11)),
                  Text('EVIDENCE SUBMITTED → ', style: TextStyle(color: AppColors.purpleAI, fontSize: 11)),
                  Text('REVIEW → ', style: TextStyle(color: AppColors.safetyAmber, fontSize: 11)),
                  Text('APPROVED / CLOSED', style: TextStyle(color: AppColors.emeraldGreen, fontSize: 11, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ),
          const Divider(height: 1, color: AppColors.cardBorder),

          Expanded(
            child: verProv.isLoading
                ? const Center(child: CircularProgressIndicator(color: AppColors.safetyOrange))
                : verProv.verifications.isEmpty
                    ? const Center(
                        child: Text(
                          'No pending corrective actions or verification tasks.',
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16.0),
                        itemCount: verProv.verifications.length,
                        itemBuilder: (context, index) {
                          final item = verProv.verifications[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        'Task #${item.id.substring(0, 8)}',
                                        style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                                      ),
                                      SeverityBadge(severity: item.status),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Source: ${item.issueType} • Ref: ${item.sourceId.substring(0, 8)}',
                                    style: const TextStyle(color: AppColors.safetyOrange, fontSize: 12),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    item.remediationNotes ?? 'No remediation remarks recorded yet.',
                                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                                  ),
                                  const SizedBox(height: 12),

                                  // Action buttons based on current state
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      if (item.status == 'REPORTED')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.safetyOrange,
                                            foregroundColor: Colors.black,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(item.id, 'VERIFIED');
                                          },
                                          child: const Text('VERIFY ISSUE', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'VERIFIED')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.electricBlue,
                                            foregroundColor: Colors.white,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(
                                              item.id,
                                              'CORRECTIVE_ACTION',
                                              notes: 'Assigned to pit contractor for remediation within 24h SLA',
                                            );
                                          },
                                          child: const Text('ASSIGN ACTION', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'CORRECTIVE_ACTION')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.purpleAI,
                                            foregroundColor: Colors.white,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(
                                              item.id,
                                              'EVIDENCE_SUBMITTED',
                                              evidence: ['/storage/uploads/fix_proof_${DateTime.now().millisecondsSinceEpoch}.jpg'],
                                            );
                                          },
                                          child: const Text('UPLOAD FIX EVIDENCE', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'EVIDENCE_SUBMITTED')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.safetyAmber,
                                            foregroundColor: Colors.black,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(item.id, 'SUPERVISOR_REVIEW');
                                          },
                                          child: const Text('REVIEW EVIDENCE', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'SUPERVISOR_REVIEW')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.emeraldGreen,
                                            foregroundColor: Colors.black,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(item.id, 'APPROVED');
                                          },
                                          child: const Text('APPROVE FIX', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'APPROVED')
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: AppColors.emeraldGreen,
                                            foregroundColor: Colors.black,
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                          ),
                                          onPressed: () {
                                            verProv.advanceWorkflow(item.id, 'CLOSED');
                                          },
                                          child: const Text('CLOSE CASE', style: TextStyle(fontSize: 11)),
                                        ),
                                      if (item.status == 'CLOSED')
                                        const Chip(
                                          backgroundColor: AppColors.surface,
                                          avatar: Icon(Icons.check_circle, color: AppColors.emeraldGreen, size: 16),
                                          label: Text('OFFICIALLY CLOSED', style: TextStyle(color: AppColors.emeraldGreen, fontSize: 11, fontWeight: FontWeight.bold)),
                                        ),
                                    ],
                                  ),
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
