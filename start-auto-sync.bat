@echo off
echo Starting Meta Leads Auto-Sync Server...
echo.
echo Server will start with automatic lead syncing every 5 minutes
echo Access token: EAAgVjAbsIWoBQG62BB2cOAwa0KTl6A9GKAf2UcIJwfVOqZAyV5fVw9SCBE87XQk05CkW5gMZC60aBheUfUB2S9mFhu3HxXWxEwRxwZCFuyzuT3NBqGZCSW8lKCnmnBDCOlubQCws2QgSZAHigxB8YRlXByVlQP7eQvpSUmtoQCJq34YfyI73iPZA0BdGqYKpFQVILCunWs
echo.
echo Available endpoints:
echo - GET http://localhost:3000/leads
echo - POST http://localhost:3000/sync-leads
echo - POST http://localhost:3000/start-auto-sync
echo - POST http://localhost:3000/stop-auto-sync
echo - GET http://localhost:3000/sync-status
echo.
echo Press Ctrl+C to stop the server
echo.

npm install
node app.js

pause