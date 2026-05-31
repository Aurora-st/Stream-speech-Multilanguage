import os
import shutil
from pathlib import Path


def safe_delete(path: Path):
    if path.exists():
        print(f"Removing: {path}")
        shutil.rmtree(path, ignore_errors=True)
    else:
        print(f"Not found: {path}")


def main():
    user_home = Path.home()

    targets = [
        user_home / ".cache" / "huggingface",
        user_home / ".cache" / "torch",
        user_home / ".cache" / "TTS",
        user_home / ".cache" / "pip",
    ]

    print("\nCleaning old model downloads from C drive...\n")

    for path in targets:
        safe_delete(path)

    print("\nCleanup complete. Future downloads will go to D drive.\n")


if __name__ == "__main__":
    main()
