import os
import re
import unicodedata

RAW_DIR = "downloads"

def normalize_text(text):
    """Remove accents, normalize spaces, punctuation, and casing."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = text.upper().strip()
    return text

def clean_title(title: str) -> str:
    """Standardize YouTube-like match commentary titles."""
    title = normalize_text(title)

    # Remove known recurring parts
    title = re.sub(r"BBC\s*RADIO\s*5\s*LIVE\s*COMMENTARY", "", title)
    title = re.sub(r"\(.*?\)", "", title)  # remove brackets
    title = re.sub(r"COMMENTARY", "", title)
    title = re.sub(r"FINAL", "FINAL_", title)  # avoid confusion with 'Final:' 
    title = re.sub(r"EUROPEAN", "EURO", title)

    # Normalize "VS" and "V"
    title = re.sub(r"\bVS\b|\bV\b", "_", title)

    # Remove tournament years and words
    title = re.sub(r"\bBBC\b|\bLIVE\b", "", title)
    title = re.sub(r"UEFA_", "UEFA_", title)
    title = re.sub(r"FIFA_", "FIFA_", title)

    # Replace separators and punctuation
    title = re.sub(r"[-:–]+", "_", title)
    title = re.sub(r"[^A-Z0-9_]+", "_", title)
    title = re.sub(r"_+", "_", title).strip("_")

    # Shorten redundant endings
    for bad in ["RADIO_5", "BBC", "MATCHDAY", "COMMENTARY"]:
        title = title.replace(bad, "")
    title = re.sub(r"_+", "_", title).strip("_")

    return title

def rename_files():
    os.makedirs(RAW_DIR, exist_ok=True)
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".mp3")]
    if not files:
        print("No MP3 files found")
        return

    for f in files:
        old_path = os.path.join(RAW_DIR, f)
        base, _ = os.path.splitext(f)
        new_base = clean_title(base)
        new_name = new_base + ".mp3"
        new_path = os.path.join(RAW_DIR, new_name)

        # Avoid overwriting
        if os.path.exists(new_path):
            i = 1
            while os.path.exists(os.path.join(RAW_DIR, f"{new_base}_{i}.mp3")):
                i += 1
            new_name = f"{new_base}_{i}.mp3"
            new_path = os.path.join(RAW_DIR, new_name)

        os.rename(old_path, new_path)
        print(f"Renamed: {f}  →  {new_name}")

if __name__ == "__main__":
    rename_files()