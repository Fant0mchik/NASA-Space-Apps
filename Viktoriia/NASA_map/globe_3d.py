
import numpy as np
import plotly.graph_objects as go
import rasterio

from pathlib import Path
from PIL import Image

from config import OUTPUT_DIR


# ==========================================
# 1. НАЛАШТУВАННЯ
# ==========================================

R = 3396190

BASE_DIR = Path(__file__).resolve().parent

MARS_IMAGE_PATH = (
    BASE_DIR / "data" / "mars_viking_mosaic.png"
)

TES_PATH = (
    BASE_DIR
    / "data"
    / "TES_numeric"
    / "TES_thermophysical_units.tif"
)


# ==========================================
# 2. ЗАГАЛЬНА ФУНКЦІЯ КООРДИНАТ СФЕРИ
# ==========================================

def create_sphere_coordinates(latitudes, longitudes):

    lon_grid, lat_grid = np.meshgrid(
        longitudes,
        latitudes
    )

    lon = np.radians(lon_grid)
    lat = np.radians(lat_grid)

    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)

    return x.flatten(), y.flatten(), z.flatten()


# ==========================================
# 3. СТВОРЕННЯ ТРИКУТНИКІВ СФЕРИ
# ==========================================

def create_sphere_faces(rows, columns):

    faces_i = []
    faces_j = []
    faces_k = []

    for row in range(rows - 1):
        for col in range(columns - 1):

            top_left = row * columns + col
            top_right = top_left + 1

            bottom_left = (row + 1) * columns + col
            bottom_right = bottom_left + 1

            faces_i.extend([top_left, top_left])
            faces_j.extend([bottom_left, top_right])
            faces_k.extend([bottom_right, bottom_right])

    return (
        np.array(faces_i),
        np.array(faces_j),
        np.array(faces_k)
    )


# ==========================================
# 4. MARS GLOBE — VIKING 2 MOSAIC
# ==========================================

print("Loading Mars Viking mosaic...")

if not MARS_IMAGE_PATH.exists():
    raise FileNotFoundError(
        f"Mars mosaic not found: {MARS_IMAGE_PATH}"
    )

image = Image.open(MARS_IMAGE_PATH).convert("RGB")

# Зменшуємо текстуру для 3D-візуалізації
image = image.resize(
    (361, 181),
    Image.Resampling.LANCZOS
)

mars_colors = np.array(image)

vertex_colors = [
    f"rgb({r},{g},{b})"
    for r, g, b in mars_colors.reshape(-1, 3)
]

# Координати глобуса
latitudes = np.linspace(90, -90, 181)
longitudes = np.linspace(-180, 180, 361)

x, y, z = create_sphere_coordinates(
    latitudes,
    longitudes
)

# Трикутники
i, j, k = create_sphere_faces(181, 361)

print("Mars Globe vertices:", len(x))
print("Mars Globe triangles:", len(i))


# ==========================================
# 5. TES THERMOPHYSICAL CLASSIFICATION
# ==========================================

print("Loading TES thermophysical units...")

if not TES_PATH.exists():
    raise FileNotFoundError(
        f"TES units file not found: {TES_PATH}"
    )

with rasterio.open(TES_PATH) as src:
    tes_classes = src.read(1)

# Зменшуємо роздільність до приблизно 1 градуса
tes_small = tes_classes[10::20, 10::20]

# Кольори класів
tes_colors = {
    250: "#d73027",
    208: "#4575b4",
    192: "#fdae61",
    144: "#fee090",
    96: "#313695",
    72: "#74add1",
    24: "#1a9850",
    0: "#808080"
}

# Назви класів
tes_names = {
    250: "F — Rocks, bedrock, duricrust and polar ice",
    208: "G — Fine material with thin thermal cover",
    192: "B — Sand, rocks and bedrock",
    144: "C — Duricrust with sand, rocks and bedrock",
    96: "D — Low-density mantle deposits or dark dust",
    72: "A — Bright, unconsolidated fine material",
    24: "E — Rocky materials with little fine-grained cover"
}

print("Building TES surface...")

lat_edges = 90 - np.arange(181)
lon_edges = -180 + np.arange(361)

tes_x, tes_y, tes_z = create_sphere_coordinates(
    lat_edges,
    lon_edges
)

tes_faces = []
tes_face_colors = []

for row in range(180):
    for col in range(360):

        class_id = int(tes_small[row, col])

        if class_id not in tes_colors:
            continue

        top_left = row * 361 + col
        top_right = top_left + 1

        bottom_left = (row + 1) * 361 + col
        bottom_right = bottom_left + 1

        tes_faces.append([
            top_left,
            bottom_left,
            bottom_right
        ])

        tes_faces.append([
            top_left,
            bottom_right,
            top_right
        ])

        tes_face_colors.extend([
            tes_colors[class_id],
            tes_colors[class_id]
        ])

tes_faces = np.asarray(
    tes_faces,
    dtype=np.int64
)

print("TES vertices:", len(tes_x))
print("TES triangles:", len(tes_faces))

if len(tes_faces) == 0:
    raise ValueError("No valid TES surface cells found!")


# ==========================================
# 6. СТВОРЕННЯ ГЛОБУСА
# ==========================================

fig = go.Figure()


# ------------------------------------------
# Mars Globe
# ------------------------------------------

fig.add_trace(go.Mesh3d(
    x=x * 1.001,
    y=y * 1.001,
    z=z * 1.001,

    i=i,
    j=j,
    k=k,

    vertexcolor=vertex_colors,

    flatshading=False,

    lighting=dict(
        ambient=0.85,
        diffuse=0.55,
        specular=0.1,
        roughness=0.9
    ),

    hoverinfo="skip",
    name="Mars Globe",
    showlegend=False
))


# ------------------------------------------
# TES Surface Classification
# ------------------------------------------

fig.add_trace(go.Mesh3d(
    x=tes_x * 1.002,
    y=tes_y * 1.002,
    z=tes_z * 1.002,

    i=tes_faces[:, 0],
    j=tes_faces[:, 1],
    k=tes_faces[:, 2],

    facecolor=tes_face_colors,

    flatshading=True,

    lighting=dict(
        ambient=0.85,
        diffuse=0.55,
        specular=0.1,
        roughness=0.9
    ),

    hoverinfo="skip",
    name="TES thermophysical units",
    showlegend=False
))


# ==========================================
# 7. ЛЕГЕНДА TES
# ==========================================

for class_id, name in tes_names.items():

    fig.add_trace(go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],

        mode="markers",

        marker=dict(
            size=7,
            color=tes_colors[class_id]
        ),

        name=name,
        showlegend=True
    ))


# No data
fig.add_trace(go.Scatter3d(
    x=[None],
    y=[None],
    z=[None],

    mode="markers",

    marker=dict(
        size=8,
        color=tes_colors[0]
    ),

    name="No data",
    showlegend=True
))


# ==========================================
# 8. ПЕРЕМИКАННЯ МІЖ РЕЖИМАМИ
# ==========================================

# Усього 10 елементів:
# 1 Mars Globe
# 1 TES surface
# 7 класів TES
# 1 No data

globe_visibility = (
    [True, False]
    + [False] * 8
)

tes_visibility = (
    [False, True]
    + [True] * 8
)

fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            active=0,

            x=0.5,
            y=1.08,
            xanchor="center",

            buttons=[

                dict(
                    label="Mars Globe",
                    method="update",

                    args=[
                        {
                            "visible": globe_visibility
                        },
                        {
                            "title.text": "MARS // GLOBAL COLOR MOSAIC",
                            "legend.title.text": ""
                        }
                    ]
                ),

                dict(
                    label="Surface Classification",
                    method="update",

                    args=[
                        {
                            "visible": tes_visibility
                        },
                        {
                            "title.text": "MARS // TES SURFACE CLASSIFICATION",
                            "legend.title.text": "THERMOPHYSICAL UNITS"
                        }
                    ]
                )

            ]
        )
    ]
)
# Початково показуємо тільки кольоровий глобус
for i, visible in enumerate(globe_visibility):
    fig.data[i].visible = visible


# ==========================================
# 9. ОФОРМЛЕННЯ
# ==========================================

fig.update_layout(

    title=dict(
        text="MARS // GLOBAL COLOR MOSAIC",
        font=dict(
            size=24,
            color="#F2A36B"
        )
    ),

    template="plotly_dark",

    height=850,

    scene=dict(
        aspectmode="data",

        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),

        bgcolor="#101014"
    ),

    legend=dict(
        title=dict(text=""),
        x=1.02,
        y=1,
        font=dict(size=10),
        bgcolor="rgba(20,20,25,0.85)"
    ),

    margin=dict(
        l=0,
        r=350,
        t=70,
        b=0
    )
)


# ==========================================
# 10. ЗБЕРЕЖЕННЯ HTML
# ==========================================

OUTPUT_DIR.mkdir(exist_ok=True)

html_path = OUTPUT_DIR / "mars_globe_3d.html"

print("Saving 3D globe...")

fig.write_html(
    html_path,
    include_plotlyjs=True,
    full_html=True
)

print("Globe saved:", html_path)


print("Mars 3D globe created!")
