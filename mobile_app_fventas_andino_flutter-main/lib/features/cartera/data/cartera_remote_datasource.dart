import '../../../core/network/api_client.dart';
import '../domain/cartera_model.dart';

/// Fuente remota de la cartera desde el backend FastAPI (GET /cartera).
class CarteraRemoteDataSource {
  final ApiClient _api;
  CarteraRemoteDataSource(this._api);

  Future<List<CarteraItem>> obtenerCartera({
    required String asesorId, // el backend ya filtra por el token; se mantiene por firma
    required DateTime fecha,
  }) async {
    final fechaStr = fecha.toIso8601String().substring(0, 10);
    final data = await _api.get('/cartera?fecha=$fechaStr');
    return (data as List)
        .map((e) => CarteraItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> registrarVisita({
    required String carteraId,
    required String resultado,
    required String observacion,
    double? lat,
    double? lng,
  }) async {
    await _api.post('/cartera/$carteraId/visita', {
      'resultado': resultado,
      'observacion': observacion,
      'lat': lat,
      'lng': lng,
    });
  }
}
