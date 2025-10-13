@echo off
echo ========================================
echo  🎮 Kiro React Demo - Modern Design
echo  Starting React Development Server
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 Checking Node.js...
C:\node-v22.19.0-win-x64\node.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found at expected path
    echo Expected: C:\node-v22.19.0-win-x64\node.exe
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js found!
echo.

echo 📦 Installing/updating dependencies...
C:\node-v22.19.0-win-x64\npm.cmd install --silent
echo ✅ Dependencies ready!
echo.

echo 🚀 Starting React development server...
echo.
echo ========================================
echo  ⚛️ Modern React App: http://localhost:3000
echo  🎨 New design with gradients and glassmorphism
echo  🎭 Logo and modern interface
echo ========================================
echo.
echo 💡 Opening app in browser in 3 seconds...
echo 🔧 Press Ctrl+C to stop the server
echo.

timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo 🎯 Starting React server...
C:\node-v22.19.0-win-x64\npm.cmd start