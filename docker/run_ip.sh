#!/bin/bash
# Run produit_derive_lidar interpolation in a docker container (as generated with ./build.sh)

input_dir="TO SET"
output_dir="TO SET"
filtered_dir="TO SET"
input_tile="TO SET"

pixel_size=1
interpolation_method="startin-TINlinear"

docker run -t --rm --userns=host --shm-size=2gb  \
    -v ${input_dir}:/input \
    -v ${output_dir}:/output \
    -v ${filtered_dir}:/filtered \
    -v /var/tmp:/tmp \
    --cpus 1 \
    lidar_hd/produitderivelidar:latest \
    python -m produit_derive_lidar.ip_one_tile \
    -i /input/${input_tile} \
    -f /filtered/ \
    -o /output/ \
    -t /tmp/ \
    -s ${pixel_size} \
    -m ${interpolation_method} \

# done