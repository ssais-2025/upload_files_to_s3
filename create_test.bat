@echo off
REM Test Data Generator for AIS Uploader
REM This script creates test data to test your AIS uploader

echo AIS Uploader - Test Data Generator
echo ===================================
echo.

if "%1"=="" (
    echo Usage: create_test.bat [output_directory] [options]
    echo.
    echo Examples:
    echo   create_test.bat test_data
    echo   create_test.bat test_data --files-per-month 5
    echo   create_test.bat test_data --years 2022,2023 --months 1,2,3,4,5,6
    echo   create_test.bat test_data --files-per-month 3 --file-size 2
    echo.
    echo Options:
    echo   --files-per-month N    Number of files per month (default: 3)
    echo   --years Y1,Y2,Y3       Years to create (default: 2022,2023,2024)
    echo   --months M1,M2,M3      Months to create (default: 1-12)
    echo   --file-size N          File size in MB (default: 1)
    echo   --clean                Clean existing directory first
    echo.
    echo Default: create_test.bat test_data
    echo.
    pause
    exit /b
)

echo Creating test data...
echo.

REM Run the Python script with all arguments
python create_test_data.py %*

echo.
echo Test data generation complete!
echo.
pause
