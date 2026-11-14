# ViralClipsAI 2.0 — proyecto para Windows 10/11 de 64 bits

Esta es una **base de proyecto** para generar clips verticales a partir de videos accesibles mediante yt-dlp. No es un instalador EXE ya compilado.

## Requisitos para compilar
- Windows 10/11 de 64 bits
- Python 3.11
- Conexión a Internet

Ejecuta `build_windows.bat`. El resultado PyInstaller queda en `dist\ViralClipsAI`.

## Importante
- Usa únicamente videos propios, públicos o para los que tengas autorización.
- YouTube, Twitch y Kick pueden exigir inicio de sesión, cookies o bloquear descargas. No se garantiza que todos los enlaces funcionen.
- El filtrado `subtitles` de FFmpeg depende de que la versión incluida tenga soporte para libass. Debe probarse en el equipo de destino.
- La selección de clips es automática y básica; no garantiza que todos los fragmentos sean virales ni que siempre encuentre la cantidad solicitada.
- El primer uso de los subtítulos descarga el modelo Whisper y necesita espacio y conexión.
- Este paquete no ha sido validado mediante pruebas completas en Windows; comprueba cada función antes de distribuirlo.
