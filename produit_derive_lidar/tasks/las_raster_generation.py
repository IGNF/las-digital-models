# RASTER_GENERATION METHODS
import logging

import fiona
import rasterio.mask
from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.raster_clip import clip_raster
import numpy as np
from osgeo import gdal
import rasterio
from rasterio.transform import Affine



def check_raster(fpath):
    """Check if raster has created
    """
    # Check if DTM has created
    ds = gdal.Open(fpath)
    if ds is None:
        return False
    ds = None # Close dataset
    return True


def mask_with_no_data_shapefile(shapefile: str, input_raster: str, output_raster: str, no_data: int):
    """Burn no-data value inside polygons from shapefile (overwrites input raster)
    """
    # # Create raster
    # out = gdal.Rasterize(raster_file, shapefile, allTouched=True, burnValues=no_data)
    # print(out)
    # 1/0
    with fiona.open(shapefile, "r") as fhandle:
        shapes = [feature["geometry"] for feature in fhandle]

    with rasterio.open(input_raster) as src:
        out_image, _ = rasterio.mask.mask(src, shapes,
            crop=False, all_touched=True, invert=True)
        out_meta = src.meta

    with rasterio.open(output_raster, "w", **out_meta) as dest:
        dest.write(out_image)




# def patch(raster, res, origin, size, min_n):
#     """Patches in missing pixel values by applying a median
#     kernel (3x3) to estimate its value. This is meant to serve
#     as a means of populating missing pixels, not as a means
#     of interpolating large areas. The last parameter should
#     be an integer that specifies the minimum number of valid
#     neighbour values to fill a pixel (0 <= min_n <= 8).

#     Args:
#         raster(array) : Z interpolation
#         res(list): resolution in coordinates
#         origin(list): coordinate location of the relative origin (bottom left)
#         size (float): raster cell size
#         min_n(float): minimum number of valid neighbour values
#     """
#     mp = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
#           [0, 1], [1, -1], [1, 0], [1, 1]]
#     for yi in range(res[1]):
#         for xi in range(res[0]):
#             if raster[yi, xi] == commons.no_data_value:
#                 vals = []
#                 for m in range(8):
#                     xw, yw = xi + mp[m][0], yi + mp[m][1]
#                     if (xw >= 0 and xw < res[0]) and (yw >= 0 and yw < res[1]):
#                         val = raster[yw, xw]
#                         if val != commons.no_data_value: vals += [val]
#                 if len(vals) > min_n: raster[yi, xi] = np.median(vals)


# @commons.eval_time_with_pid
# def export_and_clip_raster(las_file, ras, origin, size, geotiff_path_temp, geotiff_path, method,
#                   spatial_ref="EPSG:2154", force_save_ras=False):
#     """Write raster in the folder DTM with clipping from the LIDAR tile."""
#     if not method.startswith("PDAL") or force_save_ras:
#         # Write geotiff (potentially with buffer)
#         write_geotiff(ras, origin, size, geotiff_path_temp, spatial_ref=spatial_ref)

#     # if check_raster(geotiff_path_temp) == True:
#     #     clip_raster(las_file, geotiff_path_temp, geotiff_path, size)




