@echo off
rem Lance le pont OpenCode pour Reasonix (port 31416 par defaut).
cd /d "%~dp0"
node "%~dp0server.mjs"
