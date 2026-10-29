@echo off
setlocal EnableExtensions
title Reasonix - traduction automatique
set "ROOT=%~dp0"
call "%ROOT%config.bat"

set "PYTHONIOENCODING=utf-8"
set "PYTHONDONTWRITEBYTECODE=1"

rem Nom du processus a surveiller (surchargeable pour les tests).
if not defined REASONIX_PROC set "REASONIX_PROC=Reasonix Studio.exe"
if not defined REASONIX_HOST set "REASONIX_HOST=reasonix-studio-host.exe"

rem --test : montre ce qui serait fait, ne ferme rien et n'applique rien.
set "TEST="
if /I "%~1"=="--test" set "TEST=1"

echo ============================================================
echo   Reasonix - mise a jour de la traduction
echo ============================================================
echo   Langue par defaut : %REASONIX_UI_DEFAULT%
if defined TEST echo   MODE TEST         : aucune fermeture, aucune application
echo.

rem Où est Studio ? Si le chemin du pack ne mene nulle part, on cherche, et en
rem dernier recours une fenetre demande le dossier (voir :ensure_app plus bas).
call :ensure_app
if errorlevel 1 (
  echo ERREUR : Reasonix Studio est introuvable.
  echo Choisis son dossier dans la fenetre, ou renseigne-le dans config.local.bat.
  echo.
  pause
  exit /b 1
)
echo   Installation      : %REASONIX_APP%

rem Python est indispensable : on le verifie AVANT de fermer Studio, pour ne pas
rem laisser l'application fermee sans qu'aucun travail ait ete fait.
call :ensure_python
if errorlevel 1 (
  echo.
  echo ECHEC : aucun Python 3 utilisable. Rien n'a ete ferme ni applique.
  echo.
  pause
  exit /b 1
)

call :ensure_closed
if errorlevel 1 (
  echo.
  echo ECHEC : Reasonix Studio n'a pas pu etre ferme.
  echo Ferme-le a la main ^(zone de notification : Quitter^), puis relance.
  echo.
  pause
  exit /b 1
)

if defined TEST (
  echo.
  echo MODE TEST : je m'arrete ici. Rien n'a ete ferme ni applique.
  exit /b 0
)

if defined REASONIX_ONLY_CLOSE (
  echo.
  echo FERMETURE SEULE : je m'arrete ici, rien n'a ete applique.
  exit /b 0
)

"%PY%" "%ROOT%tools\maj.py" --app "%REASONIX_APP%" --default-lang "%REASONIX_UI_DEFAULT%"
set "CODE=%ERRORLEVEL%"

echo.
if "%CODE%"=="0" (
  echo TERMINE. Relance Reasonix Studio.
) else if "%CODE%"=="2" (
  echo ============================================================
  echo   CE N'EST PAS UNE PANNE
  echo ============================================================
  echo.
  echo   Des libelles nouveaux attendent une traduction.
  echo   Le fichier a-traduire.tsv a ete ecrit dans ce dossier.
  echo.
  echo   ACTION : demande a Reasonix de le faire.
  echo   Ouvre une session et colle simplement :
  echo.
  echo     "Traduis les chaines de a-traduire.tsv du pack
  echo      Reasonix-Traduction-Auto."
  echo.
  echo   Il remplit le fichier, puis tu relances ce mettre-a-jour.bat.
  echo   Detail complet : A-DIRE-A-REASONIX.md
  echo ============================================================
) else (
  echo ECHEC ^(code %CODE%^). Lis le message ci-dessus.
  echo Journal : %ROOT%logs\journal.log
)
echo.
pause
exit /b %CODE%

rem ---------------------------------------------------------------------------
rem  Ferme Reasonix Studio proprement, puis de force si besoin.
rem  Laisse le noyau relacher les fichiers avant de rendre la main.
rem ---------------------------------------------------------------------------
:ensure_closed
set "TRIES=0"
:ec_check
"%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq %REASONIX_PROC%" /NH 2>nul | "%SystemRoot%\System32\find.exe" /I "%REASONIX_PROC%" >nul
if errorlevel 1 goto :ec_closed

if "%TRIES%"=="0" (
  echo Reasonix Studio est ouvert : demande de fermeture propre...
  if defined TEST (
    echo MODE TEST : taskkill /IM "%REASONIX_PROC%" serait lance ici.
    goto :ec_closed
  )
  "%SystemRoot%\System32\taskkill.exe" /IM "%REASONIX_PROC%" >nul 2>&1
  "%SystemRoot%\System32\ping.exe" -n 7 127.0.0.1 >nul
  "%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq %REASONIX_PROC%" /NH 2>nul | "%SystemRoot%\System32\find.exe" /I "%REASONIX_PROC%" >nul
  if errorlevel 1 goto :ec_closed
)

echo Fermeture forcee dans 5 secondes ^(Ctrl+C pour annuler^)...
if not defined TEST "%SystemRoot%\System32\ping.exe" -n 6 127.0.0.1 >nul
if not defined TEST "%SystemRoot%\System32\taskkill.exe" /F /IM "%REASONIX_PROC%" >nul 2>&1
if not defined TEST "%SystemRoot%\System32\ping.exe" -n 7 127.0.0.1 >nul

set /a TRIES+=1
if %TRIES% GEQ 3 exit /b 1
goto :ec_check

:ec_closed
rem Le noyau survit quelques secondes a la fenetre : on lui laisse le temps de
rem sortir seul, et on ne le force que s'il s'accroche.
if not defined TEST if not defined REASONIX_ONLY_CLOSE (
  "%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq %REASONIX_HOST%" /NH 2>nul | "%SystemRoot%\System32\find.exe" /I "%REASONIX_HOST%" >nul
  if not errorlevel 1 (
    "%SystemRoot%\System32\ping.exe" -n 7 127.0.0.1 >nul
    "%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq %REASONIX_HOST%" /NH 2>nul | "%SystemRoot%\System32\find.exe" /I "%REASONIX_HOST%" >nul
    if not errorlevel 1 "%SystemRoot%\System32\taskkill.exe" /F /IM "%REASONIX_HOST%" >nul 2>&1
  )
)
exit /b 0

rem ---------------------------------------------------------------------------
rem  Ou est Reasonix Studio ?
rem  Le pack n'est plus lie a un disque : on essaie le chemin qu'il propose, puis
rem  les emplacements standards, le registre de desinstallation et la racine de
rem  chaque disque. Si rien ne repond, une fenetre demande le dossier. La reponse
rem  est memorisee dans config.local.bat (jamais livre avec le pack).
rem ---------------------------------------------------------------------------
:ensure_app
if exist "%REASONIX_APP%\Reasonix Studio.exe" if exist "%REASONIX_APP%\resources\frontend-next\dist\index.html" exit /b 0

set "RX_TROUVE="
set "RX_SORTIE=%TEMP%\reasonix-app-%RANDOM%%RANDOM%.txt"
if exist "%RX_SORTIE%" del /q "%RX_SORTIE%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%tools\trouver-studio.ps1" -Sortie "%RX_SORTIE%"
if exist "%RX_SORTIE%" (
  set /p RX_TROUVE=<"%RX_SORTIE%"
  del /q "%RX_SORTIE%" >nul 2>&1
)
if not defined RX_TROUVE exit /b 1

set "REASONIX_APP=%RX_TROUVE%"
>"%ROOT%config.local.bat" echo rem Reponse memorisee par le lanceur - ne pas livrer avec le pack.
>>"%ROOT%config.local.bat" echo set "REASONIX_APP=%REASONIX_APP%"
exit /b 0

rem ---------------------------------------------------------------------------
rem  Python 3 : present, executable, et vraiment installe.
rem  Un « python » non installe du Microsoft Store est un simple raccourci : il
rem  repond par un code d'erreur. Le test d'execution suffit donc a le refuser,
rem  et accepte un Python installe depuis le Store comme un autre.
rem ---------------------------------------------------------------------------
:ensure_python
rem En mode test, on montre le diagnostic mais on n'installe jamais rien.
if defined TEST set "REASONIX_NO_INSTALL=1"

call :py_works "%PY%"
if not errorlevel 1 exit /b 0

call :py_from_launcher
if not errorlevel 1 exit /b 0

call :py_from_paths
if not errorlevel 1 exit /b 0

if defined REASONIX_NO_INSTALL goto :ep_missing

echo.
echo Python 3 est introuvable sur ce systeme.
echo C'est lui qui applique la traduction : sans lui, rien ne peut etre fait.
echo.
where winget.exe >nul 2>&1
if errorlevel 1 goto :ep_manual

choice /C ON /N /M "Installer Python 3.13 maintenant avec winget ? [O/N] "
if errorlevel 2 goto :ep_refused

echo.
winget install --id Python.Python.3.13 -e --scope user --accept-source-agreements --accept-package-agreements
echo.
call :py_from_paths
if not errorlevel 1 (
  echo Python installe : %PY%
  exit /b 0
)
echo L'installation n'a pas rendu Python visible.
echo Ferme cette fenetre, rouvre-la, puis relance ce fichier.
exit /b 1

:ep_refused
echo Installation refusee : rien n'a ete fait.
exit /b 1

:ep_manual
echo Installe Python 3.13 depuis https://www.python.org/downloads/windows/
echo en cochant « Add python.exe to PATH », puis relance ce fichier.
exit /b 1

:ep_missing
echo ERREUR : Python 3 introuvable, et l'installation automatique est desactivee.
exit /b 1

rem --- ce chemin est-il un vrai Python 3 ? ---
:py_works
if "%~1"=="" exit /b 1
"%~1" -c "import sys;sys.exit(0 if sys.version_info[0]==3 else 1)" >nul 2>&1
exit /b %ERRORLEVEL%

rem --- lanceur officiel py.exe ---
:py_from_launcher
where py.exe >nul 2>&1
if errorlevel 1 exit /b 1
set "PY_FOUND="
for /f "delims=" %%P in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PY_FOUND=%%P"
if not defined PY_FOUND exit /b 1
call :py_works "%PY_FOUND%"
if errorlevel 1 exit /b 1
set "PY=%PY_FOUND%"
exit /b 0

rem --- emplacements d'installation classiques ---
:py_from_paths
for %%V in (313 312 311 310 39) do (
  call :py_try "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
  if not errorlevel 1 exit /b 0
  call :py_try "%ProgramFiles%\Python%%V\python.exe"
  if not errorlevel 1 exit /b 0
)
call :py_try "C:\Python313\python.exe"
if not errorlevel 1 exit /b 0
call :py_try "C:\Python312\python.exe"
if not errorlevel 1 exit /b 0
exit /b 1

:py_try
call :py_works "%~1"
if errorlevel 1 exit /b 1
set "PY=%~1"
exit /b 0
