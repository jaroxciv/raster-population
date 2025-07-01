from config import POPULATION_RASTER, ADMIN_SHP, OUTPUTS_DIR
from src.utils import timed
import geopandas as gpd
import rasterio
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
import contextily as cx
import numpy as np

VIS_OUTPUT = OUTPUTS_DIR / "pop_raster_with_admin.png"

@timed
def plot_population_raster():
    admin_gdf = gpd.read_file(ADMIN_SHP).to_crs(epsg=3857)
    bounds = admin_gdf.total_bounds

    with rasterio.open(POPULATION_RASTER) as src:
        dst_crs = 'EPSG:3857'
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs, 'transform': transform, 'width': width, 'height': height})

        with rasterio.MemoryFile() as memfile:
            with memfile.open(**kwargs) as dst:
                reproject(
                    source=rasterio.band(src, 1),
                    destination=rasterio.band(dst, 1),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
                data = dst.read(1)
                data[data < 0] = np.nan  # mask nodata if any

                # DEBUG PRINTS
                print("Raster min:", np.nanmin(data), "max:", np.nanmax(data))
                print("Raster bounds:", dst.bounds)
                print("Admin bounds:", bounds)

                fig, ax = plt.subplots(figsize=(12, 10))
                img = ax.imshow(
                    data,
                    cmap="viridis",
                    extent=(dst.bounds.left, dst.bounds.right, dst.bounds.bottom, dst.bounds.top),
                    alpha=0.85,
                    vmin=np.nanmin(data),
                    vmax=np.nanmax(data)
                )
                # cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs=admin_gdf.crs)
                admin_gdf.boundary.plot(ax=ax, edgecolor="orange", linewidth=0.5, alpha=0.5)

                minx, miny, maxx, maxy = bounds
                ax.set_xlim(minx, maxx)
                ax.set_ylim(miny, maxy)

                ax.set_axis_off()
                plt.title("El Salvador: Population Raster (2018) & Admin Boundaries", fontsize=18, weight='bold')
                plt.colorbar(img, ax=ax, orientation='vertical', fraction=0.025, pad=0.01, label="Population per pixel")
                plt.tight_layout()
                plt.savefig(VIS_OUTPUT, transparent=True, dpi=300, bbox_inches="tight")
                plt.show()
                print(f"Figure saved: {VIS_OUTPUT}")

if __name__ == "__main__":
    plot_population_raster()
