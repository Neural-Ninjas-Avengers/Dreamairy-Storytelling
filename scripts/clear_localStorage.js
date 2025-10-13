// Script to clear localStorage and fix quota issues
// Run this in the browser console

console.log('🧹 Clearing localStorage to fix quota issues...');

// Check current localStorage usage
let totalSize = 0;
let itemCount = 0;

for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
        const value = localStorage.getItem(key);
        const size = new Blob([value]).size;
        totalSize += size;
        itemCount++;
        
        if (size > 100000) { // Items larger than 100KB
            console.log(`📦 Large item found: ${key} (${(size/1024/1024).toFixed(2)} MB)`);
        }
    }
}

console.log(`📊 Current localStorage usage:`);
console.log(`   - Total items: ${itemCount}`);
console.log(`   - Total size: ${(totalSize/1024/1024).toFixed(2)} MB`);

// Clear photo-related items
let photosCleared = 0;
let sizeFreed = 0;

for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
        if (key.startsWith('photo_') || key.includes('base64') || key.includes('image')) {
            const value = localStorage.getItem(key);
            const size = new Blob([value]).size;
            sizeFreed += size;
            photosCleared++;
            
            localStorage.removeItem(key);
            console.log(`🗑️ Removed: ${key} (${(size/1024/1024).toFixed(2)} MB)`);
        }
    }
}

console.log(`✅ Cleanup complete:`);
console.log(`   - Photos removed: ${photosCleared}`);
console.log(`   - Space freed: ${(sizeFreed/1024/1024).toFixed(2)} MB`);

// Check remaining usage
let remainingSize = 0;
let remainingItems = 0;

for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
        const value = localStorage.getItem(key);
        remainingSize += new Blob([value]).size;
        remainingItems++;
    }
}

console.log(`📊 Remaining localStorage usage:`);
console.log(`   - Items: ${remainingItems}`);
console.log(`   - Size: ${(remainingSize/1024/1024).toFixed(2)} MB`);

console.log('🎉 localStorage cleaned! Photo uploads should work now.');

// Optional: Clear everything if needed
function clearEverything() {
    localStorage.clear();
    console.log('🧹 All localStorage cleared!');
}

console.log('💡 If you still have issues, run: clearEverything()');