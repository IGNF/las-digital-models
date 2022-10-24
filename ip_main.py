# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# MAIN FILE FOR INTERPOLATION + POST-PROCESSING 
#             PRIMARY ENTRY POINT FOR PROGRAM                  



"""Key to CMD arguments:
    1:  target folder (most likely the same as the one you used with PDAL)
        [compulsory, no default value]
    2:  extension (LAS / LAZ) [default : LAS]
    3. integer to set the post-processing mode, currently these ones
        are available:
          - 0 (default, does not run post-processing)
          - 1 (runs missing pixel value patching only)
          - 2 (runs basic flattening only)
          - 3 (runs both patching and basic flattening)
          - 4 (runs patching, basic flattening and hydro-flattening)
    4:  pixel size (in metres) for interpolation
        [default: 1 metre]
    5:  interpolation method, one of:
          - startin-TINlinear
          - [default] startin-Laplace
          - CGAL-NN
          - CGAL-CDT (experimental, not ready yet)
          - PDAL-IDW
          - IDWquad
    6:  output format, one of:
          - ASC
          - [default] GeoTIFF
    7:  IDW radius (for PDAL-IDW) //
        // STARTING IDW radius/number of neighbours to query (for IDWquad)
    8:  IDW power (for PDAL-IDW and IDWquad)
    9:  IDW fallback kernel width (for PDAL-IDW) //
        // MINIMUM number of points per quadrant (for IDWquad)
    10: radius/number of neighbours INCREMENT value (for IDWquad)
    11: IDWquad method, one of:
          - radial
          - k-nearest
    12: IDWquad tolerance (epsilon)
    13: IDWquad maximum number of iteration before declaring no-data

All IDW parameters are optional, but it is assumed the user will fine-
tune them, hence the defaults are not listed.

Output files will be written to the target folder, tagged with the
name of the interpolation method that was used.
"""

from sys import argv
from ip_processing import start_pool

def main():
    if 2 <= len(argv) <= 13: start_pool(*argv[1:])
    else: print("Error: Incorrect number of arguments passed. Returning.")
    
if __name__ == '__main__':
    main()