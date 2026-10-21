@echo off
setlocal EnableExtensions
title Francisation Reasonix 2.47
set "ROOT=%~dp0"
set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================
echo  Francisation Reasonix Studio 2.47
echo ============================================
echo.

if not exist "%LOCALAPPDATA%\Programs\Reasonix Studio\resources\frontend-next\dist\index.html" (
  echo ERREUR : Reasonix Studio est introuvable.
  echo Attendu : %LOCALAPPDATA%\Programs\Reasonix Studio
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

echo [1/2] Interface ^(frontend^)...
"%PY%" "%ROOT%tools\patch247.py"
if errorlevel 1 goto :err

echo.
echo [2/2] Chaines natives ^(app.asar^)...
"%PY%" "%ROOT%tools\patch_asar247.py"
if errorlevel 1 goto :err

echo.
echo TERMINE.
echo Relance Reasonix Studio, puis : Parametres ^> Apparence ^> Langue ^> Francais
echo.
pause
exit /b 0

:err
echo.
echo ECHEC. Lis le message ci-dessus.
echo Sauvegardes : %ROOT%backups
pause
exit /b 1
