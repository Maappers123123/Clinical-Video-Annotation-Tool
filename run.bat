@echo off
setlocal enabledelayedexpansion
set VENV_DIR=.venv
set PY_CMD=

echo Checking environment...

REM ------------------------------------------------------------------
REM Locate a working Python interpreter.
REM ------------------------------------------------------------------

REM If a conda environment is already active (e.g. you launched this from
REM an Anaconda Prompt, prompt shows "(base)" or similar), use its
REM python.exe directly. This is the most reliable signal available and
REM sidesteps PATH/"where" ambiguity entirely.
if not "%CONDA_PREFIX%"=="" (
    if exist "%CONDA_PREFIX%\python.exe" (
        echo   detected active conda environment: %CONDA_PREFIX%
        set PY_CMD="%CONDA_PREFIX%\python.exe"
    )
)

if "%PY_CMD%"=="" call :try_candidate "py" "py -3"
if "%PY_CMD%"=="" call :try_candidate "python" "python"
if "%PY_CMD%"=="" call :try_candidate "python3" "python3"

if "%PY_CMD%"=="" (
    echo.
    echo ============================================================
    echo   Python was not found on this computer.
    echo ============================================================
    echo   Install Python 3.10 or newer from:
    echo       https://www.python.org/downloads
    echo.
    echo   IMPORTANT: on the first install screen, check the box
    echo   "Add python.exe to PATH" before clicking Install.
    echo.
    echo   If you use Anaconda / Miniconda instead:
    echo   this tool can only see a conda Python if it is launched
    echo   from an "Anaconda Prompt", or from a terminal where you
    echo   already ran "conda activate". Either run this file from
    echo   an Anaconda Prompt, or install a separate standalone
    echo   Python using the link above.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo Using Python: %PY_CMD%
%PY_CMD% --version

if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM From here on, "python" refers to the venv's own interpreter
REM (activate.bat has put "%VENV_DIR%\Scripts" first on PATH), so no
REM further Store-alias/conda ambiguity is possible.

echo Ensuring dependencies are installed...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Pip upgrade failed. This may be blocked by group policy.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. This may be blocked by group policy.
    pause
    exit /b 1
)

echo Launching Clinical Video Annotation Tool...
python scorer.py
pause
exit /b 0

REM ------------------------------------------------------------------
REM :try_candidate <exe_name> <run_command>
REM   exe_name    - bare executable name to resolve via "where" (e.g. python)
REM   run_command - the actual command to use afterwards, may include
REM                 arguments (e.g. "py -3")
REM
REM Looks up every matching path for exe_name on PATH, in order, and
REM accepts the first one that is NOT inside the WindowsApps alias
REM folder. If found, sets PY_CMD to run_command. Does nothing if
REM PY_CMD is already set by an earlier candidate.
REM ------------------------------------------------------------------
:try_candidate
if not "%PY_CMD%"=="" exit /b 0
set "EXE_NAME=%~1"
set "RUN_CMD=%~2"
set "FOUND_REAL="
for /f "delims=" %%P in ('where %EXE_NAME% 2^>nul') do (
    echo %%P| findstr /I "WindowsApps" >nul
    if errorlevel 1 (
        echo   found: %%P  [OK]
        if "!FOUND_REAL!"=="" set "FOUND_REAL=%%P"
    ) else (
        echo   found: %%P  [rejected - Store alias]
    )
)
if "!FOUND_REAL!"=="" (
    echo   no usable "%EXE_NAME%" found
) else (
    set "PY_CMD=%RUN_CMD%"
)
exit /b 0
