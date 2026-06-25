from datetime import datetime, timezone, date
from app.core.cfg_firebase import db
import uuid

def listar_por_asesor(asesor_id: str, fecha: date) -> list[dict]:
    """Cartera del asesor para una fecha, ordenada por score (RF-09)."""
    try:
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        print(f"🔍 Buscando cartera para asesor: {asesor_id}, fecha: {fecha_str}")
        
        docs = db.collection("cartera_diaria") \
            .where("asesor_id", "==", asesor_id) \
            .get()
        
        resultados = []
        for doc in docs:
            data = doc.to_dict()
            fecha_asignacion = data.get("fecha_asignacion")
            
            if fecha_asignacion:
                if hasattr(fecha_asignacion, 'strftime'):
                    fecha_doc = fecha_asignacion.strftime("%Y-%m-%d")
                else:
                    fecha_doc = str(fecha_asignacion)[:10]
                
                if fecha_doc != fecha_str:
                    continue
            
            cliente_id = data.get("cliente_id")
            cliente = None
            if cliente_id:
                cliente_doc = db.collection("clientes").document(cliente_id).get()
                if cliente_doc.exists:
                    cliente = cliente_doc.to_dict()
            
            resultados.append({
                "id": doc.id,
                "cliente_id": cliente_id,
                "cliente_nombre": f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip() if cliente else "",
                "documento": cliente.get("numero_documento", "") if cliente else "",
                "tipo_gestion": data.get("tipo_gestion", ""),
                "prioridad": data.get("prioridad", "normal"),
                "score_prioridad": data.get("score_prioridad", 0),
                "monto_credito": float(data.get("monto_credito", 0)),
                "estado_visita": data.get("estado_visita", "pendiente"),
                "orden_manual": data.get("orden_manual"),
                "lat": cliente.get("lat") if cliente else None,
                "lng": cliente.get("lng") if cliente else None,
            })
        
        print(f"✅ Encontrados {len(resultados)} registros")
        return resultados
    except Exception as e:
        print(f"❌ Error en listar_por_asesor: {e}")
        import traceback
        traceback.print_exc()
        return []

def marcar_visita(asesor_id: str, cartera_id: str, data: dict) -> bool:
    """Registra el resultado de una visita en Firestore."""
    try:
        print(f"📝 Registrando visita para cartera: {cartera_id}")
        print(f"   Asesor: {asesor_id}")
        print(f"   Datos: {data}")
        
        doc_ref = db.collection("cartera_diaria").document(cartera_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"❌ Documento no encontrado: {cartera_id}")
            return False
        
        doc_data = doc.to_dict()
        if doc_data.get("asesor_id") != asesor_id:
            print(f"❌ Asesor no autorizado: {doc_data.get('asesor_id')} != {asesor_id}")
            return False
        
        # ✅ ACTUALIZAR CON TODOS LOS CAMPOS
        update_data = {
            "estado_visita": "visitado",
            "resultado_visita": data.get("resultado", "visitado"),
            "observacion_visita": data.get("observacion", ""),
            "timestamp_visita": datetime.now(timezone.utc).isoformat(),
            "lat_visita": data.get("lat"),
            "lng_visita": data.get("lng"),
        }
        
        doc_ref.update(update_data)
        print(f"✅ Visita registrada correctamente para {cartera_id}")
        return True
    except Exception as e:
        print(f"❌ Error en marcar_visita: {e}")
        import traceback
        traceback.print_exc()
        return False

def crear_cartera_desde_solicitud(solicitud_id: str, cliente_id: str, asesor_id: str, monto: float = 0):
    """Crea un item en cartera_diaria para una nueva solicitud de cliente."""
    try:
        cartera_id = str(uuid.uuid4())
        hoy = date.today().isoformat()
        
        cliente_doc = db.collection("clientes").document(cliente_id).get()
        cliente_nombre = "Cliente"
        if cliente_doc.exists:
            data = cliente_doc.to_dict()
            cliente_nombre = f"{data.get('nombres', '')} {data.get('apellidos', '')}".strip()
        
        cartera_data = {
            "asesor_id": asesor_id,
            "cliente_id": cliente_id,
            "agencia_id": "agencia_001",
            "fecha_asignacion": hoy,
            "tipo_gestion": "NUEVA_SOLICITUD",
            "prioridad": "normal",
            "score_prioridad": 30,
            "monto_credito": monto,
            "estado_visita": "pendiente",
            "orden_manual": 0,
            "solicitud_id": solicitud_id,
            "cliente_nombre": cliente_nombre,
        }
        
        db.collection("cartera_diaria").document(cartera_id).set(cartera_data)
        print(f"✅ Cartera creada para solicitud {solicitud_id} - asesor {asesor_id}")
        return cartera_id
    except Exception as e:
        print(f"❌ Error al crear cartera: {e}")
        return None