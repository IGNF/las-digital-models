# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# LAS INTERPOLATION
import logging
from produit_derive_lidar.commons import commons
import pdal
import json
import numpy as np


class deterministic_method:
    """Takes the grid parameters and the ground points. Interpolates
    either using the severals interpolations methods

    Args:
        pts : ground points clouds
        res(list): resolution in coordinates
        origin(list): coordinate location of the relative origin (bottom left)
        size (int): raster cell size
        method(str): spatial interpolation
    """

    def __init__(
        self,
        pts,
        res: list,
        origin: list,
        size: float,
        method: str,
        spatial_ref: str
    ):
        self.pts = pts
        self.res = res
        self.origin = origin
        self.size = size
        self.method = method
        self.spatial_ref=spatial_ref

    @commons.eval_time
    def execute_startin(self):
        """Takes the grid parameters and the ground points. Interpolates
        either using the TIN-linear or the Laplace method. Uses a -9999 no-data value.
        Fully based on the startin package (https://startinpy.readthedocs.io/en/latest/api.html)

        Returns:
            ras(list): Z interpolation
        """
        import startinpy
        import numpy as np

        # # Startin
        tin = startinpy.DT(); tin.insert(self.pts) # # Insert each points in the array of points (a 2D array)
        ras = np.zeros([self.res[1], self.res[0]]) # # returns a new array of given shape and type, filled with zeros
        # # Interpolate method
        if self.method == 'startin-TINlinear':
            def interpolant(x, y): return tin.interpolate_tin_linear(x, y)
        elif self.method == 'startin-Laplace':
            def interpolant(x, y): return tin.interpolate_laplace(x, y)
        else:
            raise NotImplementedError(f"Method {self.method} not impplemented for execute_startin")
        yi = 0
        for y in np.arange(self.origin[1], self.origin[1] + self.res[1] * self.size, self.size):
            xi = 0
            for x in np.arange(self.origin[0], self.origin[0] + self.res[0] * self.size, self.size):
                ch = tin.is_inside_convex_hull(x, y) # check is the point [x, y] located inside  the convex hull of the DT
                if ch == False:
                    ras[yi, xi] = -9999 # no-data value
                else:
                    tri = tin.locate(x, y) # locate the triangle containing the point [x,y]. An error is thrown if it is outside the convex hull
                    if tri != [] and 0 not in tri:
                        ras[yi, xi] = interpolant(x, y)
                    else: ras[yi, xi] = -9999 # no-data value
                xi += 1
            yi += 1
        return ras

    @commons.eval_time
    def execute_cgal(self):
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

        s_idx = np.lexsort(self.pts.T); s_data = self.pts[s_idx,:]
        mask = np.append([True], np.any(np.diff(s_data[:,:2], axis = 0), 1))
        deduped = s_data[mask]
        cpts = list(map(lambda x: Point_2(*x), deduped[:,:2].tolist()))
        zs = dict(zip([tuple(x) for x in deduped[:,:2]], deduped[:,2]))

        tin = Delaunay_triangulation_2()
        for pt in cpts: tin.insert(pt)
        ras = np.zeros([self.res[1], self.res[0]])
        yi = 0
        for y in np.arange(self.origin[1], self.origin[1] + self.res[1] * self.size, self.size):
            xi = 0
            for x in np.arange(self.origin[0], self.origin[0] + self.res[0] * self.size, self.size):
                nbrs = []
                qry = natural_neighbor_coordinates_2(tin, Point_2(x, y), nbrs)
                if qry[1] == True:
                    z_out = 0
                    for nbr in nbrs:
                        z, w = zs[(nbr[0].x(), nbr[0].y())], nbr[1] / qry[0]
                        z_out += z * w
                    ras[yi, xi] = z_out
                else: ras[yi, xi] = -9999
                xi += 1
            yi += 1
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

        information = {}
        information = {
            "pipeline": [
                {
                    "type":"readers.las",
                    "filename":fpath,
                    "override_srs": self.spatial_ref,
                    "nosrs": True
                    # "NOSRS" = Don’t read the SRS VLRs. The data will not be assigned an SRS.
                },
                {
                    "output_type": method,
                    "resolution": str(self.size),
                    #"radius": str(self.size * sqrt(2)),
                    "power": 2,
                    "window_size": 5,
                    "nodata": -9999,
                    "data_type": "float32",
                    "filename": output_file
                }
            ]
        }
        las_mnt = json.dumps(information, sort_keys=True, indent=4)
        pipeline = pdal.Pipeline(las_mnt)
        pipeline.execute()

    @commons.eval_time
    def execute_idwquad(self, start_rk, pwr: float, minp: float, incr_rk: float, method: str, tolerance: float, maxiter: float):
        """Creates a KD-tree representation of the tile's points and executes a quadrant-based IDW algorithm on them.
        Although the KD-tree is based on a C implementation, the rest is coded in pure Python (below).
        Keep in mind that because of this, this is inevitably slower than the rest of the algorithms here.
        To optimise performance, one is advised to fine-tune the parametrisation, especially tolerance and maxiter.
        More info in the GitHub readme.
        """
        from scipy.spatial import cKDTree

        # Parameters
        ras = np.zeros([self.res[1], self.res[0]])
        tree = cKDTree(np.array([self.pts[:,0], self.pts[:,1]]).transpose())
        yi = 0
        for y in np.arange(self.origin[1], self.origin[1] + self.res[1] * self.size, self.size):
            xi = 0
            for x in np.arange(self.origin[0], self.origin[0] + self.res[0] * self.size, self.size):
                done, i, rk = False, 0, start_rk
                while done == False:
                    if method == "radial":
                        ix = tree.query_ball_point([x, y], rk, tolerance)
                    elif method == "k-nearest":
                        ix = tree.query([x, y], rk, tolerance)[1]
                    xyp = self.pts[ix]
                    qs = [
                            xyp[(xyp[:,0] < x) & (xyp[:,1] < y)],
                            xyp[(xyp[:,0] > x) & (xyp[:,1] < y)],
                            xyp[(xyp[:,0] < x) & (xyp[:,1] > y)],
                            xyp[(xyp[:,0] > x) & (xyp[:,1] > y)]
                        ]
                    if min(qs[0].size, qs[1].size,
                        qs[2].size, qs[3].size) >= minp: done = True
                    elif i == maxiter:
                        ras[yi, xi] = -9999; break
                    rk += incr_rk; i += 1
                else:
                    asum, bsum = 0, 0
                    for pt in xyp:
                        dst = np.sqrt((x - pt[0])**2 + (y - pt[1])**2)
                        u, w = pt[2], 1 / dst ** pwr
                        asum += u * w; bsum += w
                        ras[yi, xi] = asum / bsum
                xi += 1
            yi += 1
        return ras

    @commons.eval_time
    def execute_pdal_tin(self, fpath: str, output_file:str):
        """Sets up a PDAL pipeline that reads a ground filtered LAS
        file, and interpolates either using "Delaunay", then " Faceraster" and writes it via RASTER. Uses a -9999 no-data value.
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

        information = {}
        information = {
            "pipeline": [
                {
                    "type":"readers.las",
                    "filename":fpath,
                    "override_srs": self.spatial_ref,
                    "nosrs": True
                    # "NOSRS" = Don’t read the SRS VLRs. The data will not be assigned an SRS.
                },
                {
                    "type": "filters.delaunay"
                },
                {
                    "type": "filters.faceraster",
                    "resolution": str(self.size)
                },
                {
                    "type": "writers.raster",
                    "gdaldriver":"GTiff",
                    "nodata": -9999,
                    "data_type": "float32",
                    "filename": output_file
                }
            ]
        }
        las_mnt = json.dumps(information, sort_keys=True, indent=4)
        pipeline = pdal.Pipeline(las_mnt)
        pipeline.execute()

    def run(self, pdal_input: str, pdal_output: str):
        """Lauch the deterministic method
        Args:
            input_dir: folder to look for las file (usually temp_dir)
            tile_name: las tile name (without extension)
        Returns:
            ras(list): Z interpolation
        """
        if self.method == 'PDAL-IDW':
            self.execute_pdal(pdal_input, pdal_output, method='idw')
        elif self.method == 'PDAL-TIN':
            self.execute_pdal_tin(pdal_input, pdal_output)
            return
        if self.method == 'startin-TINlinear' or self.method == 'startin-Laplace':
            ras = self.execute_startin()
        elif self.method == 'CGAL-NN':
            ras = self.execute_cgal()
        elif self.method == 'IDWquad':
            ras = self.execute_idwquad()
        return ras