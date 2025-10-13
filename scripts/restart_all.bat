@echo off
echo ========================================
echo   🔄 DreamAIry Complete Restart
echo   Neural Ninjas Avengers
echo ========================================
echo.

echo 🛑 Stopping all running processes...

REM Kill any existing processes on our ports
echo 🔍 Checking for processes on port 3000 (React)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Killing process %%a on port 3000
    taskkill /f /pid %%a >nul 2>&1
)

echo 🔍 Checking for processes on port 3001 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3001') do (
    echo Killing process %%a on port 3001
    taskkill /f /pid %%a >nul 2>&1
)

echo 🔍 Checking for processes on port 3002 (Admin)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3002') do (
    echo Killing process %%a on port 3002
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ All processes stopped
echo.

echo 🧹 Cleaning up...
timeout /t 2 /nobreak >nul

echo 📦 Checking dependencies...

REM Check backend dependencies
echo 🐍 Checking Python dependencies...
cd ..\backend
C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Python dependencies...
    C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt
)
echo ✅ Python dependencies ready

REM Check frontend dependencies
echo ⚛️ Checking React dependencies...
cd ..\frontend
if not exist "node_modules" (
    echo 📦 Installing React dependencies...
    C:\node-v22.19.0-win-x64\npm.cmd install
)
echo ✅ React dependencies ready

REM Check admin dependencies
echo 🎮 Checking Admin dependencies...
cd ..\admin
if not exist "node_modules" (
    echo 📦 Installing Admin dependencies...
    C:\node-v22.19.0-win-x64\npm.cmd install
)
echo ✅ Admin dependencies ready

cd ..\scripts
echo.

echo 🚀 Starting all services...
echo.

REM Start Admin Panel
echo 🎮 Starting Admin Panel...
start "DreamAIry Admin" /min cmd /c "cd ..\admin && C:\node-v22.19.0-win-x64\node.exe admin-server.js"
timeout /t 3 /nobreak >nul

REM Start Backend
echo 🔧 Starting Backend Server...
start "DreamAIry Backend" cmd /c "cd ..\backend && C:\Users\fernando.bori\AppData\Local\Programs\Python\Python313\python.exe app.py"
timeout /t 5 /nobreak >nul

REM Start Frontend
echo 🎨 Starting Frontend...
start "DreamAIry Frontend" cmd /c "cd ..\frontend && C:\node-v22.19.0-win-x64\npm.cmd start"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   🎉 DreamAIry System Started!
echo ========================================
echo.
echo 🌐 Services Available:
echo   🎨 Frontend:  http://localhost:3000
echo   🔧 Backend:   http://localhost:3001
echo   🎮 Admin:     http://localhost:3002
echo.
echo 🔍 Health Checks:
echo   Backend:      http://localhost:3001/health
echo   Admin:        http://localhost:3002/health
echo.
echo 💡 Opening services in browser...
timeout /t 5 /nobreak >nul

start http://localhost:3000
start http://localhost:3002/real-admin.html

echo.
echo ✅ All services started successfully!
echo 📝 Check the individual terminal windows for logs
echo 🛑 Close terminal windows to stop services
echo.
pause