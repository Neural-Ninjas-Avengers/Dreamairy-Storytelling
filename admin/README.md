# DreamAIry Admin Panel

Panel de administración único y simplificado para configurar DreamAIry.

## Uso

### Opción 1: Abrir directamente
```bash
# Desde la raíz del proyecto
start_admin.bat
```

### Opción 2: Abrir manualmente
Abre el archivo `admin/index.html` en tu navegador.

## Configuración

1. **Selecciona el entorno**:
   - **Demo**: Sin AWS, usa plantillas locales (gratis)
   - **Staging**: AWS con configuración de prueba
   - **Production**: AWS completo

2. **Configura AWS** (solo para Staging/Production):
   - AWS Access Key ID
   - AWS Secret Access Key
   - Región (default: eu-west-1)

3. **Guarda la configuración**

4. **Reinicia el backend** para aplicar cambios

## Características

- ✅ Configuración de entorno (Demo/Staging/Production)
- ✅ Gestión de credenciales AWS
- ✅ Test de servicios AWS
- ✅ Interfaz simple y clara
- ✅ Sin servidor adicional necesario

## Notas

- La configuración se guarda en `backend/admin/config/admin_config.json`
- En modo Demo no se requiere AWS
- Reinicia el backend después de cambiar la configuración
