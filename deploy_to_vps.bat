@echo off
echo ==========================================
echo DEPLOYING CRM UPDATES TO VPS
echo ==========================================

REM Replace with your VPS IP
set VPS_IP=your-vps-ip-here
set VPS_USER=root
set VPS_PATH=/var/www/bopcrm

echo.
echo Step 1: Uploading views.py...
scp leads\views.py %VPS_USER%@%VPS_IP%:%VPS_PATH%/leads/

echo.
echo Step 2: Uploading management commands...
scp -r leads\management %VPS_USER%@%VPS_IP%:%VPS_PATH%/leads/

echo.
echo Step 3: Connecting to VPS to run sync...
echo.
echo Run these commands on your VPS:
echo   cd /var/www/bopcrm
echo   source venv/bin/activate
echo   python manage.py sync_meta_leads
echo   sudo systemctl restart crm nginx
echo.
pause
