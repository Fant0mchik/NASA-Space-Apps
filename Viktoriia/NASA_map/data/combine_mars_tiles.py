# Directory paths
DATA_DIR = Path(__file__).resolve().parent
TILES_DIR = DATA_DIR / "mars_viking_tiles"

# Size of each tile in the final texture
TILE_SIZE = 2048

# Tile order based on KMZ coordinates
north_tiles = [
    "mars45n225.png",
    "mars45n315.png",
    "mars45n045.png",
    "mars45n135.png"
]

south_tiles = [
    "mars45s225.png",
    "mars45s315.png",
    "mars45s045.png",
    "mars45s135.png"
]

# Create the global texture
mosaic = Image.new(
    "RGB",
    (TILE_SIZE * 4, TILE_SIZE * 2)
)

# Add the Northern Hemisphere
for column, filename in enumerate(north_tiles):
    image_path = TILES_DIR / filename

    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image = image.resize(
            (TILE_SIZE, TILE_SIZE),
            Image.Resampling.LANCZOS
        )

        mosaic.paste(image, (column * TILE_SIZE, 0))

    print(f"Added: {filename}")

# Add the Southern Hemisphere
for column, filename in enumerate(south_tiles):
    image_path = TILES_DIR / filename

    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image = image.resize(
            (TILE_SIZE, TILE_SIZE),
            Image.Resampling.LANCZOS
        )

        mosaic.paste(
            image,
            (column * TILE_SIZE, TILE_SIZE)
        )

    print(f"Added: {filename}")

# Save the resulting mosaic
output_path = DATA_DIR / "mars_viking_mosaic.png"
mosaic.save(output_path, optimize=True)

print("\nGlobal Mars texture created!")
print(f"Size: {mosaic.size}")
print(f"File: {output_path}")