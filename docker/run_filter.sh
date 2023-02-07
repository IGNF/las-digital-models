#!/bin/bash
# Run produit_derive_lidar preprocessing in a docker container (as generated with ./build.sh)

input_dir="TO SET"
output_dir="TO SET"
input_tile="TO SET"

docker run -t --rm --userns=host --shm-size=2gb  \
    -v ${input_dir}:/input \
    -v ${output_dir}:/output \
    -v /var/tmp:/tmp \
    lidar_hd/produitderivelidar:latest \
    python -m produit_derive_lidar.filter_one_tile \
    -i /input/${input_tile} \
    -o /output/
