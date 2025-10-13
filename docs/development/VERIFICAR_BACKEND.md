# 🔍 Verificar Backend - Solución a NetworkError

## 🐛 Error Identificado

**Error**: `Failed to generate avatar, using fallback: TypeError: NetworkError when attempting to fetch resource.`

**Causa**: El backend no está ejecutándose o no es accesible desde el frontend.

## ✅ Solución Paso a Paso

### 1. 🚀 Iniciar el Backend

```bash
# Navegar a la carpeta del proyecto
cd adaptive-storytelling-agent

# Iniciar el servidor FastAPI
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. 🔍 Verificar que el Backend Funciona

#### Opción A: Navegador
Abrir en el navegador: http://localhost:8000/docs

**Esperado**: Página de documentación de FastAPI (Swagger UI)

#### Opción B: Terminal
```bash
curl http://localhost:8000/api/v1/demo/avatar-styles
```

**Esperado**:
```json
{
  "styles": {
    "children_book_avatar": {
      "name": "Avatar de Cuento",
      "description": "Avatar estilo libro infantil, amigable y colorido"
    }
  }
}
```

### 3. 🔧 Probar Generación de Avatar

```bash
curl -X POST http://localhost:8000/api/v1/demo/sessions/test123/generate-avatar \
  -H "Content-Type: application/json" \
  -d '{"style": "children_book_avatar"}'
```

**Esperado**: JSON con `avatar_url` generada

## 🛠️ Soluciones a Problemas Comunes

### Problema 1: "ModuleNotFoundError"
```bash
# Instalar dependencias
pip install fastapi uvicorn aiohttp pillow

# O si tienes requirements.txt
pip install -r requirements.txt
```

### Problema 2: "Port already in use"
```bash
# Usar otro puerto
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Actualizar frontend para usar puerto 8001
# En StorytellingService.js cambiar getBackendUrl()
```

### Problema 3: "app.main not found"
```bash
# Verificar estructura de carpetas
ls -la app/
# Debe existir app/main.py

# Si no existe, crear archivo básico
```

### Problema 4: "CORS errors"
El backend ya tiene CORS configurado, pero si hay problemas:
```python
# En app/main.py verificar:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción usar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Fallbacks Implementados

### Si el Backend NO Funciona
La aplicación ahora tiene fallbacks locales:

#### Avatar Fallback
- **SVG generado localmente** con colores temáticos
- **Diferentes estilos** según el tipo solicitado
- **Siempre funciona** sin conexión al backend

#### Ilustración Fallback
- **SVG temático** basado en el contexto de la historia
- **5 temas diferentes**: bosque, océano, castillo, animales, mágico
- **Elementos visuales** apropiados para cada tema

### Logs Mejorados
```javascript
// En console verás:
"Attempting to generate avatar for session: demo_avatar_123"
"Backend URL: http://localhost:8000"
"Failed to generate avatar via API, using local fallback: NetworkError..."
"Avatar generated (local fallback mode)"
```

## 🚀 Iniciar Todo Correctamente

### Script Completo
```bash
# Terminal 1: Backend
cd adaptive-storytelling-agent
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (nueva ventana)
cd adaptive-storytelling-agent/react-demo
npm start

# Terminal 3: Verificar (nueva ventana)
curl http://localhost:8000/docs
```

### Orden Correcto
1. **Primero**: Iniciar backend (puerto 8000)
2. **Segundo**: Iniciar frontend (puerto 3000)
3. **Tercero**: Abrir http://localhost:3000

## 🎉 Resultado Final

### Con Backend Funcionando
- ✅ **Avatares AI reales** generados con Pollinations/Hugging Face
- ✅ **Ilustraciones AI reales** con servicios externos
- ✅ **Calidad superior** y variedad

### Sin Backend (Solo Fallbacks)
- ✅ **Avatares SVG** generados localmente
- ✅ **Ilustraciones SVG** temáticas
- ✅ **Funciona siempre** sin dependencias externas
- ✅ **Experiencia completa** garantizada

## 🔍 Debug Rápido

### Verificar Estado
```bash
# ¿Está el backend ejecutándose?
curl -I http://localhost:8000

# ¿Responde el endpoint de avatares?
curl http://localhost:8000/api/v1/demo/avatar-styles

# ¿Funciona la generación?
curl -X POST http://localhost:8000/api/v1/demo/sessions/test/generate-avatar \
  -H "Content-Type: application/json" -d '{"style": "children_book_avatar"}'
```

### Console del Frontend
```javascript
// Buscar estos logs:
"Backend URL: http://localhost:8000"  // ✅ URL correcta
"Avatar generated via API: {...}"     // ✅ Backend funciona
"Avatar generated (local fallback)"   // ⚠️ Usando fallback
```

¡Con estos fallbacks, la aplicación funcionará siempre, con o sin backend! 🎨✨