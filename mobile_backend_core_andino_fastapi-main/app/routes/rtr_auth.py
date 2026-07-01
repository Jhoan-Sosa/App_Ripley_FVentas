from fastapi import APIRouter, Depends, HTTPException
from app.schemas.sch_auth import LoginIn, TokenOut
from app.controllers import ctl_auth

router = APIRouter()

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn):
    result = ctl_auth.login(data.codigo_empleado, data.password)
    if result and result.get("_bloqueado"):
        raise HTTPException(
            status_code=423,
            detail=f"Cuenta bloqueada por intentos fallidos hasta {result['hasta']}",
        )
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    return result