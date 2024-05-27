from typing import List

import pdal
from osgeo import gdal
from pdaltools.las_info import parse_filename

from produits_derives_lidar.commons import commons

gdal.UseExceptions()


def interpolate_from_config(input_file: str, output_raster: str, config: dict):
    """API using a config dictionary for the `interpolate` method defined in this file
    Generate a Z (height) raster file from a LAS point cloud file by interpolating the Z value for each pixel center.


    Args:
        input_file (str): path to the las/laz file to interpolate
        output_file (str): path to the output raster
        config (dict): ProduitDeriveLidar config dictionary containing
        {
            "tile_geometry": {
                "tile_coord_scale": #int, scale of the tiles coordinates in the las filename
                "tile_width": #int, width of the tile in meters (used to infer the lower-left corner)
                "pixel_size": #float, pixel size of the output raster in meters (pixels are supposed to be squares)
                "no_data_value": #int, no data value for the output raster
            },
            "io": {
                "spatial_reference": #str, spatial reference to use when reading las file
            },
            "filter": {
                "keep_classes": #list of ints, classes of the points to use in the interpolation
            }
        }

    """
    interpolate(
        input_file,
        output_raster,
        config["tile_geometry"]["pixel_size"],
        config["tile_geometry"]["tile_width"],
        config["tile_geometry"]["tile_coord_scale"],
        config["io"]["spatial_reference"],
        config["tile_geometry"]["no_data_value"],
        config["filter"]["keep_classes"],
    )


@commons.eval_time_with_pid
def interpolate(
    input_file: str,
    output_file: str,
    pixel_size: float,
    tile_width: int,
    tile_coord_scale: int,
    spatial_ref: str,
    no_data_value: int,
    classes: List[int],
):
    """Generate a Z (height) raster file from a LAS point cloud file by interpolating the Z value at the center of
    each pixel.

    It uses TIN interpolation.

    Steps are:
    - filter the point cloud with classes to use in the interpolation (eg. class 2-ground for a digital terrain model)
    - triangulate the point cloud using Delaunay
    - interpolate the height values at the center of the pixels using Faceraster
    - write the result in a raster file.

    Args:
        input_file (str): path to the las/laz file to interpolate
        output_file (str): path to the output raster
        pixel_size (float): pixel size of the output raster in meters (pixels are supposed to be squares)
        tile_width (int): width of the tile in meters (used to infer the lower-left corner)
        tile_coord_scale (int): scale of the tiles coordinates in the las filename
        spatial_ref (str): spatial reference to use when reading las file
        no_data_value (int): no data value for the output raster
        classes (List[int]): classes of the points to use in the interpolation
    """

    _, coordX, coordY, _ = parse_filename(input_file)

    # Compute origin/number of pixels
    origin = [float(coordX) * tile_coord_scale, float(coordY) * tile_coord_scale]
    nb_pixels = [int(tile_width / pixel_size), int(tile_width / pixel_size)]

    # Read with pdal
    pipeline = pdal.Reader.las(filename=input_file, override_srs=spatial_ref, nosrs=True)
    if classes:
        pipeline |= pdal.Filter.range(limits=",".join(f"Classification[{c}:{c}]" for c in classes))

    # Add interpolation method to the pdal pipeline
    pipeline |= pdal.Filter.delaunay()

    pipeline |= pdal.Filter.faceraster(
        resolution=str(pixel_size),
        origin_x=str(origin[0] - pixel_size / 2),  # lower left corner
        origin_y=str(origin[1] + pixel_size / 2 - tile_width),  # lower left corner
        width=str(nb_pixels[0]),
        height=str(nb_pixels[1]),
    )
    pipeline |= pdal.Writer.raster(gdaldriver="GTiff", nodata=no_data_value, data_type="float32", filename=output_file)

    pipeline.execute()
