from pathlib import Path
import os, sys
if getattr(sys, "frozen", False):
    BASE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ViralClipsAI"
else:
    BASE = Path(__file__).resolve().parent.parent
WORK = BASE / "work"
OUTPUT = BASE / "output"
MODELS = BASE / "models"
for p in (WORK, OUTPUT, MODELS):
    p.mkdir(parents=True, exist_ok=True)
