# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# MAIN FILE FOR PRE-PROCESSING  



"""Key to CMD arguments:
    1:  target folder (most likely the same as the one you used with PDAL)
        [compulsory, no default value] (folder "data")
    2:  extension (LAS / LAZ) [default : LAS]

Output file will be written to the target folder "output" : combines input from ground pointcloud into a single output.
"""

from sys import argv
from gf_processing import start_pool

def main():
    if len(argv) <= 3: start_pool(*argv[1:])
    else: print("Error: Incorrect number of arguments passed. Returning.")
    
if __name__ == '__main__':
    main()