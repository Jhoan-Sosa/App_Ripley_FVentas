import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Intentar obtener las credenciales desde variable de entorno
firebase_creds_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
db = None  # Inicializar db

if not firebase_creds_json:
    # Fallback: intentar cargar desde archivo (solo desarrollo local)
    try:
        cred_path = os.path.join(os.path.dirname(__file__), "../../serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()  # Forma correcta
        print("✅ Firebase inicializado desde archivo local.")
    except FileNotFoundError:
        raise ValueError("No se encontró FIREBASE_SERVICE_ACCOUNT en variables de entorno ni el archivo serviceAccountKey.json")
    except Exception as e:
        raise ValueError(f"Error al inicializar Firebase desde archivo: {e}")
else:
    # Usar las credenciales desde la variable de entorno
    try:
        creds_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()  # Forma correcta
        print("✅ Firebase inicializado desde variable de entorno.")
    except json.JSONDecodeError:
        raise ValueError("El contenido de FIREBASE_SERVICE_ACCOUNT no es un JSON válido.")
    except Exception as e:
        raise ValueError(f"Error al inicializar Firebase desde variable de entorno: {e}")

# Asegurarse de que db no sea None antes de usarlo
if db is None:
    raise RuntimeError("No se pudo inicializar el cliente de Firestore.")
