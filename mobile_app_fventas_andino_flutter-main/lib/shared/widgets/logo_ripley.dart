import 'package:flutter/material.dart';

class LogoRipley extends StatelessWidget {
  final double size;
  final bool showText;

  const LogoRipley({
    super.key,
    this.size = 96,
    this.showText = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          'assets/images/logo_ripley.png',
          width: size,
          height: size,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) {
            // Si no encuentra la imagen, muestra el texto "R" como fallback
            return Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                color: const Color(0xFF4F2D7F),
                borderRadius: BorderRadius.circular(size * 0.25),
              ),
              child: Center(
                child: Text(
                  'R',
                  style: TextStyle(
                    fontSize: size * 0.55,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            );
          },
        ),
        if (showText) ...[
          const SizedBox(height: 8),
          Text(
            'Banco Ripley',
            style: TextStyle(
              fontSize: size * 0.2,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF4F2D7F),
            ),
          ),
        ],
      ],
    );
  }
}