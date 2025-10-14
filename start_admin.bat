@echo off
echo ========================================
echo    DreamAIry Admin Panel
echo ========================================
echo.
echo Iniciando Control Server...
echo.

REM Iniciar el control server en segundo plano
start "DreamAIry Control Server" cmd /k "cd /d %~dp0 && python admin\control_server.py"

REM Esperar 3 segundos para que el control server inicie
echo Esperando a que el control server inicie...
timeout /t 3 /nobreak

REM Abrir el panel de admin
echo Abriendo panel de administracion...
start "" "%~dp0admin\index.html"

echo.
echo ========================================
echo Control Server: http://localhost:3002
echo Admin Panel abierto en tu navegador
echo ========================================
echo.
echo INSTRUCCIONES:
echo 1. Usa los botones para iniciar Backend/Frontend
echo 2. Configura AWS si es necesario
echo 3. Prueba los servicios
echo.
echo Presiona cualquier tecla para salir (el servidor seguira corriendo)...
pause
