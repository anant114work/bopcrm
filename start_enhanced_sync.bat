@echo off
echo ========================================
echo Enhanced Meta Sync Service
echo Syncing 2000+ forms every minute
echo ========================================
echo.

cd /d "d:\AI-proto\CRM\drip"

echo Starting enhanced Meta sync service...
python start_enhanced_meta_sync.py

pause