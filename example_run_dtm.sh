#!/bin/bash
INPUT="/input/"
OUTPUT="/output/"
FILTERED_LAS_DIR="/tmp/"
EXTENSION="laz"

USAGE="""
Usage ./example_run_dtm.sh -i INPUT_DIR -o OUTPUT_DIR -f FILTERED_LAS_DIR \
-e EXTENSION \n
EXTENSION should be las or laz (default is laz)
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
    o)  OUTPUT=${OPTARG}
      ;;
    f)  FILTERED_LAS_DIR=${OPTARG}
      ;;
    e)  EXTENSION=${OPTARG}
      ;;
  esac
done

# Step 1 : filter ground
python -m produit_derive_lidar.filter_multiprocessing \
    -i ${INPUT} \
    -o ${FILTERED_LAS_DIR} \
    --keep_classes 2 66 \
    -e ${EXTENSION}
# Step 2 ; create DTM with the severals method
python -m produit_derive_lidar.ip_multiprocessing \
    -i ${INPUT} \
    -o ${OUTPUT}/DTM \
    -f ${FILTERED_LAS_DIR} \
    -e ${EXTENSION} \
    --interpolation_method startin-Laplace

