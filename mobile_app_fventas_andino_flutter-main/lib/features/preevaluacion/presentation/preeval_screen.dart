import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/app_colors.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/gradient_app_bar.dart';
import '../data/preeval_repository.dart';
import 'preeval_viewmodel.dart';

/// M4 — Pre-evaluacion de prospecto en campo (HU-15).
class PreEvalScreen extends ConsumerStatefulWidget {
  const PreEvalScreen({super.key});
  @override
  ConsumerState<PreEvalScreen> createState() => _PreEvalScreenState();
}

class _PreEvalScreenState extends ConsumerState<PreEvalScreen> {
  final _doc = TextEditingController();
  final _nombres = TextEditingController();
  final _apellidos = TextEditingController();
  final _ingresos = TextEditingController();
  final _destino = TextEditingController();
  String _tipoNegocio = 'Comercio';
  double _monto = 5000;
  DateTime? _fechaNac;
  int _antiguedadAnios = 1;
  int _antiguedadMeses = 0;

  @override
  void dispose() {
    _doc.dispose();
    _nombres.dispose();
    _apellidos.dispose();
    _ingresos.dispose();
    _destino.dispose();
    super.dispose();
  }

  int get _antiguedadTotalMeses => _antiguedadAnios * 12 + _antiguedadMeses;

  int? get _edad {
    if (_fechaNac == null) return null;
    final hoy = DateTime.now();
    var edad = hoy.year - _fechaNac!.year;
    if (hoy.month < _fechaNac!.month ||
        (hoy.month == _fechaNac!.month && hoy.day < _fechaNac!.day)) {
      edad--;
    }
    return edad;
  }

  Future<void> _elegirFechaNac() async {
    final hoy = DateTime.now();
    final f = await showDatePicker(
      context: context,
      initialDate: DateTime(hoy.year - 30, hoy.month, hoy.day),
      firstDate: DateTime(hoy.year - 75),
      lastDate: DateTime(hoy.year - 18, hoy.month, hoy.day),
      helpText: 'Fecha de nacimiento',
    );
    if (f != null) setState(() => _fechaNac = f);
  }

  void _evaluar() {
    // Validaciones RF-37: documento 8 digitos, edad 18-75, antiguedad >= 6 meses.
    if (_doc.text.trim().length != 8) {
      _aviso('El documento debe tener 8 digitos.');
      return;
    }
    final edad = _edad;
    if (edad == null || edad < 18 || edad > 75) {
      _aviso('La edad del prospecto debe estar entre 18 y 75 anos.');
      return;
    }
    if (_antiguedadTotalMeses < 6) {
      _aviso('El negocio debe tener una antiguedad minima de 6 meses.');
      return;
    }
    ref.read(preEvalViewModelProvider.notifier).evaluar(
          documento: _doc.text.trim(),
          nombres: _nombres.text.trim(),
          apellidos: _apellidos.text.trim(),
          fechaNacimiento: _fechaNac?.toIso8601String().substring(0, 10),
          tipoNegocio: _tipoNegocio,
          antiguedadNegocioMeses: _antiguedadTotalMeses,
          ingresos: double.tryParse(_ingresos.text) ?? 0,
          montoSolicitado: _monto,
          destino: _destino.text.trim(),
        );
  }

  void _aviso(String m) => ScaffoldMessenger.of(context)
      .showSnackBar(SnackBar(content: Text(m)));

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(preEvalViewModelProvider);
    return Scaffold(
      appBar: const GradientAppBar(title: 'Pre-evaluacion'),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _doc,
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: const InputDecoration(labelText: 'Documento (DNI)'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _nombres,
            decoration: const InputDecoration(labelText: 'Nombres'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _apellidos,
            decoration: const InputDecoration(labelText: 'Apellidos'),
          ),
          const SizedBox(height: 12),
          // Fecha de nacimiento (edad 18-75, RF-37)
          OutlinedButton.icon(
            icon: const Icon(Icons.cake_outlined, size: 18),
            label: Text(_fechaNac == null
                ? 'Fecha de nacimiento'
                : 'Nacimiento: ${Formatters.fecha(_fechaNac!)} '
                    '($_edad anos)'),
            onPressed: _elegirFechaNac,
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _tipoNegocio,
            decoration: const InputDecoration(labelText: 'Tipo de negocio'),
            items: const [
              DropdownMenuItem(value: 'Comercio', child: Text('Comercio')),
              DropdownMenuItem(value: 'Servicios', child: Text('Servicios')),
              DropdownMenuItem(value: 'Produccion', child: Text('Produccion')),
              DropdownMenuItem(
                  value: 'Agropecuario', child: Text('Agropecuario')),
            ],
            onChanged: (v) => setState(() => _tipoNegocio = v ?? 'Comercio'),
          ),
          const SizedBox(height: 12),
          // Antiguedad del negocio: anos + meses (minimo 6 meses, RF-37)
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _antiguedadAnios,
                  decoration: const InputDecoration(labelText: 'Antiguedad (anos)'),
                  items: List.generate(31, (i) => i)
                      .map((a) => DropdownMenuItem(value: a, child: Text('$a')))
                      .toList(),
                  onChanged: (v) => setState(() => _antiguedadAnios = v ?? 0),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _antiguedadMeses,
                  decoration: const InputDecoration(labelText: 'Meses'),
                  items: List.generate(12, (i) => i)
                      .map((m) => DropdownMenuItem(value: m, child: Text('$m')))
                      .toList(),
                  onChanged: (v) => setState(() => _antiguedadMeses = v ?? 0),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _ingresos,
            keyboardType: TextInputType.number,
            decoration:
                const InputDecoration(labelText: 'Ingresos mensuales (S/)'),
          ),
          const SizedBox(height: 16),
          Text('Monto solicitado: ${Formatters.soles(_monto)}',
              style: const TextStyle(fontWeight: FontWeight.w600)),
          Slider(
            value: _monto,
            min: 500,
            max: 50000,
            divisions: 99,
            label: Formatters.soles(_monto),
            activeColor: AppColors.primary,
            onChanged: (v) => setState(() => _monto = v),
          ),
          TextField(
            controller: _destino,
            decoration: const InputDecoration(labelText: 'Destino del credito'),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: state.cargando ? null : _evaluar,
            icon: state.cargando
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.fact_check),
            label: const Text('Pre-evaluar'),
          ),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(state.error!,
                  style: const TextStyle(color: AppColors.danger)),
            ),
          if (state.resultado != null) ...[
            const SizedBox(height: 16),
            _ResultadoCard(r: state.resultado!),
          ],
        ],
      ),
    );
  }
}

class _ResultadoCard extends StatelessWidget {
  final ResultadoPreEval r;
  const _ResultadoCard({required this.r});

  (Color, String, String) get _data => switch (r.calificacion) {
        'APTO' => (
            AppColors.success,
            'APTO',
            'Puede continuar la evaluacion'
          ),
        'NO_PROCEDE' => (
            AppColors.danger,
            'NO PROCEDE',
            'No cumple condiciones'
          ),
        _ => (AppColors.warning, 'REVISAR', 'Requiere analisis adicional'),
      };

  @override
  Widget build(BuildContext context) {
    final (color, titulo, sub) = _data;
    return Card(
      color: color.withValues(alpha: 0.10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: color),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.circle, color: color, size: 16),
                const SizedBox(width: 8),
                Text(titulo,
                    style: TextStyle(
                        color: color,
                        fontSize: 18,
                        fontWeight: FontWeight.bold)),
                const Spacer(),
                Text('Puntaje ${r.puntaje}',
                    style: const TextStyle(color: AppColors.textSecondary)),
              ],
            ),
            const SizedBox(height: 6),
            Text(sub, style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            Text(r.motivo,
                style: const TextStyle(color: AppColors.textSecondary)),
            if (r.calificacion == 'APTO') ...[
              const SizedBox(height: 10),
              FilledButton(
                onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Continua en el modulo Solicitud (M5).')),
                ),
                child: const Text('Iniciar solicitud formal'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
