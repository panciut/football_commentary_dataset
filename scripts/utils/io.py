import json

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_plaintext(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}] "
                    f"P:{seg['pitch']:.2f} E:{seg['energy']:.6f} | {seg['text']}\n")