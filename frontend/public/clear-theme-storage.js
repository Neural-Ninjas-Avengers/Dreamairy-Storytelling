// Auto-clear theme storage on app load
(function() {
    try {
        const themeKey = 'dreamairy_theme';
        if (localStorage.getItem(themeKey)) {
            console.log('🧹 Clearing old theme data...');
            localStorage.removeItem(themeKey);
            console.log('✅ Theme data cleared');
        }
    } catch (error) {
        console.error('Failed to clear theme data:', error);
    }
})();
