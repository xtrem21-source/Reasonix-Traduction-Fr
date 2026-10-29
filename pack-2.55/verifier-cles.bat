@echo off
rem ============================================================
rem  Reasonix - etat du coffre des cles du module micro
rem  Ne montre jamais une cle : dit seulement si le coffre existe,
rem  ce qu'il contient, et si .env est encore en clair.
rem ============================================================
setlocal
set "ROOT=%~dp0"
if exist "%ROOT%config.bat" call "%ROOT%config.bat"
title Reasonix - coffre des cles

echo ============================================================
echo   Coffre des cles du module micro
echo ============================================================
echo.

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
  echo ERREUR : Python 3 est introuvable.
  echo.
  pause
  exit /b 1
)

%PY% "%ROOT%tools\verifier-cles.py"
set "CODE=%ERRORLEVEL%"

echo.
pause
exit /b %CODE%
