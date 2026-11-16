@echo off
cd /d "%~dp0"
title Vina Auto-Factory Controller
echo ===================================================
echo   🏭 VINA AUTO-FACTORY ^& GATEWAY LAUNCHER
echo ===================================================
echo.


echo 1. Checking if local payment webhook gateway is running...
netstat -ano | findstr :8085 > nul
if %errorlevel% equ 0 (
    echo [OK] Local Gateway API is already running on port 8085.
) else (
    echo [STARTING] Launching Local Gateway API on port 8085...
    start "Vina Payment Webhook Gateway" cmd /k "python payment_webhook.py 8085"
)

echo 2. Launching Tunnel Manager in a separate window...
start "Vina Serveo Tunnel Manager" cmd /k "python -u tunnel_manager.py"

echo 3. Starting Vina Auto-Factory Autopilot Daemon...
python run_factory_autopilot.py

pause
