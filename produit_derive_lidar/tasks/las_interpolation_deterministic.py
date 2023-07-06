# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# LAS INTERPOLATION
import logging
from produit_derive_lidar.commons import commons
from produit_derive_lidar.commons.laspy_io import read_las_and_extract_points_and_classifs
import pdal
import json
import numpy as np
import rasterio
from rasterio.transform import from_origin
from typing import List


class Interpolator:
    """Interpolator class

    Create an interpolator that can generate a raster data from a LAS point cloud file.
    The interpolator can be one of:

    'pdal-idw'
    'pdal-tin'
    'startin-tinlinear'
    'startin-laplace'
    'cgal-nn'
    """

    def __init__(
            self,
            nb_pixels: List[int],
            origin: List[float],
            pixel_size: float,
            method: str,
            spatial_ref: str,
            no_data_value: int,
            tile_width: int,
            tile_coord_scale: int,
            classes: List[int]
    ):
        """Initialize the interpolator

        Args:
            nb_pixels (List[int]): number of pixels (nodes) on each axis of the output raster grid
            origin (List[float]): spatial coordinate of the upper-left corner of the raster
                (center of the upper-left pixel)
            pixel_size (float): distance between each node of the raster grid (in meters)
            method (str): interpolation method
            spatial_ref (str): spatial reference of the input LAS file
            no_data_value (int): no-data value for the output raster
            tile_width (int): width of the tile in meters (used to infer the lower-left corner for
                pdal-based interpolators)
            tile_coord_scale (int): scale of the coordinate value contained in the LAS filename
                (used to infer the coordinates of the raster grid)
            classes (List[int]): List of classes to use for the interpolation (points with other
                classification values are ignored). If empty, all classes are kept
        """
        self.nb_pixels = nb_pixels
        self.origin = origin
        self.pixel_size = pixel_size
        self.method = method
        self.spatial_ref = spatial_ref
        self.no_data_value = no_data_value
        self.tile_width = tile_width
        self.tile_coord_scale = tile_coord_scale
        self.classes = classes


    def run_method_with_standard_io(self, fn, input_file, output_file):
        _, points_np, classifs = read_las_and_extract_points_and_classifs(input_file)
        if self.classes:
            filtered_points = points_np[np.isin(classifs, self.classes), :]
        else:
            filtered_points = points_np

        logging.debug(f"Read {len(points_np)} points from {input_file}.")
        if len(filtered_points) > 0:
            raster = fn(filtered_points)
        else :
            raster = self.no_data_value * np.ones([self.nb_pixels[1], self.nb_pixels[0]])
        write_geotiff(raster, self.origin, self.pixel_size, output_file, self.spatial_ref, self.no_data_value)
        logging.debug(f"Saved to {output_file}")


    @commons.eval_time
    def execute_startin(self, pts):
        """Takes the grid parameters and the ground points. Interpolates
        either using the TIN-linear or the Laplace method. Uses a no-data value set in commons
        Fully based on the startin package (https://startinpy.readthedocs.io/en/latest/api.html)

        Returns:
            ras(list): Z interpolation
        """
        import startinpy
        import numpy as np

        # # Startin
        tin = startinpy.DT(); tin.insert(pts) # # Insert each points in the array of points (a 2D array)
        ras = np.zeros([self.nb_pixels[1], self.nb_pixels[0]]) # # returns a new array of given shape and type, filled with zeros
        # # Interpolate method
        if self.method.lower() == 'startin-tinlinear':
            def interpolant(x, y): return tin.interpolate_tin_linear(x, y)
        elif self.method.lower() == 'startin-laplace':
            def interpolant(x, y): return tin.interpolate_laplace(x, y)
        else:
            raise NotImplementedError(f"Method {self.method} not implemented for execute_startin")

        for yi in range(self.nb_pixels[1]):
            for xi in range(self.nb_pixels[0]):
                x = self.origin[0] + xi * self.pixel_size
                y = self.origin[1] - yi * self.pixel_size
                try:
                    ch = tin.is_inside_convex_hull(x, y) # check is the point [x, y] located inside  the convex hull of the DT
                except Exception as e:
                    raise ValueError(f"x: {x}, y: {y}, xi: {xi}, yi: {yi}")
                    raise e
                if ch == False:
                    ras[yi, xi] = self.no_data_value
                else:
                    tri = tin.locate(x, y) # locate the triangle containing the point [x,y]. An error is thrown if it is outside the convex hull
                    if len(tri) and (0 not in tri):
                        ras[yi, xi] = interpolant(x, y)
                    else:
                        ras[yi, xi] = self.no_data_value

        return ras

    @commons.eval_time
    def execute_cgal(self, pts):
        """Performs CGAL-NN on the input points.
        First it removes any potential duplicates from the
        input points, as these would cause issues with the
        dictionary-based attribute mapping.
        Then, it creates CGAL Point_2 object from these points,
        inserts them into a CGAL Delaunay_triangulation_2, and
        performs interpolation using CGAL natural_neighbor_coordinate_2
        by finding the attributes (Z coordinates) via the dictionary
        that was created from the deduplicated points.

        Returns:
            ras(list): Z interpolation
        """
        from CGAL.CGAL_Kernel import Point_2
        from CGAL.CGAL_Triangulation_2 import Delaunay_triangulation_2
        from CGAL.CGAL_Interpolation import natural_neighbor_coordinates_2

        s_idx = np.lexsort(pts.T); s_data = pts[s_idx,:]
        mask = np.append([True], np.any(np.diff(s_data[:,:2], axis = 0), 1))
        deduped = s_data[mask]
        cpts = list(map(lambda x: Point_2(*x), deduped[:,:2].tolist()))
        zs = dict(zip([tuple(x) for x in deduped[:,:2]], deduped[:,2]))

        tin = Delaunay_triangulation_2()
        for pt in cpts: tin.insert(pt)
        ras = np.zeros([self.nb_pixels[1], self.nb_pixels[0]])
        for yi in range(self.nb_pixels[1]):
            for xi in range(self.nb_pixels[0]):
                x = self.origin[0] + xi * self.pixel_size
                y = self.origin[1] - yi * self.pixel_size
                nbrs = []
                qry = natural_neighbor_coordinates_2(tin, Point_2(x, y), nbrs)
                if qry[1] == True:
                    z_out = 0
                    for nbr in nbrs:
                        z, w = zs[(nbr[0].x(), nbr[0].y())], nbr[1] / qry[0]
                        z_out += z * w
                    ras[yi, xi] = z_out
                else:
                    ras[yi, xi] = self.no_data_value

        return ras

    @commons.eval_time
    def execute_pdal(self, fpath: str, output_file:str, method: str):
        """Sets up a PDAL pipeline that reads a ground filtered LAS
        file, and writes it via GDAL. The GDAL writer has interpolation
        options, exposing the radius, power and a fallback kernel width
        to be configured. More about these in the readme on GitHub.

        The GDAL writer creates rasters using the data specified in the dimension option (defaults to Z).
        The writer creates up to six rasters based on different statistics in the output dataset.
        The order of the layers in the dataset is as follows:
            - min : Give the cell the minimum value of all points within the given radius.
            - max : Give the cell the maximum value of all points within the given radius.
            - mean : Give the cell the mean value of all points within the given radius.
            - idw: Cells are assigned a value based on Shepard’s inverse distance weighting algorithm, considering all points within the given radius.

        Args:
            fpath(str):  input file for the pdal pipeliine
            output_file(str): output file for the pdal pipeliine
            method(str): Chose of the method = min / max / mean / idw

            rad(float): Radius about cell center bounding points to use to calculate a cell value. [Default: resolution * sqrt(2)]
            pwr(float): Exponent of the distance when computing IDW. Close points have higher significance than far points. [Default: 1.0]
            wnd(float): The maximum distance from donor cell to a target cell when applying the fallback interpolation method. [default:0]
        """
        pipeline = pdal.Reader.las(
            filename=fpath,
            override_srs=self.spatial_ref,
            nosrs=True
        )
        if self.classes:
            pipeline |= pdal.Filter.range(
                limits=",".join(f"Classification[{c}:{c}]" for c in self.classes)
            )
        pipeline |= pdal.Writer.gdal(
            output_type=method,
            resolution=str(self.pixel_size),
            origin_x=str(self.origin[0] - self.pixel_size / 2),  # lower left corner
            origin_y=str(self.origin[1] + self.pixel_size / 2 - self.tile_width),  # lower left corner
            width=str(self.nb_pixels[0]),
            height=str(self.nb_pixels[1]),
            power=2,
            window_size=5,
            nodata=self.no_data_value,
            data_type="float32",
            filename=output_file
        )

        pipeline.execute()


    @commons.eval_time
    def execute_pdal_tin(self, fpath: str, output_file:str):
        """Sets up a PDAL pipeline that reads a ground filtered LAS
        file, and interpolates either using "Delaunay", then " Faceraster" and writes it via RASTER. Uses a no-data value set in commons.
        More about these in the readme on GitHub.

        The Delaunay Filter creates a triangulated mesh fulfilling the Delaunay condition from a collection of points.

        The FaceRaster filter creates a raster from a point cloud using an algorithm based on an existing triangulation.
        Each raster cell is given a value that is an interpolation of the known values of the containing triangle. If the raster cell center is outside of the triangulation,
        it is assigned the nodata value. Use writers.raster to write the output.
        The extent of the raster can be defined by using the origin_x, origin_y, width and height options. If these options aren’t provided the raster is sized to contain the input data.

        The Raster Writer writes an existing raster to a file. Output is produced using GDAL and can use any driver that supports creation of rasters.
        A data_type can be specified for the raster (double, float, int32, etc.).
        If no data type is specified, the data type with the largest range supported by the driver is used.

        Args:
            fpath(str):  input file for the pdal pipeliine
            output_file(str): output file for the pdal pipeliine
        """
        pipeline = pdal.Reader.las(
            filename=fpath,
            override_srs=self.spatial_ref,
            nosrs=True
        )
        if self.classes:
            pipeline |= pdal.Filter.range(
                limits=",".join(f"Classification[{c}:{c}]" for c in self.classes)
            )

        pipeline |= pdal.Filter.delaunay()

        pipeline |= pdal.Filter.faceraster(
            resolution=str(self.pixel_size),
            origin_x=str(self.origin[0] - self.pixel_size / 2),  # lower left corner
            origin_y=str(self.origin[1] + self.pixel_size / 2 - self.tile_width),  # lower left corner
            width=str(self.nb_pixels[0]),
            height=str(self.nb_pixels[1]),
        )
        pipeline |= pdal.Writer.raster(
            gdaldriver="GTiff",
            nodata=self.no_data_value,
            data_type="float32",
            filename=output_file
        )

        pipeline.execute()


    def run(self, input_file: str, output_file: str):
        """Lauch the deterministic method
        Args:
            input_dir: folder to look for las file (usually temp_dir)
            tile_name: las tile name (without extension)
        Returns:
            ras(list): Z interpolation
        """
        def exec_startin_with_io(inpf, outf):
            return self.run_method_with_standard_io(self.execute_startin, inpf, outf)

        methods_map = {
            'pdal-idw': (lambda inpf, outf : self.execute_pdal(inpf, outf, method='idw')),
            'pdal-tin': self.execute_pdal_tin,
            'startin-tinlinear': exec_startin_with_io,
            'startin-laplace': exec_startin_with_io,
            'cgal-nn': (lambda inpf, outf : self.run_method_with_standard_io(
                        self.execute_cgal, inpf, outf)),
        }

        # run method
        methods_map[self.method.lower()](input_file, output_file)


def write_geotiff(raster, origin, size, fpath, spatial_ref='EPSG:2154', no_data_value=-9999):
    """Writes the interpolated TIN-linear and Laplace rasters
    to disk using the GeoTIFF format. The header is based on
    the raster array and a manual definition of the coordinate
    system and an identity affine transform.

    Args:
        raster(array) : Z interpolation
        origin(list): coordinate location of the relative origin (bottom left)
        size (float): raster cell size
        fpath(str): path to the output geotiff file

    Returns:
        bool: If the output "DTM" saved in fpath is okay or not
    """
    with rasterio.Env():
        with rasterio.open(fpath, 'w', driver = 'GTiff',
                           height=raster.shape[0],
                           width=raster.shape[1],
                           count=1,
                           dtype=rasterio.float32,
                           crs=spatial_ref,
                           transform=from_origin(origin[0] - size/2, origin[1] + size/2, size, size),
                           nodata=no_data_value,
                           ) as out_file:
            out_file.write(raster.astype(rasterio.float32), 1)