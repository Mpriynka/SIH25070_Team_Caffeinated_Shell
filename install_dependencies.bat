@echo off
REM EasyWipe Dependencies Installation Script for Windows

echo EasyWipe - Installing Dependencies
echo ==================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo Please run as Administrator
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Verify installation
echo Verifying installation...
python --version
pip --version

echo.
echo Installation complete!
echo Run the application with: python main.py
pause
