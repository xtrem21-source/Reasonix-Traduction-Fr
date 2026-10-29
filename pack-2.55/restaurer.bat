@echo off
rem ============================================================
rem  Reasonix - restaurer l'installation
rem  Remet les fichiers d'avant la francisation (dossier backups).
rem  Double-clic : montre ce qui est disponible, puis demande.
rem ============================================================
setlocal
set "ROOT=%~dp0"
if exist "%ROOT%config.bat" call "%ROOT%config.bat"
title Reasonix - restauration

echo ============================================================
echo   Reasonix - restaurer l'installation
echo ============================================================
echo.

if not exist "%ROOT%backups" (
  echo Aucune sauvegarde : le pack n'a encore rien applique sur cette machine.
  echo.
  pause
  exit /b 1
)

rem Python, comme pour l'application : sans lui, rien ne peut etre remis.
if defined PY (
  %PY% -c "import sys" >nul 2>&1
  if errorlevel 1 set "PY=py -3"
) else (
  set "PY=py -3"
)
%PY% -c "import sys" >nul 2>&1
if errorlevel 1 set "PY=python"
%PY% -c "import sys" >nul 2>&1
if errorlevel 1 (
  echo ERREUR : Python 3 est introuvable. Rien n'a ete touche.
  echo.
  pause
  exit /b 1
)

%PY% "%ROOT%tools\restaurer.py" %*
set "CODE=%ERRORLEVEL%"

echo.
if "%CODE%"=="0" echo Termine. Rouvre Reasonix Studio pour voir l'ancien etat.
if "%CODE%"=="1" echo Rien n'a ete restaure.
if "%CODE%"=="2" echo Restauration incomplete : voir les messages ci-dessus.
echo.
pause
exit /b %CODE%
