@echo off
title DreamAIry Backend Server
color 0A
echo ========================================
echo    DreamAIry Backend Server
echo ========================================
echo.
echo Iniciando servidor backend...
echo Puerto: 3001
echo URL: http://localhost:3001
echo.
echo Para parar el servidor: Ctrl+C
echo ========================================
echo.
cd backend
python app.py
echo.
echo ========================================
echo Backend detenido.
echo ========================================
pause