import hashlib
import os
import sys
import time
import urllib.request
from pathlib import Path

MODEL_DIR = Path("data/models")
MODEL_FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
MODEL_PATH = MODEL_DIR / MODEL_FILENAME
EXPECTED_SHA256 = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"
EXPECTED_SIZE = 2104932768
OFFICIAL_HF_URL = f"https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/{MODEL_FILENAME}"

def download_and_verify():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = MODEL_DIR / f"{MODEL_FILENAME}.tmp"
    
    print(f"Connecting to official HuggingFace repository: {OFFICIAL_HF_URL}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(OFFICIAL_HF_URL, headers=headers)
    
    start_time = time.time()
    sha256_hasher = hashlib.sha256()
    
    with urllib.request.urlopen(req) as response:
        actual_size = int(response.headers.get("content-length", 0))
        print(f"Content Length: {actual_size:,} bytes (Expected: {EXPECTED_SIZE:,} bytes)")
        
        downloaded = 0
        block_size = 4 * 1024 * 1024 # 4MB buffer
        last_print = 0
        
        with open(temp_path, "wb") as f_out:
            while True:
                chunk = response.read(block_size)
                if not chunk:
                    break
                f_out.write(chunk)
                sha256_hasher.update(chunk)
                downloaded += len(chunk)
                
                now = time.time()
                if now - last_print >= 1.0 or downloaded == actual_size:
                    percent = (downloaded / actual_size * 100) if actual_size else 0
                    elapsed = now - start_time
                    speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    sys.stdout.write(f"\rDownloading: {downloaded / (1024**3):.2f} / {actual_size / (1024**3):.2f} GB ({percent:.1f}%) @ {speed:.2f} MB/s")
                    sys.stdout.flush()
                    last_print = now
                    
    computed_sha = sha256_hasher.hexdigest()
    print(f"\nDownload finished in {time.time() - start_time:.1f}s.")
    print(f"Computed SHA256: {computed_sha}")
    print(f"Expected SHA256: {EXPECTED_SHA256}")
    
    if computed_sha.lower() != EXPECTED_SHA256.lower():
        print("ERROR: SHA256 MISMATCH! Removing corrupted temporary file.")
        if temp_path.exists():
            temp_path.unlink()
        sys.exit(1)
        
    print("SHA256 verification SUCCESS! Replacing model file.")
    if MODEL_PATH.exists():
        MODEL_PATH.unlink()
    temp_path.rename(MODEL_PATH)
    print(f"Model successfully verified and ready at: {MODEL_PATH}")

if __name__ == "__main__":
    download_and_verify()
