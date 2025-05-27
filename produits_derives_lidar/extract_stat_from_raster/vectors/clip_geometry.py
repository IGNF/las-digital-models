import geopandas as gpd


def clip_lines_by_polygons(
    input_lines_gdf: gpd.GeoDataFrame,
    input_polygons_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Clip virtual lines by polygons (bridge deck)

    Args:
        input_lines_gdf (gpd.GeoDataFrame): virtual lines merged
        input_polygons_gdf (gpd.GeoDataFrame): Polygons (bridge deck)

    Returns:
        gpd.GeoDataFrame : all virtual lines clipped
    """
    lines_clip_gdf = gpd.overlay(input_lines_gdf, input_polygons_gdf, how="intersection")

    return lines_clip_gdf
