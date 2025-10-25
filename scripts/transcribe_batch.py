import whisper
import time
import os
import librosa
import numpy as np
from utils.io import save_json, save_plaintext

RAW_DIR = "../data/raw_audio"
OUT_DIR = "../data/transcripts"
MODEL_SIZE = "small"

def transcribe_audio(file_path, model, save_to):
    print(f"\n🎧 Transcribing {os.path.basename(file_path)}")
    result = model.transcribe(file_path)
    y, sr = librosa.load(file_path, sr=16000)

    enriched = []
    for i, seg in enumerate(result["segments"]):
        start, end = seg["start"], seg["end"]
        ys = y[int(start*sr):int(end*sr)]
        pitches, mags = librosa.piptrack(y=ys, sr=sr)
        pitch_vals = pitches[mags > np.median(mags)]
        pitch = np.mean(pitch_vals) if len(pitch_vals) > 0 else 0.0
        energy = np.mean(librosa.feature.rms(y=ys))
        enriched.append({
            "id": i,
            "start": start,
            "end": end,
            "text": seg["text"],
            "pitch": round(float(pitch), 2),
            "energy": round(float(energy), 6)
        })

    data = {
        "audio_path": file_path,
        "sample_rate": sr,
        "duration_sec": len(y) / sr,
        "language": result["language"],
        "transcript": result["text"],
        "segments": enriched,
    }

    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    save_json(data, save_to + ".json")

    with open(save_to + "_transcript.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])

    save_plaintext(enriched, save_to + "_segments.txt")
    print(f"✅ Saved: {save_to}.*")

if __name__ == "__main__":
    model = whisper.load_model(MODEL_SIZE)
    os.makedirs(OUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".mp3")]
    print(f"Found {len(files)} MP3 files in raw_audio.")

    for f in files:
        base = os.path.splitext(f)[0]
        out_prefix = os.path.join(OUT_DIR, base)
        json_path = out_prefix + ".json"

        # Skip if already transcribed
        if os.path.exists(json_path):
            print(f"⏩ Skipping {f} (already transcribed)")
            continue

        try:
            transcribe_audio(os.path.join(RAW_DIR, f), model, out_prefix)
        except Exception as e:
            print(f"❌ Error processing {f}: {e}")