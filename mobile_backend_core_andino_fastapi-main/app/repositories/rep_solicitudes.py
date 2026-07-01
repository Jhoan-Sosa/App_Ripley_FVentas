import json
import uuid
from datetime import datetime, timezone
from app.core.cfg_firebase import db as firestore_db


def _upsert_cliente(d: dict) -> str:
    """Devuelve el cliente_id; lo crea si no existe (por numero_documento)."""
    try:
        docs = firestore_db.collection("clientes").where("numero_documento", "==", d["numero_documento"]).limit(1).get()
        for doc in docs:
            return doc.id
        
        # Crear nuevo cliente
        cid = str(uuid.uuid4())
        firestore_db.collection("clientes").document(cid).set({
            "numero_documento": d["numero_documento"],
            "nombres": d.get("nombres", ""),
            "apellidos": d.get("apellidos", ""),
            "telefono": d.get("telefono"),
            "tipo_negocio": d.get("tipo_negocio"),
            "nombre_negocio": d.get("nombre_negocio"),
            "ingresos_estimados": d.get("ingresos_estimados"),
            "es_prospecto": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return cid
    except Exception as e:
        print(f"❌ Error en _upsert_cliente: {e}")
        raise


def crear(asesor_id: str, agencia_id: str | None, d: dict) -> dict:
    """Crea una solicitud de credito (M5 / HU-17)."""
    try:
        cliente_id = _upsert_cliente(d)
        sol_id = str(uuid.uuid4())
        expediente = "EXP-" + sol_id.replace("-", "")[:8].upper()
        
        print(f"📝 Creando solicitud para asesor: {asesor_id}")
        
        solicitud_data = {
            "numero_expediente": expediente,
            "asesor_id": asesor_id,  # ✅ USA EL ID QUE RECIBE (debe ser "asesor_0001")
            "cliente_id": cliente_id,
            "agencia_id": agencia_id,
            "canal": "asesor",
            "tipo_negocio": d.get("tipo_negocio"),
            "nombre_negocio": d.get("nombre_negocio"),
            "ingresos_estimados": d.get("ingresos_estimados"),
            "monto_solicitado": d["monto_solicitado"],
            "plazo_meses": d["plazo_meses"],
            "moneda": d.get("moneda", "PEN"),
            "tipo_cuota": d.get("tipo_cuota", "mensual"),
            "garantia": d.get("garantia", "sin_garantia"),
            "destino_credito": d.get("destino_credito"),
            "cuota_estimada": d.get("cuota_estimada"),
            "tea_referencial": d.get("tea_referencial"),
            "firma_cliente_base64": d.get("firma_cliente_base64"),
            "estado": "enviado",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        firestore_db.collection("solicitudes").document(sol_id).set(solicitud_data)
        print(f"✅ Solicitud creada: {expediente} para asesor {asesor_id}")
        return {"id": sol_id, "numero_expediente": expediente, "estado": "enviado"}
    except Exception as e:
        print(f"❌ Error en crear solicitud: {e}")
        raise


def agregar_nota(solicitud_id: str, asesor_id: str, contenido: str) -> dict:
    """Agrega una nota interna a una solicitud (RF-72)."""
    try:
        nid = str(uuid.uuid4())
        firestore_db.collection("solicitudes_notas_internas").document(nid).set({
            "solicitud_id": solicitud_id,
            "asesor_id": asesor_id,
            "contenido": contenido[:500],
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"id": nid}
    except Exception as e:
        print(f"❌ Error en agregar_nota: {e}")
        raise


def listar_notas(solicitud_id: str) -> list[dict]:
    """Notas internas de una solicitud, recientes primero (RF-72)."""
    try:
        docs = firestore_db.collection("solicitudes_notas_internas") \
            .where("solicitud_id", "==", solicitud_id) \
            .order_by("created_at", direction="DESCENDING") \
            .get()
        
        return [
            {
                "contenido": doc.to_dict().get("contenido", ""),
                "created_at": doc.to_dict().get("created_at"),
            }
            for doc in docs
        ]
    except Exception as e:
        print(f"❌ Error en listar_notas: {e}")
        return []


def listar(asesor_id: str) -> list[dict]:
    """Solicitudes del asesor (con logs para depurar)."""
    try:
        print(f"📋 Listando solicitudes para asesor: {asesor_id}")
        
        # Obtener todas las solicitudes
        docs = firestore_db.collection("solicitudes").get()
        print(f"📋 {len(docs)} solicitudes ENCONTRADAS EN TOTAL")
        
        resultados = []
        for doc in docs:
            data = doc.to_dict()
            doc_asesor_id = data.get("asesor_id")
            
            print(f"   📄 {doc.id}: expediente={data.get('numero_expediente')}, asesor={doc_asesor_id}")
            
            # Filtrar por asesor_id
            if doc_asesor_id != asesor_id:
                print(f"   ⏭️ Saltando {doc.id}: asesor no coincide ({doc_asesor_id} != {asesor_id})")
                continue
            
            created_at = data.get("created_at")
            if created_at:
                if hasattr(created_at, 'strftime'):
                    created_at_str = created_at.strftime("%Y-%m-%d")
                elif hasattr(created_at, 'isoformat'):
                    created_at_str = created_at.isoformat()[:10]
                else:
                    created_at_str = str(created_at)[:10]
            else:
                created_at_str = ""
            
            cliente_id = data.get("cliente_id")
            cliente = None
            if cliente_id:
                cliente_doc = firestore_db.collection("clientes").document(cliente_id).get()
                if cliente_doc.exists:
                    cliente = cliente_doc.to_dict()
            
            resultados.append({
                "id": doc.id,
                "numero_expediente": data.get("numero_expediente", ""),
                "cliente_nombre": f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip() if cliente else "",
                "monto_solicitado": float(data.get("monto_solicitado", 0)),
                "monto_aprobado": float(data.get("monto_aprobado", 0)),
                "estado": data.get("estado", "enviado"),
                "created_at": created_at_str,
            })
        
        resultados.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        print(f"✅ {len(resultados)} solicitudes filtradas para asesor {asesor_id}")
        return resultados
    except Exception as e:
        print(f"❌ Error en listar solicitudes: {e}")
        import traceback
        traceback.print_exc()
        return []