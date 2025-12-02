# @title 🐍 The Rattlesnake Engine (Biomimetic Edition)
# @markdown Click Play to generate your "Serpentine" Library.

import os
import csv
import zipfile
import math
import time

print("Installing Audio Engine...")
!pip install mido > /dev/null
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from google.colab import files

# ======================================================
# 1. THE REPTILIAN CONSTANTS
# ======================================================

KEYS = {"F_Minor": 53, "G_Minor": 55, "C_Minor": 48}
BPMS = range(130, 165, 5)

# SLITHER: (Magnitude, Speed) for the 808 Sine Wave
SLITHER_MATH = [(2000, 5), (4000, 8), (8192, 12)]

# RATTLE: (Speed) How fast the Hi-Hats accelerate
RATTLE_SPEEDS = [0.5, 0.8, 1.2]

OUTPUT_DIR = "/content/Panek_Trap_Library"

# ======================================================
# 2. THE ENGINE
# ======================================================

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_snake_track(key_name, root, bpm, slither_params, rattle_k, filename):
    mid = MidiFile()

    # TRACKS
    track_rattle = MidiTrack(); mid.tracks.append(track_rattle) # Hats
    track_slither = MidiTrack(); mid.tracks.append(track_slither) # 808
    track_strike = MidiTrack(); mid.tracks.append(track_strike) # Kick/Snare
    track_hiss = MidiTrack(); mid.tracks.append(track_hiss) # Melody

    # SETUP
    track_rattle.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
    track_slither.append(Message('program_change', program=38, time=0)) # Synth Bass
    track_hiss.append(Message('program_change', program=97, time=0)) # FX Soundtrack (Atmosphere)

    # --- THE LOGIC ---
    bars = 8
    ticks = 120 # 16th note
    total_steps = bars * 16

    # Phrygian Scale (The Venom): Root, b2, b3
    scale = [0, 1, 3, 5, 7, 8, 10]

    # Unpack Sine Vars
    slither_mag, slither_freq = slither_params

    events_rattle, events_slither, events_strike, events_hiss = [], [], [], []

    for i in range(total_steps):
        t = i * ticks
        beat = i % 16
        bar_pos = (i // 16) % 4

        # --- A. THE RATTLE (Accelerating Hats) ---
        # Base: 8th notes
        if i % 2 == 0:
            # Rattle Math: Density increases towards end of bar
            # Normalized position in bar (0.0 to 1.0)
            progress = (i % 16) / 16.0

            # Probability of Rattle increases with progress
            if progress > 0.5 and (progress * rattle_k) > 0.6:
                # FAST RATTLE (32nd or 64th notes)
                repeats = 4 # Machine gun
                sub_dur = int(ticks * 2 / repeats)
                for r in range(repeats):
                    # Velocity fade out like a tail
                    vel = 110 - (r * 15)
                    events_rattle.append({'n': 42, 'v': vel, 't': t + (r*sub_dur), 'd': sub_dur})
            else:
                # Standard tick
                events_rattle.append({'n': 42, 'v': 90, 't': t, 'd': 50})

        # --- B. THE SLITHER (Sinusoidal 808) ---
        # 808 hits on Kick pattern usually
        if beat == 0 or (beat == 10 and bar_pos % 2 == 0):
            note = root - 24

            # THE SINE WAVE BEND
            # We want the pitch to wiggle down
            events_slither.append({
                'n': note, 'v': 120, 't': t, 'd': 800,
                'snake': True, 'mag': slither_mag, 'freq': slither_freq
            })

        # --- C. THE STRIKE (Kick/Snare) ---
        # Kick (Head)
        if beat == 0 or beat == 10:
             events_strike.append({'n': 36, 'v': 127, 't': t, 'd': 100})
        # Snare (Bite)
        if beat == 8:
             events_strike.append({'n': 38, 'v': 127, 't': t, 'd': 100})

        # --- D. THE HISS (Atmosphere) ---
        # Dissonant semitone cluster (Root + b2)
        if i % 32 == 0:
            events_hiss.append({'n': root + 12, 'v': 60, 't': t, 'd': 3800})
            events_hiss.append({'n': root + 13, 'v': 60, 't': t, 'd': 3800}) # The rub

    # WRITE FUNCTION (With Sine Bends)
    def write(track, events):
        events.sort(key=lambda x: x['t'])
        last_t = 0
        for e in events:
            dt = max(0, e['t'] - last_t)

            if 'snake' in e:
                # 808 Sine Logic
                # 1. Start at Root
                track.append(Message('note_on', note=e['n'], velocity=e['v'], time=dt))

                # 2. Wiggle pitch during note
                wiggles = 4
                wiggle_len = int(e['d'] / wiggles)
                for w in range(wiggles):
                    # Sine Wave Math: sin(w)
                    sine_val = math.sin(w * e['freq'])
                    pitch_val = int(sine_val * e['mag'])
                    track.append(Message('pitchwheel', pitch=pitch_val, time=wiggle_len))

                # 3. Off
                track.append(Message('note_off', note=e['n'], velocity=0, time=0))
                track.append(Message('pitchwheel', pitch=0, time=0))
                last_t = e['t'] + e['d']
            else:
                track.append(Message('note_on', note=e['n'], velocity=e['v'], time=dt))
                track.append(Message('note_off', note=e['n'], velocity=0, time=e['d']))
                last_t = e['t'] + e['d']

    write(track_rattle, events_rattle)
    write(track_slither, events_slither)
    write(track_strike, events_strike)
    write(track_hiss, events_hiss)

    mid.save(filename)

# ======================================================
# 3. EXECUTION
# ======================================================

print("--- STARTING RATTLESNAKE FACTORY ---")
ensure_dir(OUTPUT_DIR)
csv_name = "/content/Panek_Trap_Manifest.csv"

with open(csv_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Filename", "Key", "BPM", "SlitherMath", "RattleSpeed", "Author"])

    count = 0
    for key, root in KEYS.items():
        for bpm in BPMS:
            for slither in SLITHER_MATH:
                for rattle in RATTLE_SPEEDS:
                    fname = f"Trap_{key}_{bpm}_Slither{slither[1]}_Rattle{rattle}.mid"
                    path = os.path.join(OUTPUT_DIR, fname)

                    generate_snake_track(key, root, bpm, slither, rattle, path)
                    writer.writerow([fname, key, bpm, slither, rattle, "Nick Panek"])
                    count += 1
                    if count % 50 == 0: print(f"Coiled {count} tracks...")

print(f"TOTAL: {count} assets created.")
print("--- ZIPPING ---")
zip_name = "/content/NickPanek_Trap_Collection.zip"
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(csv_name, arcname="Panek_Trap_Manifest.csv")
    for r, d, fnames in os.walk(OUTPUT_DIR):
        for f in fnames:
            z.write(os.path.join(r, f), arcname=f)

print(f"DONE. Downloading {zip_name}...")
files.download(zip_name)
