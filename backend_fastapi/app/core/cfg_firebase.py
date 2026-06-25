import firebase_admin
from firebase_admin import credentials, firestore
import os

# Ruta al archivo de credenciales (está en la raíz del proyecto)
cred_path = os.path.join(os.path.dirname(__file__), "../../serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase inicializado correctamente")

db = firestore.client()

def get_firestore():
    return db