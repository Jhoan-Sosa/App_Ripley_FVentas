from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.cfg_auth import get_current_asesor
from app.schemas.sch_solicitudes import (
    SolicitudIn, SolicitudCreada, SolicitudResumen,
)
from app.repositories import rep_solicitudes

router = APIRouter()


class NotaIn(BaseModel):
    contenido: str


class NotaOut(BaseModel):
    contenido: str
    created_at: str | None = None


@router.post("", response_model=SolicitudCreada)
def crear_solicitud(
    data: SolicitudIn,
    asesor: dict = Depends(get_current_asesor),
):
    """Registra una solicitud de credito (M5 / HU-17)."""
    try:
        print(f"📝 Creando solicitud para asesor: {asesor.get('asesor_id')}")
        print(f"📝 Datos: {data.model_dump()}")
        
        return rep_solicitudes.crear(
            asesor["asesor_id"], asesor.get("agencia_id"), data.model_dump()
        )
    except Exception as e:
        print(f"❌ Error en crear_solicitud: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[SolicitudResumen])
def listar_solicitudes(
    asesor: dict = Depends(get_current_asesor),
):
    """Historial de solicitudes del mes (HU-20) y tablero de estado (M9)."""
    try:
        return rep_solicitudes.listar(asesor["asesor_id"])
    except Exception as e:
        print(f"❌ Error en listar_solicitudes: {e}")
        return []


@router.post("/{solicitud_id}/notas")
def agregar_nota(
    solicitud_id: str,
    data: NotaIn,
    asesor: dict = Depends(get_current_asesor),
):
    """Agrega una nota interna a la solicitud (RF-72)."""
    try:
        return rep_solicitudes.agregar_nota(
            solicitud_id, asesor["asesor_id"], data.contenido
        )
    except Exception as e:
        print(f"❌ Error en agregar_nota: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{solicitud_id}/notas", response_model=list[NotaOut])
def listar_notas(
    solicitud_id: str,
    asesor: dict = Depends(get_current_asesor),
):
    """Notas internas de la solicitud (RF-72)."""
    try:
        return rep_solicitudes.listar_notas(solicitud_id)
    except Exception as e:
        print(f"❌ Error en listar_notas: {e}")
        return []