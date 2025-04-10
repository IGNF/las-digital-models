import geopandas as gpd
from rasterstats import zonal_stats
from shapely.geometry import LineString, MultiLineString


def extract_min_z_from_mns_by_polylines(lines_gdf: gpd.GeoDataFrame, mns_raster_path: str):
    """
    Extracts the minimum Z value from a DSM raster for each polyline (LineString or MultiLineString)
    in the input shapefile, keeping the original geometry.

    Args:
        lines_gdf (str): GeoDataFrame with 2D lines.
        mns_raster_path (str): Path to the DSM raster (GeoTIFF).

    Returns:
        GeoDataFrame: A GeoDataFrame with the original geometries and a 'min_z' column.
    """
    geometries = []
    min_z_values = []

    for geom in lines_gdf.geometry:
        if isinstance(geom, LineString):
            lines = [geom]
        elif isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
        else:
            continue  # Skip any geometry that is not a LineString or MultiLineString

        for line in lines:
            stats = zonal_stats(vectors=[line], raster=mns_raster_path, stats=["min"], all_touched=True, nodata=None)
            min_z = round(stats[0]["min"], 2) if stats and stats[0]["min"] is not None else None
            geometries.append(line)
            min_z_values.append(min_z)

    result_gdf = gpd.GeoDataFrame({"geometry": geometries, "min_z": min_z_values}, crs=lines_gdf.crs)
    return result_gdf
