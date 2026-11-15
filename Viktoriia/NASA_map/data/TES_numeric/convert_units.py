import numpy as np
import rasterio

from pathlib import Path
from rasterio.transform import from_origin


FILE = "ANBunits2007.bin"

with open(FILE, "rb") as f:
    f.seek(7200)
    data = np.fromfile(f, dtype=np.uint8)

data = data.reshape((3600, 7200))

print("Dimensions:", data.shape)
print("Classes:", np.unique(data, return_counts=True))

with open(FILE, "rb") as f:
    header = f.read(7200)

print(header.decode("ascii", errors="replace"))


# Convert latitude values to run from north to south
data = np.flipud(data)

# Convert longitude values from the western longitude system
# to the standard range from -180° to +180°
data = np.concatenate((
    data[:, :3600][:, ::-1],
    data[:, 3600:][:, ::-1]
), axis=1)

# Radius of Mars
R = 3396000

# Geographic reference
transform = from_origin(
    -np.pi * R,
    np.pi * R / 2,
    2 * np.pi * R / 7200,
    np.pi * R / 3600
)

output_path = Path("TES_thermophysical_units.tif")

with rasterio.open(
    output_path,
    "w",
    driver="GTiff",
    height=3600,
    width=7200,
    count=1,
    dtype="uint8",
    crs=f"+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +R={R} +units=m +no_defs",
    transform=transform,
    nodata=0,
    compress="lzw"
) as dst:
    dst.write(data, 1)

print("Done! Created:", output_path.resolve())