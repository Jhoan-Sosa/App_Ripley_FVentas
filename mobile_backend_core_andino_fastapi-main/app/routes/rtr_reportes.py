from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor
from datetime import datetime
import traceback

router = APIRouter()


class ProductividadAsesor(BaseModel):
    asesor_nombre: str
    enviadas: int
    aprobadas: int
    desembolsadas: int
    monto_total: float
    tasa_aprobacion: float


@router.get("/productividad", response_model=list[ProductividadAsesor])
def productividad(
    asesor: dict = Depends(get_current_asesor),
):
    """Reporte de productividad mensual por asesor (M11 / RF-80)."""
    try:
        print("=" * 50)
        print("🔍 INICIANDO REPORTE DE PRODUCTIVIDAD")
        
        # Paso 1: Obtener todos los asesores
        asesores_docs = db.collection("asesores").get()
        asesores_map = {}
        for doc in asesores_docs:
            data = doc.to_dict()
            nombre = f"{data.get('nombres', '')} {data.get('apellidos', '')}".strip()
            asesores_map[doc.id] = nombre if nombre else doc.id
        
        # Paso 2: Obtener el mes actual
        mes_actual = datetime.now().strftime("%Y-%m")
        print(f"📅 Mes actual: {mes_actual}")
        
        # Paso 3: Obtener todas las solicitudes
        solicitudes_docs = db.collection("solicitudes").get()
        print(f"📋 {len(solicitudes_docs)} solicitudes encontradas")
        
        # Paso 4: Procesar solicitudes
        resultados = {}
        
        for doc in solicitudes_docs:
            data = doc.to_dict()
            created_at = data.get("created_at")
            
            # ✅ CONVERTIR A STRING si es un objeto DatetimeWithNanoseconds
            if created_at:
                if hasattr(created_at, 'strftime'):
                    # Es un objeto datetime
                    created_at_str = created_at.strftime("%Y-%m-%d")
                elif hasattr(created_at, 'isoformat'):
                    # Es un objeto datetime con método isoformat
                    created_at_str = created_at.isoformat()[:10]
                else:
                    # Ya es string o tiene otro formato
                    created_at_str = str(created_at)[:10]
            else:
                continue
            
            print(f"📄 Solicitud: {doc.id} - fecha: {created_at_str}")
            
            # Verificar que la fecha es del mes actual
            if not created_at_str.startswith(mes_actual):
                print(f"   ⏭️ No es del mes actual ({created_at_str[:7]} != {mes_actual})")
                continue
            
            asesor_id = data.get("asesor_id")
            if not asesor_id:
                print(f"   ⚠️ Sin asesor_id, saltando")
                continue
            
            if asesor_id not in resultados:
                resultados[asesor_id] = {
                    "enviadas": 0,
                    "aprobadas": 0,
                    "desembolsadas": 0,
                    "monto_total": 0.0,
                }
            
            resultados[asesor_id]["enviadas"] += 1
            estado = data.get("estado", "")
            if estado in ["aprobado", "desembolsado"]:
                resultados[asesor_id]["aprobadas"] += 1
            if estado == "desembolsado":
                resultados[asesor_id]["desembolsadas"] += 1
            resultados[asesor_id]["monto_total"] += float(data.get("monto_solicitado", 0))
        
        # Paso 5: Construir respuesta
        response = []
        for asesor_id, data in resultados.items():
            nombre = asesores_map.get(asesor_id, "Desconocido")
            enviadas = data["enviadas"]
            aprobadas = data["aprobadas"]
            tasa = round((aprobadas / enviadas * 100) if enviadas > 0 else 0, 1)
            
            response.append(ProductividadAsesor(
                asesor_nombre=nombre,
                enviadas=enviadas,
                aprobadas=aprobadas,
                desembolsadas=data["desembolsadas"],
                monto_total=round(data["monto_total"], 2),
                tasa_aprobacion=tasa,
            ))
        
        print(f"✅ Reporte generado con {len(response)} asesores")
        print("=" * 50)
        return response
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        print("=" * 50)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
def test_productividad(
    asesor: dict = Depends(get_current_asesor),
):
    """Endpoint de prueba para verificar que el router funciona."""
    return {
        "status": "ok",
        "message": "Reportes router funciona correctamente",
        "asesor": asesor.get("nombre", "Desconocido")
    }