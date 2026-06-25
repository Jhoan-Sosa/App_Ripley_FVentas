import '../../../core/storage/local_db.dart';
import '../domain/cartera_model.dart';

/// Fuente local SIMPLIFICADA para Firestore.
class CarteraLocalDataSource {
  final LocalDb _db;
  CarteraLocalDataSource([LocalDb? db]) : _db = db ?? LocalDb.instance;

  Future<List<CarteraItem>> leerCache(String asesorId) async {
    // En web, no hay cache local porque usamos Firestore
    return [];
  }

  Future<void> guardarCache(String asesorId, List<CarteraItem> items) async {
    // En web, no guardamos cache local
  }

  Future<void> actualizarOrden(List<CarteraItem> items) async {
    // En web, no guardamos orden local
  }

  Future<void> actualizarEstadoVisita(String id, String estado) async {
    // En web, no actualizamos cache local
  }

  Future<void> encolarVisita({
    required String carteraId,
    required String resultado,
    required String observacion,
    double? lat,
    double? lng,
  }) async {
    // En web, no encolamos visitas localmente
  }

  Future<void> seedDemo(String asesorId) async {
    // No hacer nada en web
  }

  Future<List<Map<String, Object?>>> visitasPendientes() async {
    return [];
  }

  Future<void> eliminarPendiente(String id) async {}

  Future<int> contarPendientes() async {
    return 0;
  }
}