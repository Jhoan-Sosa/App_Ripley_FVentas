import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../network/api_client.dart';
import '../notificaciones/notificacion_service.dart';
import '../../features/cartera/data/cartera_local_datasource.dart';
import '../../features/cartera/data/cartera_remote_datasource.dart';

const _kUltimaSync = 'ultima_sync_cartera';

/// HU-05 — Descarga automatica nocturna de la cartera (VERSIÓN SIMPLIFICADA)
class SyncNocturna {
  SyncNocturna._();
  static const _storage = FlutterSecureStorage();

  static Future<void> init() async {
    // No hace nada en web, solo para compatibilidad
    print('🔁 SyncNocturna.init() - Versión simplificada');
  }

  static Future<void> programar() async {
    print('🔁 SyncNocturna.programar() - Versión simplificada');
  }

  static Future<bool> ejecutarSync() async {
    try {
      WidgetsFlutterBinding.ensureInitialized();
      final token = await _storage.read(key: 'auth_token');
      final asesorJson = await _storage.read(key: 'auth_asesor');
      if (token == null || asesorJson == null) return true;
      
      final asesorId =
          (jsonDecode(asesorJson) as Map<String, dynamic>)['id'] as String? ?? '';
      
      final api = ApiClient()..setToken(token);
      final manana = DateTime.now().add(const Duration(days: 1));
      final items = await CarteraRemoteDataSource(api)
          .obtenerCartera(asesorId: asesorId, fecha: manana);

      await CarteraLocalDataSource().guardarCache(asesorId, items);
      await guardarUltimaSync();
      return true;
    } catch (_) {
      return false;
    }
  }

  static Future<void> guardarUltimaSync() async {
    await _storage.write(
        key: _kUltimaSync, value: DateTime.now().toIso8601String());
  }

  static Future<DateTime?> ultimaSync() async {
    final v = await _storage.read(key: _kUltimaSync);
    return v == null ? null : DateTime.tryParse(v);
  }
}

final ultimaSyncProvider =
    FutureProvider.autoDispose<DateTime?>((ref) => SyncNocturna.ultimaSync());