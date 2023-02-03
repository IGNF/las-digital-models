#!/bin/bash
INPUT="/input/"
OUTPUT="/output/"
FORMAT="laz"

USAGE="""
Usage ./run.sh -i INPUT_DIR -o OUTPUT_DIR -f FORMAT \n
FORMAT should be las or laz (default is laz)
"""
# Parse arguments in order to possibly overwrite paths
while getopts "h?i:o:f:" opt; do
  case "$opt" in
    h|\?)
      echo -e ${USAGE}
      exit 0
      ;;
    i)  INPUT=${OPTARG}
      ;;
      ;;
    i_s)  INPUT_DSM=${OPTARG}
      ;;
      ;;
    i_t)  INPUT_DTM=${OPTARG}
      ;;
    o)  OUTPUT=${OPTARG}
      ;;
    f)  FORMAT=${OPTARG}
      ;;
  esac
done

# Step 1 : filter ground
python -m produit_derive_lidar.gf_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} --keep_classes 2 9 66
# Step 2 ; create DTM with the severals method
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m startin-TINlinear
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5 -m PDAL-IDW
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m CGAL-NN
# Step 3 : filter ground and upground 
python -m produit_derive_lidar.gf_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} --keep_classes 2 3 4 5 6 9 66
# Step 4 ; create DSM with the severals method
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m startin-TINlinear
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5 -m PDAL-IDW
python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m CGAL-NN
# Step 4 ; create DHM with the severals method
python -m produit_derive_lidar.dhm_multiprocessing -i ${INPUT} -i_m ${INPUT_DSM} -i_t ${INPUT_DTM} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5
python -m produit_derive_lidar.dhm_multiprocessing -i ${INPUT} -i_m ${INPUT_DSM} -i_t ${INPUT_DTM} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m startin-TINlinear
python -m produit_derive_lidar.dhm_multiprocessing -i ${INPUT} -i_m ${INPUT_DSM} -i_t ${INPUT_DTM} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp -e ${FORMAT} -p 0 -s 0.5 -m PDAL-IDW
python -m produit_derive_lidar.dhm_multiprocessing -i ${INPUT} -i_m ${INPUT_DSM} -i_t ${INPUT_DTM} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m CGAL-NN
# Not working for now:
# python -m produit_derive_lidar.ip_multiprocessing -i ${INPUT} -o ${OUTPUT}/DTM -t ${OUTPUT}/_tmp  -e ${FORMAT} -p 0 -s 0.5 -m IDWquad
