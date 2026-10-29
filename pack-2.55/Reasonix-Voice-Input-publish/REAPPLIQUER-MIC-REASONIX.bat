@echo off
setlocal
title Reasonix Voice Input - Mise a jour
cd /d "%~dp0"
echo  [EN] Reapplies the mic patch after a Reasonix Studio update.

echo.
echo  ============================================================
echo    Reasonix Voice Input  -  MISE A JOUR / REPARATION
echo  ============================================================
echo.
echo    A utiliser quand le correctif est deja installe, ou apres
echo    une mise a jour de Reasonix Studio qui a remplace le frontend.
echo.
echo    Le script restaure la sauvegarde propre puis reapplique la
echo    version courante du module.
echo.
echo    Reasonix Studio n'est PAS ferme : recharge la page (Ctrl+R)
echo    ou relance l'application apres l'operation.
echo  ------------------------------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -ScriptPath "%~dp0src\voice-input.reasonix.js" -Force

if errorlevel 1 goto :echec

echo.
echo  ============================================================
echo    MISE A JOUR TERMINEE - recharge Reasonix Studio (Ctrl+R).
echo    Journal : dossier "logs" (patch-ReasonixStudio-*.log)
echo  ============================================================
echo.
pause
exit /b 0

:echec
echo.
echo  ============================================================
echo    ECHEC - voir le detail dans le dossier "logs".
echo  ============================================================
echo.
pause
exit /b 1
