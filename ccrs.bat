@echo off
REM CCRS CLI Wrapper for Windows
REM Simple, effective Claude Code routing service

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "CCRS_CLI=%SCRIPT_DIR%cli.py"

REM Handle help and version
if "%~1"=="" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
if "%~1"=="help" goto :show_help
if "%~1"=="-v" goto :show_version
if "%~1"=="--version" goto :show_version

REM Handle Docker shortcuts
if "%~1"=="up" goto :docker_up
if "%~1"=="start" goto :docker_up
if "%~1"=="down" goto :docker_down
if "%~1"=="stop" goto :docker_down
if "%~1"=="logs" goto :docker_logs
if "%~1"=="ps" goto :docker_ps

REM Check if CLI exists
if not exist "%CCRS_CLI%" (
    echo [91mError: CCRS CLI not found at %CCRS_CLI%[0m
    echo Make sure you're running from the CCRS directory
    exit /b 1
)

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [91mError: Python not found[0m
    echo Please install Python 3.11+ to use CCRS
    exit /b 1
)

REM Handle command shortcuts
if "%~1"=="c" (
    shift & python "%CCRS_CLI%" chat %*
    goto :eof
)
if "%~1"=="chat" (
    shift & python "%CCRS_CLI%" chat %*
    goto :eof
)
if "%~1"=="cmd" (
    shift & python "%CCRS_CLI%" command %*
    goto :eof
)
if "%~1"=="command" (
    shift & python "%CCRS_CLI%" command %*
    goto :eof
)
if "%~1"=="s" (
    shift & python "%CCRS_CLI%" status %*
    goto :eof
)
if "%~1"=="status" (
    shift & python "%CCRS_CLI%" status %*
    goto :eof
)
if "%~1"=="h" (
    python "%CCRS_CLI%" health
    goto :eof
)
if "%~1"=="health" (
    python "%CCRS_CLI%" health
    goto :eof
)

REM Forward all other arguments to Python CLI
python "%CCRS_CLI%" %*
goto :eof

:show_help
echo.
echo   [94m╔═══════════════════════════════════════╗[0m
echo   [94m║              CCRS                   ║[0m
echo   [94m║    Claude Code Routing Service        ║[0m
echo   [94m║           [92mSimple ^& Effective[94m           ║[0m
echo   [94m╚═══════════════════════════════════════╝[0m
echo.
echo [92mUSAGE:[0m
echo   ccrs ^<command^> [options]
echo.
echo [92mCOMMANDS:[0m
echo   [93mchat[0m ^<message^>           Send message to Claude
echo   [93mcommand[0m ^<cmd^>            Execute Claude command
echo   [93mstatus[0m ^<job-id^>          Check job status
echo   [93mhealth[0m                   Check service health
echo   [93mversion[0m                  Show version
echo.
echo [92mEXAMPLES:[0m
echo   ccrs chat "Hello Claude!" --wait
echo   ccrs command "/help" --wait
echo   ccrs health
echo   ccrs up                     ^(start services^)
echo   ccrs down                   ^(stop services^)
goto :eof

:show_version
echo [92mCCRS CLI Wrapper v2.0.0[0m
echo Simple, effective Claude Code routing service
goto :eof

:docker_up
echo [92mStarting CCRS services...[0m
docker-compose up -d
goto :eof

:docker_down
echo [93mStopping CCRS services...[0m
docker-compose down
goto :eof

:docker_logs
echo [94mCCRS service logs:[0m
docker-compose logs -f
goto :eof

:docker_ps
echo [94mCCRS service status:[0m
docker-compose ps
goto :eof