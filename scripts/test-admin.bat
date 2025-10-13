@echo off
echo ========================================
echo   🧪 Testing Admin Panel
echo ========================================
echo.

echo 🔍 Checking admin directory...
if not exist "..\admin" (
    echo ❌ ERROR: Admin directory not found
    pause
    exit /b 1
)
echo ✅ Admin directory found!

echo.
echo 📂 Changing to admin directory...
cd ..\admin

echo.
echo 🔍 Checking admin files...
if not exist "admin-server.js" (
    echo ❌ ERROR: admin-server.js not found
    pause
    exit /b 1
)
echo ✅ admin-server.js found!

if not exist "package.json" (
    echo ❌ ERROR: package.json not found
    pause
    exit /b 1
)
echo ✅ package.json found!

echo.
echo 📦 Installing dependencies if needed...
if not exist "node_modules" (
    echo Installing admin dependencies...
    C:\node-v22.19.0-win-x64\npm.cmd install
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed!
) else (
    echo ✅ Dependencies already installed!
)

echo.
echo 🚀 Starting admin server...
echo.
echo ========================================
echo  🎮 Admin Panel will be available at:
echo  http://localhost:3002
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

C:\node-v22.19.0-win-x64\node.exe admin-server.js