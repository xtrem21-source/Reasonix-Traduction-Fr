@echo off
setlocal
title Reasonix Voice Input - Desinstallation
cd /d "%~dp0"
echo  [EN] Same as RESTAURER: restores index.html and removes voice-input.js.

echo.
echo  ============================================================
echo    Reasonix Voice Input  -  RETOUR A L'ETAT PROPRE
echo  ============================================================
echo.
echo    Restaure index.html depuis index.html.bak et retire
echo    voice-input.js du dossier frontend.
echo.
echo    La sauvegarde index.html.bak est conservee.
echo  ------------------------------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -Rollback

if errorlevel 1 goto :echec

echo.
echo  ============================================================
echo    DESINSTALLATION TERMINEE - recharge Reasonix Studio (Ctrl+R).
echo  ============================================================
echo.
pause
exit /b 0

:echec
echo.
echo  ============================================================
echo    ECHEC - aucune sauvegarde n'a ete retiree.
echo    Voir le detail dans le dossier "logs".
echo  ============================================================
echo.
pause
exit /b 1
