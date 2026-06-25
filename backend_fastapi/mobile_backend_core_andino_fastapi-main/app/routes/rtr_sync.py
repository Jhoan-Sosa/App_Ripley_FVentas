from fastapi import APIRouter, Depends
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_asesor

router = APIRouter()


@router.post("/promover")
def promover(
    asesor: dict = Depends(get_current_asesor),
):
    """Promueve las solicitudes pendientes al nucleo bancario."""
    # En Firestore, la promoción es automática
    # Este endpoint se mantiene por compatibilidad
    return {"aplicados": 0, "errores": 0, "total": 0}


@router.get("/outbox")
def outbox(
    asesor: dict = Depends(get_current_asesor),
):
    """Estado de la cola de sincronizacion al core."""
    # En Firestore no hay cola de sincronización
    return []