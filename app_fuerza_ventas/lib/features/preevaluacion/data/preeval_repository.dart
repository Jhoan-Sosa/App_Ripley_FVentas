import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';

/// Resultado de pre-evaluacion (M4 / RF-38).
class ResultadoPreEval {
  final String calificacion; // APTO / REVISAR / NO_PROCEDE
  final String motivo;
  final int puntaje;
  const ResultadoPreEval(this.calificacion, this.motivo, this.puntaje);

  factory ResultadoPreEval.fromJson(Map<String, dynamic> j) => ResultadoPreEval(
        j['calificacion'] as String? ?? 'REVISAR',
        j['motivo'] as String? ?? '',
        (j['puntaje'] as num?)?.toInt() ?? 0,
      );
}

class PreEvalRepository {
  final ApiClient _api;
  PreEvalRepository(this._api);

  Future<ResultadoPreEval> preEvaluar({
    required String documento,
    required String nombres,
    String apellidos = '',
    String? fechaNacimiento, // YYYY-MM-DD
    required String tipoNegocio,
    int antiguedadNegocioMeses = 0,
    required double ingresos,
    required double montoSolicitado,
    required String destino,
  }) async {
    final data = await _api.post('/pre-evaluar', {
      'numero_documento': documento,
      'nombres': nombres,
      'apellidos': apellidos,
      'fecha_nacimiento': fechaNacimiento,
      'tipo_negocio': tipoNegocio,
      'antiguedad_negocio_meses': antiguedadNegocioMeses,
      'ingresos_estimados': ingresos,
      'monto_solicitado': montoSolicitado,
      'destino_credito': destino,
    });
    return ResultadoPreEval.fromJson(data as Map<String, dynamic>);
  }
}

final preEvalRepositoryProvider = Provider<PreEvalRepository>((ref) {
  return PreEvalRepository(ref.watch(apiClientProvider));
});
