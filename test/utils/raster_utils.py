import numpy as np
import rasterio
from osgeo import gdal

# Make gdal forward exceptions to python pinding
gdal.UseExceptions()


# https://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
def get_tif_extent(filename):
    """Return list of corner coordinates from a tif image"""
    ds = gdal.Open(filename)

    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    # close gdal dataset (cf. https://gis.stackexchange.com/questions/80366/why-close-a-dataset-in-gdal-python)
    ds = None

    return (xmin, ymin), (xmax, ymax)


def allclose_mm(a, b):
    """Check that values are similar with milimeter precision
    Use this nstead of np.allclose to use only an absolute tolerance"""
    if isinstance(a, tuple) or isinstance(b, tuple):
        a = np.array(a)
        b = np.array(b)
    return np.all(np.less(np.abs(b - a), 1e-3))


def tif_values_all_close(filename1, filename2):
    with rasterio.Env():
        src1 = rasterio.open(filename1)
        data1 = src1.read(1)

        src2 = rasterio.open(filename2)
        data2 = src2.read(1)

    return allclose_mm(data1, data2)
