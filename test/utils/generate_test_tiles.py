"""Script to generate small test tiles from a laz file
Take a grid of 3x3 tiles of size 'tiles_size', with a given offset from the bottom-left corner of
the input tile.
Save only part of the tiles, the indices of the output tiles are located like:
6, 7, 8
3, 4, 5
0, 1, 2
(the up-left corner of tile 4 is centered to make it easier to compute)
"""

import argparse
import os
import test.utils.point_cloud_utils as pcu

import numpy as np
from las_stitching.las_clip import las_crop


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", help="Input laz file")
    parser.add_argument("--output", "-o", help="Folder for las outpout", default="test/data/")
    parser.add_argument("--tiles_size", "-s", type=int, help="Size (in meter) for the output tiles", default=10)
    parser.add_argument("--keep", "-k", type=int, help="Number of tiles to keep (out of 9). Default: all", default=9)
    parser.add_argument(
        "--offset",
        "-d",
        nargs=2,
        type=int,
        help="Offset in xy of the input tile from the corner of the input file (in meters)",
        default=[0, 0],
    )

    return parser.parse_args()


def main(args):
    bounds = pcu.get_2d_bounding_box(args.input)
    assert np.all(
        bounds[1] - bounds[0] > (np.array(args.offset) + 3 * args.tiles_size)
    ), "Output tiles fall outside of input tile"
    [xmin_in, ymin_in], _ = bounds
    gridy, gridx = np.mgrid[0:3, 0:3]
    ii = 0
    for xx, yy in zip(np.nditer(gridx), np.nditer(gridy)):
        output_path = os.path.join(args.output, f"test_data_{xx:04d}_{yy:04d}_LA93_IGN69.laz")
        xmin = xmin_in + args.offset[0] + xx * args.tiles_size
        xmax = xmin_in + args.offset[0] + (xx + 1) * args.tiles_size
        ymin = ymin_in + args.offset[1] + yy * args.tiles_size
        ymax = ymin_in + args.offset[1] + (yy + 1) * args.tiles_size
        las_crop(args.input, output_path, ([xmin, xmax], [ymin, ymax]))
        ii += 1
        if ii >= args.keep:
            break


if __name__ == "__main__":
    args = parse_args()
    main(args)
