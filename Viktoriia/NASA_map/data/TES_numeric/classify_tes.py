from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS


# ==========================================
# 1. SETTINGS
# ==========================================

DATA_DIR = Path(__file__).resolve().parent

ROWS = 3600
COLS = 7200

MARS_RADIUS = 3_396_000

# Class thresholds obtained from the analysis of the nighttime map
THRESHOLDS = [128, 207, 263, 407]

CLASS_NAMES = {
    0: "No coverage",
    1: "Very low thermal inertia",
    2: "Low thermal inertia",
    3: "Medium thermal inertia",
    4: "High thermal inertia",
    5: "Very high thermal inertia",
}


# ==========================================
# 2. FINDING AND LOADING FILES
# ==========================================

def find_file(filename):
    matches = [
        p for p in DATA_DIR.rglob("*")
        if p.is_file() and p.name.lower() == filename.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"File not found: {filename}"
        )

    return matches[0]


print("Loading the TES nighttime map...")

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
# 3. CLASSIFICATION
# ==========================================

print("Classifying the surface...")

# 0 — pixels outside the main coverage area.
# 1–5 — thermal inertia classes.

classes = (
    np.digitize(
        thermal,
        bins=THRESHOLDS
    ) + 1
).astype(np.uint8)

# 20 pixels per degree.
# Rows 60–3539 correspond to latitudes between 87°N and 87°S.

classes[:60, :] = 0
classes[3540:, :] = 0

# Separate data quality information:
# 1 — non-interpolated pixel;
# 0 — interpolated pixel;
# 255 — outside the coverage area.

quality = np.full(
    (ROWS, COLS),
    255,
    dtype=np.uint8
)

quality[60:3540, :] = mask[60:3540, :]


# ==========================================
# 4. CREATING THE GEOGRAPHIC REFERENCE
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
# 5. SAVING THE RESULT
# ==========================================

output_path = DATA_DIR / "TES_thermal_classes.tif"

print("Saving the GeoTIFF...")

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
# 6. RESULTS
# ==========================================

print("\n" + "=" * 55)
print("CLASSIFICATION COMPLETED!")
print("=" * 55)

for code, name in CLASS_NAMES.items():

    count = np.count_nonzero(classes == code)

    print(
        f"\nClass {code}: {name}"
    )

    print(
        f"Pixels: {count:,}"
    )

    if code != 0:
        total = np.count_nonzero(classes != 0)

        print(
            f"Share: {count / total * 100:.2f}%"
        )

print("\nFile created:")
print(output_path)