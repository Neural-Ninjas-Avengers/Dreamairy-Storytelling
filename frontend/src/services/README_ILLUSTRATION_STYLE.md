# IllustrationStyleTracker

Servicio para mantener consistencia visual en las ilustraciones de historias a lo largo de una sesión.

## Características

- ✅ Generación de guías de estilo con Claude
- ✅ Tracking de prompts e imágenes generadas
- ✅ Aplicación automática de estilo consistente
- ✅ Historial de prompts (máximo 20)
- ✅ Puntuación de consistencia
- ✅ Export/Import de sesiones
- ✅ Fallbacks por tema

## Uso Básico

```javascript
import illustrationStyleTracker from './services/IllustrationStyleTracker';

// 1. Inicializar guía de estilo al comenzar historia
const styleGuide = await illustrationStyleTracker.initializeStyleGuide(
  'fantasy',              // theme
  7,                      // age
  'young wizard in blue robes'  // avatarDescription
);

// 2. Generar ilustraciones con estilo consistente
const basePrompt = 'The wizard enters a magical forest';
const styledPrompt = illustrationStyleTracker.getStyleConsistentPrompt(basePrompt);

// 3. Generar imagen con AWS Titan
const imageUrl = await generateImageWithTitan(styledPrompt);

// 4. Trackear prompt e imagen
illustrationStyleTracker.trackPrompt(styledPrompt, imageUrl);
```

## Inicializar Guía de Estilo

```javascript
// Inicializar con Claude (recomendado)
const styleGuide = await illustrationStyleTracker.initializeStyleGuide(
  'fantasy',  // theme: animals, fantasy, adventure, friendship
  7,          // age: 3-12
  'young wizard with blue robes and a magical staff'  // avatarDescription
);

console.log('Style guide:', styleGuide);
```

**Respuesta:**
```javascript
{
  artStyle: "Digital fantasy illustration with magical elements",
  colorApproach: "Vibrant, magical colors with sparkles and glows",
  characterDesign: "Whimsical wizard character with blue robes, maintaining consistent features",
  environmentStyle: "Enchanted landscapes with castles, clouds, and mystical elements",
  lighting: "Magical, ethereal lighting with glowing effects",
  composition: "Dynamic angles with sense of wonder and scale",
  technicalNotes: "Add magical particles and light effects",
  theme: "fantasy",
  age: 7,
  avatarDescription: "young wizard with blue robes and a magical staff",
  createdAt: "2024-01-01T12:00:00Z",
  source: "claude"  // or "fallback"
}
```

## Aplicar Estilo Consistente

```javascript
// Prompt base del segmento de historia
const basePrompt = "The wizard discovers a hidden cave with glowing crystals";

// Aplicar guía de estilo
const styledPrompt = illustrationStyleTracker.getStyleConsistentPrompt(basePrompt);

console.log(styledPrompt);
// "The wizard discovers a hidden cave with glowing crystals
//
// Style Guide:
// - Art style: Digital fantasy illustration with magical elements
// - Color approach: Vibrant, magical colors with sparkles and glows
// - Character design: Whimsical wizard character with blue robes...
// - Environment: Enchanted landscapes with castles, clouds...
// - Lighting: Magical, ethereal lighting with glowing effects
// - Composition: Dynamic angles with sense of wonder and scale
//
// Maintain consistency with previous illustrations in this session."
```

## Trackear Prompts e Imágenes

```javascript
// Después de generar cada imagen
illustrationStyleTracker.trackPrompt(
  styledPrompt,           // prompt usado
  imageUrl,               // URL de imagen generada
  {                       // metadata opcional
    segmentNumber: 3,
    storyTheme: 'fantasy',
    generationTime: 2.5
  }
);

// Ver historial
const history = illustrationStyleTracker.getPromptHistory();
console.log(`Tracked ${history.length} illustrations`);
```

## Obtener Prompts Anteriores

```javascript
// Obtener últimos 3 prompts para contexto
const previousPrompts = illustrationStyleTracker.getPreviousPrompts(3);

previousPrompts.forEach((entry, index) => {
  console.log(`Prompt ${index + 1}:`, entry.prompt);
  console.log(`Image:`, entry.imageUrl);
  console.log(`Time:`, entry.timestamp);
});

// Solo los textos de prompts
const promptTexts = illustrationStyleTracker.getPreviousPromptTexts(3);
console.log('Previous prompts:', promptTexts);
```

## Integración con ClaudeDesignService

```javascript
import claudeDesignService from './services/ClaudeDesignService';
import illustrationStyleTracker from './services/IllustrationStyleTracker';

// 1. Inicializar estilo
await illustrationStyleTracker.initializeStyleGuide('fantasy', 7, 'young wizard');

// 2. Generar prompt optimizado con Claude
const storySegment = "The wizard enters a magical forest";
const avatarDesc = "young wizard with blue robes";
const previousPrompts = illustrationStyleTracker.getPreviousPromptTexts(2);

const optimizedPrompt = await claudeDesignService.optimizeIllustrationPrompt(
  storySegment,
  avatarDesc,
  previousPrompts
);

// 3. Aplicar guía de estilo
const finalPrompt = illustrationStyleTracker.getStyleConsistentPrompt(
  optimizedPrompt.prompt
);

// 4. Generar imagen
const imageUrl = await generateImageWithTitan(finalPrompt);

// 5. Trackear
illustrationStyleTracker.trackPrompt(finalPrompt, imageUrl);
```

## Gestión de Sesiones

### Obtener Guía de Estilo Actual
```javascript
const styleGuide = illustrationStyleTracker.getStyleGuide();
if (styleGuide) {
  console.log('Current style:', styleGuide.artStyle);
  console.log('Theme:', styleGuide.theme);
}
```

### Limpiar Sesión
```javascript
// Al terminar una historia o comenzar una nueva
illustrationStyleTracker.clearSession();
console.log('Session cleared, ready for new story');
```

### Export/Import de Sesiones
```javascript
// Exportar sesión actual
const sessionData = illustrationStyleTracker.exportSession();
const sessionJson = JSON.stringify(sessionData);

// Guardar en localStorage
localStorage.setItem('story_session', sessionJson);

// Importar sesión guardada
const savedSession = localStorage.getItem('story_session');
if (savedSession) {
  illustrationStyleTracker.importSession(JSON.parse(savedSession));
  console.log('Session restored');
}
```

## Métricas de Consistencia

### Puntuación de Consistencia
```javascript
const score = illustrationStyleTracker.getConsistencyScore();
console.log(`Consistency score: ${(score * 100).toFixed(0)}%`);

// Score calculation:
// - Base: 0.5 (has style guide)
// - +0.2 if 3+ prompts tracked
// - +0.1 if 5+ prompts tracked
// - +0.2 if using Claude-generated style guide
// Maximum: 1.0 (100%)
```

### Resumen de Estilo
```javascript
const summary = illustrationStyleTracker.getStyleSummary();
console.log(summary);
// "Style: Digital fantasy illustration with magical elements
//  Theme: fantasy
//  Age: 7 years
//  Prompts tracked: 5
//  Consistency score: 90%
//  Source: claude"
```

## Guías de Estilo por Tema

### Animals (Animales)
```javascript
{
  artStyle: "Watercolor storybook illustration",
  colorApproach: "Warm, natural colors with soft gradients",
  characterDesign: "Cute, friendly animals with expressive eyes",
  environmentStyle: "Lush forest and nature scenes",
  lighting: "Soft, natural daylight with warm tones",
  composition: "Medium shots focusing on character interactions"
}
```

### Fantasy (Fantasía)
```javascript
{
  artStyle: "Digital fantasy illustration with magical elements",
  colorApproach: "Vibrant, magical colors with sparkles and glows",
  characterDesign: "Whimsical characters with magical accessories",
  environmentStyle: "Enchanted landscapes with castles and mystical elements",
  lighting: "Magical, ethereal lighting with glowing effects",
  composition: "Dynamic angles with sense of wonder and scale"
}
```

### Adventure (Aventura)
```javascript
{
  artStyle: "Bold cartoon adventure style",
  colorApproach: "Bright, energetic colors with strong contrasts",
  characterDesign: "Dynamic characters in action poses with adventurer gear",
  environmentStyle: "Exciting locations with sense of exploration",
  lighting: "Dramatic lighting emphasizing action and movement",
  composition: "Wide shots showing environment and adventure scale"
}
```

### Friendship (Amistad)
```javascript
{
  artStyle: "Warm, inviting storybook style",
  colorApproach: "Friendly, harmonious colors that feel welcoming",
  characterDesign: "Relatable characters with warm expressions",
  environmentStyle: "Cozy, familiar settings like homes and parks",
  lighting: "Warm, comforting light creating safe atmosphere",
  composition: "Close-ups emphasizing character connections"
}
```

## Adaptación por Edad

### Edad 3-5 años
- Formas simples y contornos claros
- Colores primarios brillantes con alto contraste
- Personajes grandes y expresivos
- Fondos mínimos para evitar distracción
- Atmósfera alegre y reconfortante

### Edad 6-8 años
- Nivel de detalle balanceado
- Paleta de colores vibrante y variada
- Personajes con personalidad
- Fondos atractivos con elementos de historia
- Sentido de aventura y maravilla

### Edad 9-12 años
- Detalle y composición sofisticados
- Paleta de colores matizada con profundidad
- Diseños de personajes complejos
- Ambientes ricos y atmosféricos
- Iluminación y mood dramáticos

## Integración con React

### Hook Personalizado
```javascript
import { useState, useEffect } from 'react';
import illustrationStyleTracker from '../services/IllustrationStyleTracker';

function useIllustrationStyle(theme, age, avatarDescription) {
  const [styleGuide, setStyleGuide] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initStyle() {
      try {
        const guide = await illustrationStyleTracker.initializeStyleGuide(
          theme, age, avatarDescription
        );
        setStyleGuide(guide);
      } catch (error) {
        console.error('Failed to initialize style:', error);
      } finally {
        setLoading(false);
      }
    }
    
    initStyle();
    
    // Cleanup on unmount
    return () => {
      illustrationStyleTracker.clearSession();
    };
  }, [theme, age, avatarDescription]);

  return { styleGuide, loading };
}

// Uso en componente
function StoryComponent() {
  const { styleGuide, loading } = useIllustrationStyle('fantasy', 7, 'young wizard');

  if (loading) return <div>Initializing style...</div>;

  return (
    <div>
      <h2>Story Style: {styleGuide.artStyle}</h2>
      {/* Generar ilustraciones con estilo consistente */}
    </div>
  );
}
```

### Context Provider
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import illustrationStyleTracker from '../services/IllustrationStyleTracker';

const StyleContext = createContext();

export function StyleProvider({ children, theme, age, avatarDescription }) {
  const [styleGuide, setStyleGuide] = useState(null);
  const [promptHistory, setPromptHistory] = useState([]);

  useEffect(() => {
    async function init() {
      const guide = await illustrationStyleTracker.initializeStyleGuide(
        theme, age, avatarDescription
      );
      setStyleGuide(guide);
    }
    init();
  }, [theme, age, avatarDescription]);

  const trackPrompt = (prompt, imageUrl, metadata) => {
    illustrationStyleTracker.trackPrompt(prompt, imageUrl, metadata);
    setPromptHistory(illustrationStyleTracker.getPromptHistory());
  };

  const getStyledPrompt = (basePrompt) => {
    return illustrationStyleTracker.getStyleConsistentPrompt(basePrompt);
  };

  return (
    <StyleContext.Provider value={{ 
      styleGuide, 
      promptHistory, 
      trackPrompt, 
      getStyledPrompt 
    }}>
      {children}
    </StyleContext.Provider>
  );
}

export function useStyle() {
  return useContext(StyleContext);
}

// Uso
function App() {
  return (
    <StyleProvider theme="fantasy" age={7} avatarDescription="young wizard">
      <StoryComponent />
    </StyleProvider>
  );
}

function StoryComponent() {
  const { styleGuide, getStyledPrompt, trackPrompt } = useStyle();
  
  const generateIllustration = async (storySegment) => {
    const styledPrompt = getStyledPrompt(storySegment);
    const imageUrl = await generateImage(styledPrompt);
    trackPrompt(styledPrompt, imageUrl);
  };
  
  return <div>...</div>;
}
```

## Mejores Prácticas

### 1. Inicializar al Comenzar Historia
```javascript
// Al inicio de cada nueva historia
useEffect(() => {
  async function startStory() {
    await illustrationStyleTracker.initializeStyleGuide(
      theme, age, avatarDescription
    );
  }
  startStory();
}, [storyId]); // Reiniciar cuando cambia la historia
```

### 2. Siempre Trackear Prompts
```javascript
// Después de cada generación exitosa
if (imageUrl) {
  illustrationStyleTracker.trackPrompt(prompt, imageUrl, {
    segmentNumber: currentSegment,
    timestamp: Date.now()
  });
}
```

### 3. Usar Prompts Anteriores para Contexto
```javascript
// Al generar nuevas ilustraciones
const previousPrompts = illustrationStyleTracker.getPreviousPromptTexts(2);
const optimizedPrompt = await claudeDesignService.optimizeIllustrationPrompt(
  storySegment,
  avatarDescription,
  previousPrompts  // Proporciona contexto para consistencia
);
```

### 4. Limpiar al Terminar
```javascript
// Al finalizar historia o cambiar de sesión
useEffect(() => {
  return () => {
    illustrationStyleTracker.clearSession();
  };
}, []);
```

### 5. Guardar Sesiones Importantes
```javascript
// Guardar sesión para continuar después
const saveSession = () => {
  const sessionData = illustrationStyleTracker.exportSession();
  localStorage.setItem(`story_${storyId}`, JSON.stringify(sessionData));
};

// Restaurar sesión
const restoreSession = (storyId) => {
  const saved = localStorage.getItem(`story_${storyId}`);
  if (saved) {
    illustrationStyleTracker.importSession(JSON.parse(saved));
  }
};
```

## Performance

- **Inicialización**: ~2-3 segundos (llamada a Claude)
- **Aplicar estilo**: <1ms (concatenación de strings)
- **Trackear prompt**: <1ms (push a array)
- **Memoria**: ~100KB por sesión (20 prompts + imágenes URLs)

## Limitaciones

- **Historial máximo**: 20 prompts (configurable)
- **Sesión única**: Solo una sesión activa a la vez
- **Sin persistencia automática**: Debes exportar/importar manualmente
- **Dependencia de Claude**: Fallback disponible si Claude falla

## Troubleshooting

### Estilo Inconsistente
```javascript
// Verificar que la guía de estilo esté inicializada
const styleGuide = illustrationStyleTracker.getStyleGuide();
if (!styleGuide) {
  console.error('Style guide not initialized!');
  await illustrationStyleTracker.initializeStyleGuide(theme, age, avatar);
}

// Verificar puntuación de consistencia
const score = illustrationStyleTracker.getConsistencyScore();
if (score < 0.7) {
  console.warn('Low consistency score:', score);
}
```

### Prompts No Se Trackean
```javascript
// Asegurarse de llamar trackPrompt después de cada generación
illustrationStyleTracker.trackPrompt(prompt, imageUrl);

// Verificar historial
const history = illustrationStyleTracker.getPromptHistory();
console.log('Tracked prompts:', history.length);
```

### Claude No Disponible
```javascript
// El servicio usa fallbacks automáticamente
const styleGuide = await illustrationStyleTracker.initializeStyleGuide(
  theme, age, avatar
);

if (styleGuide.source === 'fallback') {
  console.warn('Using fallback style guide (Claude unavailable)');
}
```
