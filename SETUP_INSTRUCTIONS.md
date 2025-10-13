# 🔧 Instrucciones de Configuración - DreamAIry

## ⚠️ IMPORTANTE: Configuración de Credenciales AWS

### **Paso 1: Copiar el archivo de ejemplo**

```bash
# Windows
copy start_with_aws.bat.example start_with_aws.bat

# Linux/Mac
cp start_with_aws.bat.example start_with_aws.bat
```

### **Paso 2: Editar con tus credenciales reales**

Abre `start_with_aws.bat` y reemplaza:

```bat
set AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
set AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
```

Con tus credenciales reales de AWS (obtenlas de tu cuenta AWS IAM)

### **Paso 3: Verificar que está en .gitignore**

El archivo `start_with_aws.bat` (con credenciales reales) está en `.gitignore` y **NUNCA** se subirá a Git.

## 🔒 Seguridad

- ✅ `start_with_aws.bat.example` - Se sube a Git (sin credenciales)
- ❌ `start_with_aws.bat` - NO se sube a Git (con credenciales reales)

## 🚀 Inicio Rápido

Una vez configurado:

```bash
# Opción 1: Con AWS
start_with_aws.bat

# Opción 2: Script principal
python start_dreamairy.py
```

## 📝 Alternativa: Usar archivo de configuración

También puedes configurar las credenciales en:
```
backend/admin/config/admin_config.json
```

Copia el ejemplo:
```bash
copy backend\admin\config\admin_config.example.json backend\admin\config\admin_config.json
```

Y edita con tus credenciales.

---

**NUNCA compartas tus credenciales de AWS públicamente**
