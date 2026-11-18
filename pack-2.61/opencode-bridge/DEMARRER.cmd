@echo off
rem Lance le pont OpenCode en tache de fond, journal dans pont.log.
cd /d "%~dp0"
"C:\Program Files\nodejs\node.exe" "%~dp0server.mjs" >> "%~dp0pont.log" 2>&1
