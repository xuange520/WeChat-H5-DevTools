import sys
import subprocess
from pathlib import Path

def main():
    gui_app = Path(__file__).resolve().parent / "supabase_gui" / "app.py"
    cmd = [sys.executable, str(gui_app)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))

if __name__ == "__main__":
    main()