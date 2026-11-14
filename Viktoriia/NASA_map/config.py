
from pathlib import Path

# Основна папка проєкту
BASE_DIR = Path(__file__).resolve().parent

# Можливі розташування датасету
DATA_LOCATIONS = [
    BASE_DIR / "data" / "SIM3292_Global_Geology",
    BASE_DIR / "SIM3292_Global_Geology",
    Path(r"C:\Users\Victoria\Downloads\SIM3292_Global_Geology")
]

# Знаходимо папку з картою
DATA_DIR = next(
    (
        folder for folder in DATA_LOCATIONS
        if (folder / "SIM3292_Global_Geology.shp").exists()
    ),
    None
)

if DATA_DIR is None:
    raise FileNotFoundError(
        "Не знайдено SIM3292_Global_Geology.shp. "
        "Перевір розташування папки з датасетом."
    )

# Шлях до Shapefile
MAP_PATH = DATA_DIR / "SIM3292_Global_Geology.shp"

# Папка для результатів
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

print("Project:", BASE_DIR)
print("Map:", MAP_PATH)
