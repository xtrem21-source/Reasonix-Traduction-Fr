@echo off
rem ============================================================
rem  Reasonix-Traduction-Auto - variables du pack
rem  Seul fichier a modifier si l'installation change de disque.
rem ============================================================

rem Dossier d'installation de Reasonix Studio.
set "REASONIX_APP=J:\Reasonix Studio"

rem Langue de repli quand rien n'est enregistre : fr, en ou auto.
set "REASONIX_UI_DEFAULT=fr"

rem Python 3.13, sinon python du PATH.
set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

rem Node (facultatif : l'Electron de Studio sert de repli).
set "REASONIX_NODE="

rem ------------------------------------------------------------------
rem  Ne pas modifier ce bloc : il charge la reponse memorisee par le
rem  lanceur quand Studio n'est pas a l'emplacement par defaut.
rem  Ce fichier n'est jamais livre avec le pack.
rem ------------------------------------------------------------------
if exist "%~dp0config.local.bat" call "%~dp0config.local.bat"
