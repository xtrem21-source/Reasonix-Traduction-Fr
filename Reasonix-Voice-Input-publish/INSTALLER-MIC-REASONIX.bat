@echo off
setlocal
title Reasonix Voice Input - Installation
cd /d "%~dp0"
echo  [EN] Installs the mic patch after verifying a backup. Rollback: RESTAURER-MIC-REASONIX.bat

echo.
echo  ============================================================
echo    Reasonix Voice Input  -  bouton micro pour Reasonix Studio
echo  ============================================================
echo.
echo    Ce script :
echo      1. sauvegarde resources\frontend-next\dist\index.html
echo      2. ajoute voice-input.js a cote
echo      3. injecte une balise script dans index.html
echo.
echo    Reasonix Studio n'est PAS ferme : apres l'installation,
echo    recharge la page (Ctrl+R) ou relance l'application.
echo.
echo    Un journal (.log) est ecrit dans le dossier logs.
echo  ------------------------------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -ScriptPath "%~dp0src\voice-input.reasonix.js" -Force

if errorlevel 1 goto :echec

echo.
echo  ============================================================
echo    TERMINE - correctif applique.
echo.
echo    EN CAS DE PROBLEME :
echo      double-clique RESTAURER-MIC-REASONIX.bat
echo    (la sauvegarde index.html.bak est creee et verifiee
echo     avant toute modification).
echo.
echo    Recharge Reasonix Studio (Ctrl+R) ou relance-le, puis :
echo      - clic droit sur le micro  ^>  colle ta cle Gemini
echo      - Enregistrer, puis Tester la cle Gemini
echo.
echo    Journal : dossier "logs" (patch-ReasonixStudio-*.log)
echo  ============================================================
echo.
pause
exit /b 0

:echec
echo.
echo  ============================================================
echo    ECHEC - voir le detail dans le dossier "logs".
echo    Si l'application a ete mise a jour, relance ce script.
echo  ============================================================
echo.
pause
exit /b 1
