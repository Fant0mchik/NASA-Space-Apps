from pathlib import Path
import requests

OUTPUT_DIR = Path(__file__).resolve().parent / "mars_viking_tiles"
OUTPUT_DIR.mkdir(exist_ok=True)

base_url = "http://jmars.asu.edu/data/mdim_color/large/"

tiles = [
    "mars45n225.png",
    "mars45n315.png",
    "mars45n045.png",
    "mars45n135.png",
    "mars45s225.png",
    "mars45s315.png",
    "mars45s045.png",
    "mars45s135.png"
]

for filename in tiles:
    url = base_url + filename

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    file_path = OUTPUT_DIR / filename
    file_path.write_bytes(response.content)

    print(f"Downloaded: {filename}")

print("\nAll 8 tiles have been downloaded!")