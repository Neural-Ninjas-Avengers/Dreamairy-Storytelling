# Claude Design Enhancement System - Design Document

## Overview

The Claude Design Enhancement System integrates Claude 3 Haiku as an intelligent design assistant to elevate DreamAIry's visual experience. The system focuses on frontend improvements, dynamic design generation, and user experience optimization while keeping the existing backend architecture intact. Claude will act as a design consultant, generating color palettes, optimizing illustration prompts, creating SVG assets, and providing real-time design recommendations.

## Architecture

### Core Components

1. **Claude Design Service (Frontend)**
   - Browser-based Claude API integration
   - Design request orchestration
   - Response parsing and validation
   - Caching layer for design assets

2. **Dynamic Theme Engine (Frontend)**
   - Real-time color palette application
   - CSS variable management
   - Age-adaptive styling
   - Theme persistence

3. **Illustration Prompt Optimizer (Frontend Service)**
   - Story context analysis
   - Prompt enhancement for AWS Titan
   - Style consistency tracking
   - Fallback prompt generation

4. **SVG Asset Generator (Frontend)**
   - Claude-powered SVG creation
   - Asset validation and optimization
   - Dynamic icon generation
   - Decorative element library

5. **Design Studio Admin Panel (Frontend)**
   - Visual design configuration
   - Real-time preview system
   - Claude chat interface
   - Design export/import

## Components and Interfaces

### 1. Claude Design Service

```javascript
// frontend/src/services/ClaudeDesignService.js

class ClaudeDesignService {
  constructor() {
    this.apiEndpoint = '/api/v1/design/claude';
    this.cache = new Map();
    this.rateLimiter = new RateLimiter(10, 60000); // 10 requests per minute
  }

  /**
   * Generate age-appropriate color palette
   */
  async generateColorPalette(theme, age, emotionalGoal) {
    const cacheKey = `palette_${theme}_${age}_${emotionalGoal}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const prompt = this._buildPalettePrompt(theme, age, emotionalGoal);
    const response = await this._callClaude(prompt);
    const palette = this._parsePaletteResponse(response);
    
    this.cache.set(cacheKey, palette);
    return palette;
  }

  /**
   * Optimize illustration prompt for AWS Titan
   */
  async optimizeIllustrationPrompt(storySegment, avatarDescription, previousPrompts = []) {
    const prompt = this._buildPromptOptimizationRequest(
      storySegment,
      avatarDescription,
      previousPrompts
    );
    
    const response = await this._callClaude(prompt);
    return this._parseOptimizedPrompt(response);
  }

  /**
   * Generate SVG asset
   */
  async generateSVGAsset(description, style, colorPalette) {
    const prompt = this._buildSVGGenerationPrompt(description, style, colorPalette);
    const response = await this._callClaude(prompt);
    const svg = this._extractAndValidateSVG(response);
    
    return svg;
  }

  /**
   * Get UI component recommendations
   */
  async getUIRecommendations(componentType, context) {
    const prompt = this._buildUIRecommendationPrompt(componentType, context);
    const response = await this._callClaude(prompt);
    
    return this._parseUIRecommendations(response);
  }

  /**
   * Request design feedback
   */
  async getDesignFeedback(componentCode, designContext) {
    const prompt = this._buildDesignFeedbackPrompt(componentCode, designContext);
    const response = await this._callClaude(prompt);
    
    return this._parseDesignFeedback(response);
  }

  // Private methods
  async _callClaude(prompt) {
    await this.rateLimiter.waitForToken();
    
    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'anthropic.claude-3-haiku-20240307-v1:0',
          prompt: prompt,
          max_tokens: 2000,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`Claude API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Claude API call failed:', error);
      return this._getFallbackResponse(prompt);
    }
  }

  _buildPalettePrompt(theme, age, emotionalGoal) {
    return `You are a professional UI/UX designer specializing in children's applications.

Generate a cohesive color palette for a children's storytelling app with these parameters:
- Theme: ${theme}
- Child's age: ${age} years
- Emotional goal: ${emotionalGoal}

Requirements:
1. All colors must meet WCAG AA contrast standards
2. Age ${age} requires ${this._getAgeColorGuidance(age)}
3. Theme "${theme}" should influence the palette
4. Include: primary, secondary, accent, background, text colors
5. Provide hex codes and usage recommendations

Return ONLY a JSON object in this exact format:
{
  "primary": "#hexcode",
  "secondary": "#hexcode",
  "accent": "#hexcode",
  "background": "#hexcode",
  "text": "#hexcode",
  "gradient": ["#hex1", "#hex2", "#hex3"],
  "usage": {
    "primary": "description",
    "secondary": "description",
    "accent": "description"
  }
}`;
  }

  _buildPromptOptimizationRequest(storySegment, avatarDescription, previousPrompts) {
    return `You are an expert at creating prompts for AI image generation (AWS Titan).

Story segment: "${storySegment}"
Avatar description: "${avatarDescription}"
Previous prompts: ${JSON.stringify(previousPrompts)}

Create an optimized prompt for AWS Titan Image Generator that:
1. Maintains visual consistency with previous illustrations
2. Is child-safe and age-appropriate
3. Includes the avatar character naturally in the scene
4. Specifies art style (watercolor, cartoon, storybook, etc.)
5. Describes composition, lighting, and mood
6. Avoids any content that might trigger AWS filters

Return ONLY a JSON object:
{
  "prompt": "detailed prompt text",
  "negative_prompt": "things to avoid",
  "style": "art style name",
  "fallback_prompts": ["alternative 1", "alternative 2"]
}`;
  }

  _buildSVGGenerationPrompt(description, style, colorPalette) {
    return `You are an expert SVG designer.

Create an SVG graphic with these specifications:
- Description: ${description}
- Style: ${style}
- Color palette: ${JSON.stringify(colorPalette)}

Requirements:
1. Valid, clean SVG code
2. Viewbox: 0 0 100 100
3. Use colors from the provided palette
4. Simple, recognizable shapes
5. Optimized for performance
6. No external dependencies

Return ONLY the SVG code wrapped in a JSON object:
{
  "svg": "<svg>...</svg>",
  "description": "what the SVG represents"
}`;
  }

  _getAgeColorGuidance(age) {
    if (age <= 5) return 'bright primary colors with high contrast';
    if (age <= 8) return 'balanced vibrant colors with medium contrast';
    return 'sophisticated nuanced colors with subtle gradients';
  }
}

export default new ClaudeDesignService();
```

### 2. Dynamic Theme Engine

```javascript
// frontend/src/services/DynamicThemeEngine.js

class DynamicThemeEngine {
  constructor() {
    this.currentTheme = null;
    this.themeHistory = [];
  }

  /**
   * Apply color palette to the application
   */
  applyPalette(palette, age) {
    const root = document.documentElement;
    
    // Set CSS variables
    root.style.setProperty('--color-primary', palette.primary);
    root.style.setProperty('--color-secondary', palette.secondary);
    root.style.setProperty('--color-accent', palette.accent);
    root.style.setProperty('--color-background', palette.background);
    root.style.setProperty('--color-text', palette.text);
    
    // Set gradient
    if (palette.gradient && palette.gradient.length >= 2) {
      const gradientCSS = `linear-gradient(135deg, ${palette.gradient.join(', ')})`;
      root.style.setProperty('--gradient-primary', gradientCSS);
    }
    
    // Apply age-specific adjustments
    this._applyAgeStyles(age);
    
    // Store theme
    this.currentTheme = { palette, age, timestamp: Date.now() };
    this.themeHistory.push(this.currentTheme);
    
    // Persist to localStorage
    localStorage.setItem('dreamairy_theme', JSON.stringify(this.currentTheme));
  }

  /**
   * Apply age-appropriate styling adjustments
   */
  _applyAgeStyles(age) {
    const root = document.documentElement;
    
    if (age <= 5) {
      root.style.setProperty('--font-size-base', '18px');
      root.style.setProperty('--button-size', '60px');
      root.style.setProperty('--border-radius', '25px');
      root.style.setProperty('--animation-speed', '0.5s');
    } else if (age <= 8) {
      root.style.setProperty('--font-size-base', '16px');
      root.style.setProperty('--button-size', '50px');
      root.style.setProperty('--border-radius', '20px');
      root.style.setProperty('--animation-speed', '0.3s');
    } else {
      root.style.setProperty('--font-size-base', '14px');
      root.style.setProperty('--button-size', '44px');
      root.style.setProperty('--border-radius', '15px');
      root.style.setProperty('--animation-speed', '0.2s');
    }
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    if (!this.currentTheme) {
      const stored = localStorage.getItem('dreamairy_theme');
      if (stored) {
        this.currentTheme = JSON.parse(stored);
      }
    }
    return this.currentTheme;
  }

  /**
   * Reset to default theme
   */
  resetTheme() {
    const root = document.documentElement;
    root.removeAttribute('style');
    this.currentTheme = null;
    localStorage.removeItem('dreamairy_theme');
  }
}

export default new DynamicThemeEngine();
```

### 3. Illustration Style Tracker

```javascript
// frontend/src/services/IllustrationStyleTracker.js

class IllustrationStyleTracker {
  constructor() {
    this.styleGuide = null;
    this.promptHistory = [];
  }

  /**
   * Initialize style guide for a story session
   */
  async initializeStyleGuide(theme, age, avatarDescription) {
    const claudeService = require('./ClaudeDesignService').default;
    
    const prompt = `Create a consistent illustration style guide for a children's story.

Parameters:
- Theme: ${theme}
- Age: ${age}
- Avatar: ${avatarDescription}

Define:
1. Art style (watercolor, cartoon, digital, etc.)
2. Color palette approach
3. Character design principles
4. Environment/background style
5. Lighting and mood
6. Composition rules

Return JSON:
{
  "artStyle": "style name",
  "colorApproach": "description",
  "characterDesign": "guidelines",
  "environmentStyle": "description",
  "lighting": "description",
  "composition": "rules"
}`;

    const response = await claudeService._callClaude(prompt);
    this.styleGuide = JSON.parse(response.content);
    
    return this.styleGuide;
  }

  /**
   * Get style-consistent prompt
   */
  getStyleConsistentPrompt(basePrompt) {
    if (!this.styleGuide) {
      return basePrompt;
    }

    return `${basePrompt}

Style guide:
- Art style: ${this.styleGuide.artStyle}
- Color approach: ${this.styleGuide.colorApproach}
- Lighting: ${this.styleGuide.lighting}
- Composition: ${this.styleGuide.composition}`;
  }

  /**
   * Track prompt for consistency
   */
  trackPrompt(prompt, imageUrl) {
    this.promptHistory.push({
      prompt,
      imageUrl,
      timestamp: Date.now()
    });
  }

  /**
   * Get previous prompts for context
   */
  getPreviousPrompts(count = 3) {
    return this.promptHistory.slice(-count);
  }
}

export default new IllustrationStyleTracker();
```

## Data Models

### Color Palette Structure

```typescript
interface ColorPalette {
  primary: string;        // Hex color
  secondary: string;      // Hex color
  accent: string;         // Hex color
  background: string;     // Hex color
  text: string;           // Hex color
  gradient: string[];     // Array of hex colors
  usage: {
    primary: string;      // Usage description
    secondary: string;
    accent: string;
  };
  metadata: {
    theme: string;
    age: number;
    emotionalGoal: string;
    generatedAt: string;
  };
}
```

### Optimized Prompt Structure

```typescript
interface OptimizedPrompt {
  prompt: string;              // Main prompt for AWS Titan
  negative_prompt: string;     // Things to avoid
  style: string;               // Art style identifier
  fallback_prompts: string[];  // Alternative prompts if main fails
  metadata: {
    storyContext: string;
    avatarIncluded: boolean;
    consistencyScore: number;
  };
}
```

### SVG Asset Structure

```typescript
interface SVGAsset {
  svg: string;           // SVG code
  description: string;   // What it represents
  category: string;      // icon | decoration | illustration
  colorPalette: string[]; // Colors used
  size: {
    width: number;
    height: number;
  };
  metadata: {
    generatedAt: string;
    claudeGenerated: boolean;
  };
}
```

### Design Recommendation Structure

```typescript
interface DesignRecommendation {
  component: string;
  recommendations: {
    layout: string[];
    colors: string[];
    typography: string[];
    accessibility: string[];
    responsive: string[];
  };
  codeExamples: {
    html?: string;
    css?: string;
    tailwind?: string;
  };
  priority: 'high' | 'medium' | 'low';
}
```

## Error Handling

### Claude API Failures

```javascript
function handleClaudeError(error) {
  console.error('Claude API error:', error);
  
  // Use fallback design system
  return {
    useFallback: true,
    fallbackType: 'local_templates',
    message: 'Using local design templates'
  };
}
```

### Invalid Response Parsing

```javascript
function parseClaudeResponse(response, expectedFormat) {
  try {
    const parsed = JSON.parse(response.content);
    
    // Validate structure
    if (!validateResponseStructure(parsed, expectedFormat)) {
      throw new Error('Invalid response structure');
    }
    
    return parsed;
  } catch (error) {
    console.error('Failed to parse Claude response:', error);
    return getDefaultResponse(expectedFormat);
  }
}
```

### Rate Limiting

```javascript
class RateLimiter {
  constructor(maxRequests, timeWindow) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;
    this.requests = [];
  }

  async waitForToken() {
    const now = Date.now();
    this.requests = this.requests.filter(t => now - t < this.timeWindow);
    
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.timeWindow - (now - oldestRequest);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.requests.push(now);
  }
}
```

## Testing Strategy

### 1. Claude Integration Testing

```javascript
describe('ClaudeDesignService', () => {
  test('generates valid color palette', async () => {
    const palette = await claudeService.generateColorPalette('fantasy', 7, 'entertain');
    
    expect(palette).toHaveProperty('primary');
    expect(palette).toHaveProperty('secondary');
    expect(palette.primary).toMatch(/^#[0-9A-F]{6}$/i);
    expect(palette.gradient).toBeInstanceOf(Array);
  });

  test('handles API failures gracefully', async () => {
    // Mock API failure
    jest.spyOn(global, 'fetch').mockRejectedValue(new Error('Network error'));
    
    const palette = await claudeService.generateColorPalette('adventure', 5, 'calm');
    
    expect(palette).toBeDefined();
    expect(palette.fallback).toBe(true);
  });
});
```

### 2. Theme Engine Testing

```javascript
describe('DynamicThemeEngine', () => {
  test('applies palette to CSS variables', () => {
    const palette = {
      primary: '#FF6B6B',
      secondary: '#4ECDC4',
      accent: '#FFE66D',
      background: '#FFFFFF',
      text: '#2C3E50'
    };
    
    themeEngine.applyPalette(palette, 6);
    
    const root = document.documentElement;
    expect(root.style.getPropertyValue('--color-primary')).toBe('#FF6B6B');
  });

  test('applies age-appropriate styles', () => {
    themeEngine._applyAgeStyles(4);
    
    const root = document.documentElement;
    expect(root.style.getPropertyValue('--font-size-base')).toBe('18px');
    expect(root.style.getPropertyValue('--button-size')).toBe('60px');
  });
});
```

### 3. Prompt Optimization Testing

```javascript
describe('Illustration Prompt Optimization', () => {
  test('maintains style consistency', async () => {
    const styleTracker = new IllustrationStyleTracker();
    await styleTracker.initializeStyleGuide('fantasy', 8, 'young wizard');
    
    const prompt1 = await claudeService.optimizeIllustrationPrompt(
      'The wizard enters a magical forest',
      'young wizard with blue robes',
      []
    );
    
    const prompt2 = await claudeService.optimizeIllustrationPrompt(
      'The wizard meets a friendly dragon',
      'young wizard with blue robes',
      [prompt1.prompt]
    );
    
    expect(prompt2.style).toBe(prompt1.style);
    expect(prompt2.prompt).toContain('blue robes');
  });
});
```

## Performance Optimization

### Caching Strategy

```javascript
class DesignCache {
  constructor() {
    this.cache = new Map();
    this.maxSize = 100;
    this.ttl = 3600000; // 1 hour
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  get(key) {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
}
```

### Lazy Loading

```javascript
// Load Claude service only when needed
const loadClaudeService = async () => {
  if (!window.claudeService) {
    const module = await import('./services/ClaudeDesignService');
    window.claudeService = module.default;
  }
  return window.claudeService;
};
```

## Security Considerations

### API Key Management

- Claude API calls go through backend proxy
- No API keys exposed in frontend code
- Rate limiting on backend to prevent abuse

### Content Validation

- All Claude responses validated before use
- SVG code sanitized to prevent XSS
- Color codes validated against hex format

### Privacy

- No user data sent to Claude except design parameters
- Design preferences stored locally only
- No tracking of design choices

## Accessibility

### WCAG Compliance

- All generated color palettes meet WCAG AA standards
- Contrast ratios validated programmatically
- Alternative text for all generated SVGs

### Reduced Motion

```javascript
function applyReducedMotion() {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  if (prefersReducedMotion) {
    document.documentElement.style.setProperty('--animation-speed', '0.01s');
  }
}
```

## Implementation Phases

### Phase 1: Core Claude Integration (Week 1-2)
- Set up Claude API proxy in backend
- Implement ClaudeDesignService
- Create basic prompt templates
- Add error handling and fallbacks

### Phase 2: Dynamic Theming (Week 2-3)
- Implement DynamicThemeEngine
- Create color palette generation
- Add CSS variable management
- Test age-adaptive styling

### Phase 3: Prompt Optimization (Week 3-4)
- Build IllustrationStyleTracker
- Integrate with existing story generation
- Test style consistency
- Add fallback prompts

### Phase 4: SVG Generation (Week 4-5)
- Implement SVG asset generator
- Create validation and sanitization
- Build asset library
- Add to UI components

### Phase 5: Design Studio (Week 5-6)
- Create admin panel interface
- Add real-time preview
- Implement Claude chat
- Add export/import features

### Phase 6: Testing & Optimization (Week 6-7)
- Comprehensive testing
- Performance optimization
- User feedback integration
- Documentation
