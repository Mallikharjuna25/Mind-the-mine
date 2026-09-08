import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/offline_status_banner.dart';

class MapViewScreen extends StatelessWidget {
  const MapViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('GIS Mine Pit Map (Geo-Handoff)')),
      body: Column(
        children: [
          const OfflineStatusBanner(),
          Expanded(
            child: Stack(
              children: [
                // Simulated Mine Pit Topology Canvas
                Container(
                  color: const Color(0xFF131A24),
                  child: CustomPaint(
                    size: Size.infinite,
                    painter: _MinePitPainter(),
                  ),
                ),
                // Legend Overlay
                Positioned(
                  top: 16,
                  left: 16,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.surface.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppColors.cardBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('MINE-DHANBAD-01 • SEAM 4', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppColors.textPrimary)),
                        const SizedBox(height: 6),
                        _buildLegendRow('Haul Road Crossing (Incident)', AppColors.dangerRed),
                        _buildLegendRow('Inspection Checkpoint', AppColors.safetyOrange),
                        _buildLegendRow('Field Hazard Observation', AppColors.safetyAmber),
                        _buildLegendRow('Active Coal Bench Face', AppColors.emeraldGreen),
                      ],
                    ),
                  ),
                ),
                // Current Inspector GPS Indicator
                Positioned(
                  bottom: 24,
                  right: 16,
                  child: FloatingActionButton.extended(
                    backgroundColor: AppColors.safetyOrange,
                    foregroundColor: Colors.black,
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('GPS Centered: 23.7957° N, 86.4304° E (Accuracy: ±3m)')),
                      );
                    },
                    icon: const Icon(Icons.my_location),
                    label: const Text('MY LOCATION'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegendRow(String label, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 8),
          Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 10)),
        ],
      ),
    );
  }
}

class _MinePitPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final contourPaint = Paint()
      ..color = const Color(0xFF263345)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    // Draw concentric bench contour lines
    final center = Offset(size.width * 0.5, size.height * 0.45);
    for (double r = 40; r < size.width * 0.6; r += 45) {
      canvas.drawOval(Rect.fromCenter(center: center, width: r * 2.2, height: r * 1.5), contourPaint);
    }

    // Draw Pin 1: Incident Location
    final incidentPaint = Paint()..color = AppColors.dangerRed;
    final pin1 = Offset(size.width * 0.4, size.height * 0.35);
    canvas.drawCircle(pin1, 8, incidentPaint);
    canvas.drawCircle(pin1, 14, incidentPaint..color = AppColors.dangerRed.withOpacity(0.3));

    // Draw Pin 2: Statutory Inspection Checkpoint
    final inspPaint = Paint()..color = AppColors.safetyOrange;
    final pin2 = Offset(size.width * 0.6, size.height * 0.5);
    canvas.drawCircle(pin2, 7, inspPaint);

    // Draw Pin 3: Field Hazard Observation
    final hazardPaint = Paint()..color = AppColors.safetyAmber;
    final pin3 = Offset(size.width * 0.52, size.height * 0.28);
    canvas.drawCircle(pin3, 6, hazardPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
