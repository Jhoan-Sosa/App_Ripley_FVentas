import 'package:sqflite/sqflite.dart';

/// Base de datos local SIMPLIFICADA para Firestore.
/// En web, no usamos SQLite porque usamos Firestore directamente.
class LocalDb {
  LocalDb._();
  static final LocalDb instance = LocalDb._();

  /// En web, no hay base de datos local
  Future<Database> get database async {
    throw UnsupportedError('SQLite no soportado en web con Firestore');
  }

  Future<int> contarPendientesSync() async {
    return 0; // No hay pendientes porque usamos Firestore
  }

  Future<void> limpiarCacheSesion() async {
    // No hacer nada en web
  }

  Future<void> seedDemoSiVacio(String asesorId) async {
    // No hacer nada en web
  }
}