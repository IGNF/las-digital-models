from produit_derive_lidar import ip_one_tile
import logging
import os
import pytest
import shutil
import test.utils.raster_utils as ru
from hydra import initialize, compose


coordX = 77055
coordY = 627760
tile_coord_scale = 10
tile_width = 50
pixel_size = 0.5

test_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(test_path, "tmp")
ground_truth_folder = os.path.join(test_path, "data", "interpolation")

expected_xmin = coordX * tile_coord_scale - pixel_size/2
expected_ymax = coordY * tile_coord_scale  + pixel_size/2
expected_raster_bounds = (expected_xmin, expected_ymax - tile_width), (expected_xmin + tile_width, expected_ymax)

shapefile = os.path.join(test_path, "data", "mask_shapefile", "test_multipolygon_shapefile.shp")
expected_output_using_shapefile = os.path.join(
    ground_truth_folder,
    'test_data_77055_627760_LA93_IGN69_50CM_TIN_no_data.tif')


def setup_module(module):
    try:
        shutil.rmtree(tmp_path)

    except (FileNotFoundError):
        pass
    os.mkdir(tmp_path)


def get_expected_output_file(method_postfix):
    expected_output_file = os.path.join(
        tmp_path, "hydra_ip",
        f"test_data_{coordX}_{coordY}_LA93_IGN69_50CM_{method_postfix}.tif")

    return expected_output_file


def compute_test_ip_one_tile(method):
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                      overrides=["io=test", "tile_geometry=test", f"interpolation={method}",
                                 "filter.keep_classes=[]"])
        assert cfg.interpolation.algo_name == method  # Check that the correct method is used

        output_file = get_expected_output_file(cfg.interpolation.method_postfix)
        logging.debug(output_file)
        logging.debug(f"Pixel size: {cfg.tile_geometry.pixel_size}")

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, expected_raster_bounds)

        assert ru.tif_values_all_close(
            output_file,
            os.path.join(ground_truth_folder, os.path.basename(output_file)))



def test_ip_one_tile_all_methods():
    for method in ["cgal-nn", "pdal-idw", "pdal-tin", "startin-laplace", "startin-tinlinear"]:

        logging.debug(f"Test for method: {method}")
        compute_test_ip_one_tile(method)


def test_ip_with_no_data_mask():
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                      overrides=["io=test", "tile_geometry=test", "interpolation=pdal-tin",
                                 "filter.keep_classes=[]",
                                 f"io.no_data_mask_shapefile={shapefile}"])

        output_file = get_expected_output_file(cfg.interpolation.method_postfix)

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, expected_raster_bounds)

        assert ru.tif_values_all_close(output_file, expected_output_using_shapefile)


def test_ip_dtm_classes_tin():
    expected_output = os.path.join(test_path, "data", "interpolation",
                                   "test_data_77055_627760_LA93_IGN69_50CM_TIN_dtm_classes.tif")
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(config_name="config",
                      overrides=["io=test", "tile_geometry=test", "interpolation=pdal-tin",
                                 "filter=dtm", "io.output_dir=./test/tmp/hydra_ip/DTM"])

        output_file = get_expected_output_file(cfg.interpolation.method_postfix)

        ip_one_tile.run_ip_on_tile(cfg)
        assert os.path.isfile(output_file)

        raster_bounds = ru.get_tif_extent(output_file)
        assert ru.allclose_mm(raster_bounds, expected_raster_bounds)

        assert ru.tif_values_all_close(output_file, expected_output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_ip_one_tile_all_methods()
    test_ip_with_no_data_mask()

