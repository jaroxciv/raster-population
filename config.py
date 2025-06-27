from pathlib import Path

# Inputs
POPULATION_RASTER = Path("data/population_slv_2018-10-01/population_slv_2018-10-01.tif")
ADMIN_SHP = Path("data/segmentos_censales/DIGESTYC_Segmentos2007.shp")

# Outputs base dir
OUTPUTS_DIR = Path("outputs")
ADMIN_POP_GPKG = OUTPUTS_DIR / "segmentos_censales_pop_2018.gpkg"

# Optional: Default CRS
FORCE_CRS = None
