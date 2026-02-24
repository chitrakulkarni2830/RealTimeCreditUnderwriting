import os
import subprocess
import sys

def build():
    # 1. Install PyInstaller if not present
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pywebview"])

# 2. Define the PyInstaller command
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "CreditUnderwriter",
        "--onedir", 
        "--windowed",
        "--add-data", f"{root_dir}/data:data",
        "--add-data", f"{root_dir}/assets:assets",
        "--add-data", f"{root_dir}/src:src",
        "--collect-all", "nicegui",
        str(root_dir / "src" / "dashboard.py")
    ]
    
    print(f"Running in {root_dir}: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=root_dir)

    # 3. Clear quarantine flags (macOS specific fix for "App won't open")
    app_path = root_dir / "dist" / "CreditUnderwriter.app"
    if app_path.exists():
        print(f"Clearing quarantine flags for {app_path}...")
        subprocess.run(["xattr", "-cr", str(app_path)])

if __name__ == "__main__":
    build()
