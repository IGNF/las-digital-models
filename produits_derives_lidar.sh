#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda env create -n dtm -f environment.yml
conda activate dtm

python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/poc/ laz 0 1
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/poc/ laz 0 1 startin-TINlinear
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/poc/ laz 0 1 PDAL-IDW
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/poc/ laz 0 1 CGAL-NN
python3 ip_main.py /var/data/store-lidarhd/projet-LHD/Malvina/poc/ laz 0 1 IDWquad
