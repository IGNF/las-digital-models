# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.1 06/12/2022
# LAS INTERPOLATION
import logging
import os
from omegaconf import OmegaConf
from commons import commons
import pdal
import json

log = logging.getLogger(__name__)


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
        method: str
    ):
        self.pts = pts
        self.res = res
        self.origin = origin
        self.size = size
        self.method = method

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
            print('error')
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
        ras = np.zeros([res[1], res[0]])
        yi = 0
        for y in np.arange(self.origin[1], self.origin[1] + self.res[1] * self.size, self.size):
            xi = 0
            for x in np.arange(self.origin[0], self.origin[0] + self.res[0] * self.size, self.size):
                nbrs = [];
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

    def give_name_resolution_raster(self):
        """
        Give a resolution from raster

        Return:
            _size(str): resolution from raster for output's name
        """
        if float(self.size) == 1.0:
            _size = str('_1M')
        elif float(self.size) == 0.5:
            _size = str('_50CM')
        elif float(self.size) == 5.0:
            _size = str('_5M')
        else:
            _size = str(self.size)
        return _size

    @commons.eval_time
    def execute_pdal(self, fpath: str, method: str):
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
            fpath(str): target folder 
            method(str): Chose of the method = min / max / mean / idw
            rad(float): Radius about cell center bounding points to use to calculate a cell value. [Default: resolution * sqrt(2)]
            pwr(float): Exponent of the distance when computing IDW. Close points have higher significance than far points. [Default: 1.0]
            wnd(float): The maximum distance from donor cell to a target cell when applying the fallback interpolation method. [default:0]
        """
        import pdal
        import json

        # # Return size for output's name
        _size = self.give_name_resolution_raster()
        Fileoutput = "".join([fpath[:-9], "_".join([_size,'IDW.tif'])])
        information = {}
        information = {
            "pipeline": [
                {
                    "type":"readers.las",
                    "filename":fpath,
                    "override_srs": "EPSG:2154",
                    "nosrs": True
                    # "NOSRS" = Don’t read the SRS VLRs. The data will not be assigned an SRS. 
                },
                {
                    "type":"filters.range",
                    "limits":"Classification[2:2],Classification[66:66]"
                },
                {
                    "output_type": method,
                    "resolution": str(self.size),
                    #"radius": str(self.size * sqrt(2)),
                    "power": 2,
                    "window_size": 1,
                    "nodata": -9999,    
                    "data_type": "float32",
                    "filename": Fileoutput
                }
            ]
        }
        las_mnt = json.dumps(information, sort_keys=True, indent=4)
        pipeline = pdal.Pipeline(las_mnt)
        pipeline.execute()

    @commons.eval_time
    def execute_idwquad(start_rk, pwr: float, minp: float, incr_rk: float, method: str, tolerance: float, maxiter: float):
        """Creates a KD-tree representation of the tile's points and executes a quadrant-based IDW algorithm on them. 
        Although the KD-tree is based on a C implementation, the rest is coded in pure Python (below). 
        Keep in mind that because of this, this is inevitably slower than the rest of the algorithms here.
        To optimise performance, one is advised to fine-tune the parametrisation, especially tolerance and maxiter.
        More info in the GitHub readme.
        """
        from scipy.spatial import cKDTree

        # Parameters
        size = self.size
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
                    xyp = pts[ix]
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

    def run(self, target_folder: str, fname: str):
        """Lauch the deterministic method

        Returns:
            ras(list): Z interpolation
        """
        if self.method == 'PDAL-IDW':
            self.execute_pdal(("_tmp/".join([target_folder[:-5], "_crop".join([fname[:-4], ".las"])])), method='idw')
            return
        if self.method == 'startin-TINlinear' or self.method == 'startin-Laplace':
            ras = self.execute_startin()
        elif self.method == 'CGAL-NN':
            ras = self.execute_cgal()
        elif self.method == 'IDWquad':
            ras = self.execute_idwquad()
        return ras