import 'package:flutter/material.dart';

/// 🎨 Paleta de marca — Banco Ripley
class AppColors {
  AppColors._();

  // Colores corporativos Ripley
  static const Color primary = Color(0xFF4F2D7F);      // Morado Minsk
  static const Color primaryDark = Color(0xFF3A1F5E);   // Morado oscuro
  static const Color primaryLight = Color(0xFF6B3FA0);  // Morado claro
  static const Color secondary = Color(0xFFE4606D);     // Rosa Mandy
  static const Color accent = Color(0xFF491217);        // Rojo Paco

  // Colores de texto y fondo
  static const Color background = Color(0xFFF5F5F5);
  static const Color surface = Colors.white;
  static const Color visitedTile = Color(0xFFE8E8E8);

  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF666666);
  static const Color onPrimary = Colors.white;

  // Estados / semáforo
  static const Color success = Color(0xFF2E7D32);
  static const Color warning = Color(0xFFF9A825);
  static const Color danger = Color(0xFFC62828);
  static const Color info = Color(0xFF1565C0);
  static const Color neutral = Color(0xFF8D7B81);

  // Tipos de gestión
  static const Color renovacion = Color(0xFF1976D2);
  static const Color ampliacion = Color(0xFF388E3C);
  static const Color nuevaSolicitud = Color(0xFFF57C00);
  static const Color seguimiento = Color(0xFF757575);
  static const Color recuperacionMora = Color(0xFFD32F2F);
  static const Color desertor = Color(0xFF7B1FA2);

  // Prioridad
  static const Color prioridadAlta = recuperacionMora;
  static const Color prioridadMedia = warning;
  static const Color prioridadNormal = success;

  /// Degradado de marca Ripley (Morado → Rosa)
  static const List<Color> brandGradient = [
    Color(0xFF4F2D7F),  // Morado Minsk
    Color(0xFF6B3FA0),  // Morado intermedio
    Color(0xFFE4606D),  // Rosa Mandy
  ];
}