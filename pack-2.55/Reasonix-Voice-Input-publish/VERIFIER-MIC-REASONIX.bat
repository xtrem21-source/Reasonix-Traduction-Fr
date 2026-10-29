@echo off
setlocal
title Reasonix Voice Input - Verification
cd /d "%~dp0"
echo  [EN] Read-only check: script tag, module hash, verified backup.

echo.
echo  Verification de l'etat du patch (lecture seule)...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -Check -ScriptPath "%~dp0src\voice-input.reasonix.js"

if errorlevel 1 goto :absente

echo.
echo  Etat : PATCH PRESENT, voice-input.js identique a la source,
echo         sauvegarde index.html.bak presente et verifiee.
echo.
pause
exit /b 0

:absente
echo.
echo  Etat : patch absent/incomplet, ou sauvegarde manquante/non verifiee.
echo  Utilise REAPPLIQUER-MIC-REASONIX.bat ou, en cas de probleme,
echo  RESTAURER-MIC-REASONIX.bat.
echo.
pause
exit /b 1
