# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0.1.0 02/02/2023
# Calculate DHM
import lidarutils.gdal_calc as gdal_calc
from produit_derive_lidar.commons import commons


def calculate_dhm(input_image_dsm, input_image_dtm, output_image):
    """ Calculate DHM from DSM and DTM (DHM = DSM - DTM)

    Args:
        input_file_dsm (str): DSM by tile
        input_file_dtm (str): DTM by tile
        output_dir (str) : directory "DHM"
        fname (str): name of LIDAR tile

    """
    # Calculate A - B where A and B have valid values, else return a no_data value
    gdal_calc.Calc("(A - B) * (A > -9999) * (B > -9999) + (-9999) * (1 - (A > -9999) * (B > -9999))",
                   outfile=output_image,
                   A=input_image_dsm, A_band=1,
                   B=input_image_dtm, B_band=1, type="Float32", quiet=True)