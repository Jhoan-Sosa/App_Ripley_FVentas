from app.core.cfg_firebase import db

def get_db():
    """Dependencia para FastAPI que retorna el cliente de Firestore."""
    return db