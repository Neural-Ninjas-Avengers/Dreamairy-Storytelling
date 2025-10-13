# 🧪 Instrucciones para Probar la Generación de Imágenes AI

## 🚀 Prueba Rápida

### 1. Probar Servicios AI (Backend)
```bash
cd adaptive-storytelling-agent
python test_ai_services.py --quick
```

**Resultado esperado**:
```
🚀 Quick Test: Generating a simple avatar...
✅ SUCCESS! AI image generation is working!
Generated: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...
```

### 2. Iniciar la Aplicación
```bash
# Terminal 1: Backend
cd adaptive-storytelling-agent
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd react-demo
npm start
```

### 3. Probar en el Navegador
1. **Abrir**: http://localhost:3000
2. **Tomar foto**: Clic en "📸 Tomar Foto"
3. **Esperar avatar**: Debería aparecer "🎨 Creando tu avatar mágico..."
4. **Ver resultado**: Avatar reemplaza el logo de Kiro
5. **Iniciar historia**: Completar edad y tema
6. **Generar ilustración**: En el cuento, clic en "🎨 Generar Ilustración AI"

## 🔍 Verificación Paso a Paso

### Paso 1: Verificar Backend
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

### Paso 2: Probar Generación de Avatar
```bash
curl -X POST http://localhost:8000/api/v1/demo/sessions/test123/generate-avatar \
  -H "Content-Type: application/json" \
  -d '{"style": "children_book_avatar"}'
```

**Esperado**:
```json
{
  "success": true,
  "avatar_url": "data:image/jpeg;base64,/9j/4AAQ...",
  "generation_time": 3.2,
  "style_applied": "children_book_avatar"
}
```

### Paso 3: Verificar Frontend
Abrir DevTools (F12) y buscar estos logs:

#### Al tomar foto:
```
Photo captured and ready for AI generation
Starting avatar generation...
Avatar generation result: {success: true, avatar_url: "data:image/jpeg;base64,..."}
Avatar generated successfully: data:image/jpeg;base64,...
```

#### Al generar ilustración:
```
AIImageGenerator - capturedPhoto changed: {url: "blob:...", avatar: "data:image/jpeg;base64,..."}
AIImageGenerator - Setting hasUserPhoto to true
Using captured photo for AI generation: {...}
```

## 🎯 Puntos de Verificación

### ✅ Avatar Automático
- [ ] Foto se captura correctamente
- [ ] Aparece "🎨 Creando tu avatar mágico..."
- [ ] Avatar se genera (2-10 segundos)
- [ ] Logo de Kiro se reemplaza por avatar
- [ ] Texto cambia a "¡Tu Historia Mágica!"

### ✅ Ilustraciones en el Cuento
- [ ] Botón "🎨 Generar Ilustración AI" aparece
- [ ] Se muestra "¡Foto detectada!" (verde)
- [ ] Al generar, aparece "Generando Ilustración AI..."
- [ ] Imagen se genera y se muestra
- [ ] Información de estilo y tiempo aparece

## 🚨 Solución de Problemas

### Problema: "Avatar generation failed"
**Diagnóstico**:
```bash
# Probar servicios manualmente
curl "https://image.pollinations.ai/prompt/cute%20child%20avatar?width=512&height=512"
```

**Soluciones**:
1. Verificar conexión a internet
2. Revisar logs del backend
3. Reiniciar el servidor

### Problema: "No se genera ilustración"
**Diagnóstico**:
1. Abrir DevTools → Console
2. Buscar errores en rojo
3. Verificar que `hasUserPhoto: true`

**Soluciones**:
1. Verificar que la foto se capturó correctamente
2. Reiniciar la aplicación
3. Probar con una nueva foto

### Problema: "Imagen tarda mucho"
**Causa**: Hugging Face modelo cargándose
**Solución**: Esperar 10-20 segundos, Pollinations tomará el relevo

### Problema: "Solo aparecen placeholders"
**Causa**: Todos los servicios AI fallaron
**Solución**: 
1. Verificar conexión a internet
2. Probar URLs manualmente
3. Revisar logs del backend

## 📊 Tiempos Esperados

### Generación de Avatar
- **Pollinations**: 2-5 segundos
- **Hugging Face**: 3-10 segundos (primera vez más lento)
- **Fallback**: <1 segundo

### Generación de Ilustraciones
- **Pollinations**: 3-7 segundos
- **Hugging Face**: 5-15 segundos
- **Fallback**: <1 segundo

## 🎉 Resultado Final Esperado

### En la Página de Bienvenida
```
[TU AVATAR GENERADO]
¡Tu Historia Mágica!
Protagonizada por ti

📸 ¡Toma una foto para ser el protagonista!
[AVATAR PEQUEÑO] ✓ ¡Foto lista para IA!
```

### En el Cuento
```
🎨 Generador de Ilustraciones AI
✅ ¡Foto detectada!
[TU FOTO] Aparecerás como personaje en la imagen

[IMAGEN GENERADA CON IA]
Estilo: Libro Infantil
Tiempo: 4.2s
Personaje: ¡Tú apareces! 👤
```

¡Con esta configuración, la generación de imágenes AI funcionará de verdad! 🎨✨