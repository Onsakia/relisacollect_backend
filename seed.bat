@echo off
REM EC Carbon Survey - Windows Seed Script
REM Place this file in your Django project root (same folder as manage.py)
REM
REM Usage:
REM   seed.bat              - Seed 50 plots
REM   seed.bat 100          - Seed 100 plots
REM   seed.bat flush        - Clear all data and seed 50 plots
REM   seed.bat 100 flush    - Clear all data and seed 100 plots

echo ===========================================
echo EC Carbon Survey - Database Seeder
echo ===========================================

if "%1"=="flush" (
    python seed_standalone.py --plots 50 --flush
    goto :end
)

if "%2"=="flush" (
    python seed_standalone.py --plots %1 --flush
    goto :end
)

if "%1"=="" (
    python seed_standalone.py --plots 50
    goto :end
)

python seed_standalone.py --plots %1

:end
echo.
pause
