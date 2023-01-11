from osgeo import gdal


# https://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
def get_tif_extent(filename):
    """ Return list of corner coordinates from a tif image """
    ds = gdal.Open(filename)

    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    ds = None  # close gdal dataset (cf. https://gis.stackexchange.com/questions/80366/why-close-a-dataset-in-gdal-python)

    return (xmin, ymin), (xmax, ymax)