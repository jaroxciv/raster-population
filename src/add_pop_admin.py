from config import ADMIN_SHP, POPULATION_RASTER, OUTPUTS_DIR
import geopandas as gpd
from rasterstats import zonal_stats
import rasterio
from src.utils import timed, make_output_path

@timed
def main():
    admin_gdf = gpd.read_file(ADMIN_SHP)
    print(f"Loaded admin boundaries: {len(admin_gdf)} features")

    # Ensure CRS matches raster
    with rasterio.open(POPULATION_RASTER) as src:
        raster_crs = src.crs
    if admin_gdf.crs != raster_crs:
        print(f"Reprojecting admin boundaries from {admin_gdf.crs} to {raster_crs}")
        admin_gdf = admin_gdf.to_crs(raster_crs)

    # Choose statistics
    stat_list = ["count", "min", "mean", "max", "median", "sum"]

    print("Computing zonal statistics...")
    stats = zonal_stats(
        admin_gdf,
        POPULATION_RASTER,
        stats=stat_list,
        nodata=-9999,   # Change if your raster's nodata is different!
        geojson_out=False,
        all_touched=False
    )

    # Attach stats to gdf with pop_ prefix
    for stat in stat_list:
        admin_gdf[f"pop_{stat}"] = [s[stat] for s in stats]

    # Output
    output_path = make_output_path(ADMIN_SHP, OUTPUTS_DIR, suffix="_stats.gpkg")
    admin_gdf.to_file(output_path, driver="GPKG")
    print(f"\n✅ Saved: {output_path}")

    # Show preview
    cols = [c for c in admin_gdf.columns if c.startswith("pop_")]
    print(admin_gdf[cols].head())

if __name__ == "__main__":
    main()
