#!/bin/bash
source get_conda.sh
conda activate lidar_prod

bash ./run.sh -i /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ \
              -o /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ \
              -f laz
