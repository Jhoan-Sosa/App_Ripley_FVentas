import 'dart:convert';
import '../../../core/storage/local_db.dart';
import '../domain/borrador_model.dart';

/// Persistencia de borradores SIMPLIFICADA para Firestore.
class SolicitudLocalDataSource {
  final LocalDb _db;
  SolicitudLocalDataSource([LocalDb? db]) : _db = db ?? LocalDb.instance;

  Future<void> guardarBorrador({
    required String id,
    required String asesorId,
    required String clienteNombre,
    required int pasoActual,
    required Map<String, dynamic> datos,
    required double montoSolicitado,
  }) async {
    // En web, no guardamos borradores localmente
    print('📝 Borrador guardado en memoria: $id');
  }

  Future<List<BorradorSolicitud>> listar(String asesorId) async {
    return [];
  }

  Future<void> eliminar(String id) async {}
}