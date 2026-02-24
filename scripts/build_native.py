import os
import subprocess
import sys

def build():
    # 1. Install PyInstaller if not present
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pywebview"])

    # 2. Define the PyInstaller command
    # We include data and assets folders
    # --onefile: bundle into a single executable
    # --windowed: no terminal on macOS
    # --add-data: source:destination
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "CreditUnderwriter",
        "--onedir", # More stable for macOS .app bundles
        "--windowed",
        "--add-data", "data:data",
        "--add-data", "assets:assets",
        "--add-data", "src:src",
        "--collect-all", "nicegui", # Ensures all NiceGUI assets are included
        "src/dashboard.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

    # 3. Clear quarantine flags (macOS specific fix for "App won't open")
    app_path = os.path.join("dist", "CreditUnderwriter.app")
    if os.path.exists(app_path):
        print(f"Clearing quarantine flags for {app_path}...")
        subprocess.run(["xattr", "-cr", app_path])

if __name__ == "__main__":
    build()
