#!/bin/bash
# Run lidar_prod preprocessing in a docker container (as generated with ./build.sh)

input_dir="TO SET"
output_dir="TO SET"
input_tiles="TO SET"

docker run -t -d --userns=host --shm-size=2gb  \
    -v ${input_dir}:/input \
    -v ${output_dir}:/output \
    -v /var/tmp:/tmp \
    lidar_hd/produitderivelidar:latest \
    python -m lidar_prod.gf_one_tile \
    -i /input/${input_tile} \
    -o /output/DTM
