@echo off
setlocal EnableExtensions
title Reasonix Studio FR 2.52
set "ROOT=%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

rem Installation location. Override it before launching if yours differs:
rem   set "REASONIX_STUDIO_DIR=J:\Reasonix Studio"
if not defined REASONIX_STUDIO_DIR set "REASONIX_STUDIO_DIR=%LOCALAPPDATA%\Programs\Reasonix Studio"

rem Fallback language when nothing is saved: fr, en or auto.
if not defined REASONIX_UI_DEFAULT set "REASONIX_UI_DEFAULT=fr"

echo ============================================
echo  Reasonix Studio FR 2.52
echo ============================================
echo  Installation     : %REASONIX_STUDIO_DIR%
echo  Langue par defaut: %REASONIX_UI_DEFAULT%
echo.

if not exist "%REASONIX_STUDIO_DIR%\resources\frontend-next\dist\index.html" (
  echo ERREUR : Reasonix Studio est introuvable.
  echo Cherche : %REASONIX_STUDIO_DIR%
  echo.
  echo Si l'application est ailleurs, definis REASONIX_STUDIO_DIR avant de lancer :
  echo   set "REASONIX_STUDIO_DIR=J:\Reasonix Studio"
  echo.
  pause
  exit /b 1
)

tasklist /FI "IMAGENAME eq Reasonix Studio.exe" /NH 2>nul | find /I "Reasonix Studio.exe" >nul
if not errorlevel 1 (
  echo Reasonix Studio est ouvert.
  echo Ferme-le completement ^(zone de notification : Quitter^), puis relance ce fichier.
  echo.
  pause
  exit /b 1
)

echo [1/1] Interface : dictionnaire, selecteur, langue par defaut...
"%PY%" "%ROOT%scripts\patch252.py" --default-lang %REASONIX_UI_DEFAULT%
if errorlevel 1 goto :err

echo.
echo TERMINE.
echo Relance Reasonix Studio : l'interface doit s'ouvrir en francais.
echo Sauvegardes : %ROOT%work\backup
echo.
pause
exit /b 0

:err
echo.
echo ECHEC. Lis le message ci-dessus.
echo Sauvegardes : %ROOT%work\backup
pause
exit /b 1
