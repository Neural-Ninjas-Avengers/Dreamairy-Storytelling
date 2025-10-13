@echo off
echo 🎮 DreamAIry Launcher
echo ==================

:menu
echo.
echo Choose what to start:
echo 1. Backend only (Python)
echo 2. Frontend only (React)  
echo 3. Both (Full System)
echo 4. Test Backend
echo 5. Open Admin Panel
echo 6. Exit
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto test
if "%choice%"=="5" goto admin
if "%choice%"=="6" goto exit
echo Invalid choice, try again.
goto menu

:backend
echo 🐍 Starting Python Backend...
cd backend
python app.py
cd ..
goto menu

:frontend
echo ⚛️ Starting React Frontend...
cd frontend
npm start
cd ..
goto menu

:both
echo 🚀 Starting Full System...
echo Starting backend first...
start "DreamAIry Backend" cmd /k "cd backend && python app.py"
timeout /t 5 /nobreak
echo Starting frontend...
cd frontend
npm start
cd ..
goto menu

:test
echo 🧪 Testing Backend...
python scripts/quick_test.py
pause
goto menu

:admin
echo 🌐 Opening Admin Panel...
start admin/simple-admin.html
goto menu

:exit
echo 👋 Goodbye!
pause