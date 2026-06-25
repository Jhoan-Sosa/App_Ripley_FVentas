"""
Rutas de la **app de clientes** (appbanco / Flutter clientes).
Login con DNI (usuarios_cliente) y consulta de productos del cliente.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid
from app.core.cfg_firebase import db
from app.core.cfg_auth import get_current_cliente
from app.schemas.sch_cliente import (
    LoginClienteIn, TokenClienteOut, ClienteOut, CuentaAhorroOut, CreditoOut,
    CuotaOut, MovimientoOut, TarjetaOut, NotificacionOut, OperacionIn, OperacionOut,
)
from app.schemas.sch_solicitudes import SolicitudIn, SolicitudCreada
from app.controllers import ctl_auth_cliente
from app.repositories import rep_cartera  # ✅ IMPORTAR CARTERA

router = APIRouter()


@router.post("/login", response_model=TokenClienteOut)
def login(data: LoginClienteIn):
    """Login del cliente (numero_documento + password) -> JWT."""
    result = ctl_auth_cliente.login(data.numero_documento, data.password)
    if result and result.get("_bloqueado"):
        raise HTTPException(status_code=423, detail="Usuario bloqueado por intentos fallidos")
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    return result


@router.get("/perfil", response_model=ClienteOut)
def perfil(cli: dict = Depends(get_current_cliente)):
    doc = db.collection("clientes").document(cli["cliente_id"]).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    data = doc.to_dict()
    return {
        "id": doc.id,
        "cod_cliente": data.get("cod_cliente"),
        "numero_documento": data.get("numero_documento", ""),
        "nombres": data.get("nombres", ""),
        "apellidos": data.get("apellidos", ""),
        "email": data.get("email"),
        "telefono": data.get("telefono"),
    }


@router.get("/cuentas", response_model=list[CuentaAhorroOut])
def cuentas(cli: dict = Depends(get_current_cliente)):
    docs = db.collection("cr_cuentas_ahorro").where("cliente_id", "==", cli["cliente_id"]).get()
    return [
        {
            "id": doc.id,
            "cod_cuenta_ahorro": data.get("cod_cuenta_ahorro", ""),
            "tipo_cuenta": data.get("tipo_cuenta"),
            "moneda": data.get("moneda", "PEN"),
            "saldo_capital": float(data.get("saldo_capital", 0)),
            "saldo_interes": float(data.get("saldo_interes", 0)),
            "tea": float(data.get("tea", 0)),
            "estado": data.get("estado"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.get("/creditos", response_model=list[CreditoOut])
def creditos(cli: dict = Depends(get_current_cliente)):
    docs = db.collection("creditos").where("cliente_id", "==", cli["cliente_id"]).get()
    return [
        {
            "id": doc.id,
            "cod_cuenta_credito": data.get("cod_cuenta_credito", ""),
            "producto": data.get("producto"),
            "monto_desembolsado": float(data.get("monto_desembolsado", 0)),
            "saldo_capital": float(data.get("saldo_capital", 0)),
            "saldo_total": float(data.get("saldo_total", 0)),
            "dias_mora": data.get("dias_mora", 0),
            "calificacion_interna": data.get("calificacion_interna"),
            "estado": data.get("estado"),
            "fecha_desembolso": data.get("fecha_desembolso"),
            "tea": float(data.get("tea", 0)),
            "cuotas_total": data.get("cuotas_total"),
            "cuotas_pagadas": data.get("cuotas_pagadas"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.get("/creditos/{cod_cuenta_credito}/cronograma", response_model=list[CuotaOut])
def cronograma(
    cod_cuenta_credito: str,
    cli: dict = Depends(get_current_cliente),
):
    docs = db.collection("cr_cronograma_pagos") \
        .where("cod_cuenta_credito", "==", cod_cuenta_credito) \
        .order_by("nro_cuota") \
        .get()
    return [
        {
            "id": doc.id,
            "cod_cuenta_credito": data.get("cod_cuenta_credito", ""),
            "nro_cuota": data.get("nro_cuota", 0),
            "fecha_vencimiento": data.get("fecha_vencimiento"),
            "monto_cuota": float(data.get("monto_cuota", 0)),
            "monto_capital": float(data.get("monto_capital", 0)),
            "monto_interes": float(data.get("monto_interes", 0)),
            "saldo": float(data.get("saldo", 0)),
            "estado_cuota": data.get("estado_cuota"),
            "fecha_pago": data.get("fecha_pago"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.get("/movimientos", response_model=list[MovimientoOut])
def movimientos(
    limit: int = 20,
    cli: dict = Depends(get_current_cliente),
):
    docs = db.collection("cr_movimientos") \
        .where("cliente_id", "==", cli["cliente_id"]) \
        .order_by("fecha_operacion", direction="DESCENDING") \
        .limit(limit) \
        .get()
    return [
        {
            "id": doc.id,
            "cod_operacion": data.get("cod_operacion", ""),
            "cod_cuenta": data.get("cod_cuenta"),
            "tipo": data.get("tipo"),
            "concepto": data.get("concepto"),
            "canal": data.get("canal"),
            "monto": float(data.get("monto", 0)),
            "moneda": data.get("moneda", "PEN"),
            "fecha_operacion": data.get("fecha_operacion"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.get("/tarjetas", response_model=list[TarjetaOut])
def tarjetas(cli: dict = Depends(get_current_cliente)):
    docs = db.collection("tarjetas").where("cliente_id", "==", cli["cliente_id"]).get()
    return [
        {
            "id": doc.id,
            "numero_enmascarado": data.get("numero_enmascarado", ""),
            "marca": data.get("marca"),
            "linea_credito": float(data.get("linea_credito", 0)),
            "saldo_utilizado": float(data.get("saldo_utilizado", 0)),
            "fecha_corte": data.get("fecha_corte"),
            "fecha_pago": data.get("fecha_pago"),
            "estado": data.get("estado", "activa"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.get("/notificaciones", response_model=list[NotificacionOut])
def notificaciones(cli: dict = Depends(get_current_cliente)):
    docs = db.collection("notificaciones") \
        .where("destinatario_tipo", "==", "cliente") \
        .where("cliente_id", "==", cli["cliente_id"]) \
        .order_by("created_at", direction="DESCENDING") \
        .limit(30) \
        .get()
    return [
        {
            "id": doc.id,
            "titulo": data.get("titulo", ""),
            "cuerpo": data.get("cuerpo"),
            "tipo": data.get("tipo"),
            "leida": data.get("leida", False),
            "created_at": data.get("created_at"),
        }
        for doc in docs
        for data in [doc.to_dict()]
    ]


@router.post("/operaciones", response_model=OperacionOut)
def crear_operacion(
    data: OperacionIn,
    cli: dict = Depends(get_current_cliente),
):
    """Registra una operación iniciada por el cliente (transferencia / pago)."""
    op_id = str(uuid.uuid4())
    operacion_data = {
        "cliente_id": cli["cliente_id"],
        "cod_cuenta_origen": data.cod_cuenta_origen,
        "cod_cuenta_destino": data.cod_cuenta_destino,
        "tipo": data.tipo,
        "monto": data.monto,
        "moneda": data.moneda,
        "estado": "pendiente",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.collection("operaciones_cliente").document(op_id).set(operacion_data)
    operacion_data["id"] = op_id
    return operacion_data


# ✅ ENDPOINT PARA CLIENTE CREAR SOLICITUD + CREAR CARTERA
@router.post("/solicitudes", response_model=SolicitudCreada)
def crear_solicitud_cliente(
    data: SolicitudIn,
    cli: dict = Depends(get_current_cliente),
):
    """Cliente crea una solicitud de crédito."""
    try:
        print(f"📝 Cliente creando solicitud: {cli['cliente_id']}")
        
        cliente_doc = db.collection("clientes").document(cli["cliente_id"]).get()
        if not cliente_doc.exists:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        cliente_data = cliente_doc.to_dict()
        
        sol_id = str(uuid.uuid4())
        expediente = "EXP-" + sol_id.replace("-", "")[:8].upper()
        
        solicitud_data = {
            "numero_expediente": expediente,
            "cliente_id": cli["cliente_id"],
            "cliente_nombre": f"{cliente_data.get('nombres', '')} {cliente_data.get('apellidos', '')}".strip(),
            "canal": "cliente",
            "tipo_negocio": data.tipo_negocio,
            "nombre_negocio": data.nombre_negocio,
            "ingresos_estimados": data.ingresos_estimados,
            "monto_solicitado": data.monto_solicitado,
            "plazo_meses": data.plazo_meses,
            "moneda": data.moneda,
            "tipo_cuota": data.tipo_cuota,
            "garantia": data.garantia,
            "destino_credito": data.destino_credito,
            "cuota_estimada": data.cuota_estimada,
            "tea_referencial": data.tea_referencial,
            "firma_cliente_base64": data.firma_cliente_base64,
            "estado": "enviado",
            "asesor_id": "asesor_001",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        db.collection("solicitudes").document(sol_id).set(solicitud_data)
        
        # ✅ CREAR CARTERA PARA EL ASESOR
        rep_cartera.crear_cartera_desde_solicitud(
            sol_id, 
            cli["cliente_id"], 
            "asesor_001", 
            data.monto_solicitado
        )
        
        print(f"✅ Solicitud creada: {expediente} - cartera creada para asesor_001")
        return {"id": sol_id, "numero_expediente": expediente, "estado": "enviado"}
        
    except Exception as e:
        print(f"❌ Error en crear_solicitud_cliente: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))