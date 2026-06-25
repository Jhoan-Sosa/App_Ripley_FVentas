import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../shared/widgets/gradient_app_bar.dart';

class PendientesScreen extends ConsumerWidget {
  const PendientesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: const GradientAppBar(title: 'Pendientes de aprobación'),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection('solicitudes')
            .where('estado', isEqualTo: 'recibido_comite')
            .orderBy('created_at', descending: true)
            .snapshots(),
        builder: (context, snapshot) {
          // ✅ LOGS PARA DEPURAR
          print('🔍 Pendientes - ConnectionState: ${snapshot.connectionState}');
          print('🔍 Pendientes - hasData: ${snapshot.hasData}');
          print('🔍 Pendientes - hasError: ${snapshot.hasError}');
          
          if (snapshot.hasError) {
            print('❌ Pendientes - Error: ${snapshot.error}');
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Error al cargar solicitudes',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    snapshot.error.toString(),
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
            );
          }

          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
            print('❌ Pendientes - No hay solicitudes');
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                  SizedBox(height: 16),
                  Text(
                    'No hay solicitudes pendientes',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'Todas las solicitudes han sido revisadas',
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
            );
          }

          final docs = snapshot.data!.docs;
          print('✅ Pendientes - ${docs.length} solicitudes encontradas');

          // ✅ Mostrar los expedientes encontrados
          for (var doc in docs) {
            final data = doc.data() as Map<String, dynamic>;
            print('   📄 ${data['numero_expediente']} - ${data['cliente_nombre']}');
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final data = docs[index].data() as Map<String, dynamic>;
              final id = docs[index].id;

              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            data['numero_expediente'] ?? 'Sin expediente',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: AppColors.primary,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.orange.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: Colors.orange),
                            ),
                            child: const Text(
                              'PENDIENTE',
                              style: TextStyle(
                                color: Colors.orange,
                                fontWeight: FontWeight.bold,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Cliente: ${data['cliente_nombre'] ?? 'N/A'}',
                        style: const TextStyle(fontSize: 14),
                      ),
                      Text(
                        'Monto: S/ ${data['monto_solicitado']?.toStringAsFixed(2) ?? '0.00'}',
                        style: const TextStyle(fontSize: 14),
                      ),
                      Text(
                        'Fecha: ${data['created_at']?.toString().substring(0, 10) ?? 'N/A'}',
                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => _aprobarSolicitud(context, id),
                              icon: const Icon(Icons.check_circle),
                              label: const Text('Aprobar'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => _rechazarSolicitud(context, id),
                              icon: const Icon(Icons.cancel),
                              label: const Text('Rechazar'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: Colors.red,
                                side: const BorderSide(color: Colors.red),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }

  void _aprobarSolicitud(BuildContext context, String solicitudId) async {
    print('🔍 Aprobando solicitud: $solicitudId');
    
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Aprobar solicitud'),
        content: const Text('¿Estás seguro que deseas aprobar esta solicitud?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Aprobar'),
          ),
        ],
      ),
    );

    if (confirmar != true) return;

    try {
      print('📝 Actualizando estado a aprobado...');
      
      await FirebaseFirestore.instance
          .collection('solicitudes')
          .doc(solicitudId)
          .update({
        'estado': 'aprobado',
        'decision_at': DateTime.now().toIso8601String(),
        'decision': 'aprobado',
      });

      print('✅ Solicitud aprobada correctamente');

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Solicitud aprobada'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      print('❌ Error al aprobar: $e');
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _rechazarSolicitud(BuildContext context, String solicitudId) async {
    print('🔍 Rechazando solicitud: $solicitudId');
    
    final motivoController = TextEditingController();

    final confirmar = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Rechazar solicitud'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Ingresa el motivo del rechazo:'),
            const SizedBox(height: 8),
            TextField(
              controller: motivoController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: 'Motivo del rechazo...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Rechazar'),
          ),
        ],
      ),
    );

    if (confirmar != true) return;

    try {
      print('📝 Actualizando estado a rechazado...');
      
      await FirebaseFirestore.instance
          .collection('solicitudes')
          .doc(solicitudId)
          .update({
        'estado': 'rechazado',
        'decision_at': DateTime.now().toIso8601String(),
        'decision': 'rechazado',
        'motivo_rechazo': motivoController.text.trim() ?? 'Sin motivo especificado',
      });

      print('✅ Solicitud rechazada correctamente');

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('❌ Solicitud rechazada'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      print('❌ Error al rechazar: $e');
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}