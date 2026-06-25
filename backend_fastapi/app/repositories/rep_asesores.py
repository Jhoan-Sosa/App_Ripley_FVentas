from app.core.cfg_firebase import db

def get_by_codigo(codigo_empleado: str) -> dict | None:
    """Busca un asesor por su código de empleado en Firestore."""
    try:
        docs = db.collection("asesores").where("codigo_empleado", "==", codigo_empleado).limit(1).get()
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    except Exception as e:
        print(f"Error en get_by_codigo: {e}")
        return None

def get_by_id(asesor_id: str) -> dict | None:
    """Busca un asesor por su ID en Firestore."""
    try:
        doc = db.collection("asesores").document(asesor_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    except Exception as e:
        print(f"Error en get_by_id: {e}")
        return None