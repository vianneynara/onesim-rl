@echo off
REM Batch file to activate virtual environment and navigate to roblox_macro
REM Changes to the script's directory and opens PowerShell with venv activated

cd /d "%~dp0"
powershell -NoExit -Command "& {. .\.venv\Scripts\Activate.ps1; Write-Host 'Virtual environment activated and in pyplotter directory' -ForegroundColor Green}"