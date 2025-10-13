@echo off
title Kiro Admin Panel
echo 🎮 Starting Kiro Admin Panel...

cd admin
start "" "http://localhost:3002/real-admin.html"
C:\node-v22.19.0-win-x64\node.exe admin-server.js