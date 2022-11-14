# -*- coding: utf-8 -*-
# maintener : MDupays
# version : v.0 10/10/2022
# MAIN FILE FOR PRE-PROCESSING  



"""Key to CMD arguments:
    1:  target folder (most likely the same as the one you used with PDAL)
        [compulsory, no default value] (folder "data")
    2:  Directory folder for saving the outputs
    3:  extension (LAS / LAZ) [default : LAS]

Output file will be written to the target folder "output" : combines input from ground pointcloud into a single output.
"""
import os
from sys import argv
from gf_processing import start_pool

def create_folder():
    """Create the severals folders "DTM" and "_tmp" if not exist"""
    # Create folder "DTM"
    if os.path.isdir('./DTM') is False:
        os.makedirs('DTM')
    # Create folder "DTM"
    if os.path.isdir('./_tmp') is False:
        os.makedirs('_tmp')

def main():    
    # Create the severals folder if not exists
    create_folder()
    if len(argv) <= 4: start_pool(*argv[1:])
    else: print("Error: Incorrect number of arguments passed. Returning.")
    
if __name__ == '__main__':
    main()