import shutil
from pathlib import Path

import pytest

test_path = Path(__file__).resolve().parent
tmp_path = test_path / "tmp"
data_path = test_path / "data"
ground_truth_folder = data_path / "interpolation"


def get_expected_raster_bounds(coord_x, coord_y, tile_coord_scale, tile_width, pixel_size):
    expected_xmin = coord_x * tile_coord_scale - pixel_size / 2
    expected_ymax = coord_y * tile_coord_scale + pixel_size / 2
    expected_raster_bounds = (expected_xmin, expected_ymax - tile_width), (expected_xmin + tile_width, expected_ymax)
    return expected_raster_bounds


class TestTile:
    coord_x = 77055
    coord_y = 627760
    tile_coord_scale = 10
    tile_width = 50
    pixel_size = 0.5
    origin = [coord_x * tile_coord_scale, coord_y * tile_coord_scale]
    tilename = f"test_data_{coord_x}_{coord_y}_LA93_IGN69"

    input_filename = f"{tilename}.laz"
    input_path = data_path / input_filename
    output_filename = f"{tilename}_50CM.tif"

    shapefile = data_path / "mask_shapefile" / "test_multipolygon_shapefile.shp"

    expected_raster_bounds = get_expected_raster_bounds(coord_x, coord_y, tile_coord_scale, tile_width, pixel_size)

    def expected_interpolation(self, suffix=""):
        return ground_truth_folder / f"{self.tilename}_50CM{suffix}.tif"


@pytest.fixture(scope="session")
def test_tile():
    return TestTile()


def pytest_sessionstart(session):
    # Clean and recreate local_output
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def base_tmp_path():
    return tmp_path


@pytest.fixture(scope="session")
def base_data_path():
    return data_path
