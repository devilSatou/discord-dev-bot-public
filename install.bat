@echo off
echo ================================
echo Discord Dev Bot - Setup
echo ================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Recommend running as administrator
    echo Right-click and select "Run as administrator"
    echo.
    pause
)

echo [1/5] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11 or higher
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo [2/5] Installing required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed
    pause
    exit /b 1
)
echo.

echo [3/5] Creating config file...
if not exist config.json (
    echo {> config.json
    echo   "discord_token": "",>> config.json
    echo   "command_prefix": "!dev ",>> config.json
    echo   "project_dir": "C:\\path\\to\\your\\project",>> config.json
    echo   "auto_reconnect": true,>> config.json
    echo   "startup_delay": 30>> config.json
    echo }>> config.json
    echo config.json created
) else (
    echo config.json already exists
)
echo.

echo [4/5] Creating logs directory...
if not exist logs mkdir logs
echo.

echo [5/5] Registering to startup...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_DIR=%~dp0"
set "VBS_FILE=%SCRIPT_DIR%start_bot.vbs"
set "SHORTCUT_FILE=%STARTUP_FOLDER%\Discord Dev Bot.lnk"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_FILE%'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '\"%VBS_FILE%\"'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Discord Dev Bot Auto Start'; $Shortcut.Save()"

if exist "%SHORTCUT_FILE%" (
    echo OK: Registered to startup
    echo Location: %SHORTCUT_FILE%
) else (
    echo [WARNING] Failed to register startup
    echo Please register manually:
    echo 1. Win+R and type: shell:startup
    echo 2. Create shortcut of start_bot.vbs
)
echo.

echo ================================
echo Setup Complete!
echo ================================
echo.
echo [NEXT STEPS]
echo 1. Create Discord Bot
echo    https://discord.com/developers/applications
echo.
echo 2. Get Bot Token
echo    Bot tab - Reset Token - Copy
echo.
echo 3. Edit config.json
echo    Set "discord_token": "YOUR_TOKEN_HERE"
echo.
echo 4. Invite Bot to your server
echo    OAuth2 - URL Generator
echo    Scopes: bot
echo    Permissions: Send Messages, Read Message History
echo.
echo 5. Test run
echo    Double-click start_bot.vbs
echo.
echo 6. Check if working
echo    Type in Discord: !dev status
echo.
echo [TROUBLESHOOTING]
echo - Check logs: logs\bot.log
echo - Manual run: python bot.py
echo - Re-setup: Run this file again
echo.

pause
