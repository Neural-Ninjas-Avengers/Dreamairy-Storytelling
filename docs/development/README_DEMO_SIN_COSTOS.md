# 🎭 Demo Sin Costos AWS - Adaptive Storytelling Agent

## ⚠️ IMPORTANTE: MODO DEMO GRATUITO

Este proyecto está configurado por defecto para funcionar **SIN INCURRIR EN COSTOS DE AWS**. Utiliza servicios simulados (mock) que replican la funcionalidad completa sin conectarse a AWS.

## 🚀 Inicio Rápido (Sin Costos)

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Copia el archivo de configuración (ya está configurado para modo offline)
cp .env.example .env
```

### 3. Ejecutar la Aplicación
```bash
uvicorn app.main:app --reload
```

### 4. Acceder al Demo
- **Demo Web**: http://localhost:3001/demo
- **API Docs**: http://localhost:3001/docs
- **Health Check**: http://localhost:3001/health

## ✅ Funcionalidades Disponibles en Modo Demo

### 🎯 Todo Funciona Sin AWS:
- ✅ **Generación de Historias** - Plantillas locales predefinidas
- ✅ **Detección de Emociones** - Simulación realista de audio/imagen
- ✅ **Adaptación en Tiempo Real** - Lógica completa de adaptación
- ✅ **Narración de Voz** - Audio silencioso (placeholder)
- ✅ **WebSocket en Tiempo Real** - Comunicación bidireccional
- ✅ **Métricas y Analytics** - Seguimiento completo de engagement
- ✅ **Escenarios de Demo** - 4 escenarios predefinidos
- ✅ **Interfaz Web Completa** - UI totalmente funcional

### 🎪 Escenarios de Demo Incluidos:
1. **"Boredom to Engagement"** - Niño aburrido → sistema adapta → engagement
2. **"Fear to Comfort"** - Niño asustado → sistema calma → tranquilidad
3. **"Excitement Management"** - Niño muy emocionado → sistema calma gradualmente
4. **"Multi-Emotion Journey"** - Viaje emocional complejo con múltiples adaptaciones

## 🔧 Configuración del Modo Demo

El archivo `.env` está preconfigurado con:

```bash
# Modo Sin Costos AWS
OFFLINE_MODE=true          # No conecta a AWS
USE_MOCK_SERVICES=true     # Usa servicios simulados
DEMO_MODE=true             # Habilita funciones de demo

# Configuración de Desarrollo
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## 🎮 Cómo Usar el Demo

### Interfaz Web (/demo):
1. **Configurar Perfil del Niño**:
   - Edad (3-12 años)
   - Preferencias (animales, aventura, amistad, etc.)
   - Objetivo emocional (entretener, calmar, estimular juego)

2. **Iniciar Sesión de Cuentos**:
   - Click en "Start Storytelling Session"
   - La historia comenzará automáticamente

3. **Simular Emociones**:
   - Click en botones de emociones (😄 Happy, 😴 Bored, etc.)
   - Sube archivos de audio/imagen (se procesarán localmente)
   - Observa cómo la historia se adapta en tiempo real

4. **Monitorear Métricas**:
   - Segmentos de historia generados
   - Adaptaciones realizadas
   - Score de engagement
   - Log de actividad en tiempo real

### API Endpoints (/api/v1):
```bash
# Crear sesión
POST /api/v1/sessions

# Procesar emociones
POST /api/v1/sessions/{id}/emotion/audio
POST /api/v1/sessions/{id}/emotion/image

# Escenarios de demo automáticos
GET /api/v1/demo/scenarios
POST /api/v1/demo/scenarios/{name}/start

# WebSocket en tiempo real
WS /api/v1/ws/{connection_id}
```

## 🔄 Cambiar a AWS Real (Opcional)

Si quieres usar AWS real (incurrirá en costos):

1. **Modificar .env**:
```bash
OFFLINE_MODE=false
USE_MOCK_SERVICES=false

# Descomentar y configurar:
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
```

2. **Servicios AWS Necesarios**:
   - Amazon Bedrock (Claude/Titan)
   - Amazon Transcribe
   - Amazon Rekognition
   - Amazon Polly
   - Amazon S3

## 📊 Métricas del Demo

El sistema rastrea automáticamente:
- **Tiempo de respuesta** de adaptaciones
- **Score de engagement** basado en confianza emocional
- **Precisión de adaptación** vs escenarios esperados
- **Duración de sesión** y segmentos generados

## 🛡️ Características de Seguridad

Incluso en modo demo:
- ✅ Validación de entrada completa
- ✅ Filtrado de contenido apropiado para la edad
- ✅ Gestión de sesiones segura
- ✅ Rate limiting
- ✅ Manejo de errores robusto

## 🎯 Perfecto para:
- **Demos de hackathon** sin costos
- **Desarrollo local** sin AWS
- **Testing de funcionalidad** completa
- **Presentaciones** en vivo
- **Prototipado** rápido

## 🚨 Nota Importante

**El modo demo NO incurre en costos de AWS** porque:
- No se conecta a servicios AWS reales
- Usa plantillas de historias predefinidas
- Simula detección de emociones localmente
- Genera audio silencioso como placeholder
- Almacena datos solo en memoria local

¡Perfecto para demostrar todas las capacidades sin preocuparte por los costos! 🎉