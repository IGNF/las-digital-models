from typing import List, Tuple

import pdal
from osgeo import gdal

from las_digital_models.commons import commons

gdal.UseExceptions()


@commons.eval_time_with_pid
def interpolate(
    input_file: str,
    output_file: str,
    tile_origin: Tuple[int, int],
    pixel_size: float,
    tile_width: int,
    spatial_ref: str,
    no_data_value: int,
    filter_dimension: str,
    filter_values: List[int],
):
    """Generate a Z (height) raster file from a LAS point cloud file by interpolating the Z value at the center of
    each pixel.

    It uses TIN interpolation.

    Steps are:
    - filter the points to use in the interplation (using one dimension name and a list of values)
    (eg. Classification=2(ground) for a digital terrain model)
    - triangulate the point cloud using Delaunay
    - interpolate the height values at the center of the pixels using Faceraster
    - write the result in a raster file.

    Args:
        input_file (str): path to the las/laz file to interpolate
        output_file (str): path to the output raster
        tile_origin (Tuple[int, int]): coordinates of the upper left corner of the tile (in meters)
        pixel_size (float): pixel size of the output raster in meters (pixels are supposed to be squares)
        tile_width (int): width of the tile in meters (used to infer the lower-left corner)
        spatial_ref (str): spatial reference to use when reading las file
        no_data_value (int): no data value for the output raster
        filter_dimension (str): Name of the dimension along which to filter input points
        (keep empty to disable input filter)
        filter_values (List[int]): Values to keep for input points along filter_dimension
    """

    nb_pixels = [int(tile_width / pixel_size), int(tile_width / pixel_size)]

    # Read with pdal
    pipeline = pdal.Reader.las(filename=input_file, override_srs=spatial_ref, nosrs=True)
    if filter_dimension and filter_values:
        pipeline |= pdal.Filter.range(limits=",".join(f"{filter_dimension}[{v}:{v}]" for v in filter_values))

    # Add interpolation method to the pdal pipeline
    pipeline |= pdal.Filter.delaunay()

    pipeline |= pdal.Filter.faceraster(
        resolution=str(pixel_size),
        origin_x=str(tile_origin[0] - pixel_size / 2),  # lower left corner
        origin_y=str(tile_origin[1] + pixel_size / 2 - tile_width),  # lower left corner
        width=str(nb_pixels[0]),
        height=str(nb_pixels[1]),
    )
    pipeline |= pdal.Writer.raster(gdaldriver="GTiff", nodata=no_data_value, data_type="float32", filename=output_file)

    pipeline.execute()
