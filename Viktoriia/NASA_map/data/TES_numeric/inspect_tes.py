from pathlib import Path
import numpy as np

# ==========================================
# 1. SETTINGS
# ==========================================

DATA_DIR = Path(__file__).resolve().parent

ROWS = 3600
COLS = 7200

BINS = [5, 50, 100, 150, 200, 250, 300,
        400, 500, 750, 1000, 2000, 5000]


def find_file(filename):
    """Finds a file in the directory and its subdirectories."""
    matches = [
        p for p in DATA_DIR.rglob("*")
        if p.is_file() and p.name.lower() == filename.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"File not found: {filename}"
        )

    return matches[0]


# ==========================================
# 2. DATA READING
# ==========================================

def load_map(filename):
    path = find_file(filename)

    data = np.fromfile(path, dtype=">i2")

    if data.size != ROWS * COLS:
        raise ValueError(
            f"Incorrect map size {filename}: "
            f"{data.size} values"
        )

    return data.reshape((ROWS, COLS))


def load_mask(filename):
    path = find_file(filename)

    data = np.fromfile(path, dtype=np.uint8)

    if data.size != ROWS * COLS:
        raise ValueError(
            f"Incorrect mask size {filename}: "
            f"{data.size} values"
        )

    return data.reshape((ROWS, COLS))


# ==========================================
# 3. STATISTICS FOR ONE MAP
# ==========================================

def analyze_map(name, data, mask):

    print("\n" + "=" * 65)
    print(f"ANALYSIS: {name}")
    print("=" * 65)

    valid = data[mask != 0]

    print("\nDIMENSIONS:")
    print("Map:", data.shape)
    print("Mask:", mask.shape)

    print("\nMASK:")

    values, counts = np.unique(
        mask, return_counts=True
    )

    for value, count in zip(values, counts):
        print(
            f"Value {value}: "
            f"{count:,} pixels "
            f"({count / mask.size * 100:.2f}%)"
        )

    print("\nMAIN STATISTICS:")
    print("Number of valid pixels:", len(valid))
    print("Minimum:", valid.min())
    print("Maximum:", valid.max())
    print("Mean:", round(float(valid.mean()), 2))
    print("Median:", float(np.median(valid)))

    print("\nPERCENTILES:")

    for p in [5, 25, 50, 75, 90, 95, 97, 98, 99, 99.5, 99.9]:
        print(
            f"{p}%: "
            f"{np.percentile(valid, p):.2f}"
        )

    print("\nVALUE DISTRIBUTION:")

    counts, edges = np.histogram(
        valid, bins=BINS
    )

    for i in range(len(counts)):
        percentage = counts[i] / len(valid) * 100

        print(
            f"{edges[i]:.0f}–{edges[i+1]:.0f}: "
            f"{counts[i]:,} pixels "
            f"({percentage:.2f}%)"
        )

    print("\nHIGH VALUES (>1000):")

    high = valid[valid > 1000]

    print("Count:", len(high))

    if len(high) > 0:
        print("Minimum:", high.min())
        print("Maximum:", high.max())
        print("Mean:", round(float(high.mean()), 2))

        unique, freq = np.unique(
            high, return_counts=True
        )

        order = np.argsort(freq)[::-1]

        print("15 most frequent values:")

        for i in order[:15]:
            print(
                f"{unique[i]}: {freq[i]:,} pixels"
            )

    return valid


# ==========================================
# 4. LOADING NIGHTTIME AND DAYTIME MAPS
# ==========================================

print("=" * 65)
print("NASA MGS TES — ANALYSIS OF MARTIAN THERMAL INERTIA")
print("=" * 65)

print("\nLoading the nighttime map...")
night = load_map("global_ti_night_2007.img")

print("Loading the nighttime mask...")
night_mask = load_mask("global_ti_msk_night_2007.img")

print("Loading the daytime map...")
day = load_map("global_ti_day_2007.img")

print("Loading the daytime mask...")
day_mask = load_mask("global_ti_msk_day_2007.img")

print("\nAll four files have been read successfully!")


# ==========================================
# 5. NIGHTTIME MAP ANALYSIS
# ==========================================

night_valid = analyze_map(
    "NIGHTTIME THERMAL INERTIA",
    night,
    night_mask
)


# ==========================================
# 6. DAYTIME MAP ANALYSIS
# ==========================================

day_valid = analyze_map(
    "DAYTIME THERMAL INERTIA",
    day,
    day_mask
)


# ==========================================
# 7. COMPARISON OF DAYTIME AND NIGHTTIME MAPS
# ==========================================

print("\n" + "=" * 65)
print("COMPARISON OF DAYTIME AND NIGHTTIME MAPS")
print("=" * 65)

# Use only pixels that are not interpolated
# in either of the two maps.

common_mask = (
    (night_mask != 0) &
    (day_mask != 0)
)

common_count = int(np.count_nonzero(common_mask))

print("\nNumber of common valid pixels:", f"{common_count:,}")
print(
    "Percentage of the entire map:",
    f"{common_count / common_mask.size * 100:.2f}%"
)

# Comparison using common pixels
night_common = night[common_mask]
day_common = day[common_mask]

difference = (
    day_common.astype(np.int32) -
    night_common.astype(np.int32)
)

print("\nNIGHTTIME VALUES AT COMMON PIXELS:")
print("Mean:", round(float(night_common.mean()), 2))
print("Median:", float(np.median(night_common)))

print("\nDAYTIME VALUES AT COMMON PIXELS:")
print("Mean:", round(float(day_common.mean()), 2))
print("Median:", float(np.median(day_common)))

print("\nDIFFERENCE (DAY - NIGHT):")
print("Minimum:", int(difference.min()))
print("Maximum:", int(difference.max()))
print("Mean:", round(float(difference.mean()), 2))
print("Median:", float(np.median(difference)))

print("\nDIFFERENCE PERCENTILES:")

for p in [5, 25, 50, 75, 95]:
    print(
        f"{p}%: "
        f"{np.percentile(difference, p):.2f}"
    )

# Correlation using a uniform sample of pixels
# To avoid unnecessary memory usage.

flat_indices = np.flatnonzero(
    common_mask.ravel()
)[::100]

night_sample = night.ravel()[flat_indices].astype(float)
day_sample = day.ravel()[flat_indices].astype(float)

correlation = np.corrcoef(
    night_sample, day_sample
)[0, 1]

print("\nCORRELATION BETWEEN DAYTIME AND NIGHTTIME DATA:")
print("Pearson correlation coefficient:", round(float(correlation), 4))
print("Number of sample points:", len(flat_indices))


# ==========================================
# 8. COMPLETION
# ==========================================

print("\n" + "=" * 65)
print("ANALYSIS COMPLETED SUCCESSFULLY!")
print("=" * 65)


# ==========================================
# 9. ADDITIONAL CHECK OF MASKS AND VALUE RANGES
# ==========================================

print("\n" + "=" * 65)
print("ADDITIONAL CHECK")
print("=" * 65)

# 20 pixels per degree.
# From 90°N to 87°N — 60 rows.
# From 87°S to 90°S — the last 60 rows.

inside = slice(60, 3540)

for name, mask in [
    ("Nighttime mask", night_mask),
    ("Daytime mask", day_mask)
]:
    print(f"\n{name}:")

    for region_name, region in [
        ("Entire map", mask),
        ("Between 87°N and 87°S", mask[inside]),
        ("Polar regions beyond 87°", np.concatenate([
            mask[:60].ravel(),
            mask[3540:].ravel()
        ]))
    ]:
        zeros = np.count_nonzero(region == 0)
        total = region.size

        print(
            f"{region_name}: "
            f"zero values = {zeros:,} "
            f"({zeros / total * 100:.2f}%)"
        )

# Check the extreme values of the maps
for name, data, mask in [
    ("Nighttime", night, night_mask),
    ("Daytime", day, day_mask)
]:
    valid = data[mask != 0]

    print(f"\n{name} map — extreme values:")

    for value in [0, 1, 5, 4999, 5000, 32767, -32768]:
        print(
            f"{value}: "
            f"{np.count_nonzero(valid == value):,} pixels"
        )

# Check the description of the daytime mask
print("\nDAYTIME MASK DESCRIPTION:")

day_mask_label = find_file("global_ti_msk_day_2007.lbl")

label_text = day_mask_label.read_text(
    encoding="latin-1"
)

for line in label_text.splitlines():
    if any(
        key in line.upper()
        for key in [
            "SAMPLE_TYPE",
            "SAMPLE_BITS",
            "DESCRIPTION",
            "0 <",
            "1 <",
            "MISSING_CONSTANT",
            "VALID_MINIMUM",
            "VALID_MAXIMUM"
        ]
    ):
        print(line.strip())

print("\nADDITIONAL CHECK COMPLETED")