#!/bin/bash

# Break if command fails
set -e

INPUT="/input/"
OUTPUT="/output/"
FORMAT="laz"
PIXEL_SIZE=0.5
CPU_LIMIT=-1

USAGE="""
Usage ./run.sh -i INPUT_DIR -o OUTPUT_DIR -f FORMAT -p PIXEL_SIZE -c CPU_LIMIT \n
FORMAT should be las or laz (default is laz)
"""
# Parse arguments in order to possibly overwrite paths
while getopts "h?i:o:f:p:c:" opt; do
  case "$opt" in
    h|\?)
      echo -e ${USAGE}
      exit 0
      ;;
    i)  INPUT=${OPTARG}
      ;;
    o)  OUTPUT=${OPTARG}
      ;;
    f)  FORMAT=${OPTARG}
      ;;
    p)  PIXEL_SIZE=${OPTARG}
      ;;
    c)  CPU_LIMIT=${OPTARG}
      ;;
  esac
done

METHODS=($(python -c "from produit_derive_lidar.commons import commons; print(list(commons.method_postfix.keys()))" | tr -d "'[],"))

echo "GENERATE DSM/DTM/DHM FOR METHODS: ${METHODS[@]}"
echo ""

echo "------------------"
echo "RUN DTM GENERATION"
echo "------------------"


# Output filenames for each step
FILTERED_DIR=${OUTPUT}/ground
BUFFERED_DIR=${OUTPUT}/ground_with_buffer
TMP_DIR=${OUTPUT}/tmp/DTM
DTM_DIR=${OUTPUT}/DTM

# Step 1.1 : filter ground
echo "------------------"
echo "filter ground"
echo "------------------"
python -m produit_derive_lidar.filter_multiprocessing \
    -i ${INPUT} \
    -o ${FILTERED_DIR} \
    -e ${FORMAT} \
    --keep_classes 2 9 66 \
    --cpu_limit ${CPU_LIMIT}


# Step 1.2: Create las with buffer from its neighbors tiles
# /!\ rasters generated from these las tiles will need to be cropped to match the input las area
# Extension is not provided as intermediate fles are las files
echo "------------------"
echo "add buffer"
echo "------------------"
python -m produit_derive_lidar.add_buffer_multiprocessing \
    -i ${FILTERED_DIR} \
    -o ${BUFFERED_DIR} \
    -b 100 \
    --cpu_limit ${CPU_LIMIT}


# # Step 1.3 ; create DTM with the severals method
echo "------------------"
echo "interpolation"
echo "------------------"
for METHOD in ${METHODS[@]}
do
  python -m produit_derive_lidar.ip_multiprocessing \
      -or ${INPUT} \
      -i ${BUFFERED_DIR} \
      -o ${DTM_DIR} \
      -m ${METHOD} \
      -t ${TMP_DIR} \
      -e ${FORMAT} \
      -s ${PIXEL_SIZE} \
      --cpu_limit ${CPU_LIMIT}
done


echo "------------------"
echo "RUN DSM GENERATION"
echo "------------------"


# Output filenames for each step
FILTERED_DIR=${OUTPUT}/upground
BUFFERED_DIR=${OUTPUT}/upground_with_buffer
TMP_DIR=${OUTPUT}/tmp/DSM
DSM_DIR=${OUTPUT}/DSM

# Step 2.1 : filter ground + upground
python -m produit_derive_lidar.filter_multiprocessing \
    -i ${INPUT} \
    -o ${FILTERED_DIR} \
    -e ${FORMAT} \
    --keep_classes 2 3 4 5 6 9 17 \
    --cpu_limit ${CPU_LIMIT}

# Step 2.2: Create las with buffer from its neighbors tiles
#/!\ rasters generated from these las tiles will need to be cropped to match the input las area
# Extension is not provided as intermediate fles are las files
python -m produit_derive_lidar.add_buffer_multiprocessing \
    -i ${FILTERED_DIR} \
    -o ${BUFFERED_DIR} \
    -b 100 \
    --cpu_limit ${CPU_LIMIT}

# # Step 2.3 ; create DTM with the severals method
for METHOD in ${METHODS[@]}
do
  python -m produit_derive_lidar.ip_multiprocessing \
      -or ${INPUT} \
      -i ${BUFFERED_DIR} \
      -o ${DSM_DIR} \
      -m ${METHOD} \
      -t ${TMP_DIR} \
      -e ${FORMAT} \
      -s ${PIXEL_SIZE} \
    --cpu_limit ${CPU_LIMIT}
done

echo "------------------"
echo "RUN DHM GENERATION"
echo "------------------"


# # Step 4 ; create DHM with the severals method
# Output filenames for each step
DHM_DIR=${OUTPUT}/DHM

for METHOD in ${METHODS[@]}
do
  python -m produit_derive_lidar.dhm_multiprocessing \
      -or ${INPUT} \
      -is ${DSM_DIR} \
      -it ${DTM_DIR} \
      -m ${METHOD} \
      -o ${DHM_DIR} \
      -e ${FORMAT} \
      -s ${PIXEL_SIZE} \
    --cpu_limit ${CPU_LIMIT}
done