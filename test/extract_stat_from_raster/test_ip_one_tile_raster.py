import os
import shutil
import subprocess as sp
from pathlib import Path

# import pytest
# from hydra import compose, initialize

# from produits_derives_lidar.extract_stat_from_raster.ip_one_tile_raster import main

DATA_DIR = Path("data/bridge")
INPUT_DIR = DATA_DIR / "mns_hydro_postfiltre"
INPUT_GEOMETRY_DIR = DATA_DIR / "input_operators/lignes_contraintes"
OUTPUT_DIR = Path("tmp") / "main_ip_one_tile_raster"


def setup_module(module):
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():
    cmd = f"""python -m produits_derives_lidar.extract_stat_from_raster.ip_one_tile_raster \
        io.input_dir={INPUT_DIR}\
        io.input_geometry_dir={INPUT_GEOMETRY_DIR}
        io.output_dir={OUTPUT_DIR}
        """
    sp.run(cmd, shell=True, check=True)
