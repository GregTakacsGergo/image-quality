@echo off
echo ============================================
echo  Building ZoomAndSharpen.exe (SEASON3)
echo ============================================
echo.

REM Install dependencies if needed
pip install -r requirements.txt
echo.

REM Clean previous build artifacts
echo Cleaning previous build...
pyinstaller --clean ZoomAndSharpen.spec
echo.

if exist "dist\ZoomAndSharpen\ZoomAndSharpen.exe" (
    echo SUCCESS: dist\ZoomAndSharpen\ZoomAndSharpen.exe is ready
) else (
    echo ERROR: Build failed — exe not found. Check output above.
)
echo.
pause
