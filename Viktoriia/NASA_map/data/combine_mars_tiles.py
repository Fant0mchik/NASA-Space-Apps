
from pathlib import Path
from PIL import Image

# Шляхи до папок
DATA_DIR = Path(__file__).resolve().parent
TILES_DIR = DATA_DIR / "mars_viking_tiles"

# Розмір одного фрагмента у фінальній текстурі
TILE_SIZE = 2048

# Порядок фрагментів відповідно до координат KMZ
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

# Створюємо глобальну текстуру
mosaic = Image.new(
    "RGB",
    (TILE_SIZE * 4, TILE_SIZE * 2)
)

# Додаємо північну півкулю
for column, filename in enumerate(north_tiles):
    image_path = TILES_DIR / filename

    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image = image.resize(
            (TILE_SIZE, TILE_SIZE),
            Image.Resampling.LANCZOS
        )

        mosaic.paste(image, (column * TILE_SIZE, 0))

    print(f"Додано: {filename}")

# Додаємо південну півкулю
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

    print(f"Додано: {filename}")

# Зберігаємо результат
output_path = DATA_DIR / "mars_viking_mosaic.png"
mosaic.save(output_path, optimize=True)

print("\nГлобальну текстуру Марса створено!")
print(f"Розмір: {mosaic.size}")
print(f"Файл: {output_path}")
