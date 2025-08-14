#!/usr/bin/env pwsh
<#
.SYNOPSIS
    S3 Uploader - Windows PowerShell Script
    
.DESCRIPTION
    This script provides the same functionality as the Makefile for Windows users.
    Run with: .\run.ps1 <command>
    
.EXAMPLE
    .\run.ps1 help
    .\run.ps1 install
    .\run.ps1 ais-upload
#>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  install              Install the package in development mode" -ForegroundColor Green
    Write-Host "  install-dev          Install the package with development dependencies" -ForegroundColor Green
    Write-Host "  lint                 Run linting checks" -ForegroundColor Green
    Write-Host "  format               Format code with black" -ForegroundColor Green
    Write-Host "  clean                Clean up development artifacts" -ForegroundColor Green
    Write-Host "  install-aws-cli      Install AWS CLI v2 (Windows)" -ForegroundColor Green
    Write-Host "  ais-help             Show AIS CLI help" -ForegroundColor Green
    Write-Host "  test-connection      Test S3 connection" -ForegroundColor Green
    Write-Host "  ais-scan             Scan AIS data directory" -ForegroundColor Green
    Write-Host "  ais-upload           Upload AIS data files" -ForegroundColor Green
    Write-Host "  ais-status           Show AIS upload status" -ForegroundColor Green
    Write-Host "  ais-validate         Validate uploaded AIS files" -ForegroundColor Green
    Write-Host "  ais-info             Show comprehensive AIS information" -ForegroundColor Green
    Write-Host "  ais-resume           Resume AIS upload from previous session" -ForegroundColor Green
    Write-Host "  help                 Show this help message" -ForegroundColor Green
}

function Install-Package {
    Write-Host "Installing package in development mode..." -ForegroundColor Yellow
    pip install -e .
}

function Install-DevDependencies {
    Write-Host "Installing package with development dependencies..." -ForegroundColor Yellow
    pip install -e ".[dev]"
}

function Run-Lint {
    Write-Host "Running linting checks..." -ForegroundColor Yellow
    flake8 src/
    mypy src/
}

function Format-Code {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    black src/
    isort src/
}

function Clean-Artifacts {
    Write-Host "Cleaning development artifacts..." -ForegroundColor Yellow
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object { Remove-Item $_ -Recurse -Force }
    Get-ChildItem -Recurse -File -Name "*.pyc" | Remove-Item -Force
}

function Install-AWSCLI {
    Write-Host "Installing AWS CLI v2 for Windows..." -ForegroundColor Yellow
    Write-Host "Please download and install from: https://awscli.amazonaws.com/AWSCLIV2.msi" -ForegroundColor Cyan
    Write-Host "Or use: winget install -e --id Amazon.AWSCLI" -ForegroundColor Cyan
}

function Show-AISHelp {
    Write-Host "Showing AIS CLI help..." -ForegroundColor Yellow
    python main.py --help
}

function Test-Connection {
    Write-Host "Testing S3 connection..." -ForegroundColor Yellow
    python main.py test
}

function Scan-AISData {
    Write-Host "Scanning AIS data directory..." -ForegroundColor Yellow
    Write-Host "Note: Adjust the base path in this script for your system" -ForegroundColor Cyan
    python main.py scan --base-path "E:\AISDData\exactEarth" --output ais_files.json
}

function Upload-AISData {
    Write-Host "Uploading AIS data files..." -ForegroundColor Yellow
    Write-Host "Note: Adjust the base path and bucket name in this script for your system" -ForegroundColor Cyan
    python main.py upload --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
}

function Show-AISStatus {
    Write-Host "Showing AIS upload status..." -ForegroundColor Yellow
    python main.py status --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
}

function Validate-AISFiles {
    Write-Host "Validating uploaded AIS files..." -ForegroundColor Yellow
    python main.py validate --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
}

function Show-AISInfo {
    Write-Host "Showing comprehensive AIS information..." -ForegroundColor Yellow
    python main.py info --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name
}

function Resume-AISUpload {
    Write-Host "Resuming AIS upload from previous session..." -ForegroundColor Yellow
    python main.py upload --base-path "E:\AISDData\exactEarth" --bucket your-bucket-name --resume
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "install" { Install-Package }
    "install-dev" { Install-DevDependencies }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "clean" { Clean-Artifacts }
    "install-aws-cli" { Install-AWSCLI }
    "ais-help" { Show-AISHelp }
    "test-connection" { Test-Connection }
    "ais-scan" { Scan-AISData }
    "ais-upload" { Upload-AISData }
    "ais-status" { Show-AISStatus }
    "ais-validate" { Validate-AISFiles }
    "ais-info" { Show-AISInfo }
    "ais-resume" { Resume-AISUpload }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\run.ps1 help' for available commands" -ForegroundColor Cyan
        exit 1
    }
}
