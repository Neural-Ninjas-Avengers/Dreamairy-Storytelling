// Debug script for frontend image generation
// Run this in the browser console when the frontend is loaded

console.log('🔍 Debugging Frontend Image Generation');

// Test the StorytellingService directly
async function testFrontendImageGeneration() {
    console.log('📝 Testing frontend image generation...');
    
    // Check if StorytellingService is available
    if (typeof window.storyService === 'undefined') {
        console.log('⚠️ StorytellingService not found in window object');
        console.log('💡 This script should be run when the app is loaded');
        return;
    }
    
    try {
        // Create a test session
        console.log('📝 Creating test session...');
        const session = await window.storyService.createSession({
            age: 6,
            preferences: ['animals'],
            emotional_goal: 'entertain',
            anonymous_id: 'debug_test'
        });
        
        console.log('✅ Session created:', session.session_id);
        
        // Test image generation
        console.log('🎨 Testing image generation...');
        const imageRequest = {
            scene_description: 'Un pequeño conejo en un bosque mágico',
            story_context: 'Historia de prueba',
            character_description: 'Conejo amigable',
            style: 'children_book',
            has_user_photo: false,
            theme: 'animals',
            emotional_goal: 'entertain',
            child_age: 6
        };
        
        const result = await window.storyService.generateStoryImage(session.session_id, imageRequest);
        
        console.log('✅ Image generation result:', result);
        
        if (result && result.image_url) {
            console.log('✅ Image URL received:', result.image_url.substring(0, 100) + '...');
            
            // Try to display the image
            const img = document.createElement('img');
            img.src = result.image_url;
            img.style.maxWidth = '300px';
            img.style.border = '2px solid #00ff00';
            img.title = 'Debug Generated Image';
            
            document.body.appendChild(img);
            console.log('✅ Image added to page for visual verification');
        } else {
            console.log('❌ No image URL in result');
        }
        
    } catch (error) {
        console.error('❌ Error during frontend test:', error);
        console.log('📊 Error details:', {
            message: error.message,
            stack: error.stack
        });
    }
}

// Check network requests
function monitorNetworkRequests() {
    console.log('🌐 Monitoring network requests for image generation...');
    
    // Override fetch to monitor requests
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && url.includes('generate-image')) {
            console.log('🌐 Image generation request detected:', url);
            console.log('📝 Request details:', args);
        }
        
        return originalFetch.apply(this, args).then(response => {
            if (typeof url === 'string' && url.includes('generate-image')) {
                console.log('📥 Image generation response:', response.status, response.statusText);
            }
            return response;
        }).catch(error => {
            if (typeof url === 'string' && url.includes('generate-image')) {
                console.error('❌ Image generation request failed:', error);
            }
            throw error;
        });
    };
    
    console.log('✅ Network monitoring active');
}

// Check if backend is reachable
async function testBackendConnection() {
    console.log('🔗 Testing backend connection...');
    
    try {
        const response = await fetch('http://localhost:3001/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is reachable:', data);
        } else {
            console.log('⚠️ Backend responded with error:', response.status);
        }
    } catch (error) {
        console.error('❌ Cannot reach backend:', error);
        console.log('💡 Make sure backend is running on port 3001');
    }
}

// Main debug function
async function debugImageGeneration() {
    console.log('🚀 Starting image generation debug...');
    
    await testBackendConnection();
    monitorNetworkRequests();
    
    // Wait a bit for the app to load
    setTimeout(() => {
        testFrontendImageGeneration();
    }, 2000);
}

// Auto-run if this script is loaded
debugImageGeneration();

console.log('📋 Debug commands available:');
console.log('- testFrontendImageGeneration() - Test image generation');
console.log('- testBackendConnection() - Test backend connection');
console.log('- monitorNetworkRequests() - Monitor network requests');