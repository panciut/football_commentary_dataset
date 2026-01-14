import os
import shutil

SRC_DIR = "data/raw_audio"
DST_DIR = "data/summaries"

def main():
    os.makedirs(DST_DIR, exist_ok=True)

    for filename in os.listdir(SRC_DIR):
        if filename.lower().endswith(".txt"):
            src_path = os.path.join(SRC_DIR, filename)
            dst_path = os.path.join(DST_DIR, filename)

            shutil.move(src_path, dst_path)

if __name__ == "__main__":
    main()
