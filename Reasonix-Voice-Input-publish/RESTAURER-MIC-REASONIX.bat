@echo off
setlocal
title Reasonix Voice Input - Retour arriere
cd /d "%~dp0"
echo  [EN] Restores index.html and removes voice-input.js (works if the app won't start).

echo.
echo  ============================================================
echo    Reasonix Voice Input  -  RETOUR ARRIERE
echo  ============================================================
echo.
echo    Restaure index.html depuis la sauvegarde verifiee
echo      index.html.bak
echo    et retire voice-input.js du dossier frontend.
echo.
echo    La sauvegarde et son empreinte sont conservees.
echo    Fonctionne meme si Reasonix Studio ne demarre plus :
echo    ferme-le (gestionnaire de taches si besoin), lance ce
echo    script, puis relance l'application.
echo  ------------------------------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -Rollback

if errorlevel 1 goto :echec

echo.
echo  ============================================================
echo    RETOUR ARRIERE TERMINE - relance Reasonix Studio.
echo  ============================================================
echo.
pause
exit /b 0

:echec
echo.
echo  ============================================================
echo    ECHEC - rien n'a ete restaure.
echo    La sauvegarde est ici :
echo      resources\frontend-next\dist\index.html.bak
echo    Voir le detail dans le dossier "logs".
echo  ============================================================
echo.
pause
exit /b 1
