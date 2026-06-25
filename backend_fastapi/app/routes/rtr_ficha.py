from fastapi import APIRouter, Depends, HTTPException
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor
from app.schemas.sch_ficha import FichaOut, UbicacionIn
from datetime import datetime

router = APIRouter()


@router.get("/{cliente_id}/ficha", response_model=FichaOut)
def ficha_cliente(
    cliente_id: str,
    asesor: dict = Depends(get_current_asesor),
):
    """Ficha completa del cliente (M3 / HU-11)."""
    # Obtener cliente
    doc = db.collection("clientes").document(cliente_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_data = doc.to_dict()
    cliente_data["id"] = doc.id
    
    # Obtener créditos del cliente
    creditos = []
    docs = db.collection("creditos").where("cliente_id", "==", cliente_id).get()
    for cred in docs:
        cred_data = cred.to_dict()
        cred_data["id"] = cred.id
        creditos.append(cred_data)
    
    # Obtener oferta preaprobada (si existe)
    oferta = None
    ofertas = db.collection("creditos_preaprobados") \
        .where("cliente_id", "==", cliente_id) \
        .where("vigente", "==", True) \
        .limit(1) \
        .get()
    for of in ofertas:
        oferta = of.to_dict()
        break
    
    # Calcular posición del cliente
    deuda_total = sum(c.get("saldo_total", 0) for c in creditos)
    cuentas_vigentes = sum(1 for c in creditos if c.get("estado") == "vigente")
    cuentas_mora = sum(1 for c in creditos if c.get("dias_mora", 0) > 0)
    dias_mayor_mora = max([c.get("dias_mora", 0) for c in creditos], default=0)
    
    # Historial (últimos 5 créditos)
    historial = [
        {
            "producto": c.get("producto"),
            "monto_desembolsado": float(c.get("monto_desembolsado", 0)),
            "plazo_meses": c.get("cuotas_total"),
            "tea": float(c.get("tea", 0)),
            "estado": c.get("estado"),
            "dias_mora": c.get("dias_mora", 0),
            "cuotas_total": c.get("cuotas_total", 0),
            "cuotas_pagadas": c.get("cuotas_pagadas", 0),
        }
        for c in creditos[:5]
    ]
    
    # Comportamiento simulado (12 meses)
    comportamiento = [1] * 12
    if dias_mayor_mora > 0:
        for i in range(min(dias_mayor_mora // 30, 12)):
            comportamiento[11 - i] = 2
    
    return {
        "cliente": {
            "id": cliente_data["id"],
            "numero_documento": cliente_data.get("numero_documento", ""),
            "nombres": cliente_data.get("nombres", ""),
            "apellidos": cliente_data.get("apellidos", ""),
            "telefono": cliente_data.get("telefono"),
            "direccion": cliente_data.get("direccion"),
            "tipo_negocio": cliente_data.get("tipo_negocio"),
            "nombre_negocio": cliente_data.get("nombre_negocio"),
            "antiguedad_negocio_meses": cliente_data.get("antiguedad_negocio_meses"),
            "calificacion_sbs": cliente_data.get("calificacion_sbs", "NORMAL"),
        },
        "posicion": {
            "deuda_total": float(deuda_total),
            "cuentas_vigentes": cuentas_vigentes,
            "cuentas_mora": cuentas_mora,
            "dias_mayor_mora": dias_mayor_mora,
        },
        "historial": historial,
        "oferta": {
            "monto_maximo": float(oferta.get("monto_maximo", 0)),
            "plazo_sugerido_meses": oferta.get("plazo_sugerido_meses"),
            "tea_referencial": float(oferta.get("tea_referencial", 0)),
            "score_confianza": oferta.get("score_confianza", 0),
            "fecha_vencimiento": oferta.get("fecha_vencimiento"),
        } if oferta else None,
        "comportamiento": comportamiento,
        "indicadores": {
            "pct_puntual": 85.0,
            "dias_prom_mora": dias_mayor_mora,
            "monto_pagado": float(sum(c.get("monto_desembolsado", 0) for c in creditos if c.get("estado") == "pagado")),
        },
    }


@router.post("/{cliente_id}/ubicacion")
def actualizar_ubicacion(
    cliente_id: str,
    body: UbicacionIn,
    asesor: dict = Depends(get_current_asesor),
):
    """Actualiza las coordenadas del negocio del cliente (HU-10 / RF-25/26)."""
    doc_ref = db.collection("clientes").document(cliente_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    doc_ref.update({
        "lat": body.lat,
        "lng": body.lng,
        "direccion": body.direccion,
        "updated_at": datetime.now().isoformat()
    })
    return {"ok": True, "lat": body.lat, "lng": body.lng}