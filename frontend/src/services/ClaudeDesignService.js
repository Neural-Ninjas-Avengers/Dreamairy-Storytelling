/**
 * ClaudeDesignService
 * 
 * Service for interacting with Claude 3 Haiku for design assistance.
 * Provides methods for color palette generation, prompt optimization,
 * SVG asset creation, and UI recommendations.
 */

class RateLimiter {
  constructor(maxRequests, timeWindow) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow; // in milliseconds
    this.requests = [];
  }

  async waitForToken() {
    const now = Date.now();
    
    // Remove old requests outside the time window
    this.requests = this.requests.filter(timestamp => now - timestamp < this.timeWindow);
    
    // If at limit, wait for oldest request to expire
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.timeWindow - (now - oldestRequest);
      
      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
        // Recursively check again after waiting
        return this.waitForToken();
      }
    }
    
    // Add current request timestamp
    this.requests.push(now);
  }
}

class ClaudeDesignService {
  constructor() {
    this.apiEndpoint = '/api/v1/design/claude';
    this.statusEndpoint = '/api/v1/design/claude/status';
    this.cache = new Map();
    this.rateLimiter = new RateLimiter(10, 60000); // 10 requests per minute
    this.sessionId = this._generateSessionId();
  }

  /**
   * Generate a unique session ID for rate limiting
   */
  _generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Call Claude API with rate limiting and error handling
   */
  async _callClaude(prompt, maxTokens = 2000, temperature = 0.7) {
    // Wait for rate limit token
    await this.rateLimiter.waitForToken();
    
    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'anthropic.claude-3-haiku-20240307-v1:0',
          prompt: prompt,
          max_tokens: maxTokens,
          temperature: temperature,
          session_id: this.sessionId
        })
      });

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Rate limit exceeded. Please wait a moment.');
        }
        throw new Error(`Claude API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Claude API call failed');
      }

      return {
        success: true,
        content: data.content,
        timestamp: data.timestamp
      };

    } catch (error) {
      console.error('Claude API call failed:', error);
      return this._getFallbackResponse(prompt, error);
    }
  }

  /**
   * Get fallback response when Claude is unavailable
   */
  _getFallbackResponse(prompt, error) {
    console.warn('Using fallback response for prompt:', prompt.substring(0, 50) + '...');
    
    return {
      success: false,
      fallback: true,
      error: error.message,
      content: null
    };
  }

  /**
   * Check if Claude service is available
   */
  async checkStatus() {
    try {
      const response = await fetch(this.statusEndpoint);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to check Claude status:', error);
      return {
        available: false,
        error: error.message
      };
    }
  }

  /**
   * Generate cache key from parameters
   */
  _getCacheKey(prefix, ...params) {
    return `${prefix}_${params.join('_')}`;
  }

  /**
   * Get item from cache
   */
  _getFromCache(key) {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    // Check if cache item is still valid (1 hour TTL)
    const now = Date.now();
    if (now - item.timestamp > 3600000) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }

  /**
   * Store item in cache
   */
  _storeInCache(key, value) {
    // Limit cache size to 100 items
    if (this.cache.size >= 100) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      value: value,
      timestamp: Date.now()
    });
  }

  /**
   * Clear all cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Get age-specific color guidance
   */
  _getAgeColorGuidance(age) {
    if (age <= 5) {
      return 'bright primary colors with high contrast';
    } else if (age <= 8) {
      return 'balanced vibrant colors with medium contrast';
    } else {
      return 'sophisticated nuanced colors with subtle gradients';
    }
  }

  /**
   * Build prompt for color palette generation
   */
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

Return ONLY a JSON object in this exact format (no markdown, no code blocks):
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

  /**
   * Parse color palette response from Claude
   */
  _parsePaletteResponse(response) {
    try {
      // Try to extract JSON from response
      const content = response.content;
      
      // Remove markdown code blocks if present
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      
      // Parse JSON
      const palette = JSON.parse(jsonStr);
      
      // Validate required fields
      const requiredFields = ['primary', 'secondary', 'accent', 'background', 'text'];
      for (const field of requiredFields) {
        if (!palette[field]) {
          throw new Error(`Missing required field: ${field}`);
        }
        
        // Validate hex color format
        if (!/^#[0-9A-F]{6}$/i.test(palette[field])) {
          throw new Error(`Invalid hex color for ${field}: ${palette[field]}`);
        }
      }
      
      return palette;
      
    } catch (error) {
      console.error('Failed to parse palette response:', error);
      throw new Error('Invalid palette response from Claude');
    }
  }

  /**
   * Generate age-appropriate color palette
   * 
   * @param {string} theme - Story theme (animals, fantasy, adventure, friendship)
   * @param {number} age - Child's age
   * @param {string} emotionalGoal - Emotional goal (entertain, calm, stimulate)
   * @returns {Promise<Object>} Color palette object
   */
  async generateColorPalette(theme, age, emotionalGoal) {
    // Check cache first
    const cacheKey = this._getCacheKey('palette', theme, age, emotionalGoal);
    const cached = this._getFromCache(cacheKey);
    
    if (cached) {
      console.log('Returning cached palette');
      return cached;
    }

    try {
      // Build prompt
      const prompt = this._buildPalettePrompt(theme, age, emotionalGoal);
      
      // Call Claude
      const response = await this._callClaude(prompt, 1000, 0.7);
      
      if (!response.success) {
        // Return fallback palette
        return this._getFallbackPalette(theme, age);
      }
      
      // Parse response
      const palette = this._parsePaletteResponse(response);
      
      // Add metadata
      palette.metadata = {
        theme: theme,
        age: age,
        emotionalGoal: emotionalGoal,
        generatedAt: new Date().toISOString(),
        source: 'claude'
      };
      
      // Cache result
      this._storeInCache(cacheKey, palette);
      
      return palette;
      
    } catch (error) {
      console.error('Error generating color palette:', error);
      return this._getFallbackPalette(theme, age);
    }
  }

  /**
   * Build prompt for illustration optimization
   */
  _buildPromptOptimizationRequest(storySegment, avatarDescription, previousPrompts = []) {
    const previousContext = previousPrompts.length > 0 
      ? `\nPrevious prompts for consistency:\n${previousPrompts.slice(-2).join('\n')}`
      : '';

    return `You are an expert at creating prompts for AI image generation (AWS Titan).

Story segment: "${storySegment}"
Avatar description: "${avatarDescription}"${previousContext}

Create an optimized prompt for AWS Titan Image Generator that:
1. Maintains visual consistency with previous illustrations
2. Is child-safe and age-appropriate
3. Includes the avatar character naturally in the scene
4. Specifies art style (watercolor, cartoon, storybook, etc.)
5. Describes composition, lighting, and mood
6. Avoids any content that might trigger AWS filters

Return ONLY a JSON object (no markdown, no code blocks):
{
  "prompt": "detailed prompt text",
  "negative_prompt": "things to avoid",
  "style": "art style name",
  "fallback_prompts": ["alternative 1", "alternative 2"]
}`;
  }

  /**
   * Parse optimized prompt response from Claude
   */
  _parseOptimizedPrompt(response) {
    try {
      const content = response.content;
      
      // Remove markdown code blocks if present
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      
      // Parse JSON
      const promptData = JSON.parse(jsonStr);
      
      // Validate required fields
      if (!promptData.prompt) {
        throw new Error('Missing required field: prompt');
      }
      
      // Ensure fallback_prompts exists
      if (!promptData.fallback_prompts) {
        promptData.fallback_prompts = [promptData.prompt];
      }
      
      return promptData;
      
    } catch (error) {
      console.error('Failed to parse prompt response:', error);
      throw new Error('Invalid prompt response from Claude');
    }
  }

  /**
   * Optimize illustration prompt for AWS Titan
   * 
   * @param {string} storySegment - Current story text
   * @param {string} avatarDescription - Description of user's avatar
   * @param {Array<string>} previousPrompts - Previous prompts for consistency
   * @returns {Promise<Object>} Optimized prompt object
   */
  async optimizeIllustrationPrompt(storySegment, avatarDescription, previousPrompts = []) {
    try {
      // Build prompt
      const prompt = this._buildPromptOptimizationRequest(
        storySegment,
        avatarDescription,
        previousPrompts
      );
      
      // Call Claude
      const response = await this._callClaude(prompt, 1500, 0.7);
      
      if (!response.success) {
        // Return fallback prompt
        return this._getFallbackIllustrationPrompt(storySegment, avatarDescription);
      }
      
      // Parse response
      const optimizedPrompt = this._parseOptimizedPrompt(response);
      
      // Add metadata
      optimizedPrompt.metadata = {
        storyContext: storySegment.substring(0, 100),
        avatarIncluded: !!avatarDescription,
        consistencyScore: previousPrompts.length > 0 ? 0.9 : 0.7,
        generatedAt: new Date().toISOString(),
        source: 'claude'
      };
      
      return optimizedPrompt;
      
    } catch (error) {
      console.error('Error optimizing illustration prompt:', error);
      return this._getFallbackIllustrationPrompt(storySegment, avatarDescription);
    }
  }

  /**
   * Get fallback illustration prompt when Claude is unavailable
   */
  _getFallbackIllustrationPrompt(storySegment, avatarDescription) {
    const basePrompt = `Children's storybook illustration, ${avatarDescription || 'friendly character'}, ${storySegment.substring(0, 100)}, colorful, magical, cartoon style, professional children's book art`;
    
    return {
      prompt: basePrompt,
      negative_prompt: 'scary, dark, violent, inappropriate, realistic, photographic',
      style: 'cartoon storybook',
      fallback_prompts: [
        basePrompt,
        `Magical children's book scene with ${avatarDescription || 'character'}, bright colors, friendly atmosphere`,
        `Whimsical cartoon illustration for children, ${avatarDescription || 'happy character'}, colorful and safe`
      ],
      metadata: {
        storyContext: storySegment.substring(0, 100),
        avatarIncluded: !!avatarDescription,
        consistencyScore: 0.5,
        generatedAt: new Date().toISOString(),
        source: 'fallback'
      }
    };
  }

  /**
   * Build prompt for SVG generation
   */
  _buildSVGGenerationPrompt(description, style, colorPalette) {
    const colors = colorPalette 
      ? `Use these colors: ${JSON.stringify(colorPalette)}`
      : 'Use bright, child-friendly colors';

    return `You are an expert SVG designer.

Create an SVG graphic with these specifications:
- Description: ${description}
- Style: ${style}
- ${colors}

Requirements:
1. Valid, clean SVG code
2. Viewbox: 0 0 100 100
3. Simple, recognizable shapes
4. Optimized for performance
5. No external dependencies
6. Child-friendly and appealing

Return ONLY a JSON object (no markdown, no code blocks):
{
  "svg": "<svg viewBox='0 0 100 100'>...</svg>",
  "description": "what the SVG represents"
}`;
  }

  /**
   * Extract and validate SVG from Claude response
   */
  _extractAndValidateSVG(response) {
    try {
      const content = response.content;
      
      // Remove markdown code blocks if present
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      
      // Parse JSON
      const svgData = JSON.parse(jsonStr);
      
      if (!svgData.svg) {
        throw new Error('Missing SVG code in response');
      }
      
      // Basic SVG validation
      if (!svgData.svg.includes('<svg') || !svgData.svg.includes('</svg>')) {
        throw new Error('Invalid SVG structure');
      }
      
      // Sanitize SVG (remove potentially dangerous elements)
      const sanitized = this._sanitizeSVG(svgData.svg);
      
      return {
        svg: sanitized,
        description: svgData.description || 'Generated SVG asset',
        valid: true
      };
      
    } catch (error) {
      console.error('Failed to extract SVG:', error);
      throw new Error('Invalid SVG response from Claude');
    }
  }

  /**
   * Sanitize SVG code to prevent XSS
   */
  _sanitizeSVG(svgCode) {
    // Remove script tags
    let sanitized = svgCode.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    
    // Remove event handlers
    sanitized = sanitized.replace(/on\w+="[^"]*"/gi, '');
    sanitized = sanitized.replace(/on\w+='[^']*'/gi, '');
    
    // Remove javascript: URLs
    sanitized = sanitized.replace(/javascript:/gi, '');
    
    return sanitized;
  }

  /**
   * Generate SVG asset
   * 
   * @param {string} description - What to generate
   * @param {string} style - Style (icon, decoration, illustration)
   * @param {Object} colorPalette - Optional color palette to use
   * @returns {Promise<Object>} SVG asset object
   */
  async generateSVGAsset(description, style, colorPalette = null) {
    try {
      // Build prompt
      const prompt = this._buildSVGGenerationPrompt(description, style, colorPalette);
      
      // Call Claude
      const response = await this._callClaude(prompt, 1500, 0.7);
      
      if (!response.success) {
        // Return fallback SVG
        return this._getFallbackSVG(description, style);
      }
      
      // Extract and validate SVG
      const svgAsset = this._extractAndValidateSVG(response);
      
      // Add metadata
      svgAsset.category = style;
      svgAsset.colorPalette = colorPalette ? Object.values(colorPalette).slice(0, 5) : [];
      svgAsset.metadata = {
        generatedAt: new Date().toISOString(),
        claudeGenerated: true,
        description: description
      };
      
      return svgAsset;
      
    } catch (error) {
      console.error('Error generating SVG asset:', error);
      return this._getFallbackSVG(description, style);
    }
  }

  /**
   * Get fallback SVG when Claude is unavailable
   */
  _getFallbackSVG(description, style) {
    // Simple fallback SVGs based on common needs
    const fallbacks = {
      star: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 10 L61 40 L92 40 L67 58 L78 88 L50 70 L22 88 L33 58 L8 40 L39 40 Z" 
              fill="#FFD700" stroke="#FFA500" stroke-width="2"/>
      </svg>`,
      heart: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 85 C20 60, 10 40, 10 25 C10 10, 20 5, 30 5 C40 5, 45 10, 50 20 
                 C55 10, 60 5, 70 5 C80 5, 90 10, 90 25 C90 40, 80 60, 50 85 Z" 
              fill="#FF69B4" stroke="#FF1493" stroke-width="2"/>
      </svg>`,
      cloud: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="50" rx="35" ry="20" fill="#E0F7FA"/>
        <ellipse cx="30" cy="55" rx="20" ry="15" fill="#B2EBF2"/>
        <ellipse cx="70" cy="55" rx="20" ry="15" fill="#B2EBF2"/>
      </svg>`,
      sparkle: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 10 L55 45 L90 50 L55 55 L50 90 L45 55 L10 50 L45 45 Z" 
              fill="#FFE082" stroke="#FFD54F" stroke-width="2"/>
      </svg>`
    };

    // Try to match description to a fallback
    const lowerDesc = description.toLowerCase();
    let svg = fallbacks.star; // default
    
    if (lowerDesc.includes('heart')) svg = fallbacks.heart;
    else if (lowerDesc.includes('cloud')) svg = fallbacks.cloud;
    else if (lowerDesc.includes('sparkle') || lowerDesc.includes('star')) svg = fallbacks.sparkle;

    return {
      svg: svg,
      description: description,
      category: style,
      colorPalette: [],
      valid: true,
      metadata: {
        generatedAt: new Date().toISOString(),
        claudeGenerated: false,
        description: description,
        fallback: true
      }
    };
  }

  /**
   * Build prompt for UI recommendations
   */
  _buildUIRecommendationPrompt(componentType, context) {
    return `You are a UI/UX expert specializing in children's applications.

Provide design recommendations for this component:
- Component type: ${componentType}
- Context: ${JSON.stringify(context)}

Provide specific recommendations for:
1. Layout and structure
2. Colors and visual hierarchy
3. Typography and readability
4. Accessibility (WCAG AA compliance)
5. Responsive design considerations

Return ONLY a JSON object (no markdown, no code blocks):
{
  "layout": ["recommendation 1", "recommendation 2"],
  "colors": ["recommendation 1", "recommendation 2"],
  "typography": ["recommendation 1", "recommendation 2"],
  "accessibility": ["recommendation 1", "recommendation 2"],
  "responsive": ["recommendation 1", "recommendation 2"],
  "codeExamples": {
    "tailwind": "example tailwind classes",
    "css": "example css code"
  },
  "priority": "high|medium|low"
}`;
  }

  /**
   * Parse UI recommendations response
   */
  _parseUIRecommendations(response) {
    try {
      const content = response.content;
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const recommendations = JSON.parse(jsonStr);
      
      return recommendations;
    } catch (error) {
      console.error('Failed to parse UI recommendations:', error);
      throw new Error('Invalid recommendations response from Claude');
    }
  }

  /**
   * Get UI component recommendations
   * 
   * @param {string} componentType - Type of component (button, form, card, etc.)
   * @param {Object} context - Context information (age, theme, purpose, etc.)
   * @returns {Promise<Object>} UI recommendations
   */
  async getUIRecommendations(componentType, context = {}) {
    try {
      const prompt = this._buildUIRecommendationPrompt(componentType, context);
      const response = await this._callClaude(prompt, 2000, 0.7);
      
      if (!response.success) {
        return this._getFallbackUIRecommendations(componentType);
      }
      
      const recommendations = this._parseUIRecommendations(response);
      recommendations.component = componentType;
      recommendations.generatedAt = new Date().toISOString();
      
      return recommendations;
    } catch (error) {
      console.error('Error getting UI recommendations:', error);
      return this._getFallbackUIRecommendations(componentType);
    }
  }

  /**
   * Build prompt for design feedback
   */
  _buildDesignFeedbackPrompt(componentCode, designContext) {
    return `You are a senior UI/UX designer reviewing code for a children's application.

Review this component code:
\`\`\`
${componentCode}
\`\`\`

Context: ${JSON.stringify(designContext)}

Provide specific feedback on:
1. Design consistency
2. Accessibility issues
3. Responsive design
4. Color contrast and readability
5. Performance considerations

Return ONLY a JSON object (no markdown, no code blocks):
{
  "overall": "overall assessment",
  "issues": [
    {"type": "accessibility|design|performance", "severity": "high|medium|low", "description": "issue description", "suggestion": "how to fix"}
  ],
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"]
}`;
  }

  /**
   * Parse design feedback response
   */
  _parseDesignFeedback(response) {
    try {
      const content = response.content;
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const feedback = JSON.parse(jsonStr);
      
      return feedback;
    } catch (error) {
      console.error('Failed to parse design feedback:', error);
      throw new Error('Invalid feedback response from Claude');
    }
  }

  /**
   * Get design feedback for component code
   * 
   * @param {string} componentCode - Component code to review
   * @param {Object} designContext - Design context (purpose, target age, etc.)
   * @returns {Promise<Object>} Design feedback
   */
  async getDesignFeedback(componentCode, designContext = {}) {
    try {
      const prompt = this._buildDesignFeedbackPrompt(componentCode, designContext);
      const response = await this._callClaude(prompt, 2000, 0.7);
      
      if (!response.success) {
        return this._getFallbackDesignFeedback();
      }
      
      const feedback = this._parseDesignFeedback(response);
      feedback.generatedAt = new Date().toISOString();
      
      return feedback;
    } catch (error) {
      console.error('Error getting design feedback:', error);
      return this._getFallbackDesignFeedback();
    }
  }

  /**
   * Fallback UI recommendations
   */
  _getFallbackUIRecommendations(componentType) {
    return {
      component: componentType,
      layout: ['Use clear visual hierarchy', 'Ensure adequate spacing between elements'],
      colors: ['Use high contrast for readability', 'Follow WCAG AA standards'],
      typography: ['Use readable font sizes (minimum 14px)', 'Maintain consistent font families'],
      accessibility: ['Add ARIA labels', 'Ensure keyboard navigation', 'Provide alt text for images'],
      responsive: ['Use mobile-first approach', 'Test on multiple screen sizes'],
      codeExamples: {
        tailwind: 'p-4 rounded-lg shadow-md bg-white',
        css: 'padding: 1rem; border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'
      },
      priority: 'medium',
      generatedAt: new Date().toISOString(),
      fallback: true
    };
  }

  /**
   * Fallback design feedback
   */
  _getFallbackDesignFeedback() {
    return {
      overall: 'Unable to provide detailed feedback at this time',
      issues: [],
      strengths: ['Code structure appears organized'],
      improvements: ['Consider adding more accessibility features', 'Test responsive behavior'],
      generatedAt: new Date().toISOString(),
      fallback: true
    };
  }

  /**
   * Get fallback color palette when Claude is unavailable
   */
  _getFallbackPalette(theme, age) {
    const palettes = {
      animals: {
        primary: '#4CAF50',
        secondary: '#8BC34A',
        accent: '#FFC107',
        background: '#F1F8E9',
        text: '#1B5E20',
        gradient: ['#81C784', '#AED581', '#FFF59D']
      },
      fantasy: {
        primary: '#9C27B0',
        secondary: '#E91E63',
        accent: '#FFD700',
        background: '#F3E5F5',
        text: '#4A148C',
        gradient: ['#BA68C8', '#F06292', '#FFE082']
      },
      adventure: {
        primary: '#FF5722',
        secondary: '#FF9800',
        accent: '#FFEB3B',
        background: '#FFF3E0',
        text: '#BF360C',
        gradient: ['#FF8A65', '#FFB74D', '#FFF176']
      },
      friendship: {
        primary: '#2196F3',
        secondary: '#03A9F4',
        accent: '#FF4081',
        background: '#E3F2FD',
        text: '#0D47A1',
        gradient: ['#64B5F6', '#4FC3F7', '#FF80AB']
      }
    };

    const basePalette = palettes[theme] || palettes.animals;
    
    return {
      ...basePalette,
      usage: {
        primary: 'Main interactive elements and primary actions',
        secondary: 'Supporting elements and secondary actions',
        accent: 'Highlights and call-to-action elements'
      },
      metadata: {
        theme: theme,
        age: age,
        generatedAt: new Date().toISOString(),
        source: 'fallback'
      }
    };
  }
}

// Export singleton instance
const claudeDesignService = new ClaudeDesignService();
export default claudeDesignService;
