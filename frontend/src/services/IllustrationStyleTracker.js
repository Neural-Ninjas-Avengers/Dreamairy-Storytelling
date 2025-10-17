/**
 * IllustrationStyleTracker
 * 
 * Service for maintaining consistent illustration style throughout a story session.
 * Tracks prompts, style guides, and ensures visual continuity.
 */

import claudeDesignService from './ClaudeDesignService';

class IllustrationStyleTracker {
  constructor() {
    this.styleGuide = null;
    this.promptHistory = [];
    this.sessionId = null;
    this.maxHistorySize = 20;
  }

  /**
   * Initialize style guide for a story session
   * 
   * @param {string} theme - Story theme (animals, fantasy, adventure, friendship)
   * @param {number} age - Child's age
   * @param {string} avatarDescription - Description of user's avatar
   * @returns {Promise<Object>} Style guide object
   */
  async initializeStyleGuide(theme, age, avatarDescription) {
    try {
      console.log('🎨 Initializing style guide:', { theme, age, avatarDescription });
      
      // Build prompt for Claude to generate style guide
      const prompt = this._buildStyleGuidePrompt(theme, age, avatarDescription);
      
      // Call Claude
      const response = await claudeDesignService._callClaude(prompt, 1500, 0.7);
      
      if (!response.success) {
        console.warn('Claude unavailable, using fallback style guide');
        return this._getFallbackStyleGuide(theme, age, avatarDescription);
      }
      
      // Parse response
      const styleGuide = this._parseStyleGuideResponse(response);
      
      // Store style guide
      this.styleGuide = {
        ...styleGuide,
        theme: theme,
        age: age,
        avatarDescription: avatarDescription,
        createdAt: new Date().toISOString(),
        source: 'claude'
      };
      
      // Generate new session ID
      this.sessionId = `style_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Clear previous history
      this.promptHistory = [];
      
      console.log('✅ Style guide initialized:', this.styleGuide);
      
      return this.styleGuide;
      
    } catch (error) {
      console.error('Error initializing style guide:', error);
      return this._getFallbackStyleGuide(theme, age, avatarDescription);
    }
  }

  /**
   * Build prompt for style guide generation
   */
  _buildStyleGuidePrompt(theme, age, avatarDescription) {
    const ageGuidance = this._getAgeStyleGuidance(age);
    
    return `You are a professional children's book illustrator creating a consistent style guide.

Create a comprehensive illustration style guide for a children's story with these parameters:
- Theme: ${theme}
- Child's age: ${age} years
- Avatar/Character: ${avatarDescription || 'friendly character'}

${ageGuidance}

Define a consistent style guide that includes:
1. Art style (watercolor, cartoon, digital, storybook, etc.)
2. Color palette approach (bright, pastel, vibrant, etc.)
3. Character design principles (proportions, features, clothing style)
4. Environment/background style (detailed, simple, atmospheric)
5. Lighting and mood (bright, soft, magical, natural)
6. Composition rules (close-up, wide shots, perspective)

Return ONLY a JSON object (no markdown, no code blocks):
{
  "artStyle": "specific art style name",
  "colorApproach": "description of color usage",
  "characterDesign": "character design guidelines",
  "environmentStyle": "environment and background approach",
  "lighting": "lighting and mood description",
  "composition": "composition and framing rules",
  "technicalNotes": "any technical considerations"
}`;
  }

  /**
   * Get age-specific style guidance
   */
  _getAgeStyleGuidance(age) {
    if (age <= 5) {
      return `For ages 3-5:
- Use simple, bold shapes and clear outlines
- Bright, primary colors with high contrast
- Large, expressive characters with exaggerated features
- Minimal background details to avoid distraction
- Cheerful, safe, and comforting atmosphere`;
    } else if (age <= 8) {
      return `For ages 6-8:
- Balanced detail level with clear focal points
- Vibrant, varied color palette
- Characters with personality and expression
- Engaging backgrounds with story elements
- Sense of adventure and wonder`;
    } else {
      return `For ages 9-12:
- More sophisticated detail and composition
- Nuanced color palette with depth
- Complex character designs with unique traits
- Rich, atmospheric environments
- Dramatic lighting and mood`;
    }
  }

  /**
   * Parse style guide response from Claude
   */
  _parseStyleGuideResponse(response) {
    try {
      const content = response.content;
      
      // Remove markdown code blocks if present
      let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      
      // Parse JSON
      const styleGuide = JSON.parse(jsonStr);
      
      // Validate required fields
      const requiredFields = ['artStyle', 'colorApproach', 'characterDesign', 'environmentStyle', 'lighting', 'composition'];
      for (const field of requiredFields) {
        if (!styleGuide[field]) {
          throw new Error(`Missing required field: ${field}`);
        }
      }
      
      return styleGuide;
      
    } catch (error) {
      console.error('Failed to parse style guide response:', error);
      throw new Error('Invalid style guide response from Claude');
    }
  }

  /**
   * Get fallback style guide when Claude is unavailable
   */
  _getFallbackStyleGuide(theme, age, avatarDescription) {
    const styleGuides = {
      animals: {
        artStyle: 'Watercolor storybook illustration',
        colorApproach: 'Warm, natural colors with soft gradients',
        characterDesign: 'Cute, friendly animals with expressive eyes and gentle features',
        environmentStyle: 'Lush forest and nature scenes with soft details',
        lighting: 'Soft, natural daylight with warm tones',
        composition: 'Medium shots focusing on character interactions',
        technicalNotes: 'Maintain soft edges and organic shapes'
      },
      fantasy: {
        artStyle: 'Digital fantasy illustration with magical elements',
        colorApproach: 'Vibrant, magical colors with sparkles and glows',
        characterDesign: 'Whimsical characters with magical accessories and flowing elements',
        environmentStyle: 'Enchanted landscapes with castles, clouds, and mystical elements',
        lighting: 'Magical, ethereal lighting with glowing effects',
        composition: 'Dynamic angles with sense of wonder and scale',
        technicalNotes: 'Add magical particles and light effects'
      },
      adventure: {
        artStyle: 'Bold cartoon adventure style',
        colorApproach: 'Bright, energetic colors with strong contrasts',
        characterDesign: 'Dynamic characters in action poses with adventurer gear',
        environmentStyle: 'Exciting locations with sense of exploration and discovery',
        lighting: 'Dramatic lighting emphasizing action and movement',
        composition: 'Wide shots showing environment and adventure scale',
        technicalNotes: 'Emphasize movement and energy'
      },
      friendship: {
        artStyle: 'Warm, inviting storybook style',
        colorApproach: 'Friendly, harmonious colors that feel welcoming',
        characterDesign: 'Relatable characters with warm expressions and body language',
        environmentStyle: 'Cozy, familiar settings like homes, parks, and neighborhoods',
        lighting: 'Warm, comforting light creating safe atmosphere',
        composition: 'Close-ups and medium shots emphasizing character connections',
        technicalNotes: 'Focus on emotional connection and warmth'
      }
    };

    const baseGuide = styleGuides[theme] || styleGuides.animals;
    
    return {
      ...baseGuide,
      theme: theme,
      age: age,
      avatarDescription: avatarDescription,
      createdAt: new Date().toISOString(),
      source: 'fallback'
    };
  }

  /**
   * Get style-consistent prompt for illustration
   * 
   * @param {string} basePrompt - Base prompt from story segment
   * @returns {string} Enhanced prompt with style guide applied
   */
  getStyleConsistentPrompt(basePrompt) {
    if (!this.styleGuide) {
      console.warn('No style guide initialized, returning base prompt');
      return basePrompt;
    }

    // Build enhanced prompt with style guide
    const enhancedPrompt = `${basePrompt}

Style Guide:
- Art style: ${this.styleGuide.artStyle}
- Color approach: ${this.styleGuide.colorApproach}
- Character design: ${this.styleGuide.characterDesign}
- Environment: ${this.styleGuide.environmentStyle}
- Lighting: ${this.styleGuide.lighting}
- Composition: ${this.styleGuide.composition}

Maintain consistency with previous illustrations in this session.`;

    return enhancedPrompt;
  }

  /**
   * Track prompt for consistency
   * 
   * @param {string} prompt - Prompt used for generation
   * @param {string} imageUrl - URL of generated image
   * @param {Object} metadata - Additional metadata
   */
  trackPrompt(prompt, imageUrl, metadata = {}) {
    const entry = {
      prompt: prompt,
      imageUrl: imageUrl,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      metadata: metadata
    };

    this.promptHistory.push(entry);

    // Limit history size
    if (this.promptHistory.length > this.maxHistorySize) {
      this.promptHistory.shift();
    }

    console.log(`📝 Tracked prompt #${this.promptHistory.length}:`, prompt.substring(0, 50) + '...');
  }

  /**
   * Get previous prompts for context
   * 
   * @param {number} count - Number of previous prompts to retrieve
   * @returns {Array<Object>} Array of previous prompt entries
   */
  getPreviousPrompts(count = 3) {
    if (this.promptHistory.length === 0) {
      return [];
    }

    const startIndex = Math.max(0, this.promptHistory.length - count);
    return this.promptHistory.slice(startIndex);
  }

  /**
   * Get previous prompt texts only
   * 
   * @param {number} count - Number of previous prompts to retrieve
   * @returns {Array<string>} Array of prompt strings
   */
  getPreviousPromptTexts(count = 3) {
    return this.getPreviousPrompts(count).map(entry => entry.prompt);
  }

  /**
   * Get current style guide
   * 
   * @returns {Object|null} Current style guide
   */
  getStyleGuide() {
    return this.styleGuide;
  }

  /**
   * Get prompt history
   * 
   * @returns {Array<Object>} Full prompt history
   */
  getPromptHistory() {
    return this.promptHistory;
  }

  /**
   * Clear current session
   */
  clearSession() {
    this.styleGuide = null;
    this.promptHistory = [];
    this.sessionId = null;
    console.log('🔄 Style tracker session cleared');
  }

  /**
   * Export session data
   * 
   * @returns {Object} Session data including style guide and history
   */
  exportSession() {
    return {
      styleGuide: this.styleGuide,
      promptHistory: this.promptHistory,
      sessionId: this.sessionId,
      exportedAt: new Date().toISOString()
    };
  }

  /**
   * Import session data
   * 
   * @param {Object} sessionData - Previously exported session data
   */
  importSession(sessionData) {
    try {
      if (!sessionData.styleGuide) {
        throw new Error('Invalid session data: missing style guide');
      }

      this.styleGuide = sessionData.styleGuide;
      this.promptHistory = sessionData.promptHistory || [];
      this.sessionId = sessionData.sessionId || `imported_${Date.now()}`;

      console.log('✅ Session imported successfully');
    } catch (error) {
      console.error('Failed to import session:', error);
      throw error;
    }
  }

  /**
   * Get consistency score for current session
   * 
   * @returns {number} Consistency score (0-1)
   */
  getConsistencyScore() {
    if (!this.styleGuide || this.promptHistory.length === 0) {
      return 0;
    }

    // Base score on having style guide and prompt history
    let score = 0.5;

    // Increase score based on number of tracked prompts
    if (this.promptHistory.length >= 3) score += 0.2;
    if (this.promptHistory.length >= 5) score += 0.1;

    // Increase score if using Claude-generated style guide
    if (this.styleGuide.source === 'claude') score += 0.2;

    return Math.min(score, 1.0);
  }

  /**
   * Generate summary of current style
   * 
   * @returns {string} Human-readable style summary
   */
  getStyleSummary() {
    if (!this.styleGuide) {
      return 'No style guide initialized';
    }

    return `Style: ${this.styleGuide.artStyle}
Theme: ${this.styleGuide.theme}
Age: ${this.styleGuide.age} years
Prompts tracked: ${this.promptHistory.length}
Consistency score: ${(this.getConsistencyScore() * 100).toFixed(0)}%
Source: ${this.styleGuide.source}`;
  }
}

// Export singleton instance
const illustrationStyleTracker = new IllustrationStyleTracker();
export default illustrationStyleTracker;
