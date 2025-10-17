/**
 * DynamicThemeEngine
 * 
 * Service for applying and managing dynamic themes in the application.
 * Handles color palette application, age-adaptive styling, and theme persistence.
 */

class DynamicThemeEngine {
  constructor() {
    this.currentTheme = null;
    this.themeHistory = [];
    this.storageKey = 'dreamairy_theme';
    this.maxHistorySize = 10;
    
    // Load saved theme on initialization
    this._loadSavedTheme();
  }

  /**
   * Load saved theme from localStorage
   */
  _loadSavedTheme() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      if (saved) {
        this.currentTheme = JSON.parse(saved);
        console.log('📦 Loaded saved theme:', this.currentTheme.metadata);
        
        // Auto-apply the saved theme
        this._autoApplySavedTheme();
      }
    } catch (error) {
      console.error('Failed to load saved theme:', error);
      this.currentTheme = null;
    }
  }

  /**
   * Auto-apply saved theme without saving again
   */
  _autoApplySavedTheme() {
    if (!this.currentTheme || !this.currentTheme.palette) {
      return;
    }

    const { palette, age } = this.currentTheme;
    const root = document.documentElement;
    
    // Apply color variables
    root.style.setProperty('--color-primary', palette.primary);
    root.style.setProperty('--color-secondary', palette.secondary);
    root.style.setProperty('--color-accent', palette.accent);
    root.style.setProperty('--color-background', palette.background);
    root.style.setProperty('--color-text', palette.text);
    
    // Apply gradient if available
    if (palette.gradient && palette.gradient.length >= 2) {
      const gradientCSS = `linear-gradient(135deg, ${palette.gradient.join(', ')})`;
      root.style.setProperty('--gradient-primary', gradientCSS);
      
      const gradientVertical = `linear-gradient(180deg, ${palette.gradient.join(', ')})`;
      const gradientRadial = `radial-gradient(circle, ${palette.gradient.join(', ')})`;
      
      root.style.setProperty('--gradient-vertical', gradientVertical);
      root.style.setProperty('--gradient-radial', gradientRadial);
    }
    
    // Apply age-specific styles
    if (age) {
      this._applyAgeStyles(age);
    }
    
    console.log('✨ Auto-applied saved theme:', {
      primary: palette.primary,
      age: age,
      source: this.currentTheme.metadata?.source
    });
  }

  /**
   * Save theme to localStorage
   */
  _saveTheme(theme) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(theme));
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  }

  /**
   * Add theme to history
   */
  _addToHistory(theme) {
    this.themeHistory.push({
      ...theme,
      appliedAt: new Date().toISOString()
    });
    
    // Limit history size
    if (this.themeHistory.length > this.maxHistorySize) {
      this.themeHistory.shift();
    }
  }

  /**
   * Apply color palette to CSS variables
   * 
   * @param {Object} palette - Color palette object from ClaudeDesignService
   * @param {number} age - Child's age for adaptive styling
   */
  applyPalette(palette, age) {
    if (!palette) {
      console.error('No palette provided to applyPalette');
      return;
    }

    const root = document.documentElement;
    
    // Apply color variables
    root.style.setProperty('--color-primary', palette.primary);
    root.style.setProperty('--color-secondary', palette.secondary);
    root.style.setProperty('--color-accent', palette.accent);
    root.style.setProperty('--color-background', palette.background);
    root.style.setProperty('--color-text', palette.text);
    
    // Apply gradient if available
    if (palette.gradient && palette.gradient.length >= 2) {
      const gradientCSS = `linear-gradient(135deg, ${palette.gradient.join(', ')})`;
      root.style.setProperty('--gradient-primary', gradientCSS);
      
      // Create additional gradient variations
      const gradientVertical = `linear-gradient(180deg, ${palette.gradient.join(', ')})`;
      const gradientRadial = `radial-gradient(circle, ${palette.gradient.join(', ')})`;
      
      root.style.setProperty('--gradient-vertical', gradientVertical);
      root.style.setProperty('--gradient-radial', gradientRadial);
    }
    
    // Apply age-specific styles
    if (age) {
      this._applyAgeStyles(age);
    }
    
    // Create theme object
    const theme = {
      palette: palette,
      age: age,
      timestamp: Date.now(),
      metadata: palette.metadata || {}
    };
    
    // Store current theme
    this.currentTheme = theme;
    
    // Add to history
    this._addToHistory(theme);
    
    // Save to localStorage
    this._saveTheme(theme);
    
    console.log('✨ Theme applied:', {
      primary: palette.primary,
      age: age,
      source: palette.metadata?.source
    });
  }

  /**
   * Apply age-appropriate styling adjustments
   * 
   * @param {number} age - Child's age (3-12)
   */
  _applyAgeStyles(age) {
    const root = document.documentElement;
    
    if (age <= 5) {
      // Ages 3-5: Large, simple, high contrast
      root.style.setProperty('--font-size-base', '18px');
      root.style.setProperty('--font-size-large', '24px');
      root.style.setProperty('--font-size-small', '16px');
      root.style.setProperty('--button-size', '60px');
      root.style.setProperty('--button-padding', '1.5rem 2rem');
      root.style.setProperty('--border-radius', '25px');
      root.style.setProperty('--border-radius-small', '15px');
      root.style.setProperty('--spacing-unit', '1.5rem');
      root.style.setProperty('--animation-speed', '0.5s');
      root.style.setProperty('--shadow-size', '0 8px 16px rgba(0,0,0,0.15)');
      
    } else if (age <= 8) {
      // Ages 6-8: Moderate size, balanced
      root.style.setProperty('--font-size-base', '16px');
      root.style.setProperty('--font-size-large', '20px');
      root.style.setProperty('--font-size-small', '14px');
      root.style.setProperty('--button-size', '50px');
      root.style.setProperty('--button-padding', '1rem 1.5rem');
      root.style.setProperty('--border-radius', '20px');
      root.style.setProperty('--border-radius-small', '12px');
      root.style.setProperty('--spacing-unit', '1.25rem');
      root.style.setProperty('--animation-speed', '0.3s');
      root.style.setProperty('--shadow-size', '0 6px 12px rgba(0,0,0,0.12)');
      
    } else {
      // Ages 9-12: Sophisticated, detailed
      root.style.setProperty('--font-size-base', '14px');
      root.style.setProperty('--font-size-large', '18px');
      root.style.setProperty('--font-size-small', '12px');
      root.style.setProperty('--button-size', '44px');
      root.style.setProperty('--button-padding', '0.75rem 1.25rem');
      root.style.setProperty('--border-radius', '15px');
      root.style.setProperty('--border-radius-small', '8px');
      root.style.setProperty('--spacing-unit', '1rem');
      root.style.setProperty('--animation-speed', '0.2s');
      root.style.setProperty('--shadow-size', '0 4px 8px rgba(0,0,0,0.1)');
    }
    
    console.log(`🎨 Age-adaptive styles applied for age ${age}`);
  }

  /**
   * Get current theme
   * 
   * @returns {Object|null} Current theme object
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get theme history
   * 
   * @returns {Array} Array of previously applied themes
   */
  getThemeHistory() {
    return this.themeHistory;
  }

  /**
   * Reset theme to default
   */
  resetTheme() {
    const root = document.documentElement;
    
    // Remove all custom properties
    const customProps = [
      '--color-primary',
      '--color-secondary',
      '--color-accent',
      '--color-background',
      '--color-text',
      '--gradient-primary',
      '--gradient-vertical',
      '--gradient-radial',
      '--font-size-base',
      '--font-size-large',
      '--font-size-small',
      '--button-size',
      '--button-padding',
      '--border-radius',
      '--border-radius-small',
      '--spacing-unit',
      '--animation-speed',
      '--shadow-size'
    ];
    
    customProps.forEach(prop => {
      root.style.removeProperty(prop);
    });
    
    // Clear state
    this.currentTheme = null;
    
    // Clear localStorage
    localStorage.removeItem(this.storageKey);
    
    console.log('🔄 Theme reset to default');
  }

  /**
   * Apply a previous theme from history
   * 
   * @param {number} index - Index in theme history
   */
  applyThemeFromHistory(index) {
    if (index < 0 || index >= this.themeHistory.length) {
      console.error('Invalid theme history index:', index);
      return;
    }
    
    const historicalTheme = this.themeHistory[index];
    this.applyPalette(historicalTheme.palette, historicalTheme.age);
  }

  /**
   * Export current theme as JSON
   * 
   * @returns {string} JSON string of current theme
   */
  exportTheme() {
    if (!this.currentTheme) {
      console.warn('No theme to export');
      return null;
    }
    
    return JSON.stringify(this.currentTheme, null, 2);
  }

  /**
   * Import theme from JSON
   * 
   * @param {string} themeJson - JSON string of theme
   */
  importTheme(themeJson) {
    try {
      const theme = JSON.parse(themeJson);
      
      if (!theme.palette || !theme.palette.primary) {
        throw new Error('Invalid theme format');
      }
      
      this.applyPalette(theme.palette, theme.age);
      console.log('✅ Theme imported successfully');
      
    } catch (error) {
      console.error('Failed to import theme:', error);
      throw error;
    }
  }

  /**
   * Get CSS variable value
   * 
   * @param {string} varName - CSS variable name (with or without --)
   * @returns {string} Variable value
   */
  getCSSVariable(varName) {
    const root = document.documentElement;
    const name = varName.startsWith('--') ? varName : `--${varName}`;
    return getComputedStyle(root).getPropertyValue(name).trim();
  }

  /**
   * Set CSS variable value
   * 
   * @param {string} varName - CSS variable name (with or without --)
   * @param {string} value - Variable value
   */
  setCSSVariable(varName, value) {
    const root = document.documentElement;
    const name = varName.startsWith('--') ? varName : `--${varName}`;
    root.style.setProperty(name, value);
  }

  /**
   * Apply smooth transition when changing themes
   * 
   * @param {Object} newPalette - New color palette
   * @param {number} age - Child's age
   * @param {number} duration - Transition duration in ms (default: 500)
   */
  async applyPaletteWithTransition(newPalette, age, duration = 500) {
    const root = document.documentElement;
    
    // Add transition
    root.style.transition = `all ${duration}ms ease-in-out`;
    
    // Apply new palette
    this.applyPalette(newPalette, age);
    
    // Wait for transition to complete
    await new Promise(resolve => setTimeout(resolve, duration));
    
    // Remove transition
    root.style.transition = '';
  }

  /**
   * Check if reduced motion is preferred
   * 
   * @returns {boolean} True if reduced motion is preferred
   */
  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * Apply reduced motion settings
   */
  applyReducedMotion() {
    if (this.prefersReducedMotion()) {
      const root = document.documentElement;
      root.style.setProperty('--animation-speed', '0.01s');
      console.log('♿ Reduced motion applied');
    }
  }

  /**
   * Get contrast ratio between two colors
   * 
   * @param {string} color1 - First color (hex)
   * @param {string} color2 - Second color (hex)
   * @returns {number} Contrast ratio
   */
  getContrastRatio(color1, color2) {
    const getLuminance = (hex) => {
      const rgb = parseInt(hex.slice(1), 16);
      const r = ((rgb >> 16) & 0xff) / 255;
      const g = ((rgb >> 8) & 0xff) / 255;
      const b = (rgb & 0xff) / 255;
      
      const [rs, gs, bs] = [r, g, b].map(c => {
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };
    
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * Validate palette accessibility
   * 
   * @param {Object} palette - Color palette to validate
   * @returns {Object} Validation results
   */
  validatePaletteAccessibility(palette) {
    const results = {
      valid: true,
      issues: [],
      warnings: []
    };
    
    // Check text on background contrast
    const textBgRatio = this.getContrastRatio(palette.text, palette.background);
    if (textBgRatio < 4.5) {
      results.valid = false;
      results.issues.push({
        type: 'contrast',
        severity: 'high',
        message: `Text/background contrast ratio ${textBgRatio.toFixed(2)} is below WCAG AA standard (4.5:1)`,
        colors: [palette.text, palette.background]
      });
    }
    
    // Check primary on background contrast
    const primaryBgRatio = this.getContrastRatio(palette.primary, palette.background);
    if (primaryBgRatio < 3) {
      results.warnings.push({
        type: 'contrast',
        severity: 'medium',
        message: `Primary/background contrast ratio ${primaryBgRatio.toFixed(2)} may be too low`,
        colors: [palette.primary, palette.background]
      });
    }
    
    return results;
  }
}

// Export singleton instance
const dynamicThemeEngine = new DynamicThemeEngine();
export default dynamicThemeEngine;
