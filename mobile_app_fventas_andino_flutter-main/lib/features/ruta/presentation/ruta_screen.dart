import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:go_router/go_router.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/constants/app_colors.dart';
import '../../../shared/widgets/gradient_app_bar.dart';
import '../../cartera/domain/cartera_model.dart';
import '../../cartera/presentation/cartera_viewmodel.dart';

/// M2 — Planificacion de ruta (HU-08 / RF-19..22).
class RutaScreen extends ConsumerStatefulWidget {
  const RutaScreen({super.key});
  @override
  ConsumerState<RutaScreen> createState() => _RutaScreenState();
}

class _RutaScreenState extends ConsumerState<RutaScreen> {
  GoogleMapController? _map;
  LatLng? _miUbicacion;
  List<CarteraItem> _orden = []; // orden optimizado
  Set<Polyline> _polilineas = {};

  static const _lima = LatLng(-12.0464, -77.0428);

  List<CarteraItem> get _clientes => ref
      .read(carteraViewModelProvider)
      .items
      .where((c) => c.tieneUbicacion && !c.visitado)
      .toList();

  double _hue(String prioridad) {
    switch (prioridad.toLowerCase()) {
      case 'alta':
        return BitmapDescriptor.hueRed;
      case 'media':
        return BitmapDescriptor.hueYellow;
      default:
        return BitmapDescriptor.hueGreen;
    }
  }

  Set<Marker> _marcadores() {
    final items = ref.watch(carteraViewModelProvider).items;
    return {
      for (final c in items.where((e) => e.tieneUbicacion))
        Marker(
          markerId: MarkerId(c.id),
          position: LatLng(c.lat!, c.lng!),
          icon: BitmapDescriptor.defaultMarkerWithHue(
              c.visitado ? BitmapDescriptor.hueAzure : _hue(c.prioridad)),
          infoWindow: InfoWindow(
            title: c.clienteNombre,
            snippet: c.tipoGestion.replaceAll('_', ' '),
            onTap: () => context.push('/ficha/${c.clienteId}', extra: c.id),
          ),
        ),
    };
  }

  Future<void> _miPosicion() async {
    try {
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        perm = await Geolocator.requestPermission();
      }
      if (perm == LocationPermission.denied ||
          perm == LocationPermission.deniedForever) {
        return;
      }
      final p = await Geolocator.getCurrentPosition();
      setState(() => _miUbicacion = LatLng(p.latitude, p.longitude));
      _map?.animateCamera(CameraUpdate.newLatLng(_miUbicacion!));
    } catch (_) {/* sin ubicacion */}
  }

  /// Algoritmo del vecino mas cercano (RF-21).
  void _optimizar() {
    final pend = _clientes;
    if (pend.isEmpty) return;
    final inicio = _miUbicacion ?? _lima;
    final restantes = [...pend];
    final orden = <CarteraItem>[];
    var actual = inicio;
    while (restantes.isNotEmpty) {
      restantes.sort((a, b) =>
          _dist(actual, LatLng(a.lat!, a.lng!))
              .compareTo(_dist(actual, LatLng(b.lat!, b.lng!))));
      final sig = restantes.removeAt(0);
      orden.add(sig);
      actual = LatLng(sig.lat!, sig.lng!);
    }
    setState(() {
      _orden = orden;
      _polilineas = {
        Polyline(
          polylineId: const PolylineId('ruta'),
          color: AppColors.primary,
          width: 4,
          points: [
            inicio,
            ...orden.map((c) => LatLng(c.lat!, c.lng!)),
          ],
        ),
      };
    });
  }

  double _dist(LatLng a, LatLng b) {
    final dx = a.latitude - b.latitude;
    final dy = a.longitude - b.longitude;
    return math.sqrt(dx * dx + dy * dy); // euclidiana (suficiente para ordenar)
  }

  /// Lanza Waze; si no esta, Google Maps; si no, navegador (RF-22).
  Future<void> _navegar() async {
    final destino =
        _orden.isNotEmpty ? _orden.first : (_clientes.isNotEmpty ? _clientes.first : null);
    if (destino == null) return;
    final lat = destino.lat!, lng = destino.lng!;
    final waze = Uri.parse('waze://?ll=$lat,$lng&navigate=yes');
    final gmaps = Uri.parse('google.navigation:q=$lat,$lng');
    final web = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$lat,$lng');
    if (await canLaunchUrl(waze)) {
      await launchUrl(waze);
    } else if (await canLaunchUrl(gmaps)) {
      await launchUrl(gmaps);
    } else {
      await launchUrl(web, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final items = ref.watch(carteraViewModelProvider).items;
    final conUbic = items.where((e) => e.tieneUbicacion).length;

    return Scaffold(
      appBar: GradientAppBar(
        title: 'Planificacion de ruta',
        actions: [
          IconButton(
            icon: const Icon(Icons.my_location),
            tooltip: 'Mi ubicacion',
            onPressed: _miPosicion,
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                GoogleMap(
                  initialCameraPosition:
                      const CameraPosition(target: _lima, zoom: 13),
                  markers: _marcadores(),
                  polylines: _polilineas,
                  myLocationEnabled: _miUbicacion != null,
                  myLocationButtonEnabled: false,
                  onMapCreated: (c) => _map = c,
                ),
                if (conUbic == 0)
                  const Center(
                    child: Card(
                      child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Text(
                            'Sin clientes con ubicacion.\nCarga la cartera con conexion.',
                            textAlign: TextAlign.center),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          if (_orden.isNotEmpty)
            Container(
              color: AppColors.surface,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              width: double.infinity,
              child: Text(
                  'Ruta optimizada: ${_orden.length} visitas · primero ${_orden.first.clienteNombre}',
                  style: const TextStyle(fontSize: 12)),
            ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.all(10),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: conUbic == 0 ? null : _optimizar,
                      icon: const Icon(Icons.route),
                      label: const Text('Optimizar ruta'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: conUbic == 0 ? null : _navegar,
                      icon: const Icon(Icons.navigation),
                      label: const Text('Navegar'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
