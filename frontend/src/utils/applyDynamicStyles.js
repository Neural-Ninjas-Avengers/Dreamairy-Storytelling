/**
 * Apply dynamic theme styles to the DOM
 * This utility applies theme colors to elements that use inline styles or Tailwind classes
 */

export function applyDynamicStylesToDOM() {
  const root = document.documentElement;
  const style = getComputedStyle(root);
  
  // Get CSS variables
  const primary = style.getPropertyValue('--color-primary').trim();
  const secondary = style.getPropertyValue('--color-secondary').trim();
  const gradient = style.getPropertyValue('--gradient-primary').trim();
  
  if (!primary) {
    console.log('No theme variables found, skipping dynamic styles');
    return;
  }
  
  console.log('🎨 Applying dynamic styles to DOM elements');
  
  // Create or update dynamic style element
  let styleElement = document.getElementById('dynamic-theme-styles');
  if (!styleElement) {
    styleElement = document.createElement('style');
    styleElement.id = 'dynamic-theme-styles';
    document.head.appendChild(styleElement);
  }
  
  // Generate dynamic CSS
  styleElement.textContent = `
    /* Dynamic theme overrides */
    body {
      background: ${gradient} !important;
    }
    
    /* Override Tailwind gradient classes */
    .bg-gradient-to-r,
    .bg-gradient-to-br,
    .bg-gradient-to-bl {
      background: ${gradient} !important;
    }
    
    /* Primary color overrides */
    [class*="bg-coral"],
    [class*="from-coral"],
    [class*="to-coral"] {
      background-color: ${primary} !important;
    }
    
    /* Secondary color overrides */
    [class*="bg-forest"],
    [class*="from-forest"],
    [class*="to-forest"] {
      background-color: ${secondary} !important;
    }
    
    /* Ring colors */
    [class*="ring-coral"] {
      --tw-ring-color: ${primary} !important;
    }
    
    /* Border colors */
    [class*="border-coral"] {
      border-color: ${primary} !important;
    }
    
    /* Text colors */
    [class*="text-coral"] {
      color: ${primary} !important;
    }
    
    /* Hover states */
    button:hover,
    .btn-primary:hover,
    .btn-secondary:hover {
      filter: brightness(1.1);
    }
  `;
  
  console.log('✅ Dynamic styles applied');
}

/**
 * Watch for theme changes and reapply styles
 */
export function watchThemeChanges() {
  // Watch for changes to CSS variables
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
        const root = document.documentElement;
        const style = getComputedStyle(root);
        const primary = style.getPropertyValue('--color-primary').trim();
        
        if (primary) {
          console.log('🔄 Theme changed, reapplying styles');
          applyDynamicStylesToDOM();
        }
      }
    });
  });
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['style']
  });
  
  return observer;
}
