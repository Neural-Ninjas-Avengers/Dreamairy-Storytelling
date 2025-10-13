@echo off
echo ========================================
echo   🎮 Kiro - Complete System Startup
echo   Starting Everything!
echo ========================================
echo.

echo 🔍 Checking system requirements...
echo.

REM Check Python
echo Checking Python...
C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    pause
    exit /b 1
)
echo ✅ Python found!

REM Check Node.js
echo Checking Node.js...
C:\node-v22.19.0-win-x64\node.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found
    pause
    exit /b 1
)
echo ✅ Node.js found!

echo.
echo 🚀 Starting Admin Panel...
echo.

REM Check if admin dependencies are installed
if not exist "..\admin\node_modules" (
    echo 📦 Installing admin dependencies...
    cd ..\admin
    C:\node-v22.19.0-win-x64\npm.cmd install --silent
    cd ..\scripts
    echo ✅ Admin dependencies installed!
)

REM Start admin server in background
start "Kiro Admin Server" /min cmd /c "cd ..\admin && C:\node-v22.19.0-win-x64\node.exe admin-server.js"

REM Wait a moment for admin server to start
echo ⏳ Waiting for admin server to start...
timeout /t 5 /nobreak >nul

echo ✅ Admin Panel started on http://localhost:3002
echo.
echo 🌐 Opening Admin Panel in browser...
echo.

REM Open admin panel
start http://localhost:3002/real-admin.html

echo.
echo ========================================
echo   🎮 System Status:
echo   ✅ Admin Panel: Running (Port 3002)
echo   ⏳ Python Backend: Use admin panel to start
echo   ⏳ React Frontend: Use admin panel to start
echo ========================================
echo.
echo 💡 Use the admin panel to start Python and React servers
echo 🎯 Click "START EVERYTHING" in the admin panel
echo.
echo Press any key to exit this window...
pause >nul