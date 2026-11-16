"""
test some PDAL features
"""

import os

import pdal


def test_pdal_read_several_extra_dims(base_data_path):
    # test that we can read a las file with several extra dims
    test_file = os.path.join(base_data_path, "las_test_pdal/las_with_several_extra_byte_bloc.laz")

    pipeline = pdal.Reader.las(filename=test_file).pipeline()
    metadata = pipeline.quickinfo["readers.las"]

    # dimensions should contains 'Deviation' and 'confidence'
    assert "Deviation" in metadata["dimensions"]
    assert "confidence" in metadata["dimensions"]

    # Test Python PDAL bindings
    pipeline = pdal.Reader.las(filename=test_file).pipeline()
    num_points = pipeline.execute()
    assert num_points > 0
