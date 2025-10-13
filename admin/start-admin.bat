@echo off
echo ========================================
echo  🎮 Kiro Admin Server
echo  Starting Real Server Management Panel
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 Checking Node.js...
C:\node-v22.19.0-win-x64\node.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found at expected path
    echo Expected: C:\node-v22.19.0-win-x64\node.exe
    echo.
    echo Please check if Node.js is installed at the correct path
    pause
    exit /b 1
)
echo ✅ Node.js found!
echo.

echo 📦 Installing admin dependencies...
C:\node-v22.19.0-win-x64\npm.cmd install --silent
echo ✅ Dependencies ready!
echo.

echo 🚀 Starting Admin Server...
echo.
echo ========================================
echo  🎮 Admin Panel will be available at:
echo     http://localhost:3002/real-admin.html
echo ========================================
echo.
echo 💡 Opening admin panel in 3 seconds...
echo 🔧 Use this panel to start/stop servers
echo.

timeout /t 3 /nobreak >nul
start "" "http://localhost:3002/real-admin.html"

echo 🎯 Starting admin server...
echo.
C:\node-v22.19.0-win-x64\node.exe admin-server.js