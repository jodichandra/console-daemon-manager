@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM Console Daemon Manager - Build Script
REM ============================================================
REM Cara pakai:
REM   1. Simpan file ini sebagai build.bat di folder project
REM   2. Double-click untuk build
REM   3. Hasil: dist\ConsoleDaemonManager.exe
REM ============================================================

title Build - Console Daemon Manager
color 0A

echo.
echo ============================================================
echo   BUILD - CONSOLE DAEMON MANAGER
echo ============================================================
echo.

REM ---- Pindah ke folder script ini berada ----
cd /d "%~dp0"

REM ---- Cek file main.py ----
if not exist "main.py" (
    color 0C
    echo [ERROR] File main.py tidak ditemukan!
    echo         Pastikan build.bat ada di folder yang sama dengan main.py
    echo.
    pause
    exit /b 1
)

REM ---- Cek Python ----
echo [1/6] Cek Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python tidak ditemukan di PATH!
    echo         Install Python dulu dari https://python.org
    echo.
    pause
    exit /b 1
)
python --version
echo       OK
echo.

REM ---- Cek PyInstaller ----
echo [2/6] Cek PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo       PyInstaller belum terinstall, install sekarang...
    python -m pip install pyinstaller
    if errorlevel 1 (
        color 0C
        echo [ERROR] Gagal install PyInstaller!
        echo.
        pause
        exit /b 1
    )
)
python -m PyInstaller --version
echo       OK
echo.

REM ---- Cek dependency lain ----
echo [3/6] Cek dependency (PyQt5, requests, certifi, charset_normalizer)...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo       Install PyQt5...
    python -m pip install PyQt5
)
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo       Install requests...
    python -m pip install requests
)
python -c "import certifi" >nul 2>&1
if errorlevel 1 (
    echo       Install certifi...
    python -m pip install certifi
)
python -c "import charset_normalizer" >nul 2>&1
if errorlevel 1 (
    echo       Install charset_normalizer...
    python -m pip install charset_normalizer
)
echo       OK
echo.

REM ---- Hapus build lama ----
echo [4/6] Bersihkan build lama...
if exist "build" (
    rmdir /s /q "build"
    echo       - build\ dihapus
)
if exist "dist" (
    rmdir /s /q "dist"
    echo       - dist\ dihapus
)
if exist "ConsoleDaemonManager.spec" (
    del /q "ConsoleDaemonManager.spec"
    echo       - spec lama dihapus
)
echo       OK
echo.

REM ---- Build ----
echo [5/6] Build .exe (tunggu 1-3 menit)...
echo.
echo ------------------------------------------------------------
python -m PyInstaller --onefile --noconsole --name "ConsoleDaemonManager" ^
    --collect-all PyQt5 ^
    --collect-all certifi ^
    --hidden-import charset_normalizer ^
    main.py

if errorlevel 1 (
    color 0C
    echo.
    echo ------------------------------------------------------------
    echo [ERROR] Build GAGAL! Cek pesan error di atas.
    echo.
    pause
    exit /b 1
)
echo.
echo ------------------------------------------------------------
echo       OK
echo.

REM ---- Cek hasil ----
echo [6/6] Cek hasil build...
if not exist "dist\ConsoleDaemonManager.exe" (
    color 0C
    echo [ERROR] File exe tidak ditemukan di dist\!
    echo.
    pause
    exit /b 1
)

REM ---- Hitung ukuran file ----
for %%A in ("dist\ConsoleDaemonManager.exe") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576

echo.
echo ============================================================
echo   BUILD SUKSES!
echo ============================================================
echo.
echo   File   : dist\ConsoleDaemonManager.exe
echo   Ukuran : %SIZE_MB% MB
echo.
echo ============================================================
echo.

REM ---- Tanya buka folder hasil ----
choice /C YN /M "Buka folder dist sekarang"
if errorlevel 2 goto :end
if errorlevel 1 (
    explorer "dist"
)

:end
echo.
echo Selesai. Tekan tombol apa saja untuk keluar...
pause >nul