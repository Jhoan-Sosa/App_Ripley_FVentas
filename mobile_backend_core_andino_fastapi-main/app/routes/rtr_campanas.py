from datetime import date
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor

router = APIRouter()


class CampanaOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    tipo: Optional[str] = None
    monto_ofertado: float
    fecha_vencimiento: Optional[str] = None
    dias_restantes: int


@router.get("", response_model=list[CampanaOut])
def listar(
    asesor: dict = Depends(get_current_asesor),
):
    """Campanas activas del asesor, mas proximas a vencer primero (HU-16/RF-40)."""
    hoy = date.today().isoformat()
    
    docs = db.collection("campanas") \
        .where("asesor_id", "==", asesor["asesor_id"]) \
        .where("activa", "==", True) \
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
        
        fecha_vencimiento = data.get("fecha_vencimiento")
        dias_restantes = 0
        if fecha_vencimiento:
            fecha_venc = date.fromisoformat(fecha_vencimiento)
            dias_restantes = (fecha_venc - date.today()).days
        
        resultados.append(CampanaOut(
            id=doc.id,
            cliente_id=cliente_id,
            cliente_nombre=f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip() if cliente else "",
            tipo=data.get("tipo"),
            monto_ofertado=float(data.get("monto_ofertado", 0)),
            fecha_vencimiento=fecha_vencimiento,
            dias_restantes=max(0, dias_restantes),
        ))
    
    # Ordenar por fecha de vencimiento (más próximas primero)
    resultados.sort(key=lambda x: (x.fecha_vencimiento is None, x.fecha_vencimiento or ""))
    return resultados