@echo off
setlocal EnableDelayedExpansion

:: ==============================
:: CONFIGURATION
:: ==============================
set "targetdir=target"
set "srcdir=src"
set "libdir=lib"
set "resourcesdir=src\gui\buttonGraphics"

echo [INFO] Starting build process...

:: ==============================
:: CREATE TARGET DIRECTORY
:: ==============================
IF NOT EXIST "%targetdir%" (
    echo [INFO] Creating target directory...
    mkdir "%targetdir%" || (
        echo [ERROR] Failed to create target directory.
        exit /b 1
    )
)

:: ==============================
:: BUILD CLASSPATH FROM LIBS
:: ==============================
echo [INFO] Building classpath...
set "CLASSPATH="

if NOT EXIST "%libdir%" (
    echo [WARNING] Library directory '%libdir%' not found.
) else (
    for %%f in (%libdir%\*.jar) do (
        if defined CLASSPATH (
            echo [INFO] Adding '%%f' to classpath.
            set "CLASSPATH=!CLASSPATH!;%%f"
        ) else (
            set "CLASSPATH=%%f"
        )
    )
)

:: ==============================
:: VERIFY SOURCE DIRECTORY
:: ==============================
if NOT EXIST "%srcdir%" (
    echo [ERROR] Source directory '%srcdir%' not found.
    exit /b 1
)

:: ==============================
:: COLLECT JAVA FILES
:: ==============================
echo [INFO] Collecting Java source files...
dir /s /b "%srcdir%\*.java" > sources.txt 2>nul

if not exist sources.txt (
    echo [ERROR] No Java source files found in '%srcdir%'.
    exit /b 1
)

:: ==============================
:: COMPILE (WITH LOMBOK SUPPORT)
:: ==============================
echo [INFO] Compiling Java sources...

javac ^
-sourcepath "%srcdir%" ^
-d "%targetdir%" ^
-cp "%CLASSPATH%;%libdir%\lombok.jar" ^
-processorpath "%libdir%\lombok.jar" ^
@sources.txt

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Compilation failed with error code %ERRORLEVEL%.
    del sources.txt 2>nul
    exit /b %ERRORLEVEL%
)

:: ==============================
:: CLEAN TEMP FILE
:: ==============================
del sources.txt 2>nul

:: ==============================
:: COPY RESOURCES
:: ==============================
if exist "%resourcesdir%" (
    echo [INFO] Copying resources...
    if not exist "%targetdir%\gui\buttonGraphics\" (
        mkdir "%targetdir%\gui\buttonGraphics"
    )
    xcopy /y /q "%resourcesdir%\*" "%targetdir%\gui\buttonGraphics\" >nul
)

echo [INFO] Build completed successfully!
endlocal