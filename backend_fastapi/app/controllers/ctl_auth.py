from datetime import datetime, timedelta, timezone
from app.core.cfg_firebase import db
from app.core.cfg_security import verify_password, create_access_token
from app.repositories import rep_asesores

MAX_INTENTOS = 5
BLOQUEO_MIN = 30

def login(codigo_empleado: str, password: str) -> dict | None:
    asesor = rep_asesores.get_by_codigo(codigo_empleado)
    if not asesor or not asesor.get("activo", True):
        return None

    # Bloqueo por intentos fallidos (RF-04)
    ahora = datetime.now(timezone.utc)
    bloqueado_hasta = asesor.get("bloqueado_hasta")
    if bloqueado_hasta:
        if isinstance(bloqueado_hasta, str):
            bloqueado_hasta = datetime.fromisoformat(bloqueado_hasta.replace("Z", "+00:00"))
        if bloqueado_hasta > ahora:
            return {"_bloqueado": True, "hasta": bloqueado_hasta.isoformat()}

    if not verify_password(password, asesor.get("password_hash", "")):
        intentos = asesor.get("intentos_fallidos", 0) + 1
        if intentos >= MAX_INTENTOS:
            bloqueado_hasta = ahora + timedelta(minutes=BLOQUEO_MIN)
            db.collection("asesores").document(asesor["id"]).update({
                "intentos_fallidos": intentos,
                "bloqueado_hasta": bloqueado_hasta.isoformat()
            })
        else:
            db.collection("asesores").document(asesor["id"]).update({
                "intentos_fallidos": intentos
            })
        return None

    # Login correcto: resetea contador
    db.collection("asesores").document(asesor["id"]).update({
        "intentos_fallidos": 0,
        "bloqueado_hasta": None
    })

    # ✅ USAR EL ID CORRECTO DEL ASESOR (el que está en Firestore)
    asesor_id = asesor["id"]  # Esto es "asesor_0001"
    print(f"🔑 Login exitoso para: {asesor.get('codigo_empleado')} (ID: {asesor_id})")

    token = create_access_token({
        "sub": asesor["codigo_empleado"],
        "asesor_id": asesor_id,  # ✅ ID CORRECTO
        "perfil": asesor.get("perfil", "operador"),
        "nombre": f"{asesor.get('nombres', '')} {asesor.get('apellidos', '')}",
    })
    
    print(f"🔑 Token generado con asesor_id: {asesor_id}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "asesor": {
            "id": asesor_id,
            "codigo_empleado": asesor["codigo_empleado"],
            "nombres": asesor.get("nombres", ""),
            "apellidos": asesor.get("apellidos", ""),
            "perfil": asesor.get("perfil", "operador"),
            "agencia_id": asesor.get("agencia_id"),
        },
    }