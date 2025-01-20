@echo off
REM Displaying a message to the user
echo Setting up virtual environment and building the application...
echo.

REM Step 1: Install virtualenv (if not already installed)
echo Installing virtualenv...
pip install virtualenv
if %errorlevel% neq 0 (
    echo Failed to install virtualenv. Exiting...
    exit /b
)
echo.

REM Step 2: Create a virtual environment
echo Creating a virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Exiting...
    exit /b
)
echo.

REM Step 3: Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate the virtual environment. Exiting...
    exit /b
)
echo.

REM Step 4: Install PyInstaller in the virtual environment
echo Installing PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo Failed to install PyInstaller. Exiting...
    exit /b
)
echo.

REM Step 5: Build the application
echo Building the application with PyInstaller...
pyinstaller --onedir --windowed --icon="clipboard.ico" "Clipboard Data App.py"
if %errorlevel% neq 0 (
    echo Failed to build the application. Exiting...
    exit /b
)
echo.

REM Completion message
echo Application build completed successfully. Check the dist folder for the output.
echo.

REM Keeping the command prompt open for user to see results
pause
