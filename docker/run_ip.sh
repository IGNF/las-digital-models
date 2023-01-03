#!/bin/bash
# Run lidar_prod interpolation in a docker container (as generated with ./build.sh)

input_dir="TO SET"
output_dir="TO SET"
input_tile="TO SET"

postprocessing=0
pixel_size=1
interpolation_method="startin-TINlinear"

docker run -t -d --userns=host --shm-size=2gb  \
    -v ${input_dir}:/input \
    -v ${output_dir}:/output \
    -v /var/tmp:/tmp \
    --cpus 1 \
    lidar_hd/produitderivelidar:latest \
    python /app/lidar_prod/ip_one_tile.py
    -i /input/${input_tile}
    -o /output/
    -t /tmp/
    -p {postprocessing}
    -s {pixel_size}
    -m {interpolation_method}

# done