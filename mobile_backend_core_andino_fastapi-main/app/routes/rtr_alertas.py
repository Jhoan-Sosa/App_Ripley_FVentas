from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor

router = APIRouter()


class AlertaOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    tipo_alerta: str
    mensaje: Optional[str] = None
    leida: bool


@router.get("", response_model=list[AlertaOut])
def listar(
    asesor: dict = Depends(get_current_asesor),
):
    """Alertas de cartera del asesor, no leidas primero (HU-14)."""
    docs = db.collection("alertas") \
        .where("asesor_id", "==", asesor["asesor_id"]) \
        .order_by("leida") \
        .order_by("created_at", direction="DESCENDING") \
        .get()
    
    resultados = []
    for doc in docs:
        data = doc.to_dict()
        cliente_id = data.get("cliente_id")
        cliente = None
        if cliente_id:
            cliente_doc = db.collection("clientes").document(cliente_id).get()
            if cliente_doc.exists:
                cliente = cliente_doc.to_dict()
        
        resultados.append(AlertaOut(
            id=doc.id,
            cliente_id=cliente_id,
            cliente_nombre=f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip() if cliente else "",
            tipo_alerta=data.get("tipo_alerta", ""),
            mensaje=data.get("mensaje"),
            leida=data.get("leida", False),
        ))
    
    return resultados


@router.get("/no-leidas")
def no_leidas(
    asesor: dict = Depends(get_current_asesor),
):
    """Conteo de alertas no leidas (insignia, RF-36)."""
    docs = db.collection("alertas") \
        .where("asesor_id", "==", asesor["asesor_id"]) \
        .where("leida", "==", False) \
        .get()
    
    return {"no_leidas": len(docs)}


@router.post("/{alerta_id}/leer")
def marcar_leida(
    alerta_id: str,
    asesor: dict = Depends(get_current_asesor),
):
    doc_ref = db.collection("alertas").document(alerta_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"status": "error", "message": "Alerta no encontrada"}
    
    doc_ref.update({"leida": True})
    return {"status": "ok"}