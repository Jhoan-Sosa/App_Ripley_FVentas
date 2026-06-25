from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor
from app.schemas.sch_cartera import CarteraItemOut, MarcarVisitaIn

router = APIRouter()

@router.get("", response_model=list[CarteraItemOut])
def listar_cartera(
    fecha: date | None = None,
    asesor: dict = Depends(get_current_asesor),
):
    """Cartera del dia del asesor autenticado (RF-04/RF-09)."""
    try:
        from app.repositories import rep_cartera
        f = fecha or date.today()
        return rep_cartera.listar_por_asesor(asesor["asesor_id"], f)
    except Exception as e:
        print(f"❌ Error en listar_cartera: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{cartera_id}/visita")
def marcar_visita(
    cartera_id: str,
    data: MarcarVisitaIn,
    asesor: dict = Depends(get_current_asesor),
):
    """Registra el resultado de una visita (RF-07/RF-17)."""
    try:
        from app.repositories import rep_cartera
        ok = rep_cartera.marcar_visita(
            asesor["asesor_id"], 
            cartera_id, 
            data.model_dump()
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Item de cartera no encontrado o no autorizado")
        return {"status": "ok", "cartera_id": cartera_id, "estado_visita": data.resultado}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en marcar_visita: {e}")
        raise HTTPException(status_code=500, detail=str(e))