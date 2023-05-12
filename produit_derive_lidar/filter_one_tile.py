"""Run ground filtering for a single tile"""
from produit_derive_lidar.commons import commons
from produit_derive_lidar.tasks.las_filter import filter_las_classes
import logging
import os
import hydra
from omegaconf import DictConfig


log = commons.get_logger(__name__)


@hydra.main(config_path="../configs/", config_name="config.yaml", version_base="1.2")
def run_filter_on_tile(config: DictConfig):
    os.makedirs(config.io.output_dir, exist_ok=True)
    # manage paths
    input_full_path = os.path.join(config.io.input_dir, config.io.input_filename)
    _, input_basename = os.path.split(config.io.input_filename)

    if config.io.forced_intermediate_ext is None:
        output_basename = input_basename
    else:
        tilename, _ = os.path.splitext(input_basename)
        output_basename = f"{tilename}.{config.io.forced_intermediate_ext}"

    output_file = os.path.join(config.io.output_dir, output_basename)

    ## process
    log.debug(f"Keep classes: {config.filter.keep_classes}")
    filter_las_classes(input_full_path,
                       output_file,
                       spatial_ref=config.io.spatial_reference,
                       keep_classes=config.filter.keep_classes)

    return


def main():
    logging.basicConfig(level=logging.DEBUG)
    run_filter_on_tile()


if __name__ == "__main__":
    main()
