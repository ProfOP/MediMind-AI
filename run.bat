@echo off
title MediMind AI Launcher

cd /d "%~dp0"
if errorlevel 1 exit /b 1

echo ==========================================
echo          MediMind AI Launcher
echo ==========================================
echo.

set "OLLAMA_MODELS=%CD%\data\ollama\models"
set "HOME=%CD%\.localhome"
set "XDG_CACHE_HOME=%CD%\.cache"
set "STREAMLIT_CONFIG_DIR=%CD%\.streamlit"
set "TEMP=%CD%\.tmp"
set "TMP=%TEMP%"
set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"

if not exist "%CD%\data\ollama\models" mkdir "%CD%\data\ollama\models"
if not exist "%CD%\.cache" mkdir "%CD%\.cache"
if not exist "%CD%\.tmp" mkdir "%CD%\.tmp"
if not exist "%CD%\.localhome" mkdir "%CD%\.localhome"

echo Checking Ollama service...
powershell -NoProfile -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"

if errorlevel 1 (
    echo Ollama is not running. Starting Ollama...
    start "MediMind Ollama" cmd /k "set OLLAMA_MODELS=%CD%\data\ollama\models&& ollama serve"
    echo Waiting for Ollama to start...
    set "OLLAMA_READY=0"
    for /L %%i in (1,1,30) do (
        powershell -NoProfile -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
        if not errorlevel 1 (
            set "OLLAMA_READY=1"
            goto OLLAMA_CHECKED
        )
        timeout /t 2 /nobreak >nul
    )
    echo ERROR: Ollama failed to start.
    echo Check whether Ollama is installed and port 11434 is available.
    pause
    exit /b 1
) else (
    echo Ollama is already running.
)

:OLLAMA_CHECKED
echo.
echo Checking required model...
ollama list | findstr /I "smollm2:360m" >nul
if errorlevel 1 (
    echo Model not found. Downloading smollm2:360m...
    ollama pull smollm2:360m
    if errorlevel 1 (
        echo ERROR: Model download failed.
        pause
        exit /b 1
    )
)

echo Model is ready.
echo.
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8501' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
if not errorlevel 1 (
    echo MediMind AI is already running at http://127.0.0.1:8501
    start "" "http://127.0.0.1:8501"
    pause
    exit /b 0
)

echo Launching MediMind AI at http://127.0.0.1:8501
start "" "http://127.0.0.1:8501"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501

echo.
echo MediMind AI has stopped.
pause
