@echo off
echo ========================================
echo   🚀 DreamAIry Backend Server
echo   Neural Ninjas Avengers
echo ========================================
echo.

echo 🔍 Checking Python...
C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    echo Expected path: C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe
    echo.
    pause
    exit /b 1
)
echo ✅ Python found!

echo 📂 Checking backend directory...
if not exist "backend" (
    echo ❌ ERROR: Backend directory not found
    echo Expected: backend directory in project root
    echo Current directory: %CD%
    echo.
    echo 💡 Make sure you're running this from the project root
    echo 💡 Or run: scripts\start_server.bat from project root
    echo.
    pause
    exit /b 1
)

if not exist "backend\app.py" (
    echo ❌ ERROR: app.py not found
    echo Expected: backend\app.py
    echo.
    pause
    exit /b 1
)

echo ✅ Backend files found!
echo.

echo 📂 Changing to backend directory...
cd backend

echo 🔧 Checking dependencies...
C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Flask not found, installing dependencies...
    C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies ready!
echo.

echo 🚀 Starting DreamAIry Backend Server...
echo.
echo ========================================
echo  🌐 Backend API: http://localhost:3001
echo  🔍 Health Check: http://localhost:3001/health
echo  📊 System Status: http://localhost:3001/api/v1/system/status
echo ========================================
echo.
echo 💡 Server starting in DEMO MODE (no AWS costs)
echo 🛑 Press Ctrl+C to stop the server
echo.

C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe app.py

echo.
echo 🛑 Server stopped
pause