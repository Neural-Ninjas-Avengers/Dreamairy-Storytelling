@echo off
title DreamAIry Frontend Server
color 0B
echo ========================================
echo    DreamAIry Frontend Server
echo ========================================
echo.
echo Iniciando servidor frontend...
echo Puerto: 3000
echo URL: http://localhost:3000
echo.
echo Verificando dependencias...
cd frontend
if not exist node_modules (
    echo Instalando dependencias...
    cmd /c npm install
)
echo.
echo Iniciando React development server...
echo Para parar el servidor: Ctrl+C
echo ========================================
echo.
cmd /c npm start
echo.
echo ========================================
echo Frontend detenido.
echo ========================================
pause