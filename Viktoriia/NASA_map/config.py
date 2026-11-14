
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

MAP_PATH = BASE_DIR / "data" / "SIM3292_Global_Geology" / "SIM3292_Global_Geology.shp"