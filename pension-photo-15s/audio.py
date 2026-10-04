"""Synthesizes the 15s soundtrack for the photo cut (pure Python, no dependencies).

Layers: soft ambient pad (D -> Gmaj7 -> Asus4 -> D), sparse pluck arpeggio,
calculator click, paper slides, digital tone for the question mark, and a calm
resolving bell accent for the final message. Output: 44.1 kHz stereo WAV.
"""
import math
import random
import struct
import sys
import wave

SR = 44100
DUR = 15.0
N = int(SR * DUR)
TAU = 2 * math.pi
random.seed(7)

L = [0.0] * N
R = [0.0] * N


def add(i, v, pan=0.0):
    if 0 <= i < N:
        L[i] += v * (1 - pan) * 0.5 * 2 ** 0.5
        R[i] += v * (1 + pan) * 0.5 * 2 ** 0.5


def env_adsr(t, start, end, atk, rel):
    if t < start or t > end + rel:
        return 0.0
    if t < start + atk:
        return (t - start) / atk
    if t <= end:
        return 1.0
    return 1.0 - (t - end) / rel


# ---------- pad ----------
D3, E3, Fs3, G2, A2, A3, B3 = 146.83, 164.81, 185.00, 98.00, 110.00, 220.00, 246.94
Cs4, D4, E4, Fs4 = 277.18, 293.66, 329.63, 369.99
CHORDS = [
    (0.00, 8.25, [D3, A3, Cs4, E4, Fs4]),          # Dmaj9   certainty -> doubt
    (8.00, 10.95, [G2, D3, Fs3, B3, E4]),          # Gmaj7(9) the real question
    (10.50, 11.15, [A2, D3, E3, A3, D4]),          # Asus4 (tension)
    (11.00, 15.0, [D3, A3, D4, E4, Fs4]),          # Dadd9 resolve (clarity)
]
for start, end, notes in CHORDS:
    i0, i1 = int(start * SR), min(N, int((end + 1.4) * SR))
    for k, f in enumerate(notes):
        amp = 0.030 if f > 200 else 0.040
        pan = (k / (len(notes) - 1) - 0.5) * 0.6
        ph = random.random() * TAU
        for i in range(i0, i1):
            t = i / SR
            e = env_adsr(t, start, end, 1.1 if start > 0 else 0.6, 1.4)
            if e <= 0:
                continue
            lfo = 1 + 0.08 * math.sin(TAU * 0.23 * t + k)
            s = (math.sin(TAU * f * t + ph) + 0.6 * math.sin(TAU * f * 1.0025 * t)
                 + 0.18 * math.sin(TAU * 2 * f * t) + 0.05 * math.sin(TAU * 3 * f * t))
            add(i, s * amp * e * lfo, pan)

# ---------- pluck arpeggio (sparse, 96 bpm eighths) ----------
step = 60 / 96 / 2
ARP = {0: [D4 * 2, A3 * 2, Fs4 * 2, E4 * 2], 1: [B3 * 2, Fs3 * 4, D4 * 2, E4 * 2],
       2: [A3 * 2, D4 * 2, E4 * 2, D4 * 2], 3: [Fs4 * 2, D4 * 2, A3 * 2, E4 * 2]}
t = 0.45
n = 0
while t < 13.6:
    sec = 0 if t < 8 else 1 if t < 10.5 else 2 if t < 11.0 else 3
    if n % 4 != 3:  # leave breathing space
        f = ARP[sec][n % 4]
        i0 = int(t * SR)
        pan = 0.35 if n % 2 else -0.35
        for j in range(int(0.9 * SR)):
            tt = j / SR
            e = math.exp(-tt / 0.22) * min(1, tt / 0.004)
            s = math.sin(TAU * f * tt) + 0.25 * math.sin(TAU * 2 * f * tt) * math.exp(-tt / 0.06)
            add(i0 + j, 0.022 * e * s, pan)
    t += step
    n += 1

# ---------- calculator click ----------
for tc, amp in ((0.30, 0.50), (0.46, 0.20)):
    i0 = int(tc * SR)
    prev = 0.0
    for j in range(int(0.04 * SR)):
        tt = j / SR
        nz = random.uniform(-1, 1)
        hp = nz - prev
        prev = nz
        s = 0.6 * hp * math.exp(-tt / 0.0016) + math.sin(TAU * 3100 * tt) * math.exp(-tt / 0.004)
        s += 0.5 * math.sin(TAU * 950 * tt) * math.exp(-tt / 0.008)
        add(i0 + j, amp * s * 0.5, 0.05)

# ---------- document highlight tone (marker sweep over the figure) ----------
i0 = int(0.58 * SR)
for j in range(int(1.2 * SR)):
    tt = j / SR
    f = 880 + 440 * min(1, tt / 0.6)
    e = min(1, tt / 0.08) * math.exp(-tt / 0.35)
    add(i0 + j, 0.035 * e * math.sin(TAU * f * tt), -0.1)

# ---------- paper slides (one per document: right, left, below, above) ----------
for k, (tp, pan) in enumerate(((3.80, 0.45), (4.25, -0.45))):
    i0 = int((tp + 0.02) * SR)
    lp1 = lp2 = 0.0
    length = 0.55
    for j in range(int(length * SR)):
        tt = j / SR
        nz = random.uniform(-1, 1)
        lp1 += 0.35 * (nz - lp1)       # gentle low-pass
        lp2 += 0.03 * (lp1 - lp2)      # remove rumble
        band = lp1 - lp2
        flutter = 0.75 + 0.25 * math.sin(TAU * (23 + 5 * k) * tt) * random.uniform(0.6, 1)
        e = min(1, tt / 0.07) * math.exp(-max(0, tt - 0.07) / 0.16)
        add(i0 + j, 0.30 * band * e * flutter, pan)
    # soft landing tap
    i1 = int((tp + 0.78) * SR)
    for j in range(int(0.12 * SR)):
        tt = j / SR
        add(i1 + j, 0.05 * math.sin(TAU * 110 * tt) * math.exp(-tt / 0.025), pan * 0.5)

# ---------- digital tone (question mark) ----------
for tb, f in ((8.88, 1318.51), (9.00, 1975.53)):
    i0 = int(tb * SR)
    for j in range(int(0.5 * SR)):
        tt = j / SR
        e = min(1, tt / 0.006) * math.exp(-tt / 0.09)
        add(i0 + j, 0.06 * e * (math.sin(TAU * f * tt) + 0.2 * math.sin(TAU * 2 * f * tt)), 0.15)

# ---------- calm resolved accent (final message) ----------
i0 = int(11.05 * SR)
for k, f in enumerate((587.33, 739.99, 880.00, 1174.66)):
    pan = (k - 1.5) * 0.2
    for j in range(int(4.4 * SR)):
        tt = j / SR
        e = min(1, tt / 0.01) * math.exp(-tt / (1.6 - k * 0.15))
        s = math.sin(TAU * f * tt) + 0.12 * math.sin(TAU * 2.76 * f * tt) * math.exp(-tt / 0.3)
        add(i0 + j, 0.032 * e * s, pan)
for j in range(int(4.4 * SR)):  # low warm swell
    tt = j / SR
    e = min(1, tt / 0.35) * math.exp(-tt / 1.8)
    add(i0 + j, 0.09 * e * math.sin(TAU * 73.42 * tt))


# ---------- reverb (Schroeder) ----------
def reverb(x, combs, aps, fb=0.80, damp=0.25):
    out = [0.0] * len(x)
    for d in combs:
        buf = [0.0] * d
        lp = 0.0
        idx = 0
        for i, v in enumerate(x):
            y = buf[idx]
            lp = y * (1 - damp) + lp * damp
            buf[idx] = v + lp * fb
            out[i] += y
            idx = idx + 1 if idx + 1 < d else 0
    for d in aps:
        buf = [0.0] * d
        idx = 0
        g = 0.5
        for i, v in enumerate(out):
            b = buf[idx]
            y = -v + b
            buf[idx] = v + b * g
            out[i] = y
            idx = idx + 1 if idx + 1 < d else 0
    return out


wetL = reverb(L, [1557, 1617, 1491, 1422], [225, 556])
wetR = reverb(R, [1580, 1640, 1514, 1445], [248, 579])
mixL = [a + 0.07 * b for a, b in zip(L, wetL)]
mixR = [a + 0.07 * b for a, b in zip(R, wetR)]

# master fade (keep click audible), gentle tail fade
for i in range(N):
    t = i / SR
    g = 1.0
    if t > 14.0:
        g = max(0.0, 1 - (t - 14.0) / 1.0) ** 1.5
    mixL[i] *= g
    mixR[i] *= g

peak = max(max(abs(v) for v in mixL), max(abs(v) for v in mixR))
gain = 0.89 / peak
out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    frames = bytearray()
    for a, b in zip(mixL, mixR):
        frames += struct.pack('<hh', int(math.tanh(a * gain) * 32767), int(math.tanh(b * gain) * 32767))
    w.writeframes(bytes(frames))
print('wrote', out, 'peak', round(peak, 3))
