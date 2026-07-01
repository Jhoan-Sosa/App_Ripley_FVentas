# 🏦 Banco Ripley — Fuerza de Ventas

Sistema integral para la fuerza de ventas de Banco Ripley.

## 📦 Estructura del repositorio

- mobile_app_fventas_andino_flutter-main/ → App Flutter (Fuerza de Ventas)
- mobile_backend_core_andino_fastapi-main/ → Backend FastAPI
- mobile_front_core_andino_react-main/ → Frontend React


## 🚀 Despliegue

### Backend (FastAPI) - Render
- Build: pip install -r requirements.txt
- Start: uvicorn main:app --host 0.0.0.0 --port $PORT

### App Flutter - Firebase Hosting
- Build: flutter build web
- Deploy: firebase deploy --only hosting:fv-entas

## 🔐 Credenciales de prueba
- Asesor: 0001 / 1234
- Supervisor: 0002 / 1234

