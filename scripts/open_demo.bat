@echo off
echo ========================================
echo   Kiro - Opening Demo Interface
echo ========================================
echo.
echo Opening new welcome page in browser...
echo.

start http://localhost:3001/demo/welcome.html/welcome.html

echo.
echo If the page doesn't load, make sure the server is running first.
echo Run start_server.bat to start the server.
echo.
pause