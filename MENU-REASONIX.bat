@echo off
setlocal EnableExtensions
title Reasonix Studio 2.47 - outils
set "ROOT=%~dp0"
set "MIC=%ROOT%Reasonix-Voice-Input-publish"
set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "STAMP=%%i"
set "LOG=%ROOT%logs\menu-%STAMP%.log"

call :log "=== ouverture %DATE% %TIME% ==="
call :log "dossier : %ROOT%"

rem mode ligne de commande : MENU-REASONIX.bat fr | mic | both
if /I "%~1"=="fr" goto :arg_fr
if /I "%~1"=="mic" goto :arg_mic
if /I "%~1"=="both" goto :arg_both
goto :menu_affichage

:arg_fr
set "NO_PAUSE=1"
call :do_fr
goto :fin

:arg_mic
set "NO_PAUSE=1"
call :do_mic
goto :fin

:arg_both
set "NO_PAUSE=1"
call :do_fr
call :do_mic
goto :fin

:menu_affichage
cls
echo ============================================================
echo    Reasonix Studio 2.47 - outils
echo ============================================================
echo.
echo    1. Patch francais      (interface + menu contextuel)
echo    2. Integrer le micro   (bouton dictee dans l'interface)
echo    3. Les deux
echo    4. Quitter
echo.
echo    Journal de cette session :
echo      %LOG%
echo.
echo    Rappel : le menu contextuel (clic droit) exige que
echo    Reasonix Studio soit FERME - icone de la zone de
echo    notification, clic droit, Quitter.
echo.
set "choix="
set /p "choix=Votre choix [1-4] : "

if "%choix%"=="1" ( call :do_fr  & goto :menu_affichage )
if "%choix%"=="2" ( call :do_mic & goto :menu_affichage )
if "%choix%"=="3" ( call :do_fr  & call :do_mic & goto :menu_affichage )
if "%choix%"=="4" goto :fin
call :log "choix invalide : %choix%"
goto :menu_affichage

:do_fr
cls
echo [1/2] Patch francais de l'interface...
call :log ""
call :log "--- patch francais %TIME% ---"
"%PY%" "%ROOT%tools\patch247.py" > "%TEMP%\rx-fr-1.txt" 2>&1
if errorlevel 1 (set "OK1=0") else (set "OK1=1")
type "%TEMP%\rx-fr-1.txt"
type "%TEMP%\rx-fr-1.txt" >> "%LOG%"
if "%OK1%"=="1" (call :log "frontend : OK") else (call :log "frontend : ECHEC")

echo.
echo [2/2] Chaines natives (menu contextuel)...
"%PY%" "%ROOT%tools\patch_asar247.py" > "%TEMP%\rx-fr-2.txt" 2>&1
if errorlevel 1 (set "OK2=0") else (set "OK2=1")
type "%TEMP%\rx-fr-2.txt"
type "%TEMP%\rx-fr-2.txt" >> "%LOG%"
if "%OK2%"=="1" (call :log "natif : OK") else (call :log "natif : ECHEC")

echo.
if "%OK1%"=="1" (echo  [OK] Interface traitee.) else (echo  [!] Interface : echec, voir le journal.)
if "%OK2%"=="1" (echo  [OK] Menu contextuel applique ou deja en place.) else (echo  [!] Menu contextuel non applique : quitte Reasonix Studio puis relance l'option 1.)
echo.
if not defined NO_PAUSE pause
exit /b 0

:do_mic
cls
echo [MIC] Integration du bouton dictee...
call :log ""
call :log "--- micro %TIME% ---"
if not exist "%MIC%\scripts\apply-patch.ps1" (
  echo  [!] Dossier micro introuvable : %MIC%
  call :log "micro : dossier introuvable"
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%MIC%\scripts\apply-patch.ps1" -ScriptPath "%MIC%\src\voice-input.reasonix.js" -Force -LogFile "%LOG%" > "%TEMP%\rx-mic.txt" 2>&1
if errorlevel 1 (set "OK3=0") else (set "OK3=1")
type "%TEMP%\rx-mic.txt"
type "%TEMP%\rx-mic.txt" >> "%LOG%"
if "%OK3%"=="1" (call :log "micro : OK") else (call :log "micro : ECHEC")

echo.
if "%OK3%"=="1" (
  echo  [OK] Micro integre. Recharge la page ^(Ctrl+R^) ou relance l'application.
  echo       Clic droit sur le micro pour saisir ta cle Gemini.
) else (
  echo  [!] Echec du micro - voir le journal.
)
echo.
if not defined NO_PAUSE pause
exit /b 0

:log
echo %~1>>"%LOG%"
exit /b 0

:fin
call :log "=== fermeture %DATE% %TIME% ==="
exit /b 0
