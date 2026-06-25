from pydantic import BaseModel
from typing import Optional

class CarteraItemOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    documento: str
    tipo_gestion: str
    prioridad: str
    score_prioridad: int
    monto_credito: float
    estado_visita: str  # ✅ DEBE EXISTIR
    orden_manual: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class MarcarVisitaIn(BaseModel):
    resultado: str
    observacion: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None