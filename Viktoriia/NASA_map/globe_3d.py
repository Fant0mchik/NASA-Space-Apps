
import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

from config import MAP_PATH, OUTPUT_DIR

print("Loading Mars data...")

mars = gpd.read_file(MAP_PATH)

# Кольори геологічних регіонів
units = sorted(mars["Unit"].dropna().unique())
cmap = plt.get_cmap("turbo", len(units))

color_map = {
    unit: to_hex(cmap(i))
    for i, unit in enumerate(units)
}

# Перетворення координат на сферу
R = 3396190

def to_sphere(lon, lat, radius=R):
    lon = np.radians(lon)
    lat = np.radians(lat)

    x = radius * np.cos(lat) * np.cos(lon)
    y = radius * np.cos(lat) * np.sin(lon)
    z = radius * np.sin(lat)

    return x, y, z

print("Preparing geological regions...")

fig = go.Figure()

# Основа глобуса
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(-np.pi / 2, np.pi / 2, 60)

U, V = np.meshgrid(u, v)

fig.add_trace(go.Surface(
    x=R * np.cos(V) * np.cos(U),
    y=R * np.cos(V) * np.sin(U),
    z=R * np.sin(V),
    colorscale=[[0, "#9B422D"], [1, "#9B422D"]],
    showscale=False,
    hoverinfo="skip",
    opacity=1
))

# Малюємо геологічні межі кольоровими точками
for unit in units:
    subset = mars[mars["Unit"] == unit]

    xs, ys, zs = [], [], []

    for geometry in subset.geometry:
        if geometry is None or geometry.is_empty:
            continue

        point = geometry.representative_point()
        x, y, z = to_sphere(point.x, point.y, R * 1.002)

        xs.append(x)
        ys.append(y)
        zs.append(z)

    if xs:
        fig.add_trace(go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers",
            marker=dict(
                size=3,
                color=color_map[unit],
                opacity=0.95
            ),
            name=str(unit),
            hovertemplate=f"Geological unit: {unit}<extra></extra>"
        ))

fig.update_layout(
    title="MARS // GLOBAL GEOLOGY 3D",
    template="plotly_dark",
    height=800,
    scene=dict(
        aspectmode="data",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor="#101014"
    ),
    margin=dict(l=0, r=0, t=60, b=0)
)

OUTPUT_DIR.mkdir(exist_ok=True)

html_path = OUTPUT_DIR / "mars_globe_3d.html"

fig.write_html(
    html_path,
    include_plotlyjs=True,
    full_html=True
)

print("Globe saved:", html_path)

# Відкриваємо у браузері
import webbrowser
webbrowser.open(html_path.resolve().as_uri())

print("DONE!")
