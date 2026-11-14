
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS


# ==========================================
# 1. НАЛАШТУВАННЯ
# ==========================================

DATA_DIR = Path(__file__).resolve().parent

ROWS = 3600
COLS = 7200

MARS_RADIUS = 3_396_000

# Межі класів, отримані з аналізу нічної карти
THRESHOLDS = [128, 207, 263, 407]

CLASS_NAMES = {
    0: "Немає покриття",
    1: "Дуже низька теплова інерція",
    2: "Низька теплова інерція",
    3: "Середня теплова інерція",
    4: "Висока теплова інерція",
    5: "Дуже висока теплова інерція",
}


# ==========================================
# 2. ПОШУК І ЗАВАНТАЖЕННЯ ФАЙЛІВ
# ==========================================

def find_file(filename):
    matches = [
        p for p in DATA_DIR.rglob("*")
        if p.is_file() and p.name.lower() == filename.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"Не знайдено файл: {filename}"
        )

    return matches[0]


print("Завантаження нічної карти TES...")

thermal_path = find_file("global_ti_night_2007.img")
mask_path = find_file("global_ti_msk_night_2007.img")

thermal = np.fromfile(
    thermal_path,
    dtype=">i2"
).reshape((ROWS, COLS))

mask = np.fromfile(
    mask_path,
    dtype=np.uint8
).reshape((ROWS, COLS))


# ==========================================
# 3. КЛАСИФІКАЦІЯ
# ==========================================

print("Класифікація поверхні...")

# 0 — пікселі поза основною зоною покриття.
# 1–5 — класи теплової інерції.

classes = (
    np.digitize(
        thermal,
        bins=THRESHOLDS
    ) + 1
).astype(np.uint8)

# 20 пікселів на градус.
# Рядки 60–3539 відповідають широтам між 87°N та 87°S.

classes[:60, :] = 0
classes[3540:, :] = 0

# Окрема інформація про якість даних:
# 1 — неінтерпольований піксель;
# 0 — інтерпольований піксель;
# 255 — поза зоною покриття.

quality = np.full(
    (ROWS, COLS),
    255,
    dtype=np.uint8
)

quality[60:3540, :] = mask[60:3540, :]


# ==========================================
# 4. СТВОРЕННЯ ГЕОГРАФІЧНОЇ ПРИВ'ЯЗКИ
# ==========================================

pixel_size_x = (
    2 * np.pi * MARS_RADIUS / COLS
)

pixel_size_y = (
    np.pi * MARS_RADIUS / ROWS
)

transform = from_origin(
    -np.pi * MARS_RADIUS,
    np.pi * MARS_RADIUS / 2,
    pixel_size_x,
    pixel_size_y
)

mars_crs = CRS.from_proj4(
    f"+proj=eqc "
    f"+lat_ts=0 "
    f"+lat_0=0 "
    f"+lon_0=0 "
    f"+a={MARS_RADIUS} "
    f"+b={MARS_RADIUS} "
    f"+units=m "
    f"+no_defs"
)


# ==========================================
# 5. ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТУ
# ==========================================

output_path = DATA_DIR / "TES_thermal_classes.tif"

print("Збереження GeoTIFF...")

with rasterio.open(
    output_path,
    "w",
    driver="GTiff",
    height=ROWS,
    width=COLS,
    count=2,
    dtype="uint8",
    crs=mars_crs,
    transform=transform,
    compress="lzw"
) as dst:

    dst.write(classes, 1)
    dst.write(quality, 2)

    dst.set_band_description(
        1,
        "Thermal inertia classes"
    )

    dst.set_band_description(
        2,
        "Data quality mask: 1=original, 0=interpolated, 255=outside coverage"
    )


# ==========================================
# 6. РЕЗУЛЬТАТИ
# ==========================================

print("\n" + "=" * 55)
print("КЛАСИФІКАЦІЮ ЗАВЕРШЕНО!")
print("=" * 55)

for code, name in CLASS_NAMES.items():

    count = np.count_nonzero(classes == code)

    print(
        f"\nКлас {code}: {name}"
    )

    print(
        f"Пікселів: {count:,}"
    )

    if code != 0:
        total = np.count_nonzero(classes != 0)

        print(
            f"Частка: {count / total * 100:.2f}%"
        )

print("\nФайл створено:")
print(output_path)
