@echo off
setlocal
title Francir le menu clic droit
set "EXE=J:\Reasonix Studio\Reasonix Studio.exe"
set "TRAVAIL=J:\Reasonix\dev\voix-winh"

echo ============================================================
echo   Menu clic droit en francais
echo   Studio va se fermer, etre corrige, puis se relancer.
echo ============================================================
echo.
echo Fermeture de Studio...
"%SystemRoot%\System32\taskkill.exe" /IM "Reasonix Studio.exe" >nul 2>&1
"%SystemRoot%\System32\ping.exe" -n 8 127.0.0.1 >nul
"%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq Reasonix Studio.exe" | "%SystemRoot%\System32\find.exe" /I "Reasonix Studio.exe" >nul
if not errorlevel 1 (
    echo Encore ouverte : fermeture forcee...
    "%SystemRoot%\System32\taskkill.exe" /F /IM "Reasonix Studio.exe" >nul 2>&1
    "%SystemRoot%\System32\ping.exe" -n 5 127.0.0.1 >nul
)
echo Studio ferme.
echo.

cd /d "%TRAVAIL%"
python "%TRAVAIL%\patch_asar_menu.py"
set "CODE=%ERRORLEVEL%"
echo code de sortie : %CODE%
echo.

if not "%CODE%"=="0" (
    echo ECHEC - voir %TRAVAIL%\patch-menu.log
    echo.
    pause
    exit /b 1
)

echo Relance de Studio (par l'Explorateur)...
explorer.exe "%EXE%"
echo.
echo Termine. Fais un clic droit dans le composeur : le menu doit etre en francais.
pause
