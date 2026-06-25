"""
Controlador de autenticación de la app de clientes (login con DNI).
"""
from datetime import datetime, timezone
from app.core.cfg_firebase import db
from app.core.cfg_security import verify_password, create_access_token
import traceback

MAX_INTENTOS = 5


def login(numero_documento: str, password: str) -> dict | None:
    print(f"🔍 Intentando login para DNI: {numero_documento}")
    
    try:
        # Buscar usuario por username (DNI)
        docs = db.collection("usuarios_cliente").where("username", "==", numero_documento).limit(1).get()
        usuario = None
        for doc in docs:
            usuario = doc.to_dict()
            usuario["id"] = doc.id
            print(f"✅ Usuario encontrado: {usuario['id']}")
            break
        
        if not usuario:
            print(f"❌ Usuario no encontrado para DNI: {numero_documento}")
            return None
        
        if not usuario.get("activo", True):
            print(f"❌ Usuario inactivo: {usuario['id']}")
            return None

        # Bloqueo por intentos fallidos
        if usuario.get("bloqueado", False):
            print(f"❌ Usuario bloqueado: {usuario['id']}")
            return {"_bloqueado": True}

        # Verificar contraseña
        hashed = usuario.get("password_hash", "")
        print(f"🔑 Verificando contraseña para: {usuario['id']}")
        print(f"   Hash guardado: {hashed[:20]}...")
        
        if not verify_password(password, hashed):
            intentos = usuario.get("intentos_fallidos", 0) + 1
            print(f"❌ Contraseña incorrecta. Intento {intentos} de {MAX_INTENTOS}")
            if intentos >= MAX_INTENTOS:
                db.collection("usuarios_cliente").document(usuario["id"]).update({
                    "intentos_fallidos": intentos,
                    "bloqueado": True
                })
            else:
                db.collection("usuarios_cliente").document(usuario["id"]).update({
                    "intentos_fallidos": intentos
                })
            return None

        # Login correcto: resetea contador
        print(f"✅ Login exitoso para: {usuario['id']}")
        db.collection("usuarios_cliente").document(usuario["id"]).update({
            "intentos_fallidos": 0,
            "bloqueado": False,
            "ultimo_acceso": datetime.now(timezone.utc).isoformat()
        })

        # Obtener datos del cliente
        cliente_id = usuario.get("cliente_id")
        cliente = None
        if cliente_id:
            print(f"🔍 Buscando cliente con ID: {cliente_id}")
            cliente_doc = db.collection("clientes").document(cliente_id).get()
            if cliente_doc.exists:
                cliente = cliente_doc.to_dict()
                cliente["id"] = cliente_doc.id
                print(f"✅ Cliente encontrado: {cliente['id']}")
            else:
                print(f"❌ Cliente NO encontrado para ID: {cliente_id}")

        token = create_access_token({
            "sub": usuario["username"],
            "cliente_id": cliente_id,
            "nombre": f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}".strip() if cliente else usuario["username"],
        })
        
        print(f"✅ Token generado exitosamente")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "cliente": cliente,
        }
        
    except Exception as e:
        print(f"❌ ERROR en login: {e}")
        traceback.print_exc()
        return None