
import geopandas as gpd
import matplotlib.pyplot as plt

from config import MAP_PATH, OUTPUT_DIR

# Завантаження карти
mars = gpd.read_file(MAP_PATH)

fig, ax = plt.subplots(figsize=(16, 10))

fig.patch.set_facecolor("#151719")
ax.set_facecolor("#151719")

mars.plot(
    ax=ax,
    column="Unit",
    categorical=True,
    cmap="turbo",
    edgecolor="#35251F",
    linewidth=0.12,
    legend=False
)

fig.suptitle(
    "MARS // GLOBAL GEOLOGY",
    fontsize=23,
    color="#F2A36B",
    fontweight="bold",
    y=0.96
)

ax.set_title(
    "NASA Geological Dataset | SIM3292",
    fontsize=11,
    color="#A9A9A9",
    pad=18
)

ax.set_axis_off()

plt.subplots_adjust(
    left=0.02,
    right=0.98,
    top=0.88,
    bottom=0.03
)

plt.savefig(
    OUTPUT_DIR / "mars_geology_map.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=fig.get_facecolor()
)

plt.show()
