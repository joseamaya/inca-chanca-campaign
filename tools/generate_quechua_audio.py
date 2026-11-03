#!/usr/bin/env python3
"""
Genera un paquete de voces sintéticas en quechua para las unidades incas/chancas.

Requiere espeak-ng con la voz 'qu' y ffmpeg. El resultado son archivos OGG y
SoundGroup XML compatibles con 0 A.D.

La voz es sintética y aproximada; no sustituye a una grabación de un hablante
nativo de quechua.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]
OUT = MOD / "audio/voice/quechua/civ"
TMP = Path(tempfile.gettempdir()) / "inca_chanca_voice"
ESPEAK_CANDIDATES = [
    Path(os.environ["ESPEAK_NG"]) if os.environ.get("ESPEAK_NG") else None,
    Path("/usr/bin/espeak-ng"),
    Path("/usr/local/bin/espeak-ng"),
]
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "/usr/bin/ffmpeg"

PHRASES = {
    "select": ["Arí, apu", "Arí"],
    "walk": ["Riy", "Kallpachakuy", "Ñawpaqman"],
    "attack": ["Chaqmay", "Awqanakuy"],
    "gather": ["Pallay", "Allay", "Qiwiy"],
    "repair": ["Allichay"],
    "build": ["Ruway", "Wasi ruway"],
    "garrison": ["Yaykuy"],
}


def find_espeak() -> Path:
    for candidate in ESPEAK_CANDIDATES:
        if candidate and candidate.exists():
            return candidate
    found = shutil.which("espeak-ng")
    if found:
        return Path(found)
    raise SystemExit("No se encontró espeak-ng. Instalalo o definí ESPEAK_NG=/ruta/a/espeak-ng.")


def synth(espeak: Path, text: str, out_wav: Path, pitch: int, speed: int, voice: str = "qu") -> None:
    cmd = [
        str(espeak), "-v", voice, "-p", str(pitch), "-s", str(speed),
        "-w", str(out_wav), text,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def to_ogg(wav: Path, ogg: Path) -> None:
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "4", str(ogg)]
    subprocess.run(cmd, check=True)


def sound_group(path: Path, sounds: list[str]) -> None:
    lines = [
        '<?xml version="1.0" encoding="utf-8" standalone="no" ?>',
        '<SoundGroup>',
        '\t<Gain>1</Gain>',
        '\t<Priority>100</Priority>',
        '\t<ConeGain>1</ConeGain>',
        '\t<Looping>0</Looping>',
        '\t<RandOrder>1</RandOrder>',
        '\t<Distanceless>1</Distanceless>',
        '\t<RandGain>1</RandGain>',
        '\t<RandPitch>1</RandPitch>',
        '\t<Threshold>1</Threshold>',
        '\t<Path>audio/voice/quechua/civ</Path>',
    ]
    for s in sounds:
        lines.append(f'\t<Sound>{s}</Sound>')
    lines.append('</SoundGroup>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    espeak = find_espeak()
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    if not Path(FFMPEG).exists():
        raise SystemExit("No se encontró ffmpeg.")

    for phenotype, voice, pitch in (("male", "qu", 40), ("female", "qu+f3", 55)):
        for action, phrases in PHRASES.items():
            sounds: list[str] = []
            for i, phrase in enumerate(phrases, 1):
                for variant, (p, s) in enumerate(((pitch, 138), (pitch + 8, 152)), 1):
                    name = f"civ_{phenotype}_{action}_{i}_{variant}.ogg"
                    wav = TMP / name.replace(".ogg", ".wav")
                    ogg = OUT / name
                    synth(espeak, phrase, wav, p, s, voice)
                    to_ogg(wav, ogg)
                    sounds.append(name)
            sound_group(OUT / f"civ_{phenotype}_{action}.xml", sounds)
    print("Audio quechua generado en", OUT)


if __name__ == "__main__":
    main()
