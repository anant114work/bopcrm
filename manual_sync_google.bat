@echo off
echo Syncing SPJ Google Sheets...
python manage.py sync_spj_sheets
echo.
echo Sync complete!
pause
