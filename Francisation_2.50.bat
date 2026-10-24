@echo off
setlocal EnableExtensions
title Francisation Reasonix 2.50
set "ROOT=%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

if not defined REASONIX_STUDIO_DIR set "REASONIX_STUDIO_DIR=%LOCALAPPDATA%\Programs\Reasonix Studio"

echo ============================================
echo  Francisation Reasonix Studio 2.50
echo ============================================
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

tasklist /FI "IMAGENAME eq Reasonix Studio.exe" /NH 2>$null | find /I "Reasonix Studio.exe" >$null
if not errorlevel 1 (
  echo Reasonix Studio est ouvert.
  echo Ferme-le completement ^(zone de notification : Quitter^), puis relance ce fichier.
  echo.
  pause
  exit /b 1
)

echo [1/2] Interface ^(frontend^)...
"%PY%" "%ROOT%scripts\patch250.py"
if errorlevel 1 goto :err

echo [2/2] Langue automatique...
"%PY%" "%ROOT%scripts\force_auto_fr.py"
if errorlevel 1 goto :err

echo.
echo TERMINE.
echo Relance Reasonix Studio. L'interface doit s'ouvrir en francais.
echo.
pause
exit /b 0

:err
echo.
echo ECHEC. Lis le message ci-dessus.
echo Sauvegardes : %ROOT%backups
pause
exit /b 1
