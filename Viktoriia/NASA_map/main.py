
import geopandas as gpd
import matplotlib.pyplot as plt

path = r"C:\Users\Victoria\Downloads\SIM3292_Global_Geology\SIM3292_Global_Geology.shp"

# Завантаження карти
mars = gpd.read_file(path)

# Створення вікна
fig, ax = plt.subplots(figsize=(16, 10))

# Темне оформлення
fig.patch.set_facecolor("#151719")
ax.set_facecolor("#151719")

# Відображення геологічних областей
mars.plot(
    ax=ax,
    column="Unit",
    categorical=True,
    cmap="turbo",
    edgecolor="#35251F",
    linewidth=0.12,
    legend=False
)

# Заголовок
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

# Прибираємо координатні осі
ax.set_axis_off()

# Налаштування відступів
plt.subplots_adjust(
    left=0.02,
    right=0.98,
    top=0.88,
    bottom=0.03
)

# Збереження зображення
plt.savefig(
    "mars_geology_map.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=fig.get_facecolor()
)

plt.show()
