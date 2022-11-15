#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda env create -n dtm -f environment.yml
conda activate dtm

# Step 1 : filter ground
python3 gf_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz
# Step 2 ; create DTM
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz 0 0.5
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz 0 0.5 startin-TINlinear
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz 0 0.5 PDAL-IDW
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz 0 0.5 CGAL-NN
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/data/ /var/data/store-lidarhd/projet-LHD/Malvina/POC/MQ/ laz 0 0.5 IDWquad
