@echo off
echo Deteniendo todos los servicios de DreamAIry...

echo.
echo Deteniendo backend (Python Flask - puerto 3001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3001') do taskkill /F /PID %%a 2>nul

echo.
echo Deteniendo frontend (React - puerto 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a 2>nul

echo.
echo Deteniendo procesos de Node.js...
taskkill /F /IM node.exe 2>nul

echo.
echo Deteniendo procesos de Python...
taskkill /F /IM python.exe 2>nul

echo.
echo Todos los servicios detenidos.
pause
