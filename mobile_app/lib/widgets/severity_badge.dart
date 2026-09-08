import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class SeverityBadge extends StatelessWidget {
  final String severity;

  const SeverityBadge({super.key, required this.severity});

  Color _getColor() {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
      case 'FATAL':
        return AppColors.dangerRed;
      case 'HIGH':
      case 'MAJOR':
        return AppColors.safetyOrange;
      case 'MEDIUM':
      case 'MODERATE':
        return AppColors.safetyAmber;
      case 'LOW':
      case 'MINOR':
      default:
        return AppColors.emeraldGreen;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.parseBorderSide(BorderSide(color: color.withOpacity(0.4), width: 1)),
      ),
      child: Text(
        severity.toUpperCase(),
        style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold),
      ),
    );
  }
}
