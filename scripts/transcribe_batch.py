import os
import time
import whisper
import librosa
import numpy as np
import torch
from utils.io import save_json, save_plaintext

# ======= CONFIGURATION =======
INPUT_DIR = "../data/raw_audio"
OUTPUT_DIR = "../data/transcripts"
MODEL_SIZE = "small"
# =============================


def transcribe_audio(file_path: str, model, save_prefix: str):
    print(f"\n🎧 Transcribing: {os.path.abspath(file_path)}")

    start = time.time()
    result = model.transcribe(file_path)
    end = time.time()
    print(f"✅ Completed in {end - start:.2f}s")

    y, sr = librosa.load(file_path, sr=16000)
    enriched_segments = []
    for i, seg in enumerate(result["segments"]):
        start_sec, end_sec = seg["start"], seg["end"]
        y_seg = y[int(start_sec * sr): int(end_sec * sr)]

        pitches, mags = librosa.piptrack(y=y_seg, sr=sr)
        pitch_vals = pitches[mags > np.median(mags)]
        pitch = np.mean(pitch_vals) if len(pitch_vals) > 0 else 0.0
        energy = np.mean(librosa.feature.rms(y=y_seg))

        enriched_segments.append({
            "id": i,
            "start": start_sec,
            "end": end_sec,
            "text": seg["text"],
            "pitch": round(float(pitch), 2),
            "energy": round(float(energy), 6)
        })

    output = {
        "audio_path": file_path,
        "sample_rate": sr,
        "duration_sec": len(y) / sr,
        "num_segments": len(enriched_segments),
        "language": result["language"],
        "transcript": result["text"],
        "segments": enriched_segments
    }

    save_json(output, save_prefix + ".json")
    with open(save_prefix + "_transcript.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
    save_plaintext(enriched_segments, save_prefix + "_segments.txt")

    print(f"💾 Saved transcript for {os.path.basename(file_path)}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔍 Torch device detected: {device.upper()}")
    if device == "cuda":
        print(f"⚙️ CUDA device: {torch.cuda.get_device_name(0)} "
              f"({torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB VRAM)")
    else:
        print("⚠️ Using CPU only (slower).")

    # Load model
    print(f"\n⏳ Loading Whisper model '{MODEL_SIZE}'...")
    model = whisper.load_model(MODEL_SIZE).to(device)
    print("✅ Model loaded and ready.\n")

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".mp3")]
    if not files:
        print("⚠️ No MP3 files found.")
        return

    total = len(files)
    transcribed = 0
    skipped = 0
    failed = 0
    start_all = time.time()

    print(f"📁 Found {total} MP3 files to process.\n")

    for i, filename in enumerate(files, start=1):
        print(f"--- [{i}/{total}] {filename} ---")

        input_path = os.path.join(INPUT_DIR, filename)
        base_name = os.path.splitext(filename)[0]
        output_prefix = os.path.join(OUTPUT_DIR, base_name)
        json_path = output_prefix + ".json"

        if os.path.exists(json_path):
            print(f"⏩ Skipping {filename} (already transcribed)")
            skipped += 1
            continue

        try:
            transcribe_audio(input_path, model, output_prefix)
            transcribed += 1
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            failed += 1

    end_all = time.time()
    elapsed = end_all - start_all

    print("\n===== SUMMARY =====")
    print(f"🟢 Transcribed: {transcribed}")
    print(f"⏩ Skipped:     {skipped}")
    print(f"🔴 Failed:      {failed}")
    print(f"🕒 Total time:  {elapsed/60:.1f} min")
    print("===================")


if __name__ == "__main__":
    main()
