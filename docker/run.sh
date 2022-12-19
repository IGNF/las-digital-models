#!/bin/bash
# Run lidar_prod/run.sh in a docker container (as generated with ./build.sh)

input_dir="to set"
output_dir="to set"

container_name="lidarprod_runner"

docker run -t -d --userns=host --shm-size=2gb  \
    -v ${input_dir}:/input \
    -v ${output_dir}:/output \
    -v /var/tmp:/tmp \
    --name ${container_name} \
    lidar_hd/produitderivelidar:latest \
    bash /app/lidar_prod/run.sh \
    -i /input/ \
    -o /output/