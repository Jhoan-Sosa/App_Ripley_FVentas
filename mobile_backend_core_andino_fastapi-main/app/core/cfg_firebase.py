import os
import json
import firebase_admin
from firebase_admin import credentials

# Intentar obtener las credenciales desde variable de entorno
firebase_creds_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if not firebase_creds_json:
    # Fallback: intentar cargar desde archivo (solo desarrollo local)
    try:
        cred_path = os.path.join(os.path.dirname(__file__), "../../serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firebase_admin.firestore.client()
        print("✅ Firebase inicializado desde archivo local.")
    except FileNotFoundError:
        raise ValueError("No se encontró FIREBASE_SERVICE_ACCOUNT en variables de entorno ni el archivo serviceAccountKey.json")
else:
    # Usar las credenciales desde la variable de entorno
    try:
        creds_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
        db = firebase_admin.firestore.client()
        print("✅ Firebase inicializado desde variable de entorno.")
    except json.JSONDecodeError:
        raise ValueError("El contenido de FIREBASE_SERVICE_ACCOUNT no es un JSON válido.")
