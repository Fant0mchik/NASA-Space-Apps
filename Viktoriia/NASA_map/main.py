
from pathlib import Path
import runpy
import webbrowser

PROJECT_DIR = Path(__file__).resolve().parent
HTML_PATH = PROJECT_DIR / "output" / "mars_globe_3d.html"

# Create the interactive globe
runpy.run_path(str(PROJECT_DIR / "globe_3d.py"), run_name="__main__")

# Open the generated map in the browser
if HTML_PATH.exists():
    webbrowser.open(HTML_PATH.as_uri())
else:
    print("Not found")
