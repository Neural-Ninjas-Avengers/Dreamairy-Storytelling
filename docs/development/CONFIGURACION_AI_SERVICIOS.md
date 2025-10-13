# 🤖 Configuración de Servicios AI Gratuitos

## 🚀 Servicios Implementados

### 1. **Pollinations AI** (Recomendado - Sin configuración)
- **Gratis**: ✅ Completamente gratuito
- **Sin registro**: ✅ No requiere API key
- **Rápido**: ✅ 2-5 segundos por imagen
- **Calidad**: ✅ Buena calidad para cuentos infantiles
- **URL**: https://pollinations.ai/

### 2. **Hugging Face** (Opcional - Mejor calidad)
- **Gratis**: ✅ Tier gratuito generoso
- **Registro**: ⚠️ Requiere cuenta gratuita
- **Rápido**: ✅ 3-10 segundos por imagen
- **Calidad**: ✅ Excelente calidad
- **Modelos**: Stable Diffusion v1.5

### 3. **Fallback** (Siempre disponible)
- **Placeholder**: ✅ Imágenes temáticas de respaldo
- **SVG**: ✅ Iconos generados dinámicamente
- **Sin fallas**: ✅ Siempre funciona

## ⚡ Configuración Rápida (Sin API Keys)

### Opción 1: Solo Pollinations (Recomendado)
```bash
# No requiere configuración
# Funciona inmediatamente
```

La aplicación funcionará automáticamente con Pollinations AI sin necesidad de configuración adicional.

## 🔧 Configuración Avanzada (Con Hugging Face)

### Paso 1: Crear cuenta en Hugging Face
1. Ve a https://huggingface.co/join
2. Crea una cuenta gratuita
3. Verifica tu email

### Paso 2: Obtener API Token
1. Ve a https://huggingface.co/settings/tokens
2. Clic en "New token"
3. Nombre: "Kiro Storytelling"
4. Tipo: "Read"
5. Copia el token generado

### Paso 3: Configurar Variable de Entorno
```bash
# Windows (CMD)
set HUGGINGFACE_TOKEN=tu_token_aqui

# Windows (PowerShell)
$env:HUGGINGFACE_TOKEN="tu_token_aqui"

# Linux/Mac
export HUGGINGFACE_TOKEN=tu_token_aqui
```

### Paso 4: Crear archivo .env
```bash
# En la carpeta adaptive-storytelling-agent/
cp .env.example .env
```

Edita el archivo `.env`:
```
HUGGINGFACE_TOKEN=hf_tu_token_real_aqui
```

## 🧪 Probar la Configuración

### Verificar Pollinations
```bash
curl "https://image.pollinations.ai/prompt/cute%20child%20avatar%20cartoon%20style?width=512&height=512"
```

### Verificar Hugging Face
```bash
curl -X POST \
  https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5 \
  -H "Authorization: Bearer tu_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "cute child avatar cartoon style"}'
```

## 🎯 Rendimiento Esperado

### Pollinations AI
- **Tiempo**: 2-5 segundos
- **Resolución**: 512x512px
- **Estilos**: Todos los estilos soportados
- **Límites**: Sin límites conocidos

### Hugging Face
- **Tiempo**: 3-10 segundos (primera vez más lento)
- **Resolución**: 512x512px
- **Calidad**: Superior a Pollinations
- **Límites**: ~1000 requests/mes gratis

### Fallback
- **Tiempo**: <1 segundo
- **Tipo**: SVG/Placeholder
- **Siempre disponible**: ✅

## 🔍 Debug y Logs

### Verificar Servicio Activo
```python
# En los logs del backend busca:
"Image generated successfully with _generate_with_pollinations"
"Image generated successfully with _generate_with_huggingface"
"All image generation services failed"
```

### Console del Frontend
```javascript
// Busca estos logs:
"Avatar generation result: {success: true, avatar_url: '...'}"
"Avatar generated successfully: data:image/jpeg;base64,..."
"Failed to generate avatar: Error message"
```

## 🚨 Solución de Problemas

### Problema: "No se genera ninguna imagen"
**Solución**:
1. Verificar conexión a internet
2. Revisar logs del backend
3. Probar URLs manualmente

### Problema: "Avatar generation failed"
**Solución**:
1. Verificar que el backend esté ejecutándose
2. Revisar console del navegador (F12)
3. Verificar endpoint `/demo/sessions/{id}/generate-avatar`

### Problema: "Hugging Face 503 error"
**Solución**:
- Es normal, el modelo se está cargando
- Espera 10-20 segundos y reintenta
- Pollinations tomará el relevo automáticamente

## 📈 Optimizaciones

### Para Mejor Rendimiento
```python
# En ai_image_service.py, ajustar parámetros:
params = {
    "width": 256,      # Más rápido
    "height": 256,     # Más rápido
    "enhance": "false" # Más rápido
}
```

### Para Mejor Calidad
```python
params = {
    "width": 768,      # Mejor calidad
    "height": 768,     # Mejor calidad
    "enhance": "true", # Mejor calidad
    "model": "flux"    # Modelo más avanzado
}
```

## 🎉 Resultado Final

Con esta configuración tendrás:
- ✅ **Generación real de imágenes AI** (no simulación)
- ✅ **Múltiples servicios de respaldo** (alta disponibilidad)
- ✅ **Configuración flexible** (con o sin API keys)
- ✅ **Rendimiento rápido** (2-10 segundos)
- ✅ **Calidad profesional** para cuentos infantiles

¡Las imágenes AI ahora funcionarán de verdad! 🎨✨