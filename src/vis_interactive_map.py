from config import POPULATION_RASTER, ADMIN_SHP, OUTPUTS_DIR
from src.utils import timed
import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import Fullscreen
import tempfile
import pyproj

VIS_HTML = OUTPUTS_DIR / "el_salvador_pop_interactive.html"

def save_raster_png():
    """Warp raster to EPSG:3857, save as PNG for overlay, and return file path & bounds in EPSG:4326."""
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
                data[data < 0] = np.nan

                vmin, vmax = np.nanpercentile(data, 2), np.nanpercentile(data, 98)
                normed = np.clip((data - vmin) / (vmax - vmin), 0, 1)
                rgba = plt.cm.viridis(normed, bytes=True)  # Use viridis colormap
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    plt.imsave(tmp.name, rgba)

                    # Convert EPSG:3857 bounds to EPSG:4326 (lat/lon) for Folium
                    project = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
                    left, bottom = project(dst.bounds.left, dst.bounds.bottom)
                    right, top = project(dst.bounds.right, dst.bounds.top)
                    latlon_bounds = [[bottom, left], [top, right]]

                    return tmp.name, latlon_bounds

@timed
def make_interactive_map():
    raster_png, img_bounds = save_raster_png()
    admin_gdf = gpd.read_file(ADMIN_SHP).to_crs(epsg=4326)

    centroid = admin_gdf.geometry.union_all().centroid

    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=8, tiles="CartoDB positron")

    folium.raster_layers.ImageOverlay(
        name="Population Raster",
        image=raster_png,
        bounds=img_bounds,
        opacity=0.7,
        interactive=True,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    folium.GeoJson(
        admin_gdf,
        name="Admin Boundaries",
        style_function=lambda x: {
            "color": "orange",
            "weight": 1,
            "fillOpacity": 0
        }
    ).add_to(m)

    Fullscreen().add_to(m)
    folium.LayerControl().add_to(m)
    m.save(str(VIS_HTML))
    print(f"Interactive map saved to {VIS_HTML}")

if __name__ == "__main__":
    make_interactive_map()
