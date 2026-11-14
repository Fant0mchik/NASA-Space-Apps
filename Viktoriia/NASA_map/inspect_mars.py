
import geopandas as gpd

from config import MAP_PATH

mars = gpd.read_file(MAP_PATH)

print("\n===== MARS GEOLOGY DATA =====")

print("\nCoordinate system:")
print(mars.crs)

print("\nIs geographic:")
print(mars.crs.is_geographic if mars.crs else "Unknown")

print("\nMap boundaries:")
print(mars.total_bounds)

print("\nGeometry types:")
print(mars.geom_type.value_counts())

print("\nNumber of geological regions:")
print(len(mars))

print("\nAvailable columns:")
print(mars.columns.tolist())

print("\nFirst 5 geological regions:")
print(mars[["Unit", "UnitDesc", "SphArea_km"]].head())
