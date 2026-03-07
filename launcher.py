import sys
import os

# Ensure the root directory is in the PYTHONPATH so 'src' can be imported correctly by PyInstaller
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if application_path not in sys.path:
    sys.path.insert(0, application_path)

from src.main import main

if __name__ == "__main__":
    main()
