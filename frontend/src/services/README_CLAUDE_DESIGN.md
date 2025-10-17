# ClaudeDesignService

Servicio frontend para integración con Claude 3 Haiku como asistente de diseño.

## Características

- ✅ Generación de paletas de colores adaptadas por edad
- ✅ Optimización de prompts para ilustraciones
- ✅ Generación de assets SVG
- ✅ Recomendaciones de UI/UX
- ✅ Feedback de diseño para componentes
- ✅ Rate limiting (10 requests/minuto)
- ✅ Caching con TTL de 1 hora
- ✅ Fallbacks automáticos cuando Claude no está disponible

## Uso Básico

```javascript
import claudeDesignService from './services/ClaudeDesignService';

// Verificar estado del servicio
const status = await claudeDesignService.checkStatus();
console.log('Claude available:', status.available);
```

## Generación de Paletas de Colores

```javascript
// Generar paleta de colores
const palette = await claudeDesignService.generateColorPalette(
  'fantasy',  // theme: animals, fantasy, adventure, friendship
  7,          // age: 3-12
  'entertain' // emotionalGoal: entertain, calm, stimulate
);

console.log('Primary color:', palette.primary);
console.log('Gradient:', palette.gradient);
console.log('Usage:', palette.usage);

// Aplicar colores
document.documentElement.style.setProperty('--color-primary', palette.primary);
```

**Respuesta:**
```javascript
{
  primary: "#9C27B0",
  secondary: "#E91E63",
  accent: "#FFD700",
  background: "#F3E5F5",
  text: "#4A148C",
  gradient: ["#BA68C8", "#F06292", "#FFE082"],
  usage: {
    primary: "Main interactive elements",
    secondary: "Supporting elements",
    accent: "Highlights and CTAs"
  },
  metadata: {
    theme: "fantasy",
    age: 7,
    emotionalGoal: "entertain",
    generatedAt: "2024-01-01T12:00:00Z",
    source: "claude"
  }
}
```

## Optimización de Prompts para Ilustraciones

```javascript
// Optimizar prompt para AWS Titan
const optimizedPrompt = await claudeDesignService.optimizeIllustrationPrompt(
  "The wizard enters a magical forest",  // storySegment
  "young wizard with blue robes",        // avatarDescription
  ["previous prompt 1", "previous prompt 2"] // previousPrompts (opcional)
);

console.log('Optimized prompt:', optimizedPrompt.prompt);
console.log('Negative prompt:', optimizedPrompt.negative_prompt);
console.log('Fallback prompts:', optimizedPrompt.fallback_prompts);

// Usar con AWS Titan
const imageUrl = await generateImageWithTitan(optimizedPrompt.prompt);
```

**Respuesta:**
```javascript
{
  prompt: "Magical forest scene with young wizard in blue robes, children's book illustration style, watercolor art, bright colors, friendly atmosphere, Disney/Pixar quality",
  negative_prompt: "scary, dark, violent, inappropriate, realistic, photographic",
  style: "watercolor storybook",
  fallback_prompts: [
    "Alternative prompt 1",
    "Alternative prompt 2"
  ],
  metadata: {
    storyContext: "The wizard enters a magical forest",
    avatarIncluded: true,
    consistencyScore: 0.9,
    generatedAt: "2024-01-01T12:00:00Z",
    source: "claude"
  }
}
```

## Generación de Assets SVG

```javascript
// Generar SVG asset
const svgAsset = await claudeDesignService.generateSVGAsset(
  "magical star",  // description
  "icon",          // style: icon, decoration, illustration
  palette          // colorPalette (opcional)
);

console.log('SVG code:', svgAsset.svg);
console.log('Description:', svgAsset.description);

// Usar en componente
<div dangerouslySetInnerHTML={{ __html: svgAsset.svg }} />
```

**Respuesta:**
```javascript
{
  svg: "<svg viewBox='0 0 100 100'>...</svg>",
  description: "Magical star icon",
  category: "icon",
  colorPalette: ["#9C27B0", "#E91E63", "#FFD700"],
  valid: true,
  metadata: {
    generatedAt: "2024-01-01T12:00:00Z",
    claudeGenerated: true,
    description: "magical star"
  }
}
```

## Recomendaciones de UI

```javascript
// Obtener recomendaciones de UI
const recommendations = await claudeDesignService.getUIRecommendations(
  'button',  // componentType
  {
    age: 6,
    theme: 'fantasy',
    purpose: 'primary action'
  }
);

console.log('Layout recommendations:', recommendations.layout);
console.log('Color recommendations:', recommendations.colors);
console.log('Accessibility tips:', recommendations.accessibility);
console.log('Code examples:', recommendations.codeExamples);
```

**Respuesta:**
```javascript
{
  component: "button",
  layout: [
    "Use large touch targets (minimum 44px)",
    "Add adequate padding for child-friendly interaction"
  ],
  colors: [
    "Use high contrast for visibility",
    "Follow theme colors for consistency"
  ],
  typography: [
    "Use large, readable font (18px+)",
    "Bold weight for emphasis"
  ],
  accessibility: [
    "Add ARIA labels",
    "Ensure keyboard navigation",
    "Provide focus indicators"
  ],
  responsive: [
    "Scale appropriately on mobile",
    "Maintain touch target size"
  ],
  codeExamples: {
    tailwind: "px-6 py-4 text-lg font-bold rounded-full bg-purple-500 hover:bg-purple-600",
    css: "padding: 1rem 1.5rem; font-size: 1.125rem; border-radius: 9999px;"
  },
  priority: "high",
  generatedAt: "2024-01-01T12:00:00Z"
}
```

## Feedback de Diseño

```javascript
// Obtener feedback sobre código de componente
const feedback = await claudeDesignService.getDesignFeedback(
  componentCode,  // string con el código del componente
  {
    purpose: 'story display',
    targetAge: 7,
    theme: 'fantasy'
  }
);

console.log('Overall assessment:', feedback.overall);
console.log('Issues found:', feedback.issues);
console.log('Strengths:', feedback.strengths);
console.log('Improvements:', feedback.improvements);
```

**Respuesta:**
```javascript
{
  overall: "Good structure with some accessibility improvements needed",
  issues: [
    {
      type: "accessibility",
      severity: "high",
      description: "Missing ARIA labels on interactive elements",
      suggestion: "Add aria-label='description' to buttons"
    },
    {
      type: "design",
      severity: "medium",
      description: "Color contrast may not meet WCAG AA",
      suggestion: "Increase contrast ratio to at least 4.5:1"
    }
  ],
  strengths: [
    "Clear component structure",
    "Good use of semantic HTML"
  ],
  improvements: [
    "Add keyboard navigation support",
    "Implement focus management",
    "Add loading states"
  ],
  generatedAt: "2024-01-01T12:00:00Z"
}
```

## Gestión de Cache

```javascript
// Limpiar cache manualmente
claudeDesignService.clearCache();

// El cache se limpia automáticamente después de 1 hora
// Tamaño máximo: 100 items
```

## Rate Limiting

El servicio implementa rate limiting automático:
- **Límite**: 10 requests por minuto
- **Comportamiento**: Espera automáticamente si se alcanza el límite
- **Error**: Lanza error si el backend retorna 429

```javascript
// El rate limiting es transparente
try {
  const palette = await claudeDesignService.generateColorPalette('fantasy', 7, 'entertain');
} catch (error) {
  if (error.message.includes('Rate limit')) {
    console.log('Too many requests, please wait');
  }
}
```

## Fallbacks

Todos los métodos tienen fallbacks automáticos cuando Claude no está disponible:

- **Paletas**: Paletas predefinidas por tema
- **Prompts**: Templates básicos optimizados
- **SVG**: Assets SVG simples predefinidos
- **Recomendaciones**: Mejores prácticas generales
- **Feedback**: Feedback básico de estructura

Los fallbacks se identifican con `source: 'fallback'` o `fallback: true` en metadata.

## Manejo de Errores

```javascript
try {
  const palette = await claudeDesignService.generateColorPalette('fantasy', 7, 'entertain');
  
  if (palette.metadata.source === 'fallback') {
    console.warn('Using fallback palette, Claude unavailable');
  }
  
} catch (error) {
  console.error('Failed to generate palette:', error);
  // Usar valores por defecto
}
```

## Integración con Componentes React

```javascript
import React, { useState, useEffect } from 'react';
import claudeDesignService from '../services/ClaudeDesignService';

function MyComponent() {
  const [palette, setPalette] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPalette() {
      try {
        const result = await claudeDesignService.generateColorPalette(
          'fantasy', 7, 'entertain'
        );
        setPalette(result);
      } catch (error) {
        console.error('Failed to load palette:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadPalette();
  }, []);

  if (loading) return <div>Loading design...</div>;

  return (
    <div style={{ 
      backgroundColor: palette?.background,
      color: palette?.text 
    }}>
      <button style={{ backgroundColor: palette?.primary }}>
        Click me
      </button>
    </div>
  );
}
```

## Configuración

El servicio se conecta automáticamente al backend en `/api/v1/design/claude`.

Para que funcione, asegúrate de:
1. ✅ Backend corriendo en puerto 3001
2. ✅ AWS credentials configuradas en admin panel
3. ✅ Environment set to "staging" o "production"
4. ✅ AWS services enabled

Verifica el estado:
```javascript
const status = await claudeDesignService.checkStatus();
console.log('Available:', status.available);
console.log('Environment:', status.environment);
```

## Performance

- **Cache**: Reduce llamadas repetidas a Claude
- **Rate Limiting**: Previene sobrecarga del servicio
- **Fallbacks**: Respuesta instantánea cuando Claude no disponible
- **Lazy Loading**: Importa solo cuando se necesita

## Seguridad

- ✅ Sanitización de SVG para prevenir XSS
- ✅ Validación de respuestas JSON
- ✅ No expone API keys (todo via backend proxy)
- ✅ Rate limiting para prevenir abuso

## Costos

Cada llamada a Claude tiene un costo:
- **Input**: ~$0.00025 por 1K tokens
- **Output**: ~$0.00125 por 1K tokens

Ejemplo de costos típicos:
- Paleta de colores: ~$0.001 USD
- Prompt optimization: ~$0.002 USD
- SVG generation: ~$0.002 USD
- UI recommendations: ~$0.003 USD

El cache reduce significativamente los costos al evitar llamadas repetidas.
