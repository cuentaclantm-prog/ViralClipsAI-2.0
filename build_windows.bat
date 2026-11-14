@echo off
setlocal
cd /d "%~dp0"
echo Instalando dependencias...
py -3 -m pip install --upgrade pip
if errorlevel 1 goto error
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto error
py -3 -m PyInstaller --noconfirm --clean --windowed --onedir --name ViralClipsAI --collect-all yt_dlp --collect-all imageio_ffmpeg --collect-all faster_whisper --collect-all ctranslate2 --collect-all av app.py
if errorlevel 1 goto error
echo.
echo Aplicacion creada en dist\ViralClipsAI
pause
exit /b 0
:error
echo.
echo ERROR al compilar. Revisa el mensaje anterior.
pause
exit /b 1
