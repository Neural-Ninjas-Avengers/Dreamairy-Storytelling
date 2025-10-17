# DynamicThemeEngine

Motor de temas dinámicos para aplicar y gestionar paletas de colores y estilos adaptativos por edad.

## Características

- ✅ Aplicación de paletas de colores a CSS variables
- ✅ Estilos adaptativos por edad (3-12 años)
- ✅ Persistencia en localStorage
- ✅ Historial de temas aplicados
- ✅ Transiciones suaves entre temas
- ✅ Soporte para reduced motion
- ✅ Validación de accesibilidad (WCAG)
- ✅ Import/Export de temas

## Uso Básico

```javascript
import dynamicThemeEngine from './services/DynamicThemeEngine';
import claudeDesignService from './services/ClaudeDesignService';

// Generar y aplicar paleta
const palette = await claudeDesignService.generateColorPalette('fantasy', 7, 'entertain');
dynamicThemeEngine.applyPalette(palette, 7);
```

## Aplicar Paleta de Colores

```javascript
// Aplicar paleta con edad
dynamicThemeEngine.applyPalette(palette, 7);

// Aplicar con transición suave
await dynamicThemeEngine.applyPaletteWithTransition(palette, 7, 500);

// La paleta se guarda automáticamente en localStorage
```

**CSS Variables Aplicadas:**
```css
--color-primary: #9C27B0
--color-secondary: #E91E63
--color-accent: #FFD700
--color-background: #F3E5F5
--color-text: #4A148C
--gradient-primary: linear-gradient(135deg, #BA68C8, #F06292, #FFE082)
--gradient-vertical: linear-gradient(180deg, #BA68C8, #F06292, #FFE082)
--gradient-radial: radial-gradient(circle, #BA68C8, #F06292, #FFE082)
```

## Estilos Adaptativos por Edad

El motor aplica automáticamente estilos apropiados según la edad:

### Edad 3-5 años
```css
--font-size-base: 18px
--font-size-large: 24px
--button-size: 60px
--button-padding: 1.5rem 2rem
--border-radius: 25px
--spacing-unit: 1.5rem
--animation-speed: 0.5s
--shadow-size: 0 8px 16px rgba(0,0,0,0.15)
```

### Edad 6-8 años
```css
--font-size-base: 16px
--font-size-large: 20px
--button-size: 50px
--button-padding: 1rem 1.5rem
--border-radius: 20px
--spacing-unit: 1.25rem
--animation-speed: 0.3s
--shadow-size: 0 6px 12px rgba(0,0,0,0.12)
```

### Edad 9-12 años
```css
--font-size-base: 14px
--font-size-large: 18px
--button-size: 44px
--button-padding: 0.75rem 1.25rem
--border-radius: 15px
--spacing-unit: 1rem
--animation-speed: 0.2s
--shadow-size: 0 4px 8px rgba(0,0,0,0.1)
```

## Usar Variables CSS en Componentes

### En CSS/SCSS
```css
.my-button {
  background-color: var(--color-primary);
  color: white;
  padding: var(--button-padding);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  box-shadow: var(--shadow-size);
  transition: all var(--animation-speed);
}

.my-card {
  background: var(--gradient-primary);
  padding: var(--spacing-unit);
  border-radius: var(--border-radius);
}
```

### En React con Inline Styles
```javascript
function MyComponent() {
  return (
    <div style={{
      backgroundColor: 'var(--color-background)',
      color: 'var(--color-text)',
      padding: 'var(--spacing-unit)',
      borderRadius: 'var(--border-radius)'
    }}>
      <button style={{
        backgroundColor: 'var(--color-primary)',
        padding: 'var(--button-padding)',
        fontSize: 'var(--font-size-base)'
      }}>
        Click me
      </button>
    </div>
  );
}
```

### Con Styled Components
```javascript
import styled from 'styled-components';

const StyledButton = styled.button`
  background-color: var(--color-primary);
  color: white;
  padding: var(--button-padding);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  transition: all var(--animation-speed);
  
  &:hover {
    background-color: var(--color-secondary);
  }
`;
```

## Gestión de Temas

### Obtener Tema Actual
```javascript
const currentTheme = dynamicThemeEngine.getCurrentTheme();
console.log('Current theme:', currentTheme);
// {
//   palette: { primary: "#9C27B0", ... },
//   age: 7,
//   timestamp: 1234567890,
//   metadata: { theme: "fantasy", ... }
// }
```

### Historial de Temas
```javascript
const history = dynamicThemeEngine.getThemeHistory();
console.log('Theme history:', history);

// Aplicar tema anterior
dynamicThemeEngine.applyThemeFromHistory(0); // Primer tema en historial
```

### Reset a Tema por Defecto
```javascript
dynamicThemeEngine.resetTheme();
// Elimina todas las variables CSS personalizadas
// Limpia localStorage
```

## Import/Export de Temas

### Exportar Tema
```javascript
const themeJson = dynamicThemeEngine.exportTheme();
console.log(themeJson);

// Guardar en archivo
const blob = new Blob([themeJson], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'my-theme.json';
a.click();
```

### Importar Tema
```javascript
// Desde archivo
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.accept = '.json';
fileInput.onchange = (e) => {
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      dynamicThemeEngine.importTheme(event.target.result);
      console.log('Theme imported successfully');
    } catch (error) {
      console.error('Failed to import theme:', error);
    }
  };
  reader.readAsText(file);
};
fileInput.click();

// Desde string JSON
const themeJson = '{"palette":{"primary":"#9C27B0",...},"age":7}';
dynamicThemeEngine.importTheme(themeJson);
```

## Transiciones Suaves

```javascript
// Aplicar tema con transición de 500ms
await dynamicThemeEngine.applyPaletteWithTransition(newPalette, 7, 500);

// Aplicar tema con transición de 1 segundo
await dynamicThemeEngine.applyPaletteWithTransition(newPalette, 7, 1000);
```

## Accesibilidad

### Reduced Motion
```javascript
// Verificar preferencia
const prefersReduced = dynamicThemeEngine.prefersReducedMotion();
console.log('Prefers reduced motion:', prefersReduced);

// Aplicar reduced motion
dynamicThemeEngine.applyReducedMotion();
// Establece --animation-speed a 0.01s
```

### Validar Contraste
```javascript
// Validar accesibilidad de paleta
const validation = dynamicThemeEngine.validatePaletteAccessibility(palette);

if (!validation.valid) {
  console.error('Accessibility issues:', validation.issues);
  // [
  //   {
  //     type: 'contrast',
  //     severity: 'high',
  //     message: 'Text/background contrast ratio 3.2 is below WCAG AA standard (4.5:1)',
  //     colors: ['#4A148C', '#F3E5F5']
  //   }
  // ]
}

if (validation.warnings.length > 0) {
  console.warn('Accessibility warnings:', validation.warnings);
}
```

### Calcular Ratio de Contraste
```javascript
const ratio = dynamicThemeEngine.getContrastRatio('#000000', '#FFFFFF');
console.log('Contrast ratio:', ratio); // 21 (máximo contraste)

// WCAG Standards:
// AA Normal text: 4.5:1
// AA Large text: 3:1
// AAA Normal text: 7:1
// AAA Large text: 4.5:1
```

## Manipular Variables CSS Directamente

```javascript
// Obtener valor de variable
const primaryColor = dynamicThemeEngine.getCSSVariable('color-primary');
console.log('Primary color:', primaryColor); // "#9C27B0"

// Establecer valor de variable
dynamicThemeEngine.setCSSVariable('color-custom', '#FF5722');

// Usar con o sin --
dynamicThemeEngine.getCSSVariable('--color-primary'); // También funciona
dynamicThemeEngine.setCSSVariable('--color-custom', '#FF5722'); // También funciona
```

## Integración con React

### Hook Personalizado
```javascript
import { useState, useEffect } from 'react';
import dynamicThemeEngine from '../services/DynamicThemeEngine';
import claudeDesignService from '../services/ClaudeDesignService';

function useTheme(theme, age, emotionalGoal) {
  const [loading, setLoading] = useState(true);
  const [currentTheme, setCurrentTheme] = useState(null);

  useEffect(() => {
    async function loadTheme() {
      try {
        // Generar paleta
        const palette = await claudeDesignService.generateColorPalette(
          theme, age, emotionalGoal
        );
        
        // Aplicar con transición
        await dynamicThemeEngine.applyPaletteWithTransition(palette, age, 500);
        
        // Actualizar estado
        setCurrentTheme(dynamicThemeEngine.getCurrentTheme());
      } catch (error) {
        console.error('Failed to load theme:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadTheme();
  }, [theme, age, emotionalGoal]);

  return { loading, currentTheme };
}

// Uso en componente
function MyApp() {
  const { loading, currentTheme } = useTheme('fantasy', 7, 'entertain');

  if (loading) return <div>Loading theme...</div>;

  return (
    <div className="app">
      <h1>My App with Dynamic Theme</h1>
      <p>Current theme: {currentTheme?.metadata?.theme}</p>
    </div>
  );
}
```

### Context Provider
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import dynamicThemeEngine from '../services/DynamicThemeEngine';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState(
    dynamicThemeEngine.getCurrentTheme()
  );

  const applyTheme = async (palette, age) => {
    await dynamicThemeEngine.applyPaletteWithTransition(palette, age, 500);
    setCurrentTheme(dynamicThemeEngine.getCurrentTheme());
  };

  const resetTheme = () => {
    dynamicThemeEngine.resetTheme();
    setCurrentTheme(null);
  };

  return (
    <ThemeContext.Provider value={{ currentTheme, applyTheme, resetTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useThemeContext() {
  return useContext(ThemeContext);
}

// Uso
function App() {
  return (
    <ThemeProvider>
      <MyComponent />
    </ThemeProvider>
  );
}

function MyComponent() {
  const { currentTheme, applyTheme, resetTheme } = useThemeContext();
  
  return (
    <div>
      <button onClick={() => applyTheme(newPalette, 7)}>
        Apply Theme
      </button>
      <button onClick={resetTheme}>
        Reset Theme
      </button>
    </div>
  );
}
```

## Persistencia

El tema se guarda automáticamente en localStorage:
- **Key**: `dreamairy_theme`
- **Formato**: JSON con palette, age, timestamp, metadata
- **Carga automática**: Al inicializar el servicio

```javascript
// El tema se carga automáticamente al importar el servicio
import dynamicThemeEngine from './services/DynamicThemeEngine';

// Si hay un tema guardado, ya está aplicado
const savedTheme = dynamicThemeEngine.getCurrentTheme();
if (savedTheme) {
  console.log('Loaded saved theme from localStorage');
}
```

## Mejores Prácticas

### 1. Aplicar Tema al Inicio de la App
```javascript
// En App.js o index.js
useEffect(() => {
  // Aplicar reduced motion si es necesario
  dynamicThemeEngine.applyReducedMotion();
  
  // El tema guardado ya está aplicado automáticamente
  const currentTheme = dynamicThemeEngine.getCurrentTheme();
  if (currentTheme) {
    console.log('Using saved theme');
  }
}, []);
```

### 2. Validar Accesibilidad Antes de Aplicar
```javascript
const palette = await claudeDesignService.generateColorPalette('fantasy', 7, 'entertain');

const validation = dynamicThemeEngine.validatePaletteAccessibility(palette);
if (!validation.valid) {
  console.warn('Palette has accessibility issues, using fallback');
  // Usar paleta fallback o ajustar colores
} else {
  dynamicThemeEngine.applyPalette(palette, 7);
}
```

### 3. Usar Transiciones para Cambios de Tema
```javascript
// Mejor experiencia de usuario
await dynamicThemeEngine.applyPaletteWithTransition(newPalette, age, 500);

// En lugar de
dynamicThemeEngine.applyPalette(newPalette, age);
```

### 4. Mantener Historial para Deshacer
```javascript
const history = dynamicThemeEngine.getThemeHistory();

// Botón "Deshacer"
function undoTheme() {
  if (history.length > 1) {
    dynamicThemeEngine.applyThemeFromHistory(history.length - 2);
  }
}
```

## Performance

- **Carga inicial**: ~1ms (carga desde localStorage)
- **Aplicar paleta**: ~5ms (establecer CSS variables)
- **Transición**: Configurable (default 500ms)
- **Memoria**: ~1KB por tema en historial (máximo 10 temas)

## Compatibilidad

- ✅ Todos los navegadores modernos (Chrome, Firefox, Safari, Edge)
- ✅ CSS Variables soportadas desde 2016
- ✅ localStorage disponible en todos los navegadores
- ✅ Funciona sin JavaScript (usa valores por defecto de CSS)
