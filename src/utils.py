import time
from pathlib import Path
from functools import wraps

def format_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        elapsed = t1 - t0
        print(f"\nElapsed time: {format_duration(elapsed)}")
        return result
    return wrapper

def make_output_path(input_path: Path, outputs_dir: Path, suffix="_stats.gpkg") -> Path:
    """
    Returns a standardised output path based on input filename and desired suffix.
    E.g., data/new_shp.json -> outputs/new_shp_stats.gpkg
    """
    stem = input_path.stem  # 'new_shp' from 'new_shp.json'
    return outputs_dir / f"{stem}{suffix}"
