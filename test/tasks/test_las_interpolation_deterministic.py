import os
import pytest
import shutil
from produit_derive_lidar.tasks import las_interpolation_deterministic
from produit_derive_lidar.commons import commons
import test.utils.point_cloud_utils as pcu


test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_path = os.path.join(test_path, "tmp")
input_file = os.path.join(
    test_path,
    "data",
    "Semis_2021_0770_6278_LA93_IGN69.laz"
)


# def setup_module(module):
#     try:
#         shutil.rmtree(tmp_path)

#     except (FileNotFoundError):
#         pass
#     os.mkdir(tmp_path)


# def run_one_method(method):
#     raise NotImplementedError


# def test_all_methods():
#     for method in commons.method_postfix.keys():
#         print(f"Tested method: {method}")
#         run_one_method(method)


# if __name__ == "__main__":
#     test_all_methods()
