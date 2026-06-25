from fastapi import APIRouter, Depends, HTTPException
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor
from app.schemas.sch_cobranza import MoraItemOut, AccionCobranzaIn
from datetime import datetime, timezone

router = APIRouter()


@router.get("/mora", response_model=list[MoraItemOut])
def listar_mora(
    asesor: dict = Depends(get_current_asesor),
):
    """Listado de mora diaria (M10 / HU-30)."""
    # Buscar créditos con mora
    docs = db.collection("creditos").where("dias_mora", ">", 0).get()
    
    resultados = []
    for doc in docs:
        data = doc.to_dict()
        cliente_id = data.get("cliente_id")
        cliente = None
        if cliente_id:
            cliente_doc = db.collection("clientes").document(cliente_id).get()
            if cliente_doc.exists:
                cliente = cliente_doc.to_dict()
        
        if cliente:
            resultados.append({
                "id": doc.id,
                "cod_cuenta_credito": data.get("cod_cuenta_credito", ""),
                "cliente_id": cliente_id,
                "cliente_nombre": f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip(),
                "documento": cliente.get("numero_documento", ""),
                "telefono": cliente.get("telefono"),
                "dias_mora": data.get("dias_mora", 0),
                "monto_vencido": float(data.get("saldo_total", 0)),
            })
    
    # Ordenar por días de mora descendente
    resultados.sort(key=lambda x: x["dias_mora"], reverse=True)
    return resultados


@router.post("/accion")
def registrar_accion(
    data: AccionCobranzaIn,
    asesor: dict = Depends(get_current_asesor),
):
    """Registra una gestion de cobranza (M10 / HU-31)."""
    # Crear documento en acciones_cobranza
    db.collection("acciones_cobranza").add({
        "asesor_id": asesor["asesor_id"],
        "cliente_id": data.cliente_id,
        "cod_cuenta_credito": data.cod_cuenta_credito,
        "tipo_gestion": data.tipo_gestion,
        "resultado": data.resultado,
        "monto_pagado": data.monto_pagado,
        "fecha_compromiso": data.fecha_compromiso,
        "monto_compromiso": data.monto_compromiso,
        "observaciones": data.observaciones,
        "lat": data.lat,
        "lng": data.lng,
        "timestamp_gestion": datetime.now(timezone.utc).isoformat(),
        "pendiente_sync": False,
    })
    return {"status": "ok"}