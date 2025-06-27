from config import ADMIN_SHP, OUTPUTS_DIR
from scripts.utils import timed
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx


VIS_OUTPUT = OUTPUTS_DIR / "admin_boundaries.png"

@timed
def visualize_admin_boundaries():
    admin_gdf = gpd.read_file(ADMIN_SHP).to_crs(epsg=3857)
    fig, ax = plt.subplots(figsize=(12, 10))

    admin_gdf.boundary.plot(ax=ax, edgecolor="orange", linewidth=1.5, alpha=0.9)
    minx, miny, maxx, maxy = admin_gdf.total_bounds
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)

    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs=admin_gdf.crs)
    ax.set_axis_off()
    plt.title("El Salvador: Population Raster & Admin Boundaries", fontsize=18, weight='bold')
    plt.tight_layout()
    plt.savefig(VIS_OUTPUT, transparent=True, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Figure saved: {VIS_OUTPUT}")

if __name__ == "__main__":
    visualize_admin_boundaries()
