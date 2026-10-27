@echo off
rem dicter.bat — lance winh.ps1 sans fenetre. Appele par le module micro.
start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "J:\Reasonix\dev\voix-winh\winh.ps1"
exit /b 0
