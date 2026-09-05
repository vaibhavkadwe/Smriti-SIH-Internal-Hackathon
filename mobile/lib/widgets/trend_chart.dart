/// Simple 14-day sparkline for accuracy / reaction-time trends. No extra chart
/// package — CustomPaint keeps the mobile/dashboard apps dependency-light.
library;

import 'package:flutter/material.dart';

class TrendChart extends StatelessWidget {
  final List<double?> values;
  final String title;
  final String subtitle;
  final Color color;

  const TrendChart({
    super.key,
    required this.values,
    required this.title,
    this.subtitle = '',
    this.color = Colors.teal,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            if (subtitle.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(subtitle, style: const TextStyle(fontSize: 13, color: Colors.black54)),
            ],
            const SizedBox(height: 12),
            SizedBox(
              height: 88,
              width: double.infinity,
              child: CustomPaint(painter: _SparklinePainter(values, color)),
            ),
          ],
        ),
      ),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<double?> values;
  final Color color;

  _SparklinePainter(this.values, this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final pts = <Offset>[];
    final finite = values.whereType<double>().toList();
    if (finite.isEmpty || values.length < 2) {
      final p = Paint()
        ..color = Colors.grey.shade300
        ..strokeWidth = 2;
      canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), p);
      return;
    }
    final minV = finite.reduce((a, b) => a < b ? a : b);
    final maxV = finite.reduce((a, b) => a > b ? a : b);
    final span = (maxV - minV).abs() < 0.001 ? 1.0 : (maxV - minV);
    final dx = size.width / (values.length - 1);
    for (var i = 0; i < values.length; i++) {
      final v = values[i];
      if (v == null) continue;
      final y = size.height - ((v - minV) / span) * size.height;
      pts.add(Offset(i * dx, y));
    }
    if (pts.length < 2) return;
    final line = Paint()
      ..color = color
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeJoin = StrokeJoin.round;
    final path = Path()..moveTo(pts.first.dx, pts.first.dy);
    for (final p in pts.skip(1)) {
      path.lineTo(p.dx, p.dy);
    }
    canvas.drawPath(path, line);
    final dot = Paint()..color = color;
    canvas.drawCircle(pts.last, 4, dot);
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter oldDelegate) =>
      oldDelegate.values != values || oldDelegate.color != color;
}
