"""FFmpeg CLI wrapper: resolve executable on Windows (PATH or bundled binary)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _ffmpeg_executable() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "FFmpeg not found. Either install FFmpeg and add it to PATH, "
            "or run: pip install imageio-ffmpeg"
        ) from e


def convert_webm_to_wav(webm_path: str | Path, wav_path: str | Path) -> None:
    """Convert browser audio to 16 kHz mono WAV (PCM s16le)."""
    exe = _ffmpeg_executable()
    webm_path = Path(webm_path)
    wav_path = Path(wav_path)
    cmd = [
        exe,
        "-nostdin",
        "-y",
        "-i",
        str(webm_path.resolve()),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-acodec",
        "pcm_s16le",
        str(wav_path.resolve()),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip() or f"ffmpeg exited {proc.returncode}"
        raise RuntimeError(msg)


def split_wav_into_chunks(
    wav_path: str | Path,
    output_dir: str | Path,
    segment_seconds: int = 3,
) -> list[Path]:
    """Split WAV into small chunks for simulated streaming processing."""
    exe = _ffmpeg_executable()
    wav_path = Path(wav_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_pattern = output_dir / "chunk_%03d.wav"
    cmd = [
        exe,
        "-nostdin",
        "-y",
        "-i",
        str(wav_path.resolve()),
        "-f",
        "segment",
        "-segment_time",
        str(segment_seconds),
        "-c",
        "copy",
        str(out_pattern.resolve()),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip() or f"ffmpeg exited {proc.returncode}"
        raise RuntimeError(msg)
    return sorted(output_dir.glob("chunk_*.wav"))


import librosa
import soundfile as sf


def extract_speaker_reference(input_wav: str, output_wav: str):
    """
    Extract first 6 seconds as speaker reference.
    Normalize mono 16kHz.
    """
    audio, _ = librosa.load(input_wav, sr=16000, mono=True)
    audio = audio[: 16000 * 6]
    sf.write(output_wav, audio, 16000)
