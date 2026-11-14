from pathlib import Path
import subprocess, re, shutil
import yt_dlp
import imageio_ffmpeg
from faster_whisper import WhisperModel
from .config import WORK, OUTPUT, MODELS

def run(cmd):
    p = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "Error de FFmpeg")[-3500:])
    return p.stdout

def create_clips(url, count, progress, log):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    source_dir = WORK / "job"
    if source_dir.exists():
        shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True)
    progress(3, "Preparando descarga…")
    log("Descargando video. Puede tardar según su duración y conexión.")
    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                pct = int(5 + 25 * d.get("downloaded_bytes", 0) / total)
                progress(pct, f"Descargando video… {int(100*d.get('downloaded_bytes',0)/total)}%")
        elif d.get("status") == "finished":
            progress(30, "Descarga terminada; preparando video…")
    opts = {
        "outtmpl": str(source_dir / "source.%(ext)s"),
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "ffmpeg_location": ffmpeg,
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    candidates = list(source_dir.glob("source.*"))
    video = next((p for p in candidates if p.suffix.lower() in (".mp4",".mkv",".webm",".mov")), None)
    if not video:
        raise RuntimeError("La descarga no produjo un archivo de video compatible.")
    progress(34, "Analizando audio para subtítulos…")
    log("Transcribiendo audio en español. La primera ejecución puede descargar el modelo.")
    model = WhisperModel("small", device="cpu", compute_type="int8", download_root=str(MODELS))
    segments, _ = model.transcribe(str(video), language="es", word_timestamps=True, vad_filter=True)
    segments = list(segments)
    if not segments:
        raise RuntimeError("No se detectó voz en español. Prueba con otro video.")
    duration = float(info.get("duration") or 0)
    if duration <= 0:
        duration = float(run([ffmpeg, "-i", video, "-f", "null", "-"]).split("time=")[-1].split()[0]) if False else max(s.end for s in segments)
    # Select evenly spaced windows across the video, avoiding windows with no speech.
    span = min(60.0, max(20.0, duration / max(1, count)))
    windows = []
    step = max(span, duration / max(1, count))
    for i in range(count):
        start = min(max(0, i * step), max(0, duration - span))
        end = min(duration, start + span)
        if any(s.end > start and s.start < end for s in segments):
            windows.append((start, end))
    if not windows:
        raise RuntimeError("No se encontraron fragmentos con voz.")
    progress(55, "Creando clips verticales y subtítulos…")
    for idx, (start, end) in enumerate(windows, 1):
        clip = OUTPUT / f"ViralClip_{idx:02d}.mp4"
        srt = source_dir / f"clip_{idx:02d}.srt"
        lines, n = [], 1
        for seg in segments:
            if seg.end <= start or seg.start >= end:
                continue
            text = re.sub(r"\s+", " ", seg.text.strip())
            if not text:
                continue
            a, b = max(0, seg.start-start), min(end-start, seg.end-start)
            def stamp(t):
                ms = int(t*1000); h, ms = divmod(ms,3600000); m, ms = divmod(ms,60000); sec, ms = divmod(ms,1000)
                return f"{h:02}:{m:02}:{sec:02},{ms:03}"
            lines += [str(n), f"{stamp(a)} --> {stamp(b)}", text, ""]
            n += 1
        srt.write_text("\n".join(lines), encoding="utf-8-sig")
        # Escape path for FFmpeg subtitles filter.
        srt_filter = str(srt.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{srt_filter}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=130'"
        run([ffmpeg, "-y", "-ss", start, "-i", video, "-t", end-start, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", clip])
        progress(55 + int(44 * idx / len(windows)), f"Creando clip {idx} de {len(windows)}…")
        log(f"Guardado: {clip.name}")
    progress(100, "Proceso terminado")
    log(f"Listo. Clips guardados en: {OUTPUT}")
