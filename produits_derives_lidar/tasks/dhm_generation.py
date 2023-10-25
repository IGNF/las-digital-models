# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0.1.0 02/02/2023
# Calculate DHM
from osgeo import gdal
from osgeo_utils import gdal_calc

gdal.UseExceptions()


def calculate_dhm(input_image_dsm: str, input_image_dtm: str, output_image: str, no_data_value: int = -9999):
    """Calculate DHM from DSM and DTM (DHM = DSM - DTM)

    Args:
        input_file_dsm (str): path to DSM file
        input_file_dtm (str): path to DTM file
        output_image (str) : path to output DHM file
        no_data_value (int): no data value (default to -9999)

    """
    # Calculate A - B where A and B have valid values, else return a no_data value
    gdal_calc.Calc(
        f"(A - B) * (A != {no_data_value}) * (B != {no_data_value})"
        + f" + ({no_data_value}) * (1 - (A != {no_data_value}) * (B != {no_data_value}))",
        outfile=output_image,
        A=input_image_dsm,
        A_band=1,
        B=input_image_dtm,
        B_band=1,
        type="Float32",
        quiet=True,
        NoDataValue=no_data_value,
        overwrite=True,
    )
