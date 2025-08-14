@echo off
REM S3 Uploader - Windows Batch Script
REM This script provides basic functionality for Windows Command Prompt users.
REM Run with: run.bat <command>

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-dev" goto install-dev
if "%1"=="ais-help" goto ais-help
if "%1"=="test-connection" goto test-connection
if "%1"=="ais-scan" goto ais-scan
if "%1"=="ais-upload" goto ais-upload
if "%1"=="ais-status" goto ais-status
if "%1"=="ais-validate" goto ais-validate
if "%1"=="ais-info" goto ais-info
if "%1"=="ais-resume" goto ais-resume
goto unknown

:help
echo Available commands:
echo   install              Install the package in development mode
echo   install-dev          Install the package with development dependencies
echo   ais-help             Show AIS CLI help
echo   test-connection      Test S3 connection
echo   ais-scan             Scan AIS data directory
echo   ais-upload           Upload AIS data files
echo   ais-status           Show AIS upload status
echo   ais-validate         Validate uploaded AIS files
echo   ais-info             Show comprehensive AIS information
echo   ais-resume           Resume AIS upload from previous session
echo   help                 Show this help message
echo.
echo Note: For advanced commands like lint, format, clean, use PowerShell: .\run.ps1
goto end

:install
echo Installing package in development mode...
pip install -e .
goto end

:install-dev
echo Installing package with development dependencies...
pip install -e ".[dev]"
goto end

:ais-help
echo Showing AIS CLI help...
python main.py --help
goto end

:test-connection
echo Testing S3 connection...
python main.py test
goto end

:ais-scan
echo Scanning AIS data directory...
echo Note: Adjust the base path in this script for your system
python main.py scan --base-path "E:\AISDData\exactEarth" --output ais_files.json
goto end

:ais-upload
echo Uploading AIS data files...
echo Note: Adjust the base path and bucket name in this script for your system
python main.py upload --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
goto end

:ais-status
echo Showing AIS upload status...
python main.py status --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
goto end

:ais-validate
echo Validating uploaded AIS files...
python main.py validate --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
goto end

:ais-info
echo Showing comprehensive AIS information...
python main.py info --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
goto end

:ais-resume
echo Resuming AIS upload from previous session...
python main.py upload --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name --resume
goto end

:unknown
echo Unknown command: %1
echo Run 'run.bat help' for available commands
exit /b 1

:end
echo.
