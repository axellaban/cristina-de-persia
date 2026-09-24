#!/usr/bin/env python3
"""Música de la entrada de Macri (music/story_3_Jaffar_enters.ogg).

Una marcha de acto con globos, compuesta para el mod (melodía original, sin
derechos de terceros): melodía con onda cuadrada, bajo "um-pa", acordes a
contratiempo y un shaker. Suena unos 10 segundos, lo que dura la entrada.
Se puede reemplazar por otro OGG con el mismo nombre (ver music/LEEME.txt).

Hace falta: pip install numpy soundfile
"""
import os
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "music", "story_3_Jaffar_enters.ogg")

RATE = 22050
BPM = 128
BEAT = 60 / BPM
NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def freq(name):
    """'C5' -> Hz (A4 = 440)."""
    semis = NOTES[name[0]] + (1 if "#" in name else 0) + 12 * (int(name[-1]) + 1)
    return 440.0 * 2 ** ((semis - 69) / 12)


# melodía: (nota, tiempos)
MELODY = [
    ("G4", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("A5", .5), ("G5", .5), ("E5", 1),
    ("F5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("E5", 1),
    ("G4", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("C6", 1), ("B5", .5), ("A5", .5),
    ("G5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("G5", .5), ("F5", .5), ("D5", .5), ("B4", .5),
    ("C5", .5), ("E5", .5), ("G5", .5), ("C6", 2.5),
]
# acordes, de a medio compás: (fundamental del bajo, quinta del bajo, notas del acorde)
CHORDS = [
    ("C3", "G2", ["C4", "E4", "G4"]), ("C3", "G2", ["C4", "E4", "G4"]),
    ("F2", "C3", ["F4", "A4", "C5"]), ("G2", "D3", ["G4", "B4", "D5"]),
    ("C3", "G2", ["C4", "E4", "G4"]), ("A2", "E3", ["A4", "C5", "E5"]),
    ("G2", "D3", ["G4", "B4", "D5"]), ("G2", "D3", ["G4", "B4", "D5"]),
    ("C3", "G2", ["C4", "E4", "G4"]),
]
BARS = 5
TOTAL = BARS * 4 * BEAT + 0.6


def square(f, t, duty=0.25):
    return np.where((f * t) % 1.0 < duty, 1.0, -1.0)


def triangle(f, t):
    return 2 * np.abs(2 * ((f * t) % 1.0) - 1) - 1


def envelope(n, attack=0.005, release=0.04, sustain=1.0):
    env = np.full(n, sustain)
    a, r = int(attack * RATE), int(release * RATE)
    if a:
        env[:a] = np.linspace(0, sustain, a)
    if r and r < n:
        env[-r:] *= np.linspace(1, 0, r)
    return env


def add(buf, start, sig):
    i = int(start * RATE)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def main():
    rng = np.random.default_rng(1983)
    out = np.zeros(int(TOTAL * RATE))

    # melodía, con un poco de vibrato en las notas largas
    time = 0.0
    for note, beats in MELODY:
        dur = beats * BEAT
        n = int(dur * RATE)
        t = np.arange(n) / RATE
        f = freq(note) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * (t > 0.25))
        phase = np.cumsum(f) / RATE
        sig = np.where(phase % 1.0 < 0.25, 1.0, -1.0) * envelope(n, release=min(0.06, dur * 0.3))
        if beats > 2:
            sig *= np.linspace(1, 0.2, n)
        add(out, time, 0.22 * sig)
        time += dur

    # bajo "um-pa" y acordes a contratiempo
    for half, (root, fifth, chord) in enumerate(CHORDS):
        base = half * 2 * BEAT
        if base >= BARS * 4 * BEAT - 0.01:
            break
        last = half == len(CHORDS) - 1
        for k, note in enumerate([root, fifth] if not last else [root]):
            dur = BEAT * (0.9 if not last else 2.4)
            n = int(dur * RATE)
            t = np.arange(n) / RATE
            add(out, base + k * BEAT, 0.30 * triangle(freq(note), t) * envelope(n, release=0.05))
        for k in range(2 if not last else 1):
            dur = BEAT * (0.35 if not last else 2.4)
            n = int(dur * RATE)
            t = np.arange(n) / RATE
            stab = sum(square(freq(c), t, 0.5) for c in chord) / len(chord)
            add(out, base + k * BEAT + (BEAT / 2 if not last else 0), 0.07 * stab * envelope(n, release=0.03))

    # shaker en cada corchea, más fuerte a contratiempo
    for i in range(BARS * 8 - 3):
        n = int(0.05 * RATE)
        noise = rng.uniform(-1, 1, n)
        noise = np.diff(noise, prepend=0)  # más agudo
        env = np.exp(-np.arange(n) / (0.012 * RATE))
        add(out, i * BEAT / 2, (0.05 if i % 2 else 0.025) * noise * env)

    fade = int(0.5 * RATE)
    out[-fade:] *= np.linspace(1, 0, fade)
    out /= np.max(np.abs(out)) / 0.8
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sf.write(OUT, out.astype(np.float32), RATE, format="OGG", subtype="VORBIS")
    print(f"música -> {OUT} ({len(out) / RATE:.1f} s)")


if __name__ == "__main__":
    main()
