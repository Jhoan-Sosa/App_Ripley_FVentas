import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

import 'app/app.dart';
import 'core/notificaciones/notificacion_service.dart';
import 'core/sync/sync_nocturna.dart';
import 'features/auth/presentation/login_viewmodel.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ✅ INICIALIZAR FIREBASE CON TUS CREDENCIALES
  try {
    await Firebase.initializeApp(
      options: const FirebaseOptions(
        apiKey: "AIzaSyAzpxGE_o54GlOSFz0pEjKtKLSOctEp6nE",
        authDomain: "banco-ripley-mobile.firebaseapp.com",
        projectId: "banco-ripley-mobile",
        storageBucket: "banco-ripley-mobile.firebasestorage.app",
        messagingSenderId: "627842186109",
        appId: "1:627842186109:web:64fab0156a1e345b7fea14",
      ),
    );
    print('✅ Firebase inicializado correctamente');
    
    // Habilitar la persistencia offline de Firestore
    await FirebaseFirestore.instance.enablePersistence();
    print('✅ Persistencia de Firestore habilitada');
  } catch (e) {
    print('❌ Error al inicializar Firebase: $e');
  }

  // ✅ INICIALIZAR DATOS DE LOCALIZACIÓN PARA ESPAÑOL
  await initializeDateFormatting('es', null);

  try {
    await NotificacionService.init();
  } catch (_) {/* notificaciones opcionales */}

  try {
    await SyncNocturna.init();
  } catch (_) {/* background opcional */}

  final container = ProviderContainer();
  await container.read(loginViewModelProvider.notifier).restaurarSesion();

  runApp(
    UncontrolledProviderScope(
      container: container,
      child: const App(),
    ),
  );
}