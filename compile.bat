@echo off
setlocal EnableDelayedExpansion

:: ==============================
:: CONFIGURATION
:: ==============================
set "targetdir=target"
set "srcdir=src"
set "libdir=lib"
set "resourcesdir=src\gui\buttonGraphics"

echo.
echo ======================================
echo        ONE SIMULATOR BUILD
echo ======================================
echo.

:: ==============================
:: CHECK LIB FOLDER
:: ==============================
if not exist "%libdir%" (
    echo [ERROR] lib folder not found!
    echo Make sure folder "lib" exists and contains lombok.jar and other dependencies.
    exit /b 1
)

:: ==============================
:: CHECK LOMBOK
:: ==============================
if not exist "%libdir%\lombok.jar" (
    echo [ERROR] lombok.jar not found inside lib folder!
    echo Download from https://projectlombok.org/download
    exit /b 1
)

:: ==============================
:: CREATE TARGET DIRECTORY
:: ==============================
if not exist "%targetdir%" (
    echo [INFO] Creating target directory...
    mkdir "%targetdir%"
)

:: ==============================
:: COLLECT ALL JAVA FILES
:: ==============================
echo [INFO] Collecting Java source files...
dir /s /b "%srcdir%\*.java" > sources.txt

if not exist sources.txt (
    echo [ERROR] No Java files found in src folder!
    exit /b 1
)

:: ==============================
:: COMPILE
:: ==============================
echo [INFO] Compiling...

javac ^
-d "%targetdir%" ^
-cp "%libdir%\*" ^
-processorpath "%libdir%\lombok.jar" ^
@sources.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Compilation failed!
    del sources.txt
    exit /b 1
)

del sources.txt

:: ==============================
:: COPY RESOURCES (if exist)
:: ==============================
if exist "%resourcesdir%" (
    echo [INFO] Copying GUI resources...
    xcopy /y /e /q "%resourcesdir%" "%targetdir%\gui\buttonGraphics\" >nul
)

echo.
echo ======================================
echo      BUILD SUCCESSFUL
echo ======================================
echo.

endlocal