@echo off
echo ========================================
echo   🎮 DreamAIry Admin Panel
echo   Neural Ninjas Avengers
echo ========================================
echo.

echo 🔍 Checking Node.js...
C:\node-v22.19.0-win-x64\node.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found
    echo Expected path: C:\node-v22.19.0-win-x64\node.exe
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js found!
echo.

echo 📂 Checking project structure...
if not exist "..\admin" (
    echo ❌ ERROR: Admin directory not found
    echo Expected: ..\admin from scripts directory
    echo Current directory: %CD%
    echo.
    echo 💡 Make sure you're running this from the scripts directory
    echo 💡 Or run: scripts\start_admin.bat from project root
    echo.
    pause
    exit /b 1
)

if not exist "..\frontend" (
    echo ⚠️  WARNING: Frontend directory not found
    echo Expected: ..\frontend
)

if not exist "..\backend" (
    echo ⚠️  WARNING: Backend directory not found  
    echo Expected: ..\backend
)

echo ✅ Project structure verified!
echo.

echo 📂 Changing to admin directory...
cd ..\admin

echo 📦 Checking dependencies...
if not exist "node_modules" (
    echo 📦 Installing admin dependencies...
    C:\node-v22.19.0-win-x64\npm.cmd install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies ready!
echo.

echo 🚀 Starting Admin Server...
echo.
echo ========================================
echo  🎮 Admin Panel: http://localhost:3002
echo  🌐 Direct Admin: http://localhost:3002/real-admin.html
echo  📊 Simple View: http://localhost:3002/index.html
echo ========================================
echo.

echo 💡 Opening admin panel in browser...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3002/real-admin.html"

echo.
echo 🎯 Admin server starting...
echo 📝 Use the web interface to start/stop services
echo 🛑 Press Ctrl+C to stop the admin server
echo.

C:\node-v22.19.0-win-x64\node.exe admin-server.js