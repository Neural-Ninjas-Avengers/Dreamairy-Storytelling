/**
 * Design Studio JavaScript
 * Handles all interactions with Claude Design API
 */

const API_BASE = 'http://localhost:3001';
let currentPalette = null;
let currentSVG = null;
let chatHistory = [];

// Tab switching
function switchTab(tabName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.nav-item').classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Generate Color Palette
async function generatePalette() {
    const btn = document.getElementById('generate-palette-btn');
    const resultBox = document.getElementById('palette-result');
    const statusBadge = document.getElementById('palette-status');
    const colorsDiv = document.getElementById('palette-colors');

    const theme = document.getElementById('palette-theme').value;
    const age = parseInt(document.getElementById('palette-age').value);
    const emotionalGoal = document.getElementById('palette-emotion').value;

    // Show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generating...';
    resultBox.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/v1/design/claude`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildPalettePrompt(theme, age, emotionalGoal),
                max_tokens: 1000,
                temperature: 0.7
            })
        });

        const data = await response.json();

        if (data.success) {
            // Parse palette from response
            const palette = parsePaletteResponse(data.content);
            currentPalette = palette;

            // Display palette
            displayPalette(palette, colorsDiv);
            statusBadge.textContent = 'Generated with Claude';
            statusBadge.className = 'status-badge status-success';
            resultBox.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to generate palette');
        }
    } catch (error) {
        console.error('Error generating palette:', error);
        alert('Failed to generate palette: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Generate Palette';
    }
}

function buildPalettePrompt(theme, age, emotionalGoal) {
    const ageGuidance = age <= 5 ? 'bright primary colors with high contrast' :
                        age <= 8 ? 'balanced vibrant colors with medium contrast' :
                        'sophisticated nuanced colors with subtle gradients';

    return `You are a professional UI/UX designer specializing in children's applications.

Generate a cohesive color palette for a children's storytelling app with these parameters:
- Theme: ${theme}
- Child's age: ${age} years
- Emotional goal: ${emotionalGoal}

Requirements:
1. All colors must meet WCAG AA contrast standards
2. Age ${age} requires ${ageGuidance}
3. Theme "${theme}" should influence the palette
4. Include: primary, secondary, accent, background, text colors
5. Provide hex codes

Return ONLY a JSON object in this exact format (no markdown, no code blocks):
{
  "primary": "#hexcode",
  "secondary": "#hexcode",
  "accent": "#hexcode",
  "background": "#hexcode",
  "text": "#hexcode",
  "gradient": ["#hex1", "#hex2", "#hex3"]
}`;
}

function parsePaletteResponse(content) {
    try {
        // Remove markdown code blocks if present
        let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        return JSON.parse(jsonStr);
    } catch (error) {
        console.error('Failed to parse palette:', error);
        // Return fallback palette
        return {
            primary: '#667eea',
            secondary: '#764ba2',
            accent: '#f093fb',
            background: '#ffecd2',
            text: '#333333',
            gradient: ['#667eea', '#764ba2', '#f093fb']
        };
    }
}

function displayPalette(palette, container) {
    container.innerHTML = '';

    const colors = [
        { name: 'Primary', value: palette.primary },
        { name: 'Secondary', value: palette.secondary },
        { name: 'Accent', value: palette.accent },
        { name: 'Background', value: palette.background },
        { name: 'Text', value: palette.text }
    ];

    colors.forEach(color => {
        const swatch = document.createElement('div');
        swatch.className = 'color-swatch';
        swatch.innerHTML = `
            <div class="color-box" style="background-color: ${color.value}" 
                 onclick="copyToClipboard('color-${color.name}', '${color.value}')" 
                 title="Click to copy"></div>
            <div class="color-label">${color.name}</div>
            <div class="color-value" id="color-${color.name}">${color.value}</div>
        `;
        container.appendChild(swatch);
    });

    // Add gradient preview
    if (palette.gradient && palette.gradient.length >= 2) {
        const gradientSwatch = document.createElement('div');
        gradientSwatch.className = 'color-swatch';
        gradientSwatch.style.gridColumn = 'span 2';
        gradientSwatch.innerHTML = `
            <div class="color-box" style="background: linear-gradient(135deg, ${palette.gradient.join(', ')})" 
                 title="Gradient"></div>
            <div class="color-label">Gradient</div>
            <div class="color-value">${palette.gradient.join(', ')}</div>
        `;
        container.appendChild(gradientSwatch);
    }
}

function applyPaletteToApp() {
    if (!currentPalette) {
        alert('No palette generated yet');
        return;
    }

    // Save palette to localStorage so the app can pick it up
    try {
        const themeData = {
            palette: currentPalette,
            age: parseInt(document.getElementById('palette-age').value) || 7,
            timestamp: Date.now(),
            metadata: {
                theme: document.getElementById('palette-theme').value,
                emotionalGoal: document.getElementById('palette-emotion').value,
                source: 'design-studio'
            }
        };
        
        localStorage.setItem('dreamairy_theme', JSON.stringify(themeData));
        
        // Apply CSS variables directly to the document
        applyThemeToDocument(currentPalette);
        
        // Try to send message to iframe (may fail due to CORS, but worth trying)
        const iframe = document.getElementById('preview-frame');
        if (iframe && iframe.contentWindow) {
            try {
                iframe.contentWindow.postMessage({
                    type: 'APPLY_THEME',
                    theme: themeData
                }, 'http://localhost:3000');
                
                // Refresh iframe after a short delay to pick up the new theme
                setTimeout(() => {
                    iframe.src = iframe.src;
                }, 500);
            } catch (error) {
                console.log('PostMessage failed (expected with CORS):', error);
            }
        }
        
        alert('✅ Palette applied and saved!\n\n' +
              'The theme has been:\n' +
              '1. Applied to this page\n' +
              '2. Saved to localStorage\n' +
              '3. Preview will refresh automatically\n\n' +
              'Open http://localhost:3000 in a new tab to see it in the main app!');
              
    } catch (error) {
        console.error('Failed to save palette:', error);
        alert('❌ Failed to save palette: ' + error.message);
    }
}

function applyThemeToDocument(palette) {
    console.log('🎨 applyThemeToDocument called with:', palette);
    
    // Apply CSS variables to the current document
    const root = document.documentElement;
    
    console.log('Setting --color-primary to:', palette.primary);
    root.style.setProperty('--color-primary', palette.primary);
    root.style.setProperty('--color-secondary', palette.secondary);
    root.style.setProperty('--color-accent', palette.accent);
    root.style.setProperty('--color-background', palette.background);
    root.style.setProperty('--color-text', palette.text);
    
    if (palette.gradient && palette.gradient.length >= 2) {
        const gradientValue = `linear-gradient(135deg, ${palette.gradient.join(', ')})`;
        console.log('Setting --gradient-primary to:', gradientValue);
        root.style.setProperty('--gradient-primary', gradientValue);
    }
    
    // Verify the values were set
    const computedStyle = getComputedStyle(root);
    console.log('Verified --color-primary:', computedStyle.getPropertyValue('--color-primary'));
    console.log('Verified --gradient-primary:', computedStyle.getPropertyValue('--gradient-primary'));
    
    console.log('✅ Theme applied to document');
}

// Optimize Prompt
async function optimizePrompt() {
    const btn = document.getElementById('optimize-prompt-btn');
    const resultBox = document.getElementById('prompt-result');
    const promptText = document.getElementById('optimized-prompt-text');
    const fallbackDiv = document.getElementById('fallback-prompts');

    const storySegment = document.getElementById('prompt-story').value;
    const avatarDescription = document.getElementById('prompt-avatar').value;

    if (!storySegment) {
        alert('Please enter a story segment');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Optimizing...';
    resultBox.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/v1/design/claude`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildPromptOptimizationRequest(storySegment, avatarDescription),
                max_tokens: 1500,
                temperature: 0.7
            })
        });

        const data = await response.json();

        if (data.success) {
            const optimized = parseOptimizedPrompt(data.content);
            
            promptText.textContent = optimized.prompt;
            
            // Display fallback prompts
            fallbackDiv.innerHTML = '';
            if (optimized.fallback_prompts) {
                optimized.fallback_prompts.forEach((fallback, index) => {
                    const div = document.createElement('div');
                    div.className = 'code-block';
                    div.style.marginTop = '8px';
                    div.innerHTML = `
                        <button class="copy-btn" onclick="copyToClipboard('fallback-${index}', '${fallback.replace(/'/g, "\\'")}')">Copy</button>
                        <pre id="fallback-${index}">${fallback}</pre>
                    `;
                    fallbackDiv.appendChild(div);
                });
            }

            resultBox.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to optimize prompt');
        }
    } catch (error) {
        console.error('Error optimizing prompt:', error);
        alert('Failed to optimize prompt: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Optimize Prompt';
    }
}

function buildPromptOptimizationRequest(storySegment, avatarDescription) {
    return `You are an expert at creating prompts for AI image generation (AWS Titan).

Story segment: "${storySegment}"
Avatar description: "${avatarDescription}"

Create an optimized prompt for AWS Titan Image Generator that:
1. Is child-safe and age-appropriate
2. Includes the avatar character naturally in the scene
3. Specifies art style (watercolor, cartoon, storybook, etc.)
4. Describes composition, lighting, and mood
5. Avoids any content that might trigger AWS filters

Return ONLY a JSON object (no markdown, no code blocks):
{
  "prompt": "detailed prompt text",
  "negative_prompt": "things to avoid",
  "style": "art style name",
  "fallback_prompts": ["alternative 1", "alternative 2"]
}`;
}

function parseOptimizedPrompt(content) {
    try {
        let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        return JSON.parse(jsonStr);
    } catch (error) {
        console.error('Failed to parse prompt:', error);
        return {
            prompt: content,
            fallback_prompts: []
        };
    }
}

// Generate SVG
async function generateSVG() {
    const btn = document.getElementById('generate-svg-btn');
    const resultBox = document.getElementById('svg-result');
    const previewDiv = document.getElementById('svg-preview');
    const codeText = document.getElementById('svg-code-text');

    const description = document.getElementById('svg-description').value;
    const style = document.getElementById('svg-style').value;

    if (!description) {
        alert('Please enter a description');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generating...';
    resultBox.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/v1/design/claude`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: buildSVGGenerationPrompt(description, style),
                max_tokens: 1500,
                temperature: 0.7
            })
        });

        const data = await response.json();

        if (data.success) {
            const svgData = parseSVGResponse(data.content);
            currentSVG = svgData.svg;
            
            previewDiv.innerHTML = svgData.svg;
            codeText.textContent = svgData.svg;
            resultBox.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to generate SVG');
        }
    } catch (error) {
        console.error('Error generating SVG:', error);
        alert('Failed to generate SVG: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Generate SVG';
    }
}

function buildSVGGenerationPrompt(description, style) {
    return `You are an expert SVG designer.

Create an SVG graphic with these specifications:
- Description: ${description}
- Style: ${style}

Requirements:
1. Valid, clean SVG code
2. Viewbox: 0 0 100 100
3. Simple, recognizable shapes
4. Child-friendly and appealing
5. Use bright, vibrant colors

Return ONLY a JSON object (no markdown, no code blocks):
{
  "svg": "<svg viewBox='0 0 100 100'>...</svg>",
  "description": "what the SVG represents"
}`;
}

function parseSVGResponse(content) {
    try {
        let jsonStr = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        return JSON.parse(jsonStr);
    } catch (error) {
        console.error('Failed to parse SVG:', error);
        return {
            svg: '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="#667eea"/></svg>',
            description: 'Fallback SVG'
        };
    }
}

function downloadSVG() {
    if (!currentSVG) {
        alert('No SVG generated yet');
        return;
    }

    const blob = new Blob([currentSVG], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated-asset.svg';
    a.click();
    URL.revokeObjectURL(url);
}

// Claude Chat
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const messagesDiv = document.getElementById('chat-messages');
    const btn = document.getElementById('send-chat-btn');

    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage('user', message);
    input.value = '';

    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span>';

    try {
        const response = await fetch(`${API_BASE}/api/v1/design/claude`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message,
                max_tokens: 2000,
                temperature: 0.7
            })
        });

        const data = await response.json();

        if (data.success) {
            addChatMessage('claude', data.content);
        } else {
            addChatMessage('error', 'Failed to get response: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('error', 'Failed to send message: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Send';
    }
}

function addChatMessage(type, content) {
    const messagesDiv = document.getElementById('chat-messages');
    
    // Remove placeholder if exists
    if (messagesDiv.children.length === 1 && messagesDiv.children[0].style.textAlign === 'center') {
        messagesDiv.innerHTML = '';
    }

    const messageDiv = document.createElement('div');
    messageDiv.style.marginBottom = '16px';
    messageDiv.style.padding = '12px';
    messageDiv.style.borderRadius = '8px';
    
    if (type === 'user') {
        messageDiv.style.background = '#667eea';
        messageDiv.style.color = 'white';
        messageDiv.style.marginLeft = '20%';
        messageDiv.innerHTML = `<strong>You:</strong><br>${content}`;
    } else if (type === 'claude') {
        messageDiv.style.background = 'white';
        messageDiv.style.border = '1px solid #ddd';
        messageDiv.style.marginRight = '20%';
        messageDiv.innerHTML = `<strong>Claude:</strong><br>${content.replace(/\n/g, '<br>')}`;
    } else {
        messageDiv.style.background = '#f8d7da';
        messageDiv.style.color = '#721c24';
        messageDiv.innerHTML = `<strong>Error:</strong><br>${content}`;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function setPrompt(prompt) {
    document.getElementById('chat-input').value = prompt;
}

// Preview
function setPreviewDevice(device) {
    const iframe = document.getElementById('preview-frame');
    
    if (device === 'mobile') {
        iframe.style.width = '375px';
        iframe.style.margin = '0 auto';
        iframe.style.display = 'block';
    } else if (device === 'tablet') {
        iframe.style.width = '768px';
        iframe.style.margin = '0 auto';
        iframe.style.display = 'block';
    } else {
        iframe.style.width = '100%';
        iframe.style.margin = '0';
        iframe.style.display = 'block';
    }
}

function refreshPreview() {
    const iframe = document.getElementById('preview-frame');
    iframe.src = iframe.src; // Reload iframe
    console.log('Preview refreshed');
}

function openInNewTab() {
    window.open('http://localhost:3000', '_blank');
}

// Utility functions
function copyToClipboard(elementId, text) {
    const textToCopy = text || document.getElementById(elementId).textContent;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

function exportDesign() {
    const exportData = {
        palette: currentPalette,
        svg: currentSVG,
        chatHistory: chatHistory,
        exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `design-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Apply saved theme immediately on page load
(function applyThemeOnLoad() {
    try {
        const saved = localStorage.getItem('dreamairy_theme');
        if (saved) {
            const themeData = JSON.parse(saved);
            if (themeData.palette) {
                applyThemeToDocument(themeData.palette);
                currentPalette = themeData.palette;
                console.log('✨ Applied saved theme on page load');
            }
        }
    } catch (error) {
        console.error('Failed to apply saved theme on load:', error);
    }
})();

// Check Claude status on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE}/api/v1/design/claude/status`);
        const status = await response.json();
        
        if (!status.available) {
            alert('⚠️ Claude service is not available. Please enable AWS services in the admin panel.');
        } else {
            console.log('✅ Claude Design Studio ready');
        }
    } catch (error) {
        console.error('Failed to check Claude status:', error);
    }
});
