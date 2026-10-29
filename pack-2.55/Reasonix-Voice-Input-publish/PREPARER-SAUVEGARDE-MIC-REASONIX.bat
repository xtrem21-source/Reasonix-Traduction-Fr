@echo off
setlocal
title Reasonix Voice Input - Preparer la sauvegarde
cd /d "%~dp0"
echo  [EN] Creates and verifies index.html.bak without patching anything.

echo.
echo  ============================================================
echo    Reasonix Voice Input  -  POINT DE RETOUR
echo  ============================================================
echo.
echo    Ce script ne modifie PAS l'application.
echo.
echo    Il cree et verifie une copie de securite de :
echo      resources\frontend-next\dist\index.html
echo    dans :
echo      index.html.bak
echo      index.html.bak.sha256
echo    et une archive datee dans le dossier "old".
echo.
echo    Tu peux ensuite lancer REAPPLIQUER-MIC-REASONIX.bat en
echo    sachant que le retour arriere est pret.
echo  ------------------------------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\apply-patch.ps1" -BackupOnly

if errorlevel 1 goto :echec

echo.
echo  ============================================================
echo    SAUVEGARDE PRETE ET VERIFIEE.
echo    Pour revenir en arriere plus tard :
echo      RESTAURER-MIC-REASONIX.bat
echo  ============================================================
echo.
pause
exit /b 0

:echec
echo.
echo  ============================================================
echo    ECHEC - aucune modification n'a ete faite.
echo    Voir le detail dans le dossier "logs".
echo  ============================================================
echo.
pause
exit /b 1
